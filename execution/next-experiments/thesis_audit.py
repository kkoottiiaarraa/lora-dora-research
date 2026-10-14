#!/usr/bin/env python3
"""Train-only fixed-prefix audit. GPU stage exits before CPU reference/SVD.

No generation, training, downloads, test selection or full benchmark repeats.
Operational manifest and large logit caches must stay outside Git.
"""
import argparse
import contextlib
import csv
import datetime
import gc
import hashlib
import importlib.util
import importlib.metadata
import json
import os
from pathlib import Path
import resource
import signal
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from lora_dora_study.server import write_json, gpu_snapshot, available_memory_bytes
from lora_dora_study.evaluation import sha256_file
from lora_dora_study.benchmarks import user_content
from lora_dora_study.fidelity_audit import (select_cases, content_digest, magnitude_gauge,
    without_d, metrics, convert_custom, small_geometry, projection_fingerprints)


def arguments():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--phase',choices=['gpu','cpu'],required=True)
    p.add_argument('--gpu-uuid')
    p.add_argument('--manifest',type=Path,required=True)
    p.add_argument('--output-dir',type=Path,required=True)
    p.add_argument('--queue-dir',type=Path,required=True)
    p.add_argument('--budget-seconds',type=int,required=True)
    p.add_argument('--cases',type=int,default=64)
    p.add_argument('--target-tokens',type=int,default=32)
    return p.parse_args()


