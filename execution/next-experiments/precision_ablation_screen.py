#!/usr/bin/env python3
"""Bounded triangular dtype/backend and matched ablation-path screen."""
import argparse
import datetime
import gc
import importlib.metadata
import importlib.util
import json
import os
from pathlib import Path
import resource
import signal
import sys
import time
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from lora_dora_study.server import write_json,available_memory_bytes,gpu_snapshot
from lora_dora_study.evaluation import sha256_file


def main(a):
    started=time.monotonic();a.output_dir.mkdir(exist_ok=False)
    os.environ.update(CUDA_VISIBLE_DEVICES=a.gpu_uuid if a.phase=='gpu' else '',
        OMP_NUM_THREADS='16',MKL_NUM_THREADS='16',OPENBLAS_NUM_THREADS='16',
        HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',TOKENIZERS_PARALLELISM='false')
    summary=dict(status='running',phase='setup',execution_phase=a.phase,conditions=[],
        started_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),training=False)
    def save():
        summary.update(wall_seconds=time.monotonic()-started,
            rss_bytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024)
        write_json(a.output_dir/'summary.json',summary)
    def timeout(signum,frame):raise TimeoutError('Precision screen wall budget exhausted')
    signal.signal(signal.SIGALRM,timeout);signal.setitimer(signal.ITIMER_REAL,a.budget_seconds);save()
    sampler=None
    try:
        manifest=json.loads(a.manifest.read_text())
        for rel,digest in manifest['source_sha256'].items():
            if sha256_file(ROOT/rel)!=digest:raise ValueError('Frozen source changed: '+rel)
        if available_memory_bytes()<64*1024**3:raise BlockingIOError('Need64GiBavailableRAM')
        if a.phase=='gpu':
            g=next(g for g in gpu_snapshot()['gpus'] if g['uuid']==a.gpu_uuid)
            if g['index']==1 or g['total_mib']-g['used_mib']<14336 or g['utilization_percent']>=20:
                raise BlockingIOError('Fresh GPU resource guard refused')
        full=Path(manifest['full_root']);original=Path(json.loads((full/'manifest-private.json').read_text())['parent_root'])
        old=json.loads((original/'manifest-private.json').read_text())
        calpath=Path(old['calibration_cases'])
        if sha256_file(calpath)!=old['calibration_cases_sha256']:raise ValueError('Calibration changed')
        cases=json.loads(calpath.read_text())[:8]
        if len(cases)!=8 or any(len(c['targets'])!=32 for c in cases):raise ValueError('Case coverage')
        write_json(a.output_dir/'cases.json',cases)
        import torch
        from transformers import AutoModelForCausalLM
        from peft import PeftModel
        from lora_dora_study.adapters import verify_loaded_adapter
        from lora_dora_study.fidelity_audit import without_d,metrics
        from lora_dora_study.precision_ablation import place_transformer,stream_dense,apply_dense_without_d,fingerprints,load_explicit_cpu
        torch.set_num_threads(16);torch.set_num_interop_threads(1);torch.manual_seed(20261014)
        torch.set_float32_matmul_precision('highest');torch.backends.cuda.matmul.allow_tf32=False
        torch.backends.cudnn.allow_tf32=False
        versions={k:importlib.metadata.version(k) for k in old['versions']}
        if versions!=old['versions']:raise ValueError('Versions changed')
        summary.update(versions=versions,cpu_threads=16,source_sha256=manifest['source_sha256'],
            artifacts={k:{j:v[j] for j in ['repo_id','revision']} for k,v in old['artifacts'].items()},
            placement='transformer on selected device; embedding/head CPU FP32; adapters FP32',
            full_factorial=False,case_count=8,cases_sha256=sha256_file(a.output_dir/'cases.json'))
        write_json(a.output_dir/'frozen.json',dict(source_sha256=manifest['source_sha256'],
            cases_sha256=summary['cases_sha256'],before_outputs=True,exploration_only=True))
        summary['frozen_sha256']=sha256_file(a.output_dir/'frozen.json')
        device='cuda:0' if a.phase=='gpu' else 'cpu'
        if a.phase=='gpu':
            import unittest
            suite=unittest.defaultTestLoader.discover(str(ROOT/'tests'),pattern='test_precision_ablation.py')
            with (a.output_dir/'cuda-visible-tests.log').open('x') as stream:
                checked=unittest.TextTestRunner(stream=stream,verbosity=2).run(suite)
            if not checked.wasSuccessful():raise ValueError('CUDA-visible CPU fixture failed')
            from lora_dora_study.resource_sampling import ResourceSampler
            sampler=ResourceSampler(a.output_dir/'resources.jsonl',a.gpu_uuid);sampler.thread.start()
            canary=torch.full((8*1024**2,),.125,dtype=torch.float32,device='cpu').to(device)
            def canary_check():
                if not bool((canary.cpu()==.125).all()):raise FloatingPointError('Immutable device canary changed')
        else:
            def canary_check():pass
        all_rows=[]
        def record(row):
            all_rows.append(row)
            with (a.output_dir/'per-case.jsonl').open('a') as stream:stream.write(json.dumps(row)+'\n')
        for dtype in ([torch.float32,torch.bfloat16] if a.phase=='gpu' else [torch.float32]):
            label=('cuda' if a.phase=='gpu' else 'cpu')+'_'+str(dtype).split('.')[-1]
            cache=a.output_dir/'logit-cache'/label;cache.mkdir(parents=True)
            if a.phase=='gpu':torch.cuda.reset_peak_memory_stats()
            def load():
                begin=time.monotonic()
                model=load_explicit_cpu(old['artifacts']['base']['snapshot_path'],old['artifacts']['dora']['snapshot_path'],dtype)
                check=verify_loaded_adapter(model,old['artifacts']['dora']['snapshot_path'],True)
                if not check['exact_loaded_value_match'] or check['adapted_module_count']!=144:
                    raise ValueError('Adapter mismatch')
                place_transformer(model,device,dtype)
                audit={}
                for name,module in model.named_modules():
                    if hasattr(module,'use_dora') and module.use_dora.get('default'):
                        audit[name]=dict(base_dtype=str(module.get_base_layer().weight.dtype),
                            base_device=module.get_base_layer().weight.device.type,
                            a_dtype=str(module.lora_A['default'].weight.dtype),
                            b_dtype=str(module.lora_B['default'].weight.dtype),
                            m_dtype=str(module.lora_magnitude_vector['default'].weight.dtype))
                if len(audit)!=144 or any(info['base_dtype']!=str(dtype) or info['base_device']!=('cuda' if a.phase=='gpu' else 'cpu')
                    or any(info[k]!='torch.float32' for k in ['a_dtype','b_dtype','m_dtype']) for info in audit.values()):
                    raise ValueError('Explicit dtype contract failed')
                summary.setdefault('loads',[]).append(dict(cell=label,seconds=time.monotonic()-begin,adapter_exact=True,modules=144))
                write_json(a.output_dir/(label+'-dtype-audit.json'),audit);save()
                return model
            model=load()
            def logits(case):
                ids=torch.tensor([case['input_ids']],device=device,dtype=torch.long)
                with torch.inference_mode():
                    result=model(input_ids=ids,attention_mask=torch.ones_like(ids),use_cache=False,logits_to_keep=32).logits[0].detach().float().cpu()
                if result.shape[0]!=32 or not bool(result.isfinite().all()):raise FloatingPointError('Invalid readback logits')
                return result
            def run(condition,reference='native_source',count=8,save_outputs=True):
                entry=dict(cell=label,condition=condition,status='running',cases_completed=0)
                summary['conditions'].append(entry);summary['phase']='conditions';save();rows=[]
                for i,case in enumerate(cases[:count]):
                    y=logits(case)
                    ref=y if condition=='native_source' else torch.load(cache/f'{reference}-{i}.pt',map_location='cpu',weights_only=True)
                    row=dict(cell=label,condition=condition,reference=reference,case=i,**metrics(ref,y,case['targets']))
                    record(row);rows.append(row)
                    if save_outputs:torch.save(y,cache/f'{condition}-{i}.pt')
                    entry['cases_completed']=i+1;canary_check();save()
                    if condition=='native_source' and label=='cpu_float32' and i<4:
                        previous=torch.load(original/'capture/logit-cache'/f'original-{i}.pt',map_location='cpu',weights_only=True)
                        if not torch.equal(y,previous):raise ValueError('CPU native cached source changed')
                entry.update(status='complete',mean_nll_delta=sum(r['nll_difference'] for r in rows)/count,
                    mean_nll=sum(r['changed_nll'] for r in rows)/count,
                    mean_kl=sum(r['kl_reference_to_changed'] for r in rows)/count,
                    mean_rms=sum(r['rms'] for r in rows)/count,
                    argmax_disagreements=sum(r['argmax_disagreements'] for r in rows));save()
                return rows
            run('native_source')
            repeat=run('repeat_native',count=2,save_outputs=False)
            if any(r['max_abs']!=0 for r in repeat):raise ValueError('Native repeat changed')
            with without_d(model):run('native_remove_d')
            for i,case in enumerate(cases[:2]):
                previous=torch.load(cache/f'native_source-{i}.pt',map_location='cpu',weights_only=True)
                if not torch.equal(logits(case),previous):raise ValueError('Native restoration changed')
            unscaled,_=stream_dense(model)
            custom_hashes=fingerprints(model)
            if len(custom_hashes)!=144:raise ValueError('Dense coverage')
            run('dense_source')
            apply_dense_without_d(model,unscaled)
            run('dense_remove_d',reference='dense_source')
            del model,unscaled;gc.collect()
            if a.phase=='gpu':torch.cuda.empty_cache()
            model=load().merge_and_unload(safe_merge=True)
            official_hashes=fingerprints(model)
            if official_hashes!=custom_hashes:raise ValueError('Official/custom projection bytes differ')
            check_rows=run('official_dense_control',reference='dense_source',count=2,save_outputs=False)
            if any(r['max_abs']!=0 for r in check_rows):raise ValueError('Official/custom logits differ')
            write_json(a.output_dir/(label+'-merge-check.json'),dict(status='PASS',custom_sha256=custom_hashes,official_sha256=official_hashes,first2_logits_bitwise=True))
            if a.phase=='gpu':
                summary.setdefault('gpu_memory',{})[label]=dict(peak_allocated_bytes=torch.cuda.max_memory_allocated(),peak_reserved_bytes=torch.cuda.max_memory_reserved())
            del model;gc.collect()
            if a.phase=='gpu':torch.cuda.empty_cache()
            canary_check()
        if a.phase=='cpu':
            native_rms=next(c['mean_rms'] for c in summary['conditions'] if c['condition']=='native_remove_d')
            dense_rms=next(c['mean_rms'] for c in summary['conditions'] if c['condition']=='dense_source')
            if dense_rms>=.01*native_rms:raise ValueError('CPU FP32 dense control floor too large')
        if a.phase=='gpu':
            native_rms=next(c['mean_rms'] for c in summary['conditions'] if c['condition']=='native_remove_d' and c['cell']=='cuda_float32')
            dense_rms=next(c['mean_rms'] for c in summary['conditions'] if c['condition']=='dense_source' and c['cell']=='cuda_float32')
            if dense_rms>=.01*native_rms:raise ValueError('CUDA FP32 dense control floor too large')
            del canary;torch.cuda.empty_cache()
        summary.update(status='complete',phase='complete',rows=len(all_rows),full_task_accuracy=False,conference_level_established=False);save()
    except Exception as exc:
        summary.update(status='failed',error=repr(exc));save();raise
    finally:
        if sampler:sampler.close()
        signal.setitimer(signal.ITIMER_REAL,0)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--phase',choices=['gpu','cpu'],required=True)
    p.add_argument('--manifest',type=Path,required=True);p.add_argument('--output-dir',type=Path,required=True)
    p.add_argument('--queue-dir',type=Path,required=True);p.add_argument('--budget-seconds',type=int,required=True)
    p.add_argument('--gpu-uuid');main(p.parse_args())
