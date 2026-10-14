#!/usr/bin/env python3
"""Exploratory one-projection rescue using immutable allocation factors/cases."""
import argparse
import json
import os
from pathlib import Path
import resource
import signal
import sys
import time

os.environ.update(CUDA_VISIBLE_DEVICES='',OMP_NUM_THREADS='16',MKL_NUM_THREADS='16',
    OPENBLAS_NUM_THREADS='16',HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',TOKENIZERS_PARALLELISM='false')
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from lora_dora_study.server import write_json,available_memory_bytes
from lora_dora_study.evaluation import sha256_file


def main(root):
    start=time.monotonic();summary=dict(status='running',conditions=[],gpu_count=0,training=False,
        exploratory=True,equal_budget=False)
    def save():
        summary.update(wall_seconds=time.monotonic()-start,
            rss_bytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024)
        write_json(root/'summary.json',summary)
    def timeout(signum,frame):raise TimeoutError('Restoration diagnostic deadline')
    signal.signal(signal.SIGALRM,timeout);signal.setitimer(signal.ITIMER_REAL,3600);save()
    try:
        m=json.loads((root/'manifest-private.json').read_text())
        for rel,digest in m['source_sha256'].items():
            if sha256_file(ROOT/rel)!=digest:raise ValueError('Source changed: '+rel)
        parent=Path(m['allocation_root'])
        if json.loads((parent/'evaluate/summary.json').read_text())['status']!='complete':raise ValueError('Original incomplete')
        frozen=json.loads((parent/'frozen.json').read_text())
        if sha256_file(parent/'factors.pt')!=frozen['factors_sha256']:raise ValueError('Factors changed')
        em=json.loads((parent/'eval-manifest-private.json').read_text())
        full=Path(em['full_root']);fm=json.loads((full/'manifest-private.json').read_text())
        original=Path(fm['parent_root']);old=json.loads((original/'manifest-private.json').read_text())
        casespath=parent/'evaluate/cases.json';cases=json.loads(casespath.read_text())
        if sha256_file(casespath)!=json.loads((parent/'evaluate/frozen.json').read_text())['cases_sha256']:
            raise ValueError('Cases changed')
        import torch
        from transformers import AutoModelForCausalLM
        from peft import PeftModel
        from lora_dora_study.full_compression import replace_all,adapted_modules
        from lora_dora_study.adapters import verify_loaded_adapter
        from lora_dora_study.fidelity_audit import metrics
        torch.set_num_threads(16);torch.set_num_interop_threads(1);torch.manual_seed(20261014)
        torch.set_float32_matmul_precision('highest')
        if available_memory_bytes()<64*1024**3:raise BlockingIOError('Need64GiB RAM')
        model=AutoModelForCausalLM.from_pretrained(old['artifacts']['base']['snapshot_path'],local_files_only=True,
            trust_remote_code=False,torch_dtype=torch.float32,device_map={'':'cpu'},low_cpu_mem_usage=True,attn_implementation='sdpa')
        model=PeftModel.from_pretrained(model,old['artifacts']['dora']['snapshot_path'],local_files_only=True,is_trainable=False).eval()
        model.requires_grad_(False);check=verify_loaded_adapter(model,old['artifacts']['dora']['snapshot_path'],True)
        if not check['exact_loaded_value_match'] or check['adapted_module_count']!=144:raise ValueError('Adapter mismatch')
        def logits(case):
            ids=torch.tensor([case['input_ids']],dtype=torch.long)
            with torch.inference_mode():return model(input_ids=ids,attention_mask=torch.ones_like(ids),use_cache=False,logits_to_keep=32).logits[0].detach().cpu()
        for i,case in enumerate(cases[:2]):
            reference=torch.load(parent/'evaluate/logit-cache'/f'original-{i}.pt',map_location='cpu',weights_only=True)
            if not torch.equal(logits(case),reference):raise ValueError('Cached native teacher changed')
        modules=adapted_modules(model)
        matches=[(n,v) for n,v in modules.items() if n.endswith('.layers.1.self_attn.k_proj')]
        if len(matches)!=1:raise ValueError('Missing native K1')
        name,native=matches[0];owner_name,leaf=name.rsplit('.',1);owner=model.get_submodule(owner_name)
        native_elements=sum(p.numel() for p in [native.lora_A['default'].weight,native.lora_B['default'].weight,native.lora_magnitude_vector['default'].weight])
        factors=torch.load(parent/'factors.pt',map_location='cpu',weights_only=True)
        for label in ['weighted_uniform','weighted_allocated','structural_allocated']:
            replaced_elements=sum(t.numel() for t in factors[label][name].values())
            condition=dict(label=label+'_restore_k1',status='running',cases_completed=0,
                source_condition=label,additional_elements=native_elements-replaced_elements,
                actual_adapter_elements=5898240+native_elements-replaced_elements)
            summary['conditions'].append(condition);save();rows=[]
            with replace_all(model,factors[label]):
                owner._modules[leaf]=native
                for i,case in enumerate(cases):
                    reference=torch.load(parent/'evaluate/logit-cache'/f'original-{i}.pt',map_location='cpu',weights_only=True)
                    row=dict(label=condition['label'],case=i,**metrics(reference,logits(case),case['targets']));rows.append(row)
                    with (root/'per-case.jsonl').open('a') as stream:stream.write(json.dumps(row)+'\n')
                    condition['cases_completed']=i+1;save()
            condition.update(status='complete',mean_kl=sum(r['kl_reference_to_changed'] for r in rows)/64,
                mean_nll_delta=sum(r['nll_difference'] for r in rows)/64,
                argmax_disagreements=sum(r['argmax_disagreements'] for r in rows));save()
        summary.update(status='complete',source_sha256=m['source_sha256'],cases_sha256=sha256_file(casespath),full_task_accuracy=False);save()
    except Exception as exc:
        summary.update(status='failed',error=repr(exc));save();raise
    finally:signal.setitimer(signal.ITIMER_REAL,0)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True)
    args=p.parse_args();main(args.root)