def main(a):
    a.output_dir.mkdir(parents=True,exist_ok=False)
    start=time.monotonic()
    def deadline(signum,frame):raise TimeoutError('Phase time budget exhausted')
    signal.signal(signal.SIGALRM,deadline)
    signal.setitimer(signal.ITIMER_REAL,a.budget_seconds)
    summary=dict(status='starting',phase=a.phase,full_evaluation=False,
        timestamp_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        scope='Fixed-prefix fidelity, not benchmark accuracy or training causality',
        runner_sha256=sha256_file(Path(__file__)),helper_sha256=sha256_file(ROOT/'lora_dora_study/fidelity_audit.py'),
        case_count=a.cases,target_tokens=a.target_tokens,conditions=[],gpu_budget_seconds=a.budget_seconds if a.phase=='gpu' else None)
    write_json(a.output_dir/'summary.json',summary)
    sampler=None
    try:
        manifest=json.loads(a.manifest.read_text())
        for rel,expected in manifest['source_sha256'].items():
            if sha256_file(ROOT/rel)!=expected:
                raise ValueError('Frozen audit source changed: '+rel)
        summary['numeric_comparison_caveat']='BF16 CUDA versus FP32 CPU changes backend and dtype; not a pure precision-cause experiment'
        paths={k:v['snapshot_path'] for k,v in manifest['artifacts'].items()}
        for name in ['train','test']:
            if sha256_file(Path(manifest[name]['path']))!=manifest[name]['sha256']:
                raise ValueError('Dataset hash changed')
        summary['manifest_sha256']=sha256_file(a.manifest)
        summary['artifacts']={k:{z:v[z] for z in ['repo_id','revision']} for k,v in manifest['artifacts'].items()}
        if available_memory_bytes()<64*1024**3:
            raise BlockingIOError('Insufficient CPU memory for reference audit')
        if a.phase=='gpu':
            if not a.gpu_uuid or a.gpu_uuid in manifest['excluded_gpu_uuids']:
                raise ValueError('Excluded or missing GPU')
            g=next(g for g in gpu_snapshot()['gpus'] if g['uuid']==a.gpu_uuid)
            if g['index'] in manifest['excluded_gpu_indices']:
                raise ValueError('Excluded GPU index')
            if g['total_mib']-g['used_mib']<8600:
                raise BlockingIOError('Less than 8600 MiB free before load')
            os.environ['CUDA_VISIBLE_DEVICES']=a.gpu_uuid
        else:
            os.environ['CUDA_VISIBLE_DEVICES']=''
        os.environ.update(OMP_NUM_THREADS='4',MKL_NUM_THREADS='4',OPENBLAS_NUM_THREADS='4',
            TOKENIZERS_PARALLELISM='false',HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1')
        import torch
        from transformers import AutoModelForCausalLM,AutoTokenizer
        from peft import PeftModel
        from lora_dora_study.adapters import verify_loaded_adapter
        torch.set_num_threads(4);torch.set_num_interop_threads(1);torch.manual_seed(20261013)
        torch.backends.cuda.matmul.allow_tf32=False
        torch.backends.cudnn.allow_tf32=False
        dtype=torch.bfloat16 if a.phase=='gpu' else torch.float32
        device='cuda:0' if a.phase=='gpu' else 'cpu'
        summary['versions']={k:importlib.metadata.version(k) for k in ['torch','transformers','peft','safetensors','accelerate']}
        summary['dtype']=str(dtype);summary['cpu_threads']=4
        if a.phase=='gpu':
            spec=importlib.util.spec_from_file_location('audit_existing_pilot',ROOT/'execution/next-experiments/pilot.py')
            pilot=importlib.util.module_from_spec(spec);spec.loader.exec_module(pilot)
            sampler=pilot.ResourceSampler(a.output_dir/'resources.jsonl',a.gpu_uuid)
            sampler.thread.start();torch.cuda.reset_peak_memory_stats()
            canary=torch.full((32*1024*1024,),.125,dtype=torch.bfloat16,device='cpu').to(device)
            def check_canary():
                if not bool((canary.cpu()==.125).all()):
                    raise FloatingPointError('Immutable device buffer changed')
            check_canary()
        else:
            def check_canary():pass

        def load():
            begin=time.monotonic()
            model=AutoModelForCausalLM.from_pretrained(paths['base'],local_files_only=True,
                trust_remote_code=False,torch_dtype=dtype,device_map={'':device},
                low_cpu_mem_usage=True,attn_implementation='sdpa')
            model=PeftModel.from_pretrained(model,paths['dora'],local_files_only=True,is_trainable=False)
            validation=verify_loaded_adapter(model,paths['dora'],True)
            if model.config.attention_bias:
                raise ValueError('Bias-free model required')
            model.eval()
            summary.setdefault('loads',[]).append(dict(seconds=time.monotonic()-begin,
                exact_adapter_match=validation['exact_loaded_value_match'],modules=validation['adapted_module_count']))
            return model

        model=load()
        if a.phase=='gpu':
            tokenizer=AutoTokenizer.from_pretrained(paths['base'],local_files_only=True,trust_remote_code=False)
            train=[json.loads(l) for l in open(manifest['train']['path'])]
            test=[json.loads(l) for l in open(manifest['test']['path'])]
            cases=[]
            for index,row in select_cases(train,test,a.cases):
                prompt=tokenizer.apply_chat_template([dict(role='user',content=user_content('gsm8k',row))],
                    tokenize=False,add_generation_prompt=True,enable_thinking=False)
                ids=tokenizer(prompt,add_special_tokens=False)['input_ids']
                if len(ids)>512:
                    raise ValueError('Selected train prompt exceeds fixed input cap')
                targets=tokenizer(row['answer'],add_special_tokens=False)['input_ids'][:a.target_tokens]
                if len(targets)<2:raise ValueError('Insufficient target tokens')
                cases.append(dict(train_index=index,prompt_content_sha256=content_digest(row),
                    prompt_sha256=hashlib.sha256(prompt.encode()).hexdigest(),
                    input_ids=ids+targets[:-1],targets=targets))
            write_json(a.queue_dir/'cases.json',cases)
        else:
            cases=json.loads((a.queue_dir/'cases.json').read_text())
            gpu_summary=json.loads((a.queue_dir/'qwen-gpu/summary.json').read_text())
            if gpu_summary['status']!='complete':raise ValueError('GPU prerequisite incomplete')
            if len(cases)!=a.cases:raise ValueError('Case count changed')
        summary['cases_sha256']=sha256_file(a.queue_dir/'cases.json')
        cache=a.output_dir/'logit-cache';cache.mkdir()
        comparisons=[]
        def record_case(row):
            comparisons.append(row)
            with (a.output_dir/'per-case.jsonl').open('a') as f:
                f.write(json.dumps(row)+'\n')
        def save():
            summary.update(wall_seconds=time.monotonic()-start,
                max_process_rss_bytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024)
            if a.phase=='gpu':
                summary.update(peak_allocated_bytes=torch.cuda.max_memory_allocated(),
                    peak_reserved_bytes=torch.cuda.max_memory_reserved())
            write_json(a.output_dir/'summary.json',summary)

        def logits(case):
            x=torch.tensor([case['input_ids']],device=device,dtype=torch.long)
            with torch.inference_mode(),torch.autocast(device_type='cuda' if a.phase=='gpu' else 'cpu',
                                                       dtype=torch.bfloat16,enabled=a.phase=='gpu'):
                y=model(input_ids=x,attention_mask=torch.ones_like(x),use_cache=False,
                    logits_to_keep=len(case['targets'])).logits[0].detach().float().cpu()
            if y.shape[0]!=len(case['targets']) or not bool(y.isfinite().all()):
                raise FloatingPointError('Invalid read-back target logits')
            return y

        def run(label,reference='original',count=None,save_reference=False):
            begin=time.monotonic();record=dict(condition=label,status='running',cases_completed=0)
            summary['conditions'].append(record);save()
            for i,case in enumerate(cases[:count]):
                y=logits(case)
                if save_reference:
                    torch.save(y,cache/f'{label}-{i}.pt')
                if label=='custom_dense' and i<4:
                    torch.save(y,cache/f'custom_dense-{i}.pt')
                baseline=y if label=='original' else torch.load(cache/f'{reference}-{i}.pt',map_location='cpu',weights_only=True)
                result=metrics(baseline,y,case['targets'])
                if label.startswith('remove-gauge') and not torch.equal(baseline,y):
                    raise ValueError('Magnitude affected native removeD after dispatch removal')
                record_case(dict(condition=label,case=i,**result))
                if label=='official_dense' and i<4:
                    custom=torch.load(cache/f'custom_dense-{i}.pt',map_location='cpu',weights_only=True)
                    record_case(dict(condition='official_minus_custom',case=i,**metrics(custom,y,case['targets'])))
                if a.phase=='cpu' and label in ['original','remove_d']:
                    gy=torch.load(a.queue_dir/'qwen-gpu/logit-cache'/f'{label}-{i}.pt',map_location='cpu',weights_only=True)
                    record_case(dict(condition=f'bf16_minus_fp32_{label}',case=i,**metrics(y,gy,case['targets'])))
                    if label=='remove_d':
                        cpu_orig=torch.load(cache/f'original-{i}.pt',map_location='cpu',weights_only=True)
                        gpu_orig=torch.load(a.queue_dir/'qwen-gpu/logit-cache'/f'original-{i}.pt',map_location='cpu',weights_only=True)
                        action=y.double()-cpu_orig.double()
                        interaction=(gy.double()-gpu_orig.double())-action
                        record.setdefault('ablation_path_interaction',[]).append(dict(case=i,
                            rms=float(interaction.square().mean().sqrt()),
                            fp32_effect_rms=float(action.square().mean().sqrt())))
                record['cases_completed']=i+1
                if (i+1)%8==0:check_canary()
                record['elapsed_seconds']=time.monotonic()-begin
                record['forecast_seconds_for_condition']=record['elapsed_seconds']*(count or len(cases))/(i+1)
                save()
            record.update(status='complete',elapsed_seconds=time.monotonic()-begin);save()

        run('original',save_reference=True)
        run('repeat_original',count=4)
        for c in [.995,1.005]:
            with magnitude_gauge(model,c):run('gauge_'+str(c))
        with without_d(model):run('remove_d',save_reference=True)
        for c in [.995,1.005]:
            with magnitude_gauge(model,c),without_d(model):run('remove-gauge_'+str(c),reference='remove_d',count=4)
        verify_loaded_adapter(model,paths['dora'],True)

        if a.phase=='cpu':
            def avg(label,key):
                values=[r[key] for r in comparisons if r['condition']==label]
                return sum(values)/len(values)
            removal_rms=avg('remove_d','rms')
            ratios={str(c):avg('gauge_'+str(c),'rms')/removal_rms if removal_rms else None for c in [.995,1.005]}
            gate=all(r is not None and r<=.01 for r in ratios.values())
            summary['geometry_gate']=dict(passed=gate,criterion='mean FP32 gauge logit RMS <= 1% mean FP32 removeD logit RMS',
                rationale='predeclared engineering screen, not universal proof of equivalent functions',ratios=ratios)
            save()
            if gate:
                summary['geometry_rows']=len(small_geometry(model,a.output_dir))
            else:
                summary['geometry_skipped']='FP32 functional fidelity gate unresolved; no SVD expansion'
        convert_custom(model)
        custom_fingerprints=projection_fingerprints(model)
        summary['custom_dense_projection_sha256']=custom_fingerprints
        run('custom_dense')
        del model;gc.collect()
        if a.phase=='gpu':torch.cuda.empty_cache()
        model=load().merge_and_unload(safe_merge=True)
        official_fingerprints=projection_fingerprints(model)
        summary['official_dense_projection_sha256']=official_fingerprints
        summary['official_custom_projection_bytes_equal']=official_fingerprints==custom_fingerprints
        run('official_dense')
        del model;gc.collect()
        if a.phase=='gpu':
            check_canary();del canary;torch.cuda.empty_cache()
        fields=list(dict.fromkeys(k for r in comparisons for k in r))
        with open(a.output_dir/'metrics.csv','w') as f:
            w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(comparisons)
        aggregates={}
        for row in comparisons:
            d=aggregates.setdefault(row['condition'],dict(cases=0,tokens=0,rms_sum=0,nll_delta_sum=0,kl_sum=0,argmax_disagreements=0,max_abs=0))
            d['cases']+=1;d['tokens']+=row['tokens'];d['rms_sum']+=row['rms'];d['nll_delta_sum']+=row['nll_difference'];d['kl_sum']+=row['kl_reference_to_changed'];d['argmax_disagreements']+=row['argmax_disagreements'];d['max_abs']=max(d['max_abs'],row['max_abs'])
        for d in aggregates.values():
            for k in ['rms','nll_delta','kl']:d['mean_'+k]=d.pop(k+'_sum')/d['cases']
        summary.update(status='complete',aggregates=aggregates)
        save()
    except Exception as error:
        summary.update(status='failed',error=str(error),wall_seconds=time.monotonic()-start)
        write_json(a.output_dir/'summary.json',summary)
        raise
    finally:
        if sampler:sampler.close()
        signal.setitimer(signal.ITIMER_REAL,0)
    return 0


if __name__=='__main__':sys.exit(main(arguments()))
