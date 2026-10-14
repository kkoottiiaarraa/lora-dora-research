"""Bounded radial factorial decision screen/validation; no training/generation."""
import argparse,datetime,gc,hashlib,importlib.metadata,json,os,resource,signal,sys,time
from pathlib import Path
os.environ.update(CUDA_VISIBLE_DEVICES='',OMP_NUM_THREADS='8',MKL_NUM_THREADS='8',OPENBLAS_NUM_THREADS='8',HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',TOKENIZERS_PARALLELISM='false')
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from lora_dora_study.server import write_json,available_memory_bytes
from lora_dora_study.evaluation import sha256_file


def main(root):
    start=time.monotonic();summary=dict(status='running',phase='setup',gpu_hours=0,training=False,cpu_threads=8,started_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
    def save():summary.update(wall_seconds=time.monotonic()-start,peak_rss_bytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024);write_json(root/'summary.json',summary)
    def timeout(s,f):raise TimeoutError('Bounded CPU stage deadline')
    signal.signal(signal.SIGALRM,timeout);signal.setitimer(signal.ITIMER_REAL,1800);save()
    try:
        m=json.loads((root/'manifest-private.json').read_text())
        signal.setitimer(signal.ITIMER_REAL,1200 if m['phase']=='development'else 1800)
        for rel,h in m['source_sha256'].items():
            if sha256_file(ROOT/rel)!=h:raise ValueError('Frozen source changed:'+rel)
        import torch
        from transformers import AutoModelForCausalLM,AutoTokenizer
        from peft import PeftModel
        from lora_dora_study.adapters import verify_loaded_adapter
        from lora_dora_study.fidelity_audit import content_digest,metrics,convert_custom
        from lora_dora_study.benchmarks import user_content
        from lora_dora_study.radial_factorial import CONDITIONS,radial_scale
        torch.set_num_threads(8);torch.set_num_interop_threads(1);torch.manual_seed(20261014);torch.set_float32_matmul_precision('highest')
        versions={k:importlib.metadata.version(k)for k in m['versions']}
        if versions!=m['versions']:raise ValueError('Versions changed')
        if available_memory_bytes()<64*1024**3:raise BlockingIOError('Need64GiB available RAM')
        if m['phase']=='development':
            path=Path(m['development_cases'])
            if sha256_file(path)!=m['development_cases_sha256']:raise ValueError('Cases changed')
            cases=json.loads(path.read_text())[:8]
            if len(cases)!=8:raise ValueError('Development coverage')
            exclusion=None
        else:
            data={}
            for split in ['train','test']:
                entry=m[split];path=Path(entry['path'])
                if sha256_file(path)!=entry['sha256']:raise ValueError('Dataset changed')
                data[split]=[json.loads(x)for x in path.read_text().splitlines()]
            excluded={content_digest(r)for r in data['test']+data['train'][:232]};files=[]
            # Snapshot all previous own case collections before writing the new one.
            for path in sorted(Path(m['previous_case_root']).rglob('*cases*.json')):
                if root==path.parent or root in path.parents:continue
                try:j=json.loads(path.read_text())
                except (json.JSONDecodeError,UnicodeDecodeError):continue
                if not isinstance(j,list):continue
                used={r['prompt_content_sha256']for r in j if isinstance(r,dict)and 'prompt_content_sha256'in r}
                if used:excluded|=used;files.append(dict(path=str(path),sha256=sha256_file(path),hash_count=len(used)))
            exclusion=dict(content_hashes=sorted(excluded),case_files=files)
            write_json(root/'exclusions-private.json',exclusion)
            tok=AutoTokenizer.from_pretrained(m['base']['snapshot_path'],local_files_only=True,trust_remote_code=False)
            cases=[];selected=set()
            for idx,row in enumerate(data['train']):
                h=content_digest(row)
                if h in excluded or h in selected:continue
                text=tok.apply_chat_template([dict(role='user',content=user_content('gsm8k',row))],tokenize=False,add_generation_prompt=True,enable_thinking=False)
                ids=tok(text,add_special_tokens=False)['input_ids'];targets=tok(row['answer'],add_special_tokens=False)['input_ids'][:32]
                if len(ids)>512 or len(targets)!=32:continue
                selected.add(h);cases.append(dict(train_index=idx,prompt_content_sha256=h,input_ids=ids+targets[:-1],targets=targets))
                if len(cases)==64:break
            if len(cases)!=64:raise ValueError('Fresh validation coverage')
            del tok,data
        if len({c['prompt_content_sha256']for c in cases})!=len(cases):raise ValueError('Duplicate cases')
        write_json(root/'cases.json',cases)
        frozen=dict(before_outputs=True,phase=m['phase'],conditions=list(CONDITIONS),cases_sha256=sha256_file(root/'cases.json'),source_sha256=m['source_sha256'],
            threshold=.001,artifacts={role:{k:v[k]for k in ['repo_id','revision']}for role,v in [('base',m['base']),('dora',m['dora'])]},
            exclusions_sha256=hashlib.sha256(json.dumps(exclusion['content_hashes']).encode()).hexdigest()if exclusion else None,
            excluded_content_hashes=len(exclusion['content_hashes'])if exclusion else None)
        write_json(root/'frozen.json',frozen);summary.update(frozen_sha256=sha256_file(root/'frozen.json'),versions=versions,case_count=len(cases),phase='load');save()
        model=AutoModelForCausalLM.from_pretrained(m['base']['snapshot_path'],local_files_only=True,trust_remote_code=False,torch_dtype=torch.float32,device_map={'':'cpu'},low_cpu_mem_usage=True,attn_implementation='sdpa')
        model=PeftModel.from_pretrained(model,m['dora']['snapshot_path'],local_files_only=True,is_trainable=False).eval();model.requires_grad_(False)
        audit=verify_loaded_adapter(model,m['dora']['snapshot_path'],True)
        if audit['adapted_module_count']!=m['modules']or not audit['exact_loaded_value_match']:raise ValueError('Adapter mismatch')
        write_json(root/'adapter-audit.json',audit)
        if any(p.dtype!=torch.float32 or p.device.type!='cpu'for p in model.parameters()):raise ValueError('Require CPUFP32')
        def run(case):
            ids=torch.tensor([case['input_ids']])
            with torch.inference_mode():y=model(input_ids=ids,attention_mask=torch.ones_like(ids),use_cache=False,logits_to_keep=32).logits[0].detach()
            if not bool(y.isfinite().all()):raise FloatingPointError('Nonfinite logits')
            return y
        native=[run(c)for c in cases[:2]]
        if not torch.equal(native[0],run(cases[0])):raise ValueError('Native repeat')
        parts={};records=[]
        with torch.no_grad():
            for name,module in model.named_modules():
                if not hasattr(module,'use_dora')or not module.use_dora.get('default',False):continue
                if module.get_base_layer().bias is not None:raise ValueError('Bias-free projection required')
                w=module.get_base_layer().weight.detach();u=w+(module.lora_B['default'].weight@module.lora_A['default'].weight)*module.scaling['default'];a=w.norm(dim=1);n=u.norm(dim=1);mag=module.lora_magnitude_vector['default'].weight.detach().clone()
                parts[name]=dict(u=u.clone(),a=a.clone(),n=n.clone(),m=mag)
                l=(mag/a).log().double();nn=(a/n).log().double();dd=(mag/n).log().double()
                records.append(dict(module=name,coordinates=len(a),log_l_energy=float(l.square().sum()),log_n_energy=float(nn.square().sum()),log_d_energy=float(dd.square().sum()),log_l_n_inner=float((l*nn).sum()),rounded_init_equal=int((mag==a.to(torch.bfloat16).float()).sum())))
        write_json(root/'radial-components.json',records)
        from lora_dora_study.fidelity_audit import without_d
        native_conditions={}
        for condition in CONDITIONS[1:]:
            if condition=='remove_d':
                with without_d(model):native_conditions[condition]=[run(c)for c in cases[:2]]
            else:
                try:
                    with torch.no_grad():
                        for name,p in parts.items():
                            ref=p['a'].to(torch.bfloat16).float()if condition.endswith('rounded')else p['a']
                            value=ref if condition.startswith('reset_m')else (p['m']/ref)*p['n']
                            model.get_submodule(name).lora_magnitude_vector['default'].weight.copy_(value)
                    native_conditions[condition]=[run(c)for c in cases[:2]]
                finally:
                    with torch.no_grad():
                        for name,p in parts.items():model.get_submodule(name).lora_magnitude_vector['default'].weight.copy_(p['m'])
        verify_loaded_adapter(model,m['dora']['snapshot_path'],True)
        convert_custom(model)
        originals={name:model.get_submodule(name).weight.detach().clone()for name in parts}
        def set_condition(condition,gauge=1.):
            with torch.no_grad():
                for name,p in parts.items():
                    mag=p['m']*(gauge if name.endswith('v_proj')else 1/gauge if name.endswith('o_proj')else 1.)
                    value=originals[name]if condition=='native'and gauge==1 else p['u']*radial_scale(mag,p['n'],p['a'],condition,torch.bfloat16)[:,None]
                    model.get_submodule(name).weight.copy_(value)
        controls=[]
        for i,c in enumerate(cases[:2]):controls.append(dict(kind='native_dense',case=i,**metrics(native[i],run(c),c['targets'])))
        for condition,refs in native_conditions.items():
            set_condition(condition)
            for i,c in enumerate(cases[:2]):controls.append(dict(kind='native_condition_dense',condition=condition,case=i,**metrics(refs[i],run(c),c['targets'])))
        for gauge in [.995,1.005]:
            set_condition('native',gauge)
            for i,c in enumerate(cases[:2]):controls.append(dict(kind='source_gauge',gauge=gauge,case=i,**metrics(native[i],run(c),c['targets'])))
        set_condition('native');rows=[];cache=root/'logit-cache';cache.mkdir()
        summary.update(phase='evaluation',conditions=[]);save()
        for condition in CONDITIONS:
            set_condition(condition);entry=dict(condition=condition,completed=0);summary['conditions'].append(entry);save()
            for i,c in enumerate(cases):
                y=run(c)
                if condition=='native':torch.save(y,cache/f'native-{i}.pt')
                ref=y if condition=='native'else torch.load(cache/f'native-{i}.pt',map_location='cpu',weights_only=True)
                rows.append(dict(condition=condition,case=i,prompt_content_sha256=c['prompt_content_sha256'],**metrics(ref,y,c['targets'])))
                if condition!='native':torch.save(y,cache/f'{condition}-{i}.pt')
                write_json(root/'rows.json',rows);entry['completed']=i+1;save()
        set_condition('native')
        restored=run(cases[0]);expected=torch.load(cache/'native-0.pt',map_location='cpu',weights_only=True)
        if not torch.equal(restored,expected):raise ValueError('Restoration changed')
        controls.append(dict(kind='restoration',case=0,bitwise=True,**metrics(expected,restored,cases[0]['targets'])))
        write_json(root/'controls.json',controls)
        summary.update(status='complete',phase='terminal',rows=len(rows),adapter_exact=True,native_repeat_bitwise=True,restoration_bitwise=True,model_released=True);save()
        del model,parts,originals;gc.collect()
    except Exception as exc:summary.update(status='failed',error=repr(exc));save();raise
    finally:signal.setitimer(signal.ITIMER_REAL,0)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);main(p.parse_args().root)
