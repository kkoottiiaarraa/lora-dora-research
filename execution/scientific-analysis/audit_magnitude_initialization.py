"""Read only stored magnitude versus FP32 and base-storage rounded row norms."""
import argparse,contextlib,hashlib,json,os,time
from pathlib import Path
os.environ.update(CUDA_VISIBLE_DEVICES='',OMP_NUM_THREADS='2',OPENBLAS_NUM_THREADS='2')

def main(root):
    import torch
    from safetensors import safe_open
    torch.set_num_threads(2);start=time.monotonic();manifest=json.loads((root/'manifest-private.json').read_text());records=[]
    for group in manifest['groups']:
        base=Path(group['base_path']);index=base/'model.safetensors.index.json'
        mapping=json.loads(index.read_text())['weight_map']if index.exists()else None
        with contextlib.ExitStack()as stack:
            handles={}
            def get(key):
                file=mapping[key]if mapping else 'model.safetensors'
                if file not in handles:handles[file]=stack.enter_context(safe_open(str(base/file),framework='pt',device='cpu'))
                return handles[file].get_tensor(key)
            for entry in group['adapters']:
                with safe_open(str(Path(entry['snapshot_path'])/'adapter_model.safetensors'),framework='pt',device='cpu')as adapter:
                    keys=[k for k in adapter.keys()if 'lora_magnitude_vector'in k];rows=[]
                    for key in keys:
                        module=key.split('.lora_magnitude_vector')[0];bk=module.removeprefix('base_model.model.')+'.weight';w=get(bk);n=w.float().norm(dim=1);m=adapter.get_tensor(key)
                        if n.shape!=m.shape or not bool(n.isfinite().all()and m.isfinite().all()and(n>0).all()):raise ValueError('Invalid vectors')
                        rounded=n.to(w.dtype).float();native_norm=w.norm(dim=1).float();mf=m.float()
                        rows.append(dict(module=module,coordinates=n.numel(),saved_dtype=str(m.dtype),base_dtype=str(w.dtype),
                          fp32_norm_equal=int((mf==n).sum()),base_dtype_norm_equal=int((mf==rounded).sum()),native_dtype_norm_equal=int((mf==native_norm).sum()),
                          max_relative_residual_from_rounded=float(((mf-rounded)/n).abs().max()),
                          relative_rms_from_rounded=float(((mf-rounded)/n).square().mean().sqrt())))
                    total=sum(r['coordinates']for r in rows)
                    records.append(dict(repo_id=entry['repo_id'],revision=entry['revision'],base_repo_id=group['base_repo_id'],base_revision=group['base_revision'],
                      adapter_file_sha256=hashlib.sha256((Path(entry['snapshot_path'])/'adapter_model.safetensors').read_bytes()).hexdigest(),
                      modules=len(rows),coordinates=total,fp32_norm_equal_fraction=sum(r['fp32_norm_equal']for r in rows)/total,
                      base_dtype_norm_equal_fraction=sum(r['base_dtype_norm_equal']for r in rows)/total,native_dtype_norm_equal_fraction=sum(r['native_dtype_norm_equal']for r in rows)/total,
                      max_relative_residual_from_rounded=max(r['max_relative_residual_from_rounded']for r in rows),rows=rows))
    result=dict(status='complete',wall_seconds=time.monotonic()-start,gpu_hours=0,model_forwards=0,training_cause_identified=False,records=records)
    (root/'audit.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({**result,'records':[{k:v for k,v in r.items()if k!='rows'}for r in records]},indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);main(p.parse_args().root)
