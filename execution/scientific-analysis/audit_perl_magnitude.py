"""Read-only safe-tensor magnitude trajectory and initialization rounding audit."""
import argparse,hashlib,json,os,sys,time
from pathlib import Path
os.environ.update(CUDA_VISIBLE_DEVICES='',OMP_NUM_THREADS='2',OPENBLAS_NUM_THREADS='2')

def main(root):
    import torch
    from safetensors import safe_open
    torch.set_num_threads(2);start=time.monotonic();p=json.loads((root/'download-result-private.json').read_text());a=p['artifacts']
    if p['status']!='complete':raise ValueError('Incomplete downloads')
    out=[];snapshots={}
    for step in [64,512,1024]:
        with safe_open(str(Path(a[str(step)]['snapshot_path'])/'adapter_model.safetensors'),framework='pt',device='cpu')as f:
            snapshots[step]={k:f.get_tensor(k)for k in f.keys()if 'lora_magnitude_vector'in k}
    if any(len(x)!=196 for x in snapshots.values())or any(set(x)!=set(snapshots[64])for x in snapshots.values()):raise ValueError('Magnitude coverage')
    with safe_open(str(Path(a['base']['snapshot_path'])/'model.safetensors'),framework='pt',device='cpu')as base:
        for key in sorted(snapshots[64]):
            module=key.split('.lora_magnitude_vector')[0];bk=module.removeprefix('base_model.model.')+'.weight'
            w=base.get_tensor(bk);n=w.float().norm(dim=1)
            ms=[snapshots[t][key]for t in [64,512,1024]]
            if any(x.shape!=n.shape or not bool(x.isfinite().all())for x in ms):raise ValueError('Bad magnitude')
            rounded=n.to(ms[0].dtype)
            out.append(dict(module=module,storage_dtype=str(ms[0].dtype),coordinates=n.numel(),
              early_mid_equal=int((ms[0]==ms[1]).sum()),early_late_equal=int((ms[0]==ms[2]).sum()),
              early_rounded_init_equal=int((ms[0]==rounded).sum()),late_rounded_init_equal=int((ms[2]==rounded).sum()),
              early_to_late_relative_rms=float(((ms[2].float()-ms[0].float())/n).square().mean().sqrt()),
              early_to_late_max_relative=float(((ms[2].float()-ms[0].float())/n).abs().max())))
    total=sum(r['coordinates']for r in out)
    result=dict(status='complete',modules=196,coordinates=total,wall_seconds=time.monotonic()-start,gpu_hours=0,
      training_cause_identified=False,base_training_revision_known=False,stored_dtype=list(sorted({r['storage_dtype']for r in out})),
      **{k:sum(r[k]for r in out)/total for k in ['early_mid_equal','early_late_equal','early_rounded_init_equal','late_rounded_init_equal']},
      all_m_equal_early_late=all(r['early_late_equal']==r['coordinates']for r in out),
      artifact_weight_sha256={k:v['weight_sha256']for k,v in a.items()},rows=out)
    (root/'magnitude-audit.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items()if k!='rows'},indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);main(p.parse_args().root)
