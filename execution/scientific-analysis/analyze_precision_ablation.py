#!/usr/bin/env python3
"""Accept all triangular-screen cells and compute matched ablation contrasts."""
import argparse
import collections
import csv
import hashlib
import json
import math
from pathlib import Path
import statistics


def main(source,output):
    folders=[source/'precision/gpu',source/'precision/cpu']
    by=collections.defaultdict(dict);summaries=[]
    for folder in folders:
        s=json.loads((folder/'summary.json').read_text())
        if s['status']!='complete':raise ValueError('Incomplete worker')
        summaries.append(s)
        for file,key in [('frozen.json','frozen_sha256'),('cases.json','cases_sha256')]:
            if hashlib.sha256((folder/file).read_bytes()).hexdigest()!=s[key]:raise ValueError('Input changed')
        for r in map(json.loads,(folder/'per-case.jsonl').read_text().splitlines()):
            key=(r['cell'],r['condition'])
            if r['case'] in by[key] or r['tokens']!=32:raise ValueError('Duplicate/invalid row')
            if any(not math.isfinite(r[k]) for k in ['rms','nll_difference','changed_nll','reference_nll','kl_reference_to_changed']):
                raise ValueError('Nonfinite metric')
            by[key][r['case']]=r
    if summaries[0]['cases_sha256']!=summaries[1]['cases_sha256']:raise ValueError('Cells not aligned')
    cells=['cpu_float32','cuda_float32','cuda_bfloat16']
    conditions=['native_source','native_remove_d','dense_source','dense_remove_d','repeat_native','official_dense_control']
    if set(by)!={(cell,cond) for cell in cells for cond in conditions}:raise ValueError('Condition coverage')
    if sum(map(len,by.values()))!=108:raise ValueError('Row count')
    quality=[];contrasts=[];values={}
    for cell in cells:
        folder=folders[1] if cell.startswith('cpu') else folders[0]
        audit=json.loads((folder/(cell+'-dtype-audit.json')).read_text())
        if len(audit)!=144 or any(info[k]!='torch.float32' for info in audit.values() for k in ['a_dtype','b_dtype','m_dtype']):
            raise ValueError('Adapter dtype contract')
        merge=json.loads((folder/(cell+'-merge-check.json')).read_text())
        if merge['status']!='PASS' or len(merge['custom_sha256'])!=144 or merge['custom_sha256']!=merge['official_sha256']:
            raise ValueError('Official/custom mismatch')
        for cond in conditions:
            rows=by[(cell,cond)];n=2 if cond in ['repeat_native','official_dense_control'] else 8
            if set(rows)!=set(range(n)):raise ValueError('Misaligned condition')
            if n==2 and any(r['max_abs']!=0 for r in rows.values()):raise ValueError('Repeat/merge not exact')
            quality.append(dict(cell=cell,condition=cond,cases=n,mean_nll=statistics.mean(r['changed_nll'] for r in rows.values()),
                mean_nll_delta=statistics.mean(r['nll_difference'] for r in rows.values()),
                mean_rms=statistics.mean(r['rms'] for r in rows.values()),
                mean_kl=statistics.mean(r['kl_reference_to_changed'] for r in rows.values()),
                argmax_disagreements=sum(r['argmax_disagreements'] for r in rows.values())))
        values[cell]={cond:statistics.mean(r['nll_difference'] for r in by[(cell,cond)].values()) for cond in ['native_remove_d','dense_remove_d','dense_source']}
        vals=values[cell]
        contrasts.append(dict(cell=cell,native_contrast=vals['native_remove_d'],dense_matched_contrast=vals['dense_remove_d'],
            native_to_dense_source_shift=vals['dense_source'],mixed_contrast=vals['dense_remove_d']+vals['dense_source'],
            dense_minus_native_contrast=vals['dense_remove_d']-vals['native_remove_d']))
        if cell!='cuda_bfloat16':
            f=statistics.mean(r['rms'] for r in by[(cell,'dense_source')].values())
            e=statistics.mean(r['rms'] for r in by[(cell,'native_remove_d')].values())
            if f>=.01*e:raise ValueError('FP32 floor exceeds1%effect')
    threshold=max(.001,.5*abs(values['cpu_float32']['native_remove_d']))
    comparisons=[]
    for cell in cells:
        delta=values[cell]['dense_remove_d']-values[cell]['native_remove_d']
        comparisons.append(dict(comparison=cell+'_matched_path',delta=delta,gate_eligible=True,passes=abs(delta)>threshold))
    for cond in ['native_remove_d','dense_remove_d']:
        precision=values['cuda_bfloat16'][cond]-values['cuda_float32'][cond]
        backend=values['cuda_float32'][cond]-values['cpu_float32'][cond]
        comparisons.extend([dict(comparison=cond+'_cuda_precision',delta=precision,gate_eligible=True,passes=abs(precision)>threshold),
            dict(comparison=cond+'_fp32_backend',delta=backend,gate_eligible=False,passes=False)])
    output.mkdir(parents=True,exist_ok=True)
    for name,records in [('quality.csv',quality),('matched-contrasts.csv',contrasts),('path-comparisons.csv',comparisons)]:
        with (output/name).open('w',newline='') as stream:
            w=csv.DictWriter(stream,fieldnames=list(dict.fromkeys(k for r in records for k in r)));w.writeheader();w.writerows(records)
    result=dict(status='PASS',cases=8,rows=108,cases_sha256=summaries[0]['cases_sha256'],
        engineering_gate=any(r['passes'] for r in comparisons),gate_threshold_nll=threshold,
        contrasts=contrasts,comparisons=comparisons,versions=summaries[0]['versions'],artifacts=summaries[0]['artifacts'],
        source_sha256=summaries[0]['source_sha256'],gpu_success_wall_seconds=summaries[0]['wall_seconds'],
        gpu_failed_setup_wall_seconds=16.509456033003516,
        gpu_total_wall_hours=(summaries[0]['wall_seconds']+16.509456033003516)/3600,
        cpu_wall_seconds=summaries[1]['wall_seconds'],gpu_memory=summaries[0]['gpu_memory'],
        full_factorial=False,confirmed_scientific_sign_reversal=False,full_task_accuracy=False,conference_level_established=False)
    (output/'validation.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ['status','engineering_gate','contrasts','comparisons','gpu_total_wall_hours']},indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--source',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();main(a.source,a.output)
