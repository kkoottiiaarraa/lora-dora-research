#!/usr/bin/env python3
"""Prepare one joint affine candidate and three fixed-budget comparators."""
import argparse
import importlib.metadata
import json
import os
from pathlib import Path
import resource
import signal
import sys
import time

os.environ.update(CUDA_VISIBLE_DEVICES='',OMP_NUM_THREADS='8',MKL_NUM_THREADS='8',OPENBLAS_NUM_THREADS='8')
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from lora_dora_study.server import write_json,available_memory_bytes
from lora_dora_study.evaluation import sha256_file


def main(root):
    start=time.monotonic();out=root/'prepare';out.mkdir(exist_ok=False)
    summary=dict(status='running',phase='setup',gpu_count=0,training=False,modules_completed=0)
    def save():
        summary.update(wall_seconds=time.monotonic()-start,
            rss_bytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024)
        write_json(out/'summary.json',summary)
    def timeout(signum,frame):raise TimeoutError('Affine preparation deadline')
    signal.signal(signal.SIGALRM,timeout);signal.setitimer(signal.ITIMER_REAL,7200);save()
    try:
        manifest=json.loads((root/'prepare-manifest-private.json').read_text())
        for rel,digest in manifest['source_sha256'].items():
            if sha256_file(ROOT/rel)!=digest:raise ValueError('Frozen source changed: '+rel)
        gradient_summary=json.loads((root/'summary.json').read_text())
        if gradient_summary['status']!='complete' or gradient_summary['modules']!=144:
            raise ValueError('Gradient capture incomplete')
        parent=Path(manifest['full_root'])
        capture=json.loads((parent/'capture/summary.json').read_text())
        oldprep=json.loads((parent/'prepare/summary.json').read_text())
        if sha256_file(parent/'prepare/factors.pt')!=oldprep['factors_sha256']:
            raise ValueError('Existing W-SVD factors changed')
        import torch
        from lora_dora_study.affine_compression import alternating_affine,weighted_rank_factors,objective
        from lora_dora_study.full_compression import structural_ranks
        from lora_dora_study.weighted_compression import covariance_cholesky
        torch.set_num_threads(8);torch.set_num_interop_threads(1)
        torch.manual_seed(20261014);torch.set_float32_matmul_precision('highest')
        versions={k:importlib.metadata.version(k) for k in capture['versions']}
        if versions!=capture['versions']:raise ValueError('Versions changed')
        if available_memory_bytes()<16*1024**3:raise BlockingIOError('Need16GiBRAM')
        summary.update(versions=versions,cpu_threads=8,source_sha256=manifest['source_sha256'])
        shapes={item['name']:item['shape'] for item in capture['modules']}
        ranks=structural_ranks(shapes,8)
        gradients={item['module']:item for item in json.loads((root/'covariance-index.json').read_text())}
        if set(gradients)!=set(shapes):raise ValueError('Covariance coverage changed')
        old=torch.load(parent/'prepare/factors.pt',map_location='cpu',weights_only=True)
        factors=dict(weighted_uniform=old['weighted_8'],kfac_uniform={},structural_kfac={},joint_kfac={})
        del old
        folder=out/'modules';folder.mkdir();diagnostics=[];checkpoints=[]
        for index,item in enumerate(capture['modules']):
            name=item['name'];path=parent/'capture'/item['file']
            if sha256_file(path)!=item['sha256']:raise ValueError('Source capture changed')
            graditem=gradients[name];gpath=root/graditem['file']
            if sha256_file(gpath)!=graditem['sha256']:raise ValueError('Gradient covariance changed')
            data=torch.load(path,map_location='cpu',weights_only=True)
            g=torch.load(gpath,map_location='cpu',weights_only=True)['row_covariance']
            if graditem['gradient_tokens']!=2048:raise ValueError('Wrong gradient coverage')
            cl,ridge=covariance_cholesky(data['inputs'])
            gl=torch.linalg.cholesky(g)
            b,t,d=data['base'].double(),data['value'].double(),data['row_scale'].double()
            left,right,ordinary=weighted_rank_factors(t-b,gl,cl,8)
            factors['kfac_uniform'][name]=dict(left=left.float().contiguous(),right=right.float().contiguous())
            left,right,fixed=weighted_rank_factors(t-d[:,None]*b,gl,cl,ranks[name])
            factors['structural_kfac'][name]=dict(left=left.float().contiguous(),right=right.float().contiguous(),row_scale=d.float())
            record,history=alternating_affine(b,t,d,g,cl,ranks[name],iterations=5)
            candidate_loss=objective(b,t,record['row_scale'].double(),record['left'].double(),record['right'].double(),gl,cl)
            if candidate_loss>fixed*(1+1e-4):raise ValueError('Deployed candidate local objective increased')
            factors['joint_kfac'][name]=record
            checkpoint={label:records[name] for label,records in factors.items()}
            for label,rec in checkpoint.items():
                expected=(8 if label in ['weighted_uniform','kfac_uniform'] else ranks[name])*sum(item['shape'])
                if 'row_scale' in rec:expected+=item['shape'][0]
                if sum(x.numel() for x in rec.values())!=expected:raise ValueError('Module storage mismatch')
                if any(x.dtype!=torch.float32 or not bool(x.isfinite().all()) for x in rec.values()):
                    raise ValueError('Invalid exported factor')
            destination=folder/f'{index:03}.pt';torch.save(checkpoint,destination)
            checkpoints.append(dict(module=name,file=str(destination.relative_to(out)),sha256=sha256_file(destination)))
            diagnostics.append(dict(module=name,rank=ranks[name],shape=item['shape'],ridge=ridge,
                ordinary_kfac_local_loss=ordinary,fixed_kfac_local_loss=fixed,
                joint_kfac_local_loss=candidate_loss,history=history,
                maximum_diagonal_change=float((record['row_scale'].double()-d).abs().max())))
            write_json(out/'diagnostics.json',diagnostics);write_json(out/'checkpoints.json',checkpoints)
            summary.update(phase='decompose',modules_completed=index+1);save()
            del data,g,gl,cl,b,t,d,left,right,record
        counts={label:sum(x.numel() for rec in records.values() for x in rec.values())
            for label,records in factors.items()}
        if any(value!=5898240 for value in counts.values()):raise ValueError('Unequal full budgets')
        torch.save(factors,out/'factors.pt')
        write_json(out/'frozen.json',dict(factors_sha256=sha256_file(out/'factors.pt'),
            source_sha256=manifest['source_sha256'],factor_counts=counts,
            gradient_capture_sha256=sha256_file(root/'covariance-index.json'),
            calibration_cases_sha256=gradient_summary['calibration_cases_sha256'],
            frozen_before_outputs=True,iterations=5))
        fixed=sum(row['fixed_kfac_local_loss'] for row in diagnostics)
        joint=sum(row['joint_kfac_local_loss'] for row in diagnostics)
        ordinary=sum(row['ordinary_kfac_local_loss'] for row in diagnostics)
        summary.update(status='complete',phase='complete',factor_counts=counts,
            frozen_sha256=sha256_file(out/'frozen.json'),aggregate_local_gain=1-joint/fixed,
            aggregate_ratio_vs_ordinary=joint/ordinary);save()
    except Exception as exc:
        summary.update(status='failed',error=repr(exc));save();raise
    finally:signal.setitimer(signal.ITIMER_REAL,0)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True)
    args=p.parse_args();main(args.root)
