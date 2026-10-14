#!/usr/bin/env python3
"""Independent CPU comparison of base-anchored weighted compression."""
import argparse
import importlib.metadata
import json
import os
from pathlib import Path
import signal
import sys
import time

os.environ.update(CUDA_VISIBLE_DEVICES='',OMP_NUM_THREADS='8',MKL_NUM_THREADS='8',OPENBLAS_NUM_THREADS='8',
                  HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',TOKENIZERS_PARALLELISM='false')
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from lora_dora_study.server import write_json,available_memory_bytes
from lora_dora_study.evaluation import sha256_file


def main(root):
    start=time.monotonic();summary=dict(status='running',conditions=[],training=False,device='cpu_fp32',rank=32)
    def save():summary['wall_seconds']=time.monotonic()-start;write_json(root/'summary.json',summary)
    def timeout(signum,frame):raise TimeoutError('Anchored comparison CPU budget exhausted')
    signal.signal(signal.SIGALRM,timeout);signal.setitimer(signal.ITIMER_REAL,14400);save()
    try:
        m=json.loads((root/'manifest-private.json').read_text());parent=Path(m['parent_root'])
        for rel,h in m['source_sha256'].items():
            if sha256_file(ROOT/rel)!=h:raise ValueError('Frozen code changed: '+rel)
        import torch
        from transformers import AutoModelForCausalLM,AutoTokenizer
        from peft import PeftModel
        from lora_dora_study.anchored_compression import anchors,canonical_values
        from lora_dora_study.weighted_compression import covariance_cholesky,weighted_factors
        from lora_dora_study.fidelity_audit import content_digest,metrics
        from lora_dora_study.compression_audit import selected_modules,replacement
        from lora_dora_study.adapters import verify_loaded_adapter
        from lora_dora_study.benchmarks import user_content
        torch.set_num_threads(4);torch.set_num_interop_threads(1);torch.manual_seed(20261013)
        versions={k:importlib.metadata.version(k) for k in ['torch','transformers','peft','safetensors','accelerate']}
        assert versions==m['versions'];summary['versions']=versions;summary['source_sha256']=m['source_sha256']
        capture=json.loads((parent/'capture/summary.json').read_text())
        assert capture['status']=='complete'
        for name,key in [('matrices.pt','matrices_sha256'),('activations.pt','activations_sha256')]:
            assert sha256_file(parent/'capture'/name)==capture[key]
        matrices=torch.load(parent/'capture/matrices.pt',map_location='cpu',weights_only=True)
        inputs=torch.load(parent/'capture/activations.pt',map_location='cpu',weights_only=True)
        coefficients=anchors(matrices);summary['anchor_scales']=coefficients
        # Test the canonical object under independent positive gauges on the real matrices.
        transformed={}
        for i,layer in enumerate(coefficients):
            g=.995 if i%2 else 1.005
            for name,r in matrices.items():
                if name.rsplit('.',1)[0]==layer:
                    transformed[name]=dict(base=r['base'],value=r['value'].double()*(g if name.endswith('v_proj') else 1/g))
        before,after=canonical_values(matrices),canonical_values(transformed)
        invariance={name:float((before[name]-after[name]).norm()/before[name].norm()) for name in before}
        if max(invariance.values())>1e-12:raise ValueError('Canonical matrix invariance failed')
        summary['ideal_fp64_canonical_relative_errors']=invariance
        # Freeze a separate validation set before factor construction/scoring.
        assert sha256_file(Path(m['calibration_cases']))==m['calibration_cases_sha256']
        cal=json.loads(Path(m['calibration_cases']).read_text())
        assert sha256_file(parent/'validation-cases.json')==capture['validation_cases_sha256']
        generic_val=json.loads((parent/'validation-cases.json').read_text())
        train=[json.loads(x) for x in Path(m['train']['path']).read_text().splitlines()]
        test=[json.loads(x) for x in Path(m['test']['path']).read_text().splitlines()]
        for label in ['train','test']:
            assert sha256_file(Path(m[label]['path']))==m[label]['sha256']
        excluded={content_digest(r) for r in train[:232]+test}|{r['prompt_content_sha256'] for r in cal+generic_val}
        tokenizer=AutoTokenizer.from_pretrained(m['artifacts']['base']['snapshot_path'],local_files_only=True)
        val=[];skips=[]
        for i,row in enumerate(train):
            h=content_digest(row)
            if h in excluded:continue
            prompt=tokenizer.apply_chat_template([dict(role='user',content=user_content('gsm8k',row))],tokenize=False,add_generation_prompt=True,enable_thinking=False)
            ids=tokenizer(prompt,add_special_tokens=False)['input_ids'];targets=tokenizer(row['answer'],add_special_tokens=False)['input_ids'][:32]
            if len(ids)>512 or len(targets)<32:skips.append(i);continue
            val.append(dict(train_index=i,prompt_content_sha256=h,input_ids=ids+targets[:-1],targets=targets));excluded.add(h)
            if len(val)==64:break
        assert len(val)==64
        write_json(root/'validation-cases.json',val)
        summary.update(validation_cases_sha256=sha256_file(root/'validation-cases.json'),structural_skips=skips);save()
        factors={};diagnostics=[]
        for name,r in matrices.items():
            layer=name.rsplit('.',1)[0];l,ridge=covariance_cholesky(inputs[name])
            for t in [1.,.995,1.005]:
                c=coefficients[layer]*t;scale=c if name.endswith('v_proj') else 1/c
                # Compute the canonical target in FP64, then deploy FP32 factors.
                delta=(r['value'].double()*scale-r['base'].double()).float()
                left,right,info=weighted_factors(delta,l*(c if name.endswith('o_proj') else 1.),32)
                factors.setdefault('anchor_'+str(t),{})[name]=dict(left=left,right=right)
                diagnostics.append(dict(module=name,t=t,source_gauge=c,ridge=ridge,factor_elements=left.numel()+right.numel(),**info))
            summary['prepared_modules']=len(diagnostics);save()
        torch.save(factors,root/'anchor-factors.pt');write_json(root/'diagnostics.json',diagnostics)
        prepared=json.loads((parent/'prepare/summary.json').read_text())
        assert prepared['status']=='complete' and sha256_file(parent/'prepare/factors.pt')==prepared['factors_sha256']
        original_factors=torch.load(parent/'prepare/factors.pt',map_location='cpu',weights_only=True)
        factors.update(original_factors)
        if available_memory_bytes()<64*1024**3:raise BlockingIOError('Insufficient CPU RAM')
        torch.set_num_threads(8);summary['cpu_threads']=8
        model=AutoModelForCausalLM.from_pretrained(m['artifacts']['base']['snapshot_path'],local_files_only=True,
            trust_remote_code=False,torch_dtype=torch.float32,device_map={'':'cpu'},low_cpu_mem_usage=True,attn_implementation='sdpa')
        model=PeftModel.from_pretrained(model,m['artifacts']['dora']['snapshot_path'],local_files_only=True,is_trainable=False).eval()
        model.requires_grad_(False);check=verify_loaded_adapter(model,m['artifacts']['dora']['snapshot_path'],True)
        assert check['exact_loaded_value_match'] and check['adapted_module_count']==144
        cache=root/'logit-cache';cache.mkdir();rows=[]
        def logits(case):
            x=torch.tensor([case['input_ids']],dtype=torch.long)
            with torch.inference_mode():y=model(input_ids=x,attention_mask=torch.ones_like(x),use_cache=False,logits_to_keep=32).logits[0].detach().cpu()
            if not bool(y.isfinite().all()):raise FloatingPointError('Nonfinite outputs')
            return y
        def reference(split,cases):
            for i,case in enumerate(cases):
                torch.save(logits(case),cache/f'{split}-{i}.pt')
                summary.update(current=split+'_reference',cases_completed=i+1);save()
        def run(split,cases,label):
            record=dict(split=split,label=label,status='running',cases_completed=0);summary['conditions'].append(record);save()
            records={name:dict(base=module.get_base_layer().weight.detach(),**factors[label][name]) for name,module in selected_modules(model,[0,17,35]).items()}
            with replacement(model,[0,17,35],'factorized',records):
                for i,case in enumerate(cases):
                    y=logits(case);ref=torch.load(cache/f'{split}-{i}.pt',weights_only=True,map_location='cpu')
                    row=dict(split=split,label=label,case=i,**metrics(ref,y,case['targets']));rows.append(row)
                    with (root/'per-case.jsonl').open('a') as f:f.write(json.dumps(row)+'\n')
                    record['cases_completed']=i+1;save()
            record.update(status='complete',mean_kl=sum(r['kl_reference_to_changed'] for r in rows if r['split']==split and r['label']==label)/64);save()
        reference('calibration',cal)
        for label in ['anchor_1.0','anchor_0.995','anchor_1.005']:run('calibration',cal,label)
        means={r['label']:r['mean_kl'] for r in summary['conditions']}
        choice=min(means,key=lambda x:(means[x],x!='anchor_1.0'))
        selection=dict(chosen=choice,calibration_mean_kl=means,rule='minimum KL over three base-anchored candidates',
            validation_cases_sha256=summary['validation_cases_sha256'],frozen_before_validation=True,anchor_factors_sha256=sha256_file(root/'anchor-factors.pt'))
        # Match the earlier grid-search baseline if its calibration selection is available.
        selected=['svd_1.0','weighted_1.0','anchor_1.0',choice]
        if (parent/'selection.json').exists():
            generic=json.loads((parent/'selection.json').read_text());selected+=list(generic['chosen'].values());selection['generic_selection']=generic
        selected=list(dict.fromkeys(selected));selection['validation_labels']=selected
        write_json(root/'selection.json',selection);summary.update(selection=selection,selection_sha256=sha256_file(root/'selection.json'));save()
        reference('validation',val)
        for label in selected:run('validation',val,label)
        assert sha256_file(root/'selection.json')==summary['selection_sha256']
        summary.update(status='complete',accepted_gpu_hours=0);save()
    except Exception as exc:summary.update(status='failed',error=repr(exc));save();raise
    finally:signal.setitimer(signal.ITIMER_REAL,0)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);main(p.parse_args().root)
