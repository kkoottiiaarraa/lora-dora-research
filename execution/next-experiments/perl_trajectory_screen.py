"""Frozen three-checkpoint inference-role screen; no training or generation."""
import argparse,datetime,gc,hashlib,importlib.metadata,json,os,resource,signal,sys,time
from pathlib import Path
os.environ.update(CUDA_VISIBLE_DEVICES='',OMP_NUM_THREADS='8',MKL_NUM_THREADS='8',OPENBLAS_NUM_THREADS='8',HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',TOKENIZERS_PARALLELISM='false')
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from lora_dora_study.server import write_json,available_memory_bytes
from lora_dora_study.evaluation import sha256_file


def main(root):
    start=time.monotonic();summary=dict(status='running',phase='setup',gpu_hours=0,training=False,cpu_threads=8,started_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
    def save():summary.update(wall_seconds=time.monotonic()-start,peak_rss_bytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024);write_json(root/'summary.json',summary)
    def timeout(s,f):raise TimeoutError('CPU20min cap')
    signal.signal(signal.SIGALRM,timeout);signal.setitimer(signal.ITIMER_REAL,1200);save()
    try:
        m=json.loads((root/'manifest-private.json').read_text())
        for rel,h in m['source_sha256'].items():
            if sha256_file(ROOT/rel)!=h:raise ValueError('Source changed')
        if sha256_file(Path(m['train']))!=m['train_sha256']:raise ValueError('Train changed')
        if sha256_file(Path(m['test']))!=m['test_sha256']:raise ValueError('Test changed')
        provenance=json.loads((root/'download-result-private.json').read_text())
        if provenance['status']!='complete':raise ValueError('Downloads incomplete')
        if sha256_file(root/'download-result-private.json')!=m['provenance_sha256']:raise ValueError('Provenance changed')
        import torch
        from transformers import AutoTokenizer,AutoModelForCausalLM
        from peft import PeftModel
        from lora_dora_study.adapters import verify_loaded_adapter
        from lora_dora_study.fidelity_audit import content_digest,metrics,convert_custom
        torch.set_num_threads(8);torch.set_num_interop_threads(1);torch.manual_seed(20261014);torch.set_float32_matmul_precision('highest')
        if available_memory_bytes()<40*1024**3:raise BlockingIOError('Need40GiB RAM')
        versions={k:importlib.metadata.version(k)for k in m['versions']}
        if versions!=m['versions']:raise ValueError('Versions changed')
        paths={k:v['snapshot_path']for k,v in provenance['artifacts'].items()}
        states={s:json.loads((Path(paths[str(s)])/'trainer_state.json').read_text())for s in [64,512,1024]}
        if any(states[s]['global_step']!=s or len(states[s]['log_history'])!=s for s in states):raise ValueError('Trajectory steps')
        if any(states[s]['log_history']!=states[1024]['log_history'][:s]for s in [64,512]):raise ValueError('Not one logged trajectory')
        configs=[(Path(paths[str(s)])/'adapter_config.json').read_bytes()for s in states]
        if len(set(configs))!=1:raise ValueError('Configs differ')
        tok=AutoTokenizer.from_pretrained(paths['base'],local_files_only=True,trust_remote_code=False)
        train=[json.loads(l)for l in Path(m['train']).read_text().splitlines()];test=[json.loads(l)for l in Path(m['test']).read_text().splitlines()]
        excluded={content_digest(r)for r in test}|{content_digest(r)for r in train[:232]};cases=[]
        for idx,r in enumerate(train[232:],232):
            h=content_digest(r)
            if h in excluded:continue
            text=tok.apply_chat_template([dict(role='user',content=r['question'])],tokenize=False,add_generation_prompt=True)
            prompt=tok(text,add_special_tokens=False)['input_ids'];answer=tok(r['answer'],add_special_tokens=False)['input_ids']
            if len(answer)<32 or len(prompt)+31>512:continue
            excluded.add(h);cases.append(dict(case=len(cases),train_index=idx,prompt_content_sha256=h,input_ids=prompt+answer[:31],targets=answer[:32]))
            if len(cases)==16:break
        if len(cases)!=16:raise ValueError('Case coverage')
        write_json(root/'cases.json',cases)
        summary.update(versions=versions,cases_sha256=sha256_file(root/'cases.json'),source_sha256=m['source_sha256'],provenance_sha256=m['provenance_sha256'],steps=[64,512,1024])
        write_json(root/'frozen.json',dict(cases_sha256=summary['cases_sha256'],source_sha256=m['source_sha256'],provenance_sha256=m['provenance_sha256'],steps=[64,512,1024],before_outputs=True));save()
        cache=root/'logit-cache';cache.mkdir();rows=[];controls=[];parts=[]
        def load():
            model=AutoModelForCausalLM.from_pretrained(paths['base'],local_files_only=True,trust_remote_code=False,torch_dtype=torch.float32,device_map={'':'cpu'},low_cpu_mem_usage=True,attn_implementation='sdpa').eval()
            model.requires_grad_(False)
            if any(p.dtype!=torch.float32 or p.device.type!='cpu' or not bool(p.isfinite().all())for p in model.parameters()):raise ValueError('Invalid base parameters')
            return model
        def run(model,c):
            ids=torch.tensor([c['input_ids']])
            with torch.inference_mode():y=model(input_ids=ids,attention_mask=torch.ones_like(ids),use_cache=False,logits_to_keep=32).logits[0].detach()
            if not bool(y.isfinite().all()):raise FloatingPointError('Nonfinite logits')
            return y
        model=load();summary['phase']='base';save()
        for c in cases:torch.save(run(model,c),cache/f"base-{c['case']}.pt")
        del model;gc.collect()
        for step in [64,512,1024]:
            summary.update(phase='load',step=step);save();model=load()
            model=PeftModel.from_pretrained(model,paths[str(step)],local_files_only=True,is_trainable=False).eval();model.requires_grad_(False)
            audit=verify_loaded_adapter(model,paths[str(step)],True)
            if audit['adapted_module_count']!=196 or audit['saved_tensor_count']!=588:raise ValueError('Module coverage')
            if any(x['r']!=32 or x['scaling']!=2 for x in audit['modules']):raise ValueError('Rank/scaling')
            write_json(root/f'adapter-audit-{step}.json',audit)
            native=[run(model,c)for c in cases[:2]]
            if not torch.equal(native[0],run(model,cases[0])):raise ValueError('Repeat')
            directions={};base_norms={}
            with torch.no_grad():
                for name,module in model.named_modules():
                    if not hasattr(module,'use_dora')or not module.use_dora.get('default',False):continue
                    w=module.get_base_layer().weight.detach().float();u=w+(module.lora_B['default'].weight@module.lora_A['default'].weight)*module.scaling['default']
                    n=u.norm(dim=1);m0=w.norm(dim=1);mag=module.lora_magnitude_vector['default'].weight.detach().float();d=mag/n
                    if not bool((n>0).all()and(m0>0).all()and(mag>0).all()):raise ValueError('Invalid norms')
                    directions[name]=u.clone();base_norms[name]=m0.clone()
                    parts.append(dict(step=step,module=name,learned_log_rms=float((mag/m0).log().square().mean().sqrt()),normalization_log_rms=float((m0/n).log().square().mean().sqrt()),d_log_rms=float(d.log().square().mean().sqrt())))
            convert_custom(model)
            for i,c in enumerate(cases[:2]):controls.append(dict(step=step,case=i,kind='native_dense',**metrics(native[i],run(model,c),c['targets'])))
            originals={name:model.get_submodule(name).weight.detach().clone()for name in directions}
            for condition in ['native','remove_d','base_magnitude']:
                summary.update(phase=condition,completed=0);save()
                with torch.no_grad():
                    for name,u in directions.items():
                        value=originals[name]if condition=='native'else u if condition=='remove_d'else u*(base_norms[name]/u.norm(dim=1))[:,None]
                        model.get_submodule(name).weight.copy_(value)
                for c in cases:
                    y=run(model,c);i=c['case'];base=torch.load(cache/f'base-{i}.pt',map_location='cpu',weights_only=True)
                    if condition=='native':torch.save(y,cache/f'native-{step}-{i}.pt')
                    ref=y if condition=='native'else torch.load(cache/f'native-{step}-{i}.pt',map_location='cpu',weights_only=True)
                    r=dict(step=step,condition=condition,case=i,prompt_content_sha256=c['prompt_content_sha256'],**metrics(ref,y,c['targets']))
                    # Directed native||base denominator, same teacher as native||intervention.
                    base_metrics=metrics(ref,base,c['targets']);r['native_to_base_kl']=base_metrics['kl_reference_to_changed'];r['native_to_base_rms']=base_metrics['rms']
                    rows.append(r);write_json(root/'rows.json',rows);summary['completed']=i+1;save()
                if condition!='native':
                    with torch.no_grad():
                        for name,w in originals.items():model.get_submodule(name).weight.copy_(w)
                    if not torch.equal(run(model,cases[0]),torch.load(cache/f'native-{step}-0.pt',weights_only=True)):
                        raise ValueError('Restoration')
            write_json(root/'controls.json',controls);write_json(root/'radial-components.json',parts)
            del model,directions,base_norms,originals,native;gc.collect()
        summary.update(status='complete',phase='terminal',rows=len(rows),adapter_exact=True,repeat_bitwise=True,restoration_bitwise=True,model_released=True);save()
    except Exception as exc:summary.update(status='failed',error=repr(exc));save();raise
    finally:signal.setitimer(signal.ITIMER_REAL,0)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);main(p.parse_args().root)
