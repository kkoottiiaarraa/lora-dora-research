#!/usr/bin/env python3
"""One frozen radial-compensation candidate and fresh matched validation."""
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

os.environ.update(CUDA_VISIBLE_DEVICES='',OMP_NUM_THREADS='4',MKL_NUM_THREADS='4',OPENBLAS_NUM_THREADS='4',
    HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',TOKENIZERS_PARALLELISM='false')
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from lora_dora_study.server import write_json,available_memory_bytes
from lora_dora_study.evaluation import sha256_file


def main(root):
    start=time.monotonic();summary=dict(status='running',gpu_count=0,training=False,conditions=[],
        started_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
    def save():
        summary.update(wall_seconds=time.monotonic()-start,rss_bytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024)
        write_json(root/'summary.json',summary)
    def timeout(signum,frame):raise TimeoutError('Radial followup deadline')
    signal.signal(signal.SIGALRM,timeout);signal.setitimer(signal.ITIMER_REAL,3600);save()
    try:
        m=json.loads((root/'manifest-private.json').read_text());parent=Path(m['full_root'])
        fm=json.loads((parent/'manifest-private.json').read_text());original=Path(fm['parent_root'])
        old=json.loads((original/'manifest-private.json').read_text())
        for rel,digest in m['source_sha256'].items():
            if sha256_file(ROOT/rel)!=digest:raise ValueError('Frozen source changed: '+rel)
        import torch
        from transformers import AutoTokenizer,AutoModelForCausalLM
        from peft import PeftModel
        from lora_dora_study.radial_recalibration import recalibrate
        from lora_dora_study.full_compression import replace_all
        from lora_dora_study.adapters import verify_loaded_adapter
        from lora_dora_study.benchmarks import user_content
        from lora_dora_study.fidelity_audit import content_digest,metrics
        torch.set_num_threads(4);torch.set_num_interop_threads(1);torch.manual_seed(20261013)
        torch.set_float32_matmul_precision('highest')
        versions={k:importlib.metadata.version(k) for k in old['versions']}
        if versions!=old['versions']:raise ValueError('Versions changed')
        summary.update(versions=versions,source_sha256=m['source_sha256'])
        state=json.loads((parent/'state.json').read_text());capture=json.loads((parent/'capture/summary.json').read_text())
        prep=json.loads((parent/'prepare/summary.json').read_text())
        if not(state['status']==capture['status']==prep['status']=='complete'):raise ValueError('Full screen incomplete')
        if sha256_file(parent/'prepare/factors.pt')!=prep['factors_sha256']:raise ValueError('Original factors changed')
        calpath=Path(old['calibration_cases'])
        if sha256_file(calpath)!=old['calibration_cases_sha256']:raise ValueError('Cal changed')
        cal=json.loads(calpath.read_text())
        train=[json.loads(s) for s in Path(old['train']['path']).read_text().splitlines()]
        test=[json.loads(s) for s in Path(old['test']['path']).read_text().splitlines()]
        for label in ['train','test']:
            if sha256_file(Path(old[label]['path']))!=old[label]['sha256']:raise ValueError('Dataset changed')
        excluded={content_digest(r) for r in train[:232]+test}|{r['prompt_content_sha256'] for r in cal}
        for path in [original/'validation-cases.json',Path(fm['anchored_root'])/'validation-cases.json',
                     Path(fm['budget_root'])/'prepare/cases.json',parent/'cases.json']:
            excluded|={r['prompt_content_sha256'] for r in json.loads(path.read_text())}
        tokenizer=AutoTokenizer.from_pretrained(old['artifacts']['base']['snapshot_path'],local_files_only=True,trust_remote_code=False)
        cases=[]
        for index,row in enumerate(train):
            digest=content_digest(row)
            if digest in excluded:continue
            prompt=tokenizer.apply_chat_template([dict(role='user',content=user_content('gsm8k',row))],
                tokenize=False,add_generation_prompt=True,enable_thinking=False)
            ids=tokenizer(prompt,add_special_tokens=False)['input_ids'];targets=tokenizer(row['answer'],add_special_tokens=False)['input_ids'][:32]
            if len(ids)>512 or len(targets)<32:continue
            cases.append(dict(train_index=index,prompt_content_sha256=digest,input_ids=ids+targets[:-1],targets=targets))
            excluded.add(digest)
            if len(cases)==64:break
        if len(cases)!=64:raise ValueError('Insufficient new validation cases')
        write_json(root/'cases.json',cases);summary['cases_sha256']=sha256_file(root/'cases.json');save()
        factors=torch.load(parent/'prepare/factors.pt',map_location='cpu',weights_only=True)
        factors={k:factors[k] for k in ['raw_8','weighted_8','structural_8']}
        candidate={};diagnostics=[]
        for i,item in enumerate(capture['modules']):
            path=parent/'capture'/item['file']
            if sha256_file(path)!=item['sha256']:raise ValueError('Capture changed')
            data=torch.load(path,map_location='cpu',weights_only=True)
            record,info=recalibrate(data['base'],data['value'],data['inputs'],factors['structural_8'][item['name']])
            candidate[item['name']]=record;diagnostics.append(dict(module=item['name'],**info))
            summary.update(phase='prepare',modules_completed=i+1);save()
        del data,record
        if sum(t.numel() for r in candidate.values() for t in r.values())!=5898240:
            raise ValueError('Candidate storage mismatch')
        for name,r in candidate.items():
            for key in ['left','right']:
                if not torch.equal(r[key],factors['structural_8'][name][key]):raise ValueError('Direction changed')
        torch.save(candidate,root/'candidate-factors.pt');write_json(root/'diagnostics.json',diagnostics)
        frozen=dict(candidate_sha256=sha256_file(root/'candidate-factors.pt'),cases_sha256=summary['cases_sha256'],
            frozen_before_validation=True,rank_budget=8,factor_elements=5898240,primary_reference='structural_8',
            candidate='recalibrated_8',calibration_data_sha256=old['calibration_cases_sha256'])
        write_json(root/'frozen.json',frozen);summary.update(frozen_sha256=sha256_file(root/'frozen.json'),
            prepare_seconds=time.monotonic()-start,phase='evaluate');save()
        factors['recalibrated_8']=candidate
        if available_memory_bytes()<64*1024**3:raise BlockingIOError('Need 64GiB RAM')
        torch.set_num_threads(16);summary['cpu_threads']=16
        model=AutoModelForCausalLM.from_pretrained(old['artifacts']['base']['snapshot_path'],local_files_only=True,
            trust_remote_code=False,torch_dtype=torch.float32,device_map={'':'cpu'},low_cpu_mem_usage=True,attn_implementation='sdpa')
        model=PeftModel.from_pretrained(model,old['artifacts']['dora']['snapshot_path'],local_files_only=True,is_trainable=False).eval()
        model.requires_grad_(False);check=verify_loaded_adapter(model,old['artifacts']['dora']['snapshot_path'],True)
        if not check['exact_loaded_value_match'] or check['adapted_module_count']!=144:raise ValueError('Adapter mismatch')
        if any(p.dtype!=torch.float32 or p.device.type!='cpu' for p in model.parameters()):raise ValueError('Wrong execution')
        summary['adapter_exact']=True
        def logits(case):
            ids=torch.tensor([case['input_ids']],dtype=torch.long)
            with torch.inference_mode():
                y=model(input_ids=ids,attention_mask=torch.ones_like(ids),use_cache=False,logits_to_keep=32).logits[0].detach().cpu()
            if y.shape[0]!=32 or not bool(y.isfinite().all()):raise FloatingPointError('Invalid logits')
            return y
        for i in range(4):
            expected=torch.load(original/'capture/logit-cache'/f'original-{i}.pt',weights_only=True)
            if not torch.equal(logits(cal[i]),expected):raise ValueError('Reference execution changed')
        cache=root/'logit-cache';cache.mkdir()
        for i,case in enumerate(cases):
            torch.save(logits(case),cache/f'original-{i}.pt');summary.update(current='reference',cases_completed=i+1);save()
        controls=[];changed=[]
        with replace_all(model,candidate):
            for i in range(2):changed.append(logits(cases[i]))
        with replace_all(model,candidate,dense=True):
            for i in range(2):controls.append(dict(case=i,**metrics(changed[i],logits(cases[i]),cases[i]['targets'])))
        write_json(root/'controls.json',controls)
        initial_effect=sum(metrics(torch.load(cache/f'original-{i}.pt',weights_only=True),changed[i],
                                  cases[i]['targets'])['rms'] for i in range(2))/2
        floor=max(r['rms'] for r in controls)
        if floor>=.01*initial_effect:raise ValueError('Candidate factor/dense floor too large')
        rows=[]
        for label,records in factors.items():
            condition=dict(label=label,status='running',cases_completed=0);summary['conditions'].append(condition);save()
            with replace_all(model,records):
                for i,case in enumerate(cases):
                    ref=torch.load(cache/f'original-{i}.pt',weights_only=True)
                    row=dict(label=label,case=i,**metrics(ref,logits(case),case['targets']));rows.append(row)
                    with (root/'per-case.jsonl').open('a') as stream:stream.write(json.dumps(row)+'\n')
                    condition['cases_completed']=i+1;save()
            own=[r for r in rows if r['label']==label]
            condition.update(status='complete',mean_kl=sum(r['kl_reference_to_changed'] for r in own)/64,
                mean_nll_delta=sum(r['nll_difference'] for r in own)/64,mean_rms=sum(r['rms'] for r in own)/64,
                argmax_disagreements=sum(r['argmax_disagreements'] for r in own));save()
        if floor>=.01*min(r['mean_rms'] for r in summary['conditions']):raise ValueError('Fidelity floor too large')
        if sha256_file(root/'frozen.json')!=summary['frozen_sha256']:raise ValueError('Procedure changed during validation')
        summary.update(status='complete',phase='complete',controls_max_rms=floor,full_task_accuracy=False);save()
    except Exception as exc:
        summary.update(status='failed',error=repr(exc));save();raise
    finally:signal.setitimer(signal.ITIMER_REAL,0)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);a=p.parse_args();main(a.root)
