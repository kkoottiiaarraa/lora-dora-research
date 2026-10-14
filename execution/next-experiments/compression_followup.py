#!/usr/bin/env python3
"""Capture calibration, prepare frozen approximations, then select and validate."""
import argparse
import csv
import datetime
import importlib.metadata
import json
import os
from pathlib import Path
import resource
import signal
import sys
import time

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
os.environ.update(OMP_NUM_THREADS='4',MKL_NUM_THREADS='4',OPENBLAS_NUM_THREADS='4',
                  TOKENIZERS_PARALLELISM='false',HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1')
from lora_dora_study.server import write_json,available_memory_bytes
from lora_dora_study.evaluation import sha256_file


def main(a):
    root=a.root;out=root/a.phase;out.mkdir(exist_ok=False)
    start=time.monotonic()
    def deadline(signum,frame):raise TimeoutError('Phase time budget exhausted')
    signal.signal(signal.SIGALRM,deadline);signal.setitimer(signal.ITIMER_REAL,a.budget_seconds)
    status=dict(status='running',phase=a.phase,started_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                conditions=[],training=False,full_evaluation=False)
    def save():
        status.update(wall_seconds=time.monotonic()-start,rss_bytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024)
        write_json(out/'summary.json',status)
    save()
    try:
        manifest=json.loads((root/'manifest-private.json').read_text())
        for rel,h in manifest['source_sha256'].items():
            if sha256_file(ROOT/rel)!=h:raise ValueError('Frozen source changed: '+rel)
        import torch
        torch.set_num_threads(4 if a.phase=='prepare' else 16)
        torch.set_num_interop_threads(1);torch.manual_seed(20261013)
        status['cpu_threads']=torch.get_num_threads()
        torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False
        torch.set_float32_matmul_precision('highest')
        from lora_dora_study.compression_audit import selected_modules,scoped_gauge,replacement,decompose
        from lora_dora_study.fidelity_audit import metrics,content_digest
        from lora_dora_study.rank_symmetry import effective_weight
        from lora_dora_study.weighted_compression import covariance_cholesky,weighted_factors
        versions={k:importlib.metadata.version(k) for k in ['torch','transformers','peft','safetensors','accelerate']}
        if versions!=manifest['versions']:raise ValueError('Software versions changed')
        status.update(versions=versions,source_sha256=manifest['source_sha256'])
        layers=[0,17,35]
        if a.phase=='prepare':
            capture=torch.load(root/'capture/matrices.pt',map_location='cpu',weights_only=True)
            activations=torch.load(root/'capture/activations.pt',map_location='cpu',weights_only=True)
            diagnostics=[];all_factors={}
            for name,record in capture.items():
                x=activations[name];l,ridge=covariance_cholesky(x,.001)
                for c in [1.,.995,1.005]:
                    scale=c if name.endswith('v_proj') else 1/c
                    delta=record['value']*scale-record['base']
                    raw=decompose(record['base'],record['base']+delta,32)
                    # Native O input scales by c; V input is unchanged under this symmetry.
                    lc=l*(c if name.endswith('o_proj') else 1.)
                    left,right,info=weighted_factors(delta,lc,32)
                    for method,pair in [('svd',(raw['left'],raw['right'])),('weighted',(left,right))]:
                        label=method+'_'+str(c)
                        all_factors.setdefault(label,{})[name]=dict(left=pair[0],right=pair[1])
                    diagnostics.append(dict(module=name,c=c,ridge=ridge,calibration_tokens=len(x),
                        raw_energy_ranks=raw['info']['energy_ranks'],factor_elements=left.numel()+right.numel(),
                        source_adapter_elements=record['source_adapter_elements'],**info))
                    status.update(modules_completed=len(diagnostics));save()
            torch.save(all_factors,out/'factors.pt')
            write_json(out/'diagnostics.json',diagnostics)
            status.update(status='complete',factors_sha256=sha256_file(out/'factors.pt'),rank=32,
                          methods=list(all_factors),modules=6);save();return

        from transformers import AutoModelForCausalLM,AutoTokenizer
        from peft import PeftModel
        from lora_dora_study.adapters import verify_loaded_adapter
        allocation=json.loads((root/(a.phase+'-allocation-private.json')).read_text())
        gpu=allocation['mode']=='cuda'
        if gpu and not os.environ.get('CUDA_VISIBLE_DEVICES'):raise ValueError('Missing GPU visibility')
        if not gpu and available_memory_bytes()<64*1024**3:raise BlockingIOError('Need 64GiB CPU RAM')
        paths={k:v['snapshot_path'] for k,v in manifest['artifacts'].items()}
        # Balanced placement shrinks the larger GPU's usable cap on unequal cards.
        # Sequential placement retains both measured caps and keeps tied weights together.
        kwargs=dict(device_map='sequential',max_memory={i:int(g['max_memory_bytes']) for i,g in enumerate(allocation['gpus'])}) if gpu else dict(device_map={'':'cpu'})
        model=AutoModelForCausalLM.from_pretrained(paths['base'],local_files_only=True,trust_remote_code=False,
            torch_dtype=torch.float32,low_cpu_mem_usage=True,attn_implementation='sdpa',**kwargs)
        if gpu and any(str(v) in ['cpu','disk'] for v in model.hf_device_map.values()):
            raise ValueError('Unexpected CPU/disk offload in CUDA reference')
        model=PeftModel.from_pretrained(model,paths['dora'],local_files_only=True,is_trainable=False).eval()
        model.requires_grad_(False)
        check=verify_loaded_adapter(model,paths['dora'],True)
        if not check['exact_loaded_value_match'] or check['adapted_module_count']!=144:raise ValueError('Adapter load mismatch')
        if model.config.num_hidden_layers!=36 or model.config.attention_bias:raise ValueError('Unexpected architecture')
        if any(p.dtype!=torch.float32 for p in model.parameters()):raise ValueError('Not FP32')
        status.update(device='cuda_fp32' if gpu else 'cpu_fp32',adapter_exact=True,
                      load_seconds=time.monotonic()-start)
        input_device=model.get_input_embeddings().weight.device
        canaries=[]
        if gpu:
            for i in range(len(allocation['gpus'])):
                canaries.append(torch.full((16*1024*1024,),.125,dtype=torch.float32,device='cpu').to('cuda:'+str(i)))
        def canary():
            if any(not bool((x.cpu()==.125).all()) for x in canaries):raise FloatingPointError('Device buffer changed')
        canary()
        def logits(case):
            x=torch.tensor([case['input_ids']],dtype=torch.long,device=input_device)
            with torch.inference_mode():
                y=model(input_ids=x,attention_mask=torch.ones_like(x),use_cache=False,
                        logits_to_keep=32).logits[0].detach().float().cpu()
            if y.shape[0]!=32 or not bool(y.isfinite().all()):raise FloatingPointError('Nonfinite/misaligned logits')
            return y
        cal=json.loads(Path(manifest['calibration_cases']).read_text())
        if sha256_file(Path(manifest['calibration_cases']))!=manifest['calibration_cases_sha256']:raise ValueError('Calibration inputs changed')
        cache=out/'logit-cache';cache.mkdir()
        if a.phase=='capture':
            # Freeze validation inputs before any method scores, but do not run them yet.
            train=[json.loads(x) for x in Path(manifest['train']['path']).read_text().splitlines()]
            test=[json.loads(x) for x in Path(manifest['test']['path']).read_text().splitlines()]
            for label in ['train','test']:
                if sha256_file(Path(manifest[label]['path']))!=manifest[label]['sha256']:raise ValueError('Dataset changed')
            excluded={content_digest(r) for r in test+train[:232]}|{r['prompt_content_sha256'] for r in cal}
            tokenizer=AutoTokenizer.from_pretrained(paths['base'],local_files_only=True,trust_remote_code=False)
            from lora_dora_study.benchmarks import user_content
            validation=[];skips=[]
            for index,row in enumerate(train):
                h=content_digest(row)
                if h in excluded:continue
                prompt=tokenizer.apply_chat_template([dict(role='user',content=user_content('gsm8k',row))],
                    tokenize=False,add_generation_prompt=True,enable_thinking=False)
                ids=tokenizer(prompt,add_special_tokens=False)['input_ids']
                targets=tokenizer(row['answer'],add_special_tokens=False)['input_ids'][:32]
                if len(ids)>512 or len(targets)<32:
                    skips.append(dict(index=index,reason='prompt>512 or answer<32tokens'));continue
                validation.append(dict(train_index=index,prompt_content_sha256=h,input_ids=ids+targets[:-1],targets=targets))
                excluded.add(h)
                if len(validation)==64:break
            if len(validation)!=64:raise ValueError('Insufficient unseen train cases')
            write_json(root/'validation-cases.json',validation)
            status.update(validation_cases_sha256=sha256_file(root/'validation-cases.json'),structural_skips=skips)
            activations={name:[] for name in selected_modules(model,layers)};hooks=[]
            def hook(name):
                def capture(module,arguments):
                    x=arguments[0].detach().reshape(-1,arguments[0].shape[-1])[-32:].float().cpu()
                    if not bool(x.isfinite().all()):raise FloatingPointError('Nonfinite activations')
                    activations[name].append(x)
                return capture
            for name,module in selected_modules(model,layers).items():hooks.append(module.register_forward_pre_hook(hook(name)))
            for i,case in enumerate(cal):
                torch.save(logits(case),cache/f'original-{i}.pt')
                status['cases_completed']=i+1
                if (i+1)%8==0:canary()
                save()
            for h in hooks:h.remove()
            matrices={}
            for name,module in selected_modules(model,layers).items():
                base,value=effective_weight(module)
                matrices[name]=dict(base=base.cpu().clone(),value=value.cpu().clone(),
                    source_adapter_elements=sum(p.numel() for p in [module.lora_A['default'].weight,module.lora_B['default'].weight,module.lora_magnitude_vector['default'].weight]))
            torch.save(matrices,out/'matrices.pt')
            torch.save({n:torch.cat(x) for n,x in activations.items()},out/'activations.pt')
            status.update(status='complete',matrices_sha256=sha256_file(out/'matrices.pt'),
                          activations_sha256=sha256_file(out/'activations.pt'));canary();save();return

        factors=torch.load(root/'prepare/factors.pt',map_location='cpu',weights_only=True)
        prepare=json.loads((root/'prepare/summary.json').read_text())
        if prepare['status']!='complete' or sha256_file(root/'prepare/factors.pt')!=prepare['factors_sha256']:raise ValueError('Preparation incomplete/changed')
        original={};metrics_rows=[]
        def original_logits(split,cases):
            # Recompute in this execution; never mix CUDA/CPU references.
            for i,case in enumerate(cases):
                y=logits(case);path=cache/f'{split}-original-{i}.pt';torch.save(y,path)
                original[split,i]=path
                status.update(current_condition=split+'_original',cases_completed=i+1);save()
                if (i+1)%8==0:canary()
        original_logits('calibration',cal)
        def run(split,cases,label):
            record=dict(split=split,label=label,status='running',cases_completed=0)
            status['conditions'].append(record);save()
            device_records={}
            for name,module in selected_modules(model,layers).items():
                dev=module.get_base_layer().weight.device
                r=factors[label][name]
                device_records[name]=dict(base=module.get_base_layer().weight.detach(),left=r['left'].to(dev),right=r['right'].to(dev))
            begin=time.monotonic()
            with replacement(model,layers,'factorized',device_records):
                for i,case in enumerate(cases):
                    y=logits(case);reference=torch.load(original[split,i],map_location='cpu',weights_only=True)
                    row=dict(split=split,label=label,case=i,**metrics(reference,y,case['targets']))
                    metrics_rows.append(row)
                    with (out/'per-case.jsonl').open('a') as f:f.write(json.dumps(row)+'\n')
                    record.update(cases_completed=i+1,elapsed_seconds=time.monotonic()-begin);save()
                    if (i+1)%8==0:canary()
            record.update(status='complete',mean_kl=sum(r['kl_reference_to_changed'] for r in metrics_rows if r['split']==split and r['label']==label)/len(cases));save()
        # Full source-gauge controls at four cases, before method comparison.
        controls=[]
        for c in [.995,1.005]:
            with scoped_gauge(model,layers,c):
                for i,case in enumerate(cal[:4]):
                    y=logits(case);ref=torch.load(original['calibration',i],map_location='cpu',weights_only=True)
                    controls.append(dict(c=c,case=i,**metrics(ref,y,case['targets'])))
        if max(r['rms'] for r in controls)>.0006:raise ValueError('FP32 gauge control failed')
        status['gauge_controls']=controls;save()
        for label in factors:run('calibration',cal,label)
        means={r['label']:r['mean_kl'] for r in status['conditions'] if r['split']=='calibration'}
        # Tie preference to c=1 prevents arbitrary changes for equal scores.
        chosen={method:min([method+'_'+str(c) for c in [1.,.995,1.005]],key=lambda x:(means[x],x!=method+'_1.0')) for method in ['svd','weighted']}
        selection=dict(rule='minimum mean full-vocabulary calibration KL, three fixed scales; c=1 tie preference',
            chosen=chosen,calibration_mean_kl=means,factors_sha256=prepare['factors_sha256'],
            validation_cases_sha256=sha256_file(root/'validation-cases.json'),frozen_before_validation=True)
        write_json(root/'selection.json',selection)
        selection_sha=sha256_file(root/'selection.json')
        status.update(selection=selection,selection_sha256=selection_sha);save()
        val=json.loads((root/'validation-cases.json').read_text())
        assert len(val)==64 and not ({r['prompt_content_sha256'] for r in val}&{r['prompt_content_sha256'] for r in cal})
        original_logits('validation',val)
        selected=list(dict.fromkeys(['svd_1.0','weighted_1.0',chosen['svd'],chosen['weighted']]))
        for label in selected:run('validation',val,label)
        if sha256_file(root/'selection.json')!=selection_sha:raise ValueError('Selection changed after unblinding')
        with (out/'metrics.csv').open('w') as f:
            w=csv.DictWriter(f,fieldnames=list(metrics_rows[0]));w.writeheader();w.writerows(metrics_rows)
        status.update(status='complete',validation_evaluated_labels=selected,
                      gpu_peak_allocated_bytes=[torch.cuda.max_memory_allocated(i) for i in range(len(allocation['gpus']))] if gpu else [])
        canary();save()
    except Exception as exc:
        status.update(status='failed',error=repr(exc));save();raise
    finally:signal.setitimer(signal.ITIMER_REAL,0)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True)
    p.add_argument('--phase',choices=['capture','prepare','evaluate'],required=True)
    p.add_argument('--budget-seconds',type=int,required=True)
    main(p.parse_args())
