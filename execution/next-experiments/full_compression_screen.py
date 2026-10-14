#!/usr/bin/env python3
"""Capture, prepare, evaluate full adapter compression controls on CPU."""
import argparse
import datetime
import importlib.metadata
import json
import os
from pathlib import Path
import resource
import signal
import subprocess
import sys
import time

os.environ.update(CUDA_VISIBLE_DEVICES='', OMP_NUM_THREADS='4', MKL_NUM_THREADS='4',
    OPENBLAS_NUM_THREADS='4', HF_HUB_OFFLINE='1', TRANSFORMERS_OFFLINE='1', TOKENIZERS_PARALLELISM='false')
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from lora_dora_study.server import write_json, available_memory_bytes
from lora_dora_study.evaluation import sha256_file


def main(root,phase):
    out=root/phase;out.mkdir(exist_ok=False);start=time.monotonic()
    summary=dict(status='running',phase=phase,conditions=[],training=False,gpu_count=0,
        started_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
    def save():
        summary.update(wall_seconds=time.monotonic()-start,
                       rss_bytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024)
        write_json(out/'summary.json',summary)
    def timeout(signum,frame):raise TimeoutError('Full compression phase deadline')
    signal.signal(signal.SIGALRM,timeout);signal.setitimer(signal.ITIMER_REAL,1800 if phase=='capture' else 3600)
    save()
    try:
        manifest=json.loads((root/'manifest-private.json').read_text())
        parent=Path(manifest['parent_root']);old=json.loads((parent/'manifest-private.json').read_text())
        for rel,digest in manifest['source_sha256'].items():
            if sha256_file(ROOT/rel)!=digest:raise ValueError('Frozen source changed: '+rel)
        import torch
        torch.set_num_threads(4 if phase=='prepare' else 16);torch.set_num_interop_threads(1)
        torch.manual_seed(20261013);torch.set_float32_matmul_precision('highest')
        versions={k:importlib.metadata.version(k) for k in old['versions']}
        if versions!=old['versions']:raise ValueError('Versions changed')
        summary.update(versions=versions,cpu_threads=torch.get_num_threads(),source_sha256=manifest['source_sha256'])
        from lora_dora_study.full_compression import adapted_modules,structural_ranks,thin_weighted_factors,replace_all
        from lora_dora_study.weighted_compression import covariance_cholesky,weighted_factors
        from lora_dora_study.compression_audit import decompose
        from lora_dora_study.fidelity_audit import metrics,content_digest
        from lora_dora_study.rank_symmetry import effective_weight
        if available_memory_bytes()<64*1024**3:raise BlockingIOError('Need 64GiB available RAM')
        if phase=='prepare':
            capture=json.loads((root/'capture/summary.json').read_text())
            if capture['status']!='complete':raise ValueError('Capture incomplete')
            shapes={r['name']:r['shape'] for r in capture['modules']}
            structural={r:structural_ranks(shapes,r) for r in [16,8]}
            factors={f'{method}_{r}':{} for r in [16,8] for method in ['raw','weighted','structural']}
            controls={};diagnostics=[]
            for i,item in enumerate(capture['modules']):
                path=root/'capture'/item['file']
                if sha256_file(path)!=item['sha256']:raise ValueError('Capture tensor changed')
                data=torch.load(path,map_location='cpu',weights_only=True);name=item['name']
                l,ridge=covariance_cholesky(data['inputs'])
                raw=decompose(data['base'],data['value'],16)
                wl,wr,wi=weighted_factors(data['value']-data['base'],l,16)
                source_left=data['b'].double()*data['scaling']*data['row_scale'].double()[:,None]
                sf,si=thin_weighted_factors(source_left,data['a'],l,16)
                for r in [16,8]:
                    for method,pair in [('raw',dict(left=raw['left'],right=raw['right'])),
                                        ('weighted',dict(left=wl,right=wr)),('structural',sf)]:
                        k=structural[r][name] if method=='structural' else r
                        record=dict(left=pair['left'][:,:k].clone(),right=pair['right'][:k].clone())
                        if method=='structural':record['row_scale']=data['row_scale'].clone()
                        factors[f'{method}_{r}'][name]=record
                controls[name]=dict(left=(data['b']*data['scaling']*data['row_scale'][:,None]).contiguous(),
                                    right=data['a'],row_scale=data['row_scale'])
                diagnostics.append(dict(module=name,shape=item['shape'],ridge=ridge,
                    calibration_tokens=len(data['inputs']),raw_rank16_squared_tail=raw['info']['expected_squared_residual'],
                    weighted_rank16_squared_tail=wi['expected_squared_tail'],
                    structural_rank16_squared_tail=si['ideal_weighted_squared_tail']))
                summary.update(modules_completed=i+1,average_seconds_per_module=(time.monotonic()-start)/(i+1));save()
            budgets={r:r*sum(sum(s) for s in shapes.values()) for r in [16,8]}
            counts={label:sum(t.numel() for record in modules.values() for t in record.values())
                    for label,modules in factors.items()}
            for label,count in counts.items():
                if count!=budgets[int(label.rsplit('_',1)[1])]:raise ValueError('Factor budget mismatch')
            torch.save(factors,out/'factors.pt');torch.save(controls,out/'source-control.pt')
            write_json(out/'diagnostics.json',diagnostics)
            summary.update(status='complete',budgets=budgets,parameter_counts=counts,
                structural_ranks=structural,native_elements=capture['native_elements'],
                factors_sha256=sha256_file(out/'factors.pt'),controls_sha256=sha256_file(out/'source-control.pt'))
            save();return

        from transformers import AutoModelForCausalLM,AutoTokenizer
        from peft import PeftModel
        from lora_dora_study.adapters import verify_loaded_adapter
        model=AutoModelForCausalLM.from_pretrained(old['artifacts']['base']['snapshot_path'],
            local_files_only=True,trust_remote_code=False,torch_dtype=torch.float32,device_map={'':'cpu'},
            low_cpu_mem_usage=True,attn_implementation='sdpa')
        model=PeftModel.from_pretrained(model,old['artifacts']['dora']['snapshot_path'],
            local_files_only=True,is_trainable=False).eval();model.requires_grad_(False)
        check=verify_loaded_adapter(model,old['artifacts']['dora']['snapshot_path'],True)
        modules=adapted_modules(model)
        if not check['exact_loaded_value_match'] or len(modules)!=144 or check['adapted_module_count']!=144:
            raise ValueError('Full adapter load mismatch')
        if any(p.dtype!=torch.float32 or p.device.type!='cpu' for p in model.parameters()):
            raise ValueError('Unexpected dtype/device')
        summary.update(adapter_exact=True,load_seconds=time.monotonic()-start)
        def logits(case):
            ids=torch.tensor([case['input_ids']],dtype=torch.long)
            with torch.inference_mode():
                y=model(input_ids=ids,attention_mask=torch.ones_like(ids),use_cache=False,
                        logits_to_keep=32).logits[0].detach().float().cpu()
            if y.shape[0]!=32 or not bool(y.isfinite().all()):raise FloatingPointError('Invalid logits')
            return y
        calpath=Path(old['calibration_cases'])
        if sha256_file(calpath)!=old['calibration_cases_sha256']:raise ValueError('Calibration inputs changed')
        cal=json.loads(calpath.read_text())
        for i in range(4):
            expected=torch.load(parent/'capture/logit-cache'/f'original-{i}.pt',weights_only=True,map_location='cpu')
            if not torch.equal(logits(cal[i]),expected):raise ValueError('Reference execution changed')
        if phase=='capture':
            train=[json.loads(s) for s in Path(old['train']['path']).read_text().splitlines()]
            test=[json.loads(s) for s in Path(old['test']['path']).read_text().splitlines()]
            for label in ['train','test']:
                if sha256_file(Path(old[label]['path']))!=old[label]['sha256']:raise ValueError('Dataset changed')
            excluded={content_digest(r) for r in train[:232]+test}|{r['prompt_content_sha256'] for r in cal}
            for path in [parent/'validation-cases.json',Path(manifest['anchored_root'])/'validation-cases.json',
                         Path(manifest['budget_root'])/'prepare/cases.json']:
                excluded|={r['prompt_content_sha256'] for r in json.loads(path.read_text())}
            tokenizer=AutoTokenizer.from_pretrained(old['artifacts']['base']['snapshot_path'],
                local_files_only=True,trust_remote_code=False)
            from lora_dora_study.benchmarks import user_content
            cases=[]
            for index,row in enumerate(train):
                digest=content_digest(row)
                if digest in excluded:continue
                text=tokenizer.apply_chat_template([dict(role='user',content=user_content('gsm8k',row))],
                    tokenize=False,add_generation_prompt=True,enable_thinking=False)
                ids=tokenizer(text,add_special_tokens=False)['input_ids']
                targets=tokenizer(row['answer'],add_special_tokens=False)['input_ids'][:32]
                if len(ids)>512 or len(targets)<32:continue
                cases.append(dict(train_index=index,prompt_content_sha256=digest,input_ids=ids+targets[:-1],targets=targets))
                excluded.add(digest)
                if len(cases)==32:break
            if len(cases)!=32:raise ValueError('Insufficient fresh cases')
            write_json(root/'cases.json',cases)
            captured={n:[] for n in modules};hooks=[]
            def hook(name):
                def capture(module,arguments):
                    x=arguments[0].detach().reshape(-1,arguments[0].shape[-1])[-32:].float().cpu()
                    if not bool(x.isfinite().all()):raise FloatingPointError('Nonfinite activation')
                    captured[name].append(x.clone())
                return capture
            for name,module in modules.items():hooks.append(module.register_forward_pre_hook(hook(name)))
            for i,case in enumerate(cal):
                logits(case);summary.update(cases_completed=i+1);save()
            for h in hooks:h.remove()
            datafolder=out/'data';datafolder.mkdir();records=[];native=0
            for i,(name,module) in enumerate(modules.items()):
                base,value=effective_weight(module)
                a=module.lora_A['default'].weight.detach().float()
                b=module.lora_B['default'].weight.detach().float()
                u=base+(b@a)*module.scaling['default']
                d=(module.lora_magnitude_vector['default'].weight.detach().float()/u.norm(dim=1)).clone()
                count=a.numel()+b.numel()+d.numel();native+=count
                record=dict(base=base.clone(),value=value.clone(),a=a.clone(),b=b.clone(),row_scale=d,
                    scaling=float(module.scaling['default']),inputs=torch.cat(captured.pop(name)))
                if not all(bool(t.isfinite().all()) for t in record.values() if isinstance(t,torch.Tensor)):
                    raise FloatingPointError('Nonfinite source tensors')
                if not bool(torch.equal(value,u*d[:,None])):raise ValueError('DoRA reconstruction mismatch')
                path=datafolder/f'{i:03}.pt';torch.save(record,path)
                records.append(dict(name=name,file=str(path.relative_to(out)),sha256=sha256_file(path),
                                    shape=list(base.shape),native_elements=count))
                summary.update(saved_modules=i+1);save()
            summary.update(status='complete',modules=records,native_elements=native,
                cases_sha256=sha256_file(root/'cases.json'),full_adapter=True);save();return

        prep=json.loads((root/'prepare/summary.json').read_text())
        capture=json.loads((root/'capture/summary.json').read_text())
        if not (prep['status']==capture['status']=='complete'):raise ValueError('Parent phases incomplete')
        for name,key in [('factors.pt','factors_sha256'),('source-control.pt','controls_sha256')]:
            if sha256_file(root/'prepare'/name)!=prep[key]:raise ValueError('Prepared factors changed')
        if sha256_file(root/'cases.json')!=capture['cases_sha256']:raise ValueError('Cases changed')
        cases=json.loads((root/'cases.json').read_text())
        factors=torch.load(root/'prepare/factors.pt',map_location='cpu',weights_only=True)
        controls=torch.load(root/'prepare/source-control.pt',map_location='cpu',weights_only=True)
        cache=out/'logit-cache';cache.mkdir()
        for i,case in enumerate(cases):
            torch.save(logits(case),cache/f'original-{i}.pt');summary.update(current='reference',cases_completed=i+1);save()
        control_rows=[]
        with replace_all(model,controls):
            for i in range(2):
                reference=torch.load(cache/f'original-{i}.pt',weights_only=True)
                control_rows.append(dict(kind='structural_rank32_source',case=i,
                    **metrics(reference,logits(cases[i]),cases[i]['targets'])))
        factorized=[]
        with replace_all(model,factors['weighted_16']):
            for i in range(2):factorized.append(logits(cases[i]))
        with replace_all(model,factors['weighted_16'],dense=True):
            for i in range(2):control_rows.append(dict(kind='weighted_factorized_vs_dense',case=i,
                **metrics(factorized[i],logits(cases[i]),cases[i]['targets'])))
        write_json(out/'controls.json',control_rows)
        early_effect=sum(metrics(torch.load(cache/f'original-{i}.pt',weights_only=True),factorized[i],
                                 cases[i]['targets'])['rms'] for i in range(2))/2
        if max(r['rms'] for r in control_rows)>=.01*early_effect:raise ValueError('Early fidelity floor too large')
        all_rows=[]
        for label in factors:
            count=sum(t.numel() for r in factors[label].values() for t in r.values())
            if count!=prep['parameter_counts'][label]:raise ValueError('Actual deployment budget changed')
            record=dict(label=label,status='running',cases_completed=0,parameter_count=count)
            summary['conditions'].append(record);save()
            with replace_all(model,factors[label]):
                for i,case in enumerate(cases):
                    y=logits(case);reference=torch.load(cache/f'original-{i}.pt',weights_only=True)
                    row=dict(label=label,case=i,**metrics(reference,y,case['targets']));all_rows.append(row)
                    with (out/'per-case.jsonl').open('a') as stream:stream.write(json.dumps(row)+'\n')
                    record['cases_completed']=i+1;save()
            own=[r for r in all_rows if r['label']==label]
            record.update(status='complete',mean_kl=sum(r['kl_reference_to_changed'] for r in own)/32,
                mean_nll_delta=sum(r['nll_difference'] for r in own)/32,
                mean_rms=sum(r['rms'] for r in own)/32,
                argmax_disagreements=sum(r['argmax_disagreements'] for r in own));save()
        floor=max(r['rms'] for r in control_rows);minimum=min(r['mean_rms'] for r in summary['conditions'])
        if floor>=.01*minimum:raise ValueError('Fidelity floor >=1% minimum compression effect')
        summary.update(status='complete',cases_sha256=capture['cases_sha256'],controls_max_rms=floor,
            minimum_compression_rms=minimum,full_task_accuracy=False,full_adapter=True);save()
    except Exception as exc:
        summary.update(status='failed',error=repr(exc));save();raise
    finally:signal.setitimer(signal.ITIMER_REAL,0)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True)
    p.add_argument('--phase',choices=['capture','prepare','evaluate','all'],required=True);a=p.parse_args()
    if a.phase!='all':
        main(a.root,a.phase)
    else:
        state=dict(status='running',phases=[],gpu_count=0)
        write_json(a.root/'state.json',state)
        try:
            for phase in ['capture','prepare','evaluate']:
                state['current_phase']=phase;write_json(a.root/'state.json',state)
                start=time.monotonic()
                with (a.root/(phase+'.log')).open('x') as log:
                    r=subprocess.run([sys.executable,__file__,'--root',str(a.root),'--phase',phase],
                        stdout=log,stderr=subprocess.STDOUT,timeout=(1920 if phase=='capture' else 3720))
                state['phases'].append(dict(phase=phase,exit_code=r.returncode,wall_seconds=time.monotonic()-start))
                if r.returncode:raise RuntimeError('Phase failed: '+phase)
            state.update(status='complete',current_phase=None)
        except Exception as exc:
            state.update(status='failed',error=repr(exc));raise
        finally:write_json(a.root/'state.json',state)
