#!/usr/bin/env python3
"""Lightweight independent acceptance of the fixed nine-head screen."""
import argparse,csv,hashlib,json,math
from pathlib import Path


def main(source,out):
    s=json.loads((source/'summary.json').read_text());f=json.loads((source/'frozen.json').read_text())
    heads=json.loads((source/'heads.json').read_text())
    if s['status']!='complete' or s['heads_completed']!=9 or len(heads)!=9:raise ValueError('Incomplete')
    if hashlib.sha256((source/'frozen.json').read_bytes()).hexdigest()!=s['frozen_sha256']:raise ValueError('Frozen input mismatch')
    if {(r['layer'],r['head']) for r in heads}!={(l,h) for l in [0,17,35] for h in [0,15,31]}:raise ValueError('Head coverage')
    rows=[];spectra=[]
    for r in heads:
        singular=r['singular_values']
        if len(singular)!=128 or any(not math.isfinite(x) or x<0 for x in singular):raise ValueError('Invalid spectrum')
        if any(a<b for a,b in zip(singular,singular[1:])):raise ValueError('Unordered spectrum')
        tail=sum(x*x for x in singular[32:]);energy=sum(x*x for x in singular)
        if not math.isclose(tail,r['tail_energy'],rel_tol=1e-12) or not math.isclose(energy,r['outside_energy'],rel_tol=1e-12):raise ValueError('Tail recomputation mismatch')
        if r['no_d_tail_fraction_source']>1e-20 or len(r['gauges'])!=2 or any(g['relative_tail_change']>1e-10 for g in r['gauges']):raise ValueError('Algebraic control failed')
        practical=(r['tail_fraction_source']>=1e-6 and r['tail_fraction_outside']>=.05 and tail>=1000*r['fp32_merge_action_floor'])
        if practical!=r['practical_gate']:raise ValueError('Gate changed')
        rows.append({k:v for k,v in r.items() if k not in ['singular_values','gauges']})
        spectra.extend(dict(layer=r['layer'],head=r['head'],index=i+1,singular_value=v) for i,v in enumerate(singular))
    out.mkdir(parents=True,exist_ok=True)
    for filename,records in [('bounds.csv',rows),('spectra.csv',spectra)]:
        with (out/filename).open('w',newline='') as stream:
            w=csv.DictWriter(stream,fieldnames=list(records[0]));w.writeheader();w.writerows(records)
    result=dict(status='PASS',heads=9,calibration_rows_per_head=2048,practical_heads=sum(r['practical_gate'] for r in rows),
        passed_practical_gate=sum(r['practical_gate'] for r in rows)>=3,
        source_tail_range=[min(r['tail_fraction_source'] for r in rows),max(r['tail_fraction_source'] for r in rows)],
        outside_tail_range=[min(r['tail_fraction_outside'] for r in rows),max(r['tail_fraction_outside'] for r in rows)],
        maximum_no_d_tail_fraction=max(r['no_d_tail_fraction_source'] for r in rows),
        maximum_gauge_relative_tail_change=max(g['relative_tail_change'] for r in heads for g in r['gauges']),
        versions=s['versions'],artifacts=s['artifacts'],adapter_weights_sha256=s['adapter_weights_sha256'],
        calibration_cases_sha256=f['calibration_cases_sha256'],source_module_sha256=f['source_module_sha256'],source_sha256=s['source_sha256'],
        wall_seconds=s['wall_seconds'],rss_bytes=s['rss_bytes'],gpu_hours=0,model_loaded=False,
        network_expressivity_lower_bound=False,task_quality=False,conference_level_established=False)
    (out/'validation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--source',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();main(a.source,a.output)
