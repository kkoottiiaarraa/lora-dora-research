#!/usr/bin/env python3
"""Full-adapter gradient covariance capture for a bounded affine candidate."""
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

os.environ.update(CUDA_VISIBLE_DEVICES='',OMP_NUM_THREADS='16',MKL_NUM_THREADS='16',
    OPENBLAS_NUM_THREADS='16',HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',TOKENIZERS_PARALLELISM='false')
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from lora_dora_study.server import write_json,available_memory_bytes
from lora_dora_study.evaluation import sha256_file


def main(root):
    start=time.monotonic();summary=dict(status='running',phase='setup',gpu_count=0,
        training=False,started_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
    def save():
        summary.update(wall_seconds=time.monotonic()-start,
            rss_bytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024)
        write_json(root/'summary.json',summary)
    def timeout(signum,frame):raise TimeoutError('KFAC orientation probe deadline')
    signal.signal(signal.SIGALRM,timeout);signal.setitimer(signal.ITIMER_REAL,5400);save()
    try:
        manifest=json.loads((root/'manifest-private.json').read_text())
        for rel,digest in manifest['source_sha256'].items():
            if sha256_file(ROOT/rel)!=digest:raise ValueError('Source changed: '+rel)
        parent=Path(manifest['full_root']);fm=json.loads((parent/'manifest-private.json').read_text())
        original=Path(fm['parent_root']);old=json.loads((original/'manifest-private.json').read_text())
        capture=json.loads((parent/'capture/summary.json').read_text())
        import torch
        import torch.nn.functional as F
        from transformers import AutoModelForCausalLM
        from peft import PeftModel
        from lora_dora_study.adapters import verify_loaded_adapter
        from lora_dora_study.full_compression import adapted_modules
        torch.set_num_threads(16);torch.set_num_interop_threads(1);torch.manual_seed(20261014)
        torch.set_float32_matmul_precision('highest')
        versions={k:importlib.metadata.version(k) for k in old['versions']}
        if versions!=old['versions']:raise ValueError('Versions changed')
        if available_memory_bytes()<64*1024**3:raise BlockingIOError('Need 64GiB RAM')
        calpath=Path(old['calibration_cases'])
        if sha256_file(calpath)!=old['calibration_cases_sha256']:raise ValueError('Calibration changed')
        cases=json.loads(calpath.read_text())[:64]
        model=AutoModelForCausalLM.from_pretrained(old['artifacts']['base']['snapshot_path'],local_files_only=True,
            trust_remote_code=False,torch_dtype=torch.float32,device_map={'':'cpu'},low_cpu_mem_usage=True,attn_implementation='sdpa')
        model=PeftModel.from_pretrained(model,old['artifacts']['dora']['snapshot_path'],
            local_files_only=True,is_trainable=False).eval();model.requires_grad_(False)
        check=verify_loaded_adapter(model,old['artifacts']['dora']['snapshot_path'],True)
        if not check['exact_loaded_value_match'] or check['adapted_module_count']!=144:raise ValueError('Adapter mismatch')
        if any(p.dtype!=torch.float32 or p.device.type!='cpu' for p in model.parameters()):raise ValueError('Execution changed')
        for i,case in enumerate(cases[:4]):
            ids=torch.tensor([case['input_ids']])
            with torch.inference_mode():y=model(input_ids=ids,attention_mask=torch.ones_like(ids),use_cache=False,logits_to_keep=32).logits[0]
            ref=torch.load(original/'capture/logit-cache'/f'original-{i}.pt',weights_only=True,map_location='cpu')
            if not torch.equal(y,ref):raise ValueError('Native reference changed')
        selected=adapted_modules(model)
        if len(selected)!=144:raise ValueError('Module selection changed')
        covariances={};counts={n:0 for n in selected};handles=[]
        def capture_gradient(name):
            def forward_hook(module,arguments,output):
                if not output.requires_grad:raise ValueError('Missing backward graph')
                def backward_hook(grad):
                    g=grad.detach().reshape(-1,grad.shape[-1])[-32:].double()
                    if not bool(g.isfinite().all()):raise FloatingPointError('Invalid gradient')
                    gram=g.T@g
                    if name in covariances:covariances[name].add_(gram)
                    else:covariances[name]=gram
                    counts[name]+=len(g)
                output.register_hook(backward_hook)
            return forward_hook
        for name,module in selected.items():handles.append(module.register_forward_hook(capture_gradient(name)))
        handles.append(model.get_input_embeddings().register_forward_hook(
            lambda module,args,output:output.detach().requires_grad_(True)))
        for i,case in enumerate(cases):
            ids=torch.tensor([case['input_ids']]);targets=torch.tensor(case['targets'])
            y=model(input_ids=ids,attention_mask=torch.ones_like(ids),use_cache=False,logits_to_keep=32).logits[0]
            loss=F.cross_entropy(y,targets,reduction='sum')
            if not bool(loss.isfinite()):raise FloatingPointError('Invalid loss')
            loss.backward()
            if any(p.grad is not None for p in model.parameters()):raise ValueError('Parameter gradients allocated')
            del y,loss
            summary.update(phase='capture',cases_completed=i+1);save()
        for handle in handles:handle.remove()
        del model
        torch.set_num_threads(4);rows=[]
        folder=root/'covariances';folder.mkdir()
        for index,name in enumerate(list(covariances)):
            g=covariances.pop(name)/counts[name]
            if counts[name]!=2048:raise ValueError('Gradient coverage mismatch')
            diagonal=float(g.diag().mean())
            if diagonal<=0:raise ValueError('Degenerate gradient covariance')
            g.mul_(.7);g.diagonal().add_(.3*diagonal)
            path=folder/f'{index:03}.pt';torch.save(dict(row_covariance=g),path)
            rows.append(dict(module=name,gradient_tokens=counts[name],shape=list(g.shape),
                file=str(path.relative_to(root)),sha256=sha256_file(path)))
            write_json(root/'covariance-index.json',rows)
            summary.update(phase='save_covariances',modules_completed=index+1);save()
        summary.update(status='complete',phase='complete',versions=versions,adapter_exact=True,
            source_sha256=manifest['source_sha256'],calibration_cases_sha256=old['calibration_cases_sha256'],
            row_shrinkage=.3,cases=64,modules=144,no_parameter_updates=True)
        save()
    except Exception as exc:
        summary.update(status='failed',error=repr(exc));save();raise
    finally:signal.setitimer(signal.ITIMER_REAL,0)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True)
    args=p.parse_args();main(args.root)
