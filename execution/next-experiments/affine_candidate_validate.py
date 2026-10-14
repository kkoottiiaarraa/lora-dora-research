#!/usr/bin/env python3
"""Fresh matched-prefix evaluation for one frozen full affine candidate."""
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
    OPENBLAS_NUM_THREADS='16', HF_HUB_OFFLINE='1', TRANSFORMERS_OFFLINE='1',
    TOKENIZERS_PARALLELISM='false')
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from lora_dora_study.server import write_json, available_memory_bytes
from lora_dora_study.evaluation import sha256_file


def main(root):
    started=time.monotonic()
    out=root/'evaluate';out.mkdir(exist_ok=False)
    summary=dict(status='running',phase='setup',conditions=[],gpu_count=0,
        training=False,started_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
    def save():
        summary.update(wall_seconds=time.monotonic()-started,
            rss_bytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024)
        write_json(out/'summary.json',summary)
    def timeout(signum,frame):
        raise TimeoutError('Affine validation deadline')
    signal.signal(signal.SIGALRM,timeout);signal.setitimer(signal.ITIMER_REAL,7200);save()
    try:
        manifest=json.loads((root/'eval-manifest-private.json').read_text())
        for rel,digest in manifest['source_sha256'].items():
            if sha256_file(ROOT/rel)!=digest:raise ValueError('Frozen source changed: '+rel)
        prep=json.loads((root/'prepare/summary.json').read_text())
        frozen=json.loads((root/'prepare/frozen.json').read_text())
        if prep['status']!='complete' or sha256_file(root/'prepare/frozen.json')!=prep['frozen_sha256']:
            raise ValueError('Preparation not accepted')
        if sha256_file(root/'prepare/factors.pt')!=frozen['factors_sha256']:
            raise ValueError('Factors changed')
        parent=Path(manifest['full_root'])
        fm=json.loads((parent/'manifest-private.json').read_text())
        original=Path(fm['parent_root'])
        old=json.loads((original/'manifest-private.json').read_text())
        import torch
        from transformers import AutoTokenizer,AutoModelForCausalLM
        from peft import PeftModel
        from lora_dora_study.adapters import verify_loaded_adapter
        from lora_dora_study.full_compression import replace_all
        from lora_dora_study.fidelity_audit import content_digest,metrics
        from lora_dora_study.benchmarks import user_content
        torch.set_num_threads(16);torch.set_num_interop_threads(1)
        torch.manual_seed(20261014);torch.set_float32_matmul_precision('highest')
        versions={k:importlib.metadata.version(k) for k in old['versions']}
        if versions!=old['versions']:raise ValueError('Versions changed')
        if available_memory_bytes()<64*1024**3:raise BlockingIOError('Need 64GiB available RAM')
        summary.update(versions=versions,source_sha256=manifest['source_sha256'],cpu_threads=16)
        calpath=Path(old['calibration_cases'])
        if sha256_file(calpath)!=old['calibration_cases_sha256']:raise ValueError('Calibration changed')
        cal=json.loads(calpath.read_text())
        datasets={}
        for label in ['train','test']:
            path=Path(old[label]['path'])
            if sha256_file(path)!=old[label]['sha256']:raise ValueError('Dataset changed')
            datasets[label]=[json.loads(line) for line in path.read_text().splitlines()]
        excluded={content_digest(r) for r in datasets['train'][:232]+datasets['test']}
        excluded|={case['prompt_content_sha256'] for case in cal}
        for path in [original/'validation-cases.json',Path(fm['anchored_root'])/'validation-cases.json',
            Path(fm['budget_root'])/'prepare/cases.json',parent/'cases.json',
            Path(manifest['radial_root'])/'cases.json',
            Path(manifest['allocation_root'])/'evaluate/cases.json']:
            excluded|={case['prompt_content_sha256'] for case in json.loads(path.read_text())}
        tokenizer=AutoTokenizer.from_pretrained(old['artifacts']['base']['snapshot_path'],
            local_files_only=True,trust_remote_code=False)
        cases=[]
        for index,row in enumerate(datasets['train']):
            digest=content_digest(row)
            if digest in excluded:continue
            prompt=tokenizer.apply_chat_template([dict(role='user',content=user_content('gsm8k',row))],
                tokenize=False,add_generation_prompt=True,enable_thinking=False)
            ids=tokenizer(prompt,add_special_tokens=False)['input_ids']
            targets=tokenizer(row['answer'],add_special_tokens=False)['input_ids'][:32]
            if len(ids)>512 or len(targets)<32:continue
            cases.append(dict(train_index=index,prompt_content_sha256=digest,
                input_ids=ids+targets[:-1],targets=targets))
            excluded.add(digest)
            if len(cases)==128:break
        if len(cases)!=128:raise ValueError('Insufficient fresh cases')
        write_json(out/'cases.json',cases)
        factors=torch.load(root/'prepare/factors.pt',map_location='cpu',weights_only=True)
        from lora_dora_study.native_magnitude_baseline import augment
        factors.update(augment(root))
        counts={label:sum(t.numel() for record in records.values() for t in record.values())
            for label,records in factors.items()}
        if set(factors)!={'weighted_uniform','kfac_uniform','structural_kfac','joint_kfac','native_m_input','native_m_kfac'}:
            raise ValueError('Conditions changed')
        if any(count!=5898240 for count in counts.values()):raise ValueError('Budget changed')
        procedure=dict(cases_sha256=sha256_file(out/'cases.json'),factors_sha256=frozen['factors_sha256'],
            source_sha256=manifest['source_sha256'],frozen_before_new_inference=True,
            native_baselines_sha256=sha256_file(root/'native-m-baselines.pt'),primary_family_size=5,
            factor_counts=counts,calibration_cases_sha256=old['calibration_cases_sha256'])
        write_json(out/'frozen.json',procedure)
        summary['frozen_sha256']=sha256_file(out/'frozen.json');save()
        model=AutoModelForCausalLM.from_pretrained(old['artifacts']['base']['snapshot_path'],
            local_files_only=True,trust_remote_code=False,torch_dtype=torch.float32,
            device_map={'':'cpu'},low_cpu_mem_usage=True,attn_implementation='sdpa')
        model=PeftModel.from_pretrained(model,old['artifacts']['dora']['snapshot_path'],
            local_files_only=True,is_trainable=False).eval();model.requires_grad_(False)
        check=verify_loaded_adapter(model,old['artifacts']['dora']['snapshot_path'],True)
        if not check['exact_loaded_value_match'] or check['adapted_module_count']!=144:
            raise ValueError('Adapter mismatch')
        if any(p.dtype!=torch.float32 or p.device.type!='cpu' for p in model.parameters()):
            raise ValueError('Wrong execution mode')
        summary['adapter_exact']=True
        def logits(case):
            ids=torch.tensor([case['input_ids']],dtype=torch.long)
            with torch.inference_mode():
                result=model(input_ids=ids,attention_mask=torch.ones_like(ids),
                    use_cache=False,logits_to_keep=32).logits[0].detach().cpu()
            if result.shape[0]!=32 or not bool(result.isfinite().all()):
                raise FloatingPointError('Invalid logits')
            return result
        native_checks=[]
        for i in range(4):
            expected=torch.load(original/'capture/logit-cache'/f'original-{i}.pt',
                map_location='cpu',weights_only=True)
            observed=logits(cal[i])
            native_checks.append(dict(case=i,bitwise_equal=torch.equal(observed,expected),
                **metrics(expected,observed,cal[i]['targets'])))
            write_json(out/'native-reference-checks.json',native_checks)
            if not native_checks[-1]['bitwise_equal']:
                torch.save(observed,out/f'native-reference-failed-{i}.pt')
                repeated=logits(cal[i])
                write_json(out/'native-reference-failure.json',dict(case=i,
                    repeated_equal_old=torch.equal(repeated,expected),
                    repeated_equal_first=torch.equal(repeated,observed),
                    repeated_metrics=metrics(expected,repeated,cal[i]['targets'])))
                raise ValueError('Native reference changed on case '+str(i))
        cache=out/'logit-cache';cache.mkdir()
        for i,case in enumerate(cases):
            torch.save(logits(case),cache/f'original-{i}.pt')
            summary.update(phase='reference',cases_completed=i+1);save()
        controls=[]
        with replace_all(model,factors['joint_kfac']):
            first=[logits(case) for case in cases[:2]]
        with replace_all(model,factors['joint_kfac'],dense=True):
            for i,case in enumerate(cases[:2]):
                controls.append(dict(case=i,**metrics(first[i],logits(case),case['targets'])))
        write_json(out/'controls.json',controls)
        floor=max(row['rms'] for row in controls)
        for label,records in factors.items():
            condition=dict(label=label,status='running',cases_completed=0,factor_elements=counts[label])
            summary['conditions'].append(condition);summary['phase']='conditions';save()
            rows=[]
            with replace_all(model,records):
                for i,case in enumerate(cases):
                    reference=torch.load(cache/f'original-{i}.pt',map_location='cpu',weights_only=True)
                    row=dict(label=label,case=i,**metrics(reference,logits(case),case['targets']))
                    with (out/'per-case.jsonl').open('a') as stream:stream.write(json.dumps(row)+'\n')
                    rows.append(row);condition['cases_completed']=i+1;save()
            condition.update(status='complete',mean_kl=sum(r['kl_reference_to_changed'] for r in rows)/128,
                mean_nll_delta=sum(r['nll_difference'] for r in rows)/128,
                mean_rms=sum(r['rms'] for r in rows)/128,
                argmax_disagreements=sum(r['argmax_disagreements'] for r in rows));save()
        if floor>=.01*min(c['mean_rms'] for c in summary['conditions']):
            raise ValueError('Fidelity floor too large')
        if sha256_file(out/'frozen.json')!=summary['frozen_sha256']:
            raise ValueError('Procedure changed during outputs')
        summary.update(status='complete',phase='complete',controls_max_rms=floor,
            full_task_accuracy=False,cases_sha256=procedure['cases_sha256']);save()
    except Exception as exc:
        summary.update(status='failed',error=repr(exc));save();raise
    finally:signal.setitimer(signal.ITIMER_REAL,0)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--root',type=Path,required=True)
    args=parser.parse_args();main(args.root)
