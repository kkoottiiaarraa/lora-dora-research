#!/usr/bin/env python3
"""Fixed byte-baseline evaluation reusing accepted128-case source and KFAC outputs."""
import argparse
import datetime
import importlib.metadata
import json
import os
from pathlib import Path
import resource
import signal
import sys
import time
os.environ.update(CUDA_VISIBLE_DEVICES='', OMP_NUM_THREADS='16', MKL_NUM_THREADS='16',
    OPENBLAS_NUM_THREADS='16', HF_HUB_OFFLINE='1', TRANSFORMERS_OFFLINE='1', TOKENIZERS_PARALLELISM='false')
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from lora_dora_study.server import write_json,available_memory_bytes
from lora_dora_study.evaluation import sha256_file


def main(root):
    started=time.monotonic()
    summary=dict(status='running',phase='setup',conditions=[],gpu_count=0,training=False,
        started_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
    def save():
        summary.update(wall_seconds=time.monotonic()-started,rss_bytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024)
        write_json(root/'summary.json',summary)
    def timeout(signum,frame):raise TimeoutError('Byte validation deadline')
    signal.signal(signal.SIGALRM,timeout);signal.setitimer(signal.ITIMER_REAL,1800);save()
    try:
        manifest=json.loads((root/'manifest-private.json').read_text())
        for rel,digest in manifest['source_sha256'].items():
            if sha256_file(ROOT/rel)!=digest:raise ValueError('Frozen source changed: '+rel)
        screen=Path(manifest['screen_root']); sm=json.loads((screen/'manifest-private.json').read_text())
        ss=json.loads((screen/'summary.json').read_text())
        if ss['status']!='complete' or not ss['byte_frontier_gate']:raise ValueError('Screen not accepted')
        affine=Path(sm['affine_root']); evaluation=affine/'evaluate'
        full=Path(sm['full_root']); original=Path(json.loads((full/'manifest-private.json').read_text())['parent_root'])
        old=json.loads((original/'manifest-private.json').read_text())
        casepath=evaluation/'cases.json'
        expected='ae5f38d64a2487018e9e6539f0fc14a87d1ce10343dc66bae86c03ab28f7c749'
        if sha256_file(casepath)!=expected:raise ValueError('Development cases changed')
        cases=json.loads(casepath.read_text());write_json(root/'cases.json',cases)
        if len(cases)!=128 or len({c['prompt_content_sha256'] for c in cases})!=128:
            raise ValueError('Case coverage')
        screen_hashes={c['prompt_content_sha256'] for c in json.loads((screen/'cases.json').read_text())}
        if screen_hashes & {c['prompt_content_sha256'] for c in cases}:raise ValueError('Screen overlap')
        baseline=[r for r in map(json.loads,(evaluation/'per-case.jsonl').read_text().splitlines()) if r['label']=='kfac_uniform']
        if len(baseline)!=128 or {r['case'] for r in baseline}!=set(range(128)):
            raise ValueError('Cached KFAC coverage')
        baseline=sorted(baseline,key=lambda r:r['case'])
        import torch
        from safetensors.torch import load_file
        from transformers import AutoModelForCausalLM
        from peft import PeftModel
        from lora_dora_study.adapters import verify_loaded_adapter
        from lora_dora_study.adapter_storage import decode,payload_bytes
        from lora_dora_study.full_compression import replace_all,adapted_modules
        from lora_dora_study.fidelity_audit import metrics
        torch.set_num_threads(16);torch.set_num_interop_threads(1);torch.manual_seed(20261014)
        torch.set_float32_matmul_precision('highest')
        versions={k:importlib.metadata.version(k) for k in old['versions']}
        if versions!=old['versions'] or available_memory_bytes()<64*1024**3:
            raise ValueError('Execution preflight failed')
        storage=json.loads((screen/'storage.json').read_text());factors={}
        for label in ['structural_fp16_r15','structural_int8_r30']:
            archive=screen/(label+'.safetensors');config=screen/(label+'.json');entry=storage[label]
            if sha256_file(archive)!=entry['sha256'] or sha256_file(config)!=entry['config_sha256']:
                raise ValueError('Archive changed')
            if archive.stat().st_size+config.stat().st_size!=entry['total_file_bytes'] or entry['total_file_bytes']>23592960:
                raise ValueError('File budget changed')
            tensors=load_file(str(archive),device='cpu');records={}
            for key,tensor in tensors.items():
                name,field=key.rsplit('.',1);records.setdefault(name,{})[field]=tensor
            if len(records)!=144 or len(tensors)!=entry['tensor_count'] or payload_bytes(records)!=entry['payload_bytes']:
                raise ValueError('Storage coverage changed')
            factors[label]={name:decode(rec) for name,rec in records.items()}
        caches=[]
        for i,case in enumerate(cases):
            if len(case['targets'])!=32:raise ValueError('Target coverage')
            path=evaluation/'logit-cache'/f'original-{i}.pt'
            y=torch.load(path,map_location='cpu',weights_only=True)
            checks=metrics(y,y,case['targets'])
            if abs(checks['reference_nll']-baseline[i]['reference_nll'])>1e-12:
                raise ValueError('KFAC source alignment changed')
            caches.append(dict(case=i,sha256=sha256_file(path)))
        write_json(root/'cache-index.json',caches)
        write_json(root/'frozen.json',dict(cases_sha256=expected,cache_index_sha256=sha256_file(root/'cache-index.json'),
            baseline_rows_sha256=sha256_file(evaluation/'per-case.jsonl'),storage=storage,
            source_sha256=manifest['source_sha256'],before_new_outputs=True,new_independent_test=False))
        summary.update(phase='load',versions=versions,cpu_threads=16,storage=storage,
            source_sha256=manifest['source_sha256'],cases_sha256=expected,frozen_sha256=sha256_file(root/'frozen.json'),
            artifacts=ss['artifacts'],new_independent_test=False);save()
        model=AutoModelForCausalLM.from_pretrained(old['artifacts']['base']['snapshot_path'],
            local_files_only=True,trust_remote_code=False,torch_dtype=torch.float32,
            device_map={'':'cpu'},low_cpu_mem_usage=True,attn_implementation='sdpa')
        model=PeftModel.from_pretrained(model,old['artifacts']['dora']['snapshot_path'],local_files_only=True,is_trainable=False).eval()
        model.requires_grad_(False)
        check=verify_loaded_adapter(model,old['artifacts']['dora']['snapshot_path'],True)
        if not check['exact_loaded_value_match'] or check['adapted_module_count']!=144:
            raise ValueError('Native adapter mismatch')
        if any(p.dtype!=torch.float32 or p.device.type!='cpu' for p in model.parameters()):
            raise ValueError('Execution changed')
        summary['adapter_exact']=True
        def logits(case):
            ids=torch.tensor([case['input_ids']],dtype=torch.long)
            with torch.inference_mode():
                y=model(input_ids=ids,attention_mask=torch.ones_like(ids),use_cache=False,logits_to_keep=32).logits[0].detach().cpu()
            if y.shape[0]!=32 or not bool(y.isfinite().all()):raise FloatingPointError('Invalid logits')
            return y
        native_checks=[]
        cal=json.loads(Path(old['calibration_cases']).read_text())
        for label,selected,folder in [('old',cal,original/'capture/logit-cache'),('development',cases,evaluation/'logit-cache')]:
            for i,case in enumerate(selected[:4]):
                y=logits(case);cached=torch.load(folder/f'original-{i}.pt',map_location='cpu',weights_only=True)
                native_checks.append(dict(set=label,case=i,bitwise_equal=torch.equal(y,cached),**metrics(cached,y,case['targets'])))
                write_json(root/'native-checks.json',native_checks)
                if not torch.equal(y,cached):raise ValueError('Native source reload changed')
        native={}
        for name,module in adapted_modules(model).items():
            b=module.lora_B['default'].weight.detach();a=module.lora_A['default'].weight.detach()
            direction=module.get_base_layer().weight.detach()+(b@a)*module.scaling['default']
            d=module.lora_magnitude_vector['default'].weight.detach()/direction.norm(dim=1)
            native[name]=dict(left=((d[:,None]*b)*module.scaling['default']).contiguous(),right=a,row_scale=d)
        controls=[]
        with replace_all(model,native):
            for i,case in enumerate(cases[:4]):
                y=torch.load(evaluation/'logit-cache'/f'original-{i}.pt',map_location='cpu',weights_only=True)
                controls.append(dict(case=i,**metrics(y,logits(case),case['targets'])))
        write_json(root/'controls.json',controls)
        floor=max(r['rms'] for r in controls)
        with (root/'per-case.jsonl').open('x') as stream:
            for row in baseline:stream.write(json.dumps(dict(row,label='kfac_fp32_r8',reused=True))+'\n')
        summary['conditions'].append(dict(label='kfac_fp32_r8',status='complete',cases_completed=128,reused=True,
            mean_kl=sum(r['kl_reference_to_changed'] for r in baseline)/128,
            mean_nll_delta=sum(r['nll_difference'] for r in baseline)/128,
            mean_rms=sum(r['rms'] for r in baseline)/128,
            argmax_disagreements=sum(r['argmax_disagreements'] for r in baseline)));save()
        for label,records in factors.items():
            condition=dict(label=label,status='running',cases_completed=0);summary['conditions'].append(condition)
            summary['phase']='conditions';save();rows=[]
            with replace_all(model,records):
                for i,case in enumerate(cases):
                    reference=torch.load(evaluation/'logit-cache'/f'original-{i}.pt',map_location='cpu',weights_only=True)
                    row=dict(label=label,case=i,reused=False,**metrics(reference,logits(case),case['targets']))
                    with (root/'per-case.jsonl').open('a') as stream:stream.write(json.dumps(row)+'\n')
                    rows.append(row);condition['cases_completed']=i+1;save()
            condition.update(status='complete',mean_kl=sum(r['kl_reference_to_changed'] for r in rows)/128,
                mean_nll_delta=sum(r['nll_difference'] for r in rows)/128,
                mean_rms=sum(r['rms'] for r in rows)/128,
                argmax_disagreements=sum(r['argmax_disagreements'] for r in rows));save()
        if floor>=.01*min(c['mean_rms'] for c in summary['conditions']):raise ValueError('Control floor too large')
        restored=logits(cases[0]);expected_y=torch.load(evaluation/'logit-cache/original-0.pt',map_location='cpu',weights_only=True)
        if not torch.equal(restored,expected_y):raise ValueError('Source not restored')
        improvements={c['label']:1-c['mean_kl']/summary['conditions'][0]['mean_kl'] for c in summary['conditions'][1:]}
        summary.update(status='complete',phase='complete',controls_max_rms=floor,improvements_vs_fp32_kfac=improvements,
            byte_frontier_gate=any(v>=.2 for v in improvements.values()),full_task_accuracy=False,conference_level_established=False);save()
    except Exception as exc:
        summary.update(status='failed',error=repr(exc));save();raise
    finally:signal.setitimer(signal.ITIMER_REAL,0)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);main(p.parse_args().root)
