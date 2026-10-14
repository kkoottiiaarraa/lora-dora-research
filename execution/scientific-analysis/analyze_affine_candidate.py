#!/usr/bin/env python3
"""Independent paired analysis for one frozen affine candidate, stdlib only."""
import argparse
import collections
import csv
import hashlib
import json
import math
from pathlib import Path
import statistics
from analyze_allocation_diagnosis import compare


def main(source,output):
    summary=json.loads((source/'evaluate/summary.json').read_text())
    prep=json.loads((source/'prepare/summary.json').read_text())
    if summary['status']!='complete' or prep['status']!='complete':raise ValueError('Incomplete')
    rows=[json.loads(line) for line in (source/'evaluate/per-case.jsonl').read_text().splitlines()]
    groups=collections.defaultdict(dict)
    for row in rows:
        if row['case'] in groups[row['label']]:raise ValueError('Duplicate case')
        for key in ['kl_reference_to_changed','nll_difference','rms']:
            if not math.isfinite(row[key]):raise ValueError('Nonfinite metric')
        groups[row['label']][row['case']]=row
    labels=['weighted_uniform','kfac_uniform','structural_kfac','native_m_input','native_m_kfac','joint_kfac']
    if set(groups)!=set(labels) or len(rows)!=768:raise ValueError('Wrong conditions/coverage')
    if any(set(group)!=set(range(128)) for group in groups.values()):raise ValueError('Misaligned cases')
    frozen=json.loads((source/'evaluate/frozen.json').read_text())
    if hashlib.sha256((source/'evaluate/cases.json').read_bytes()).hexdigest()!=frozen['cases_sha256']:
        raise ValueError('Case hash changed')
    if any(count!=5898240 for count in frozen['factor_counts'].values()):raise ValueError('Unequal budgets')
    controls=json.loads((source/'evaluate/controls.json').read_text())
    if max(row['rms'] for row in controls)>=.01*min(c['mean_rms'] for c in summary['conditions']):
        raise ValueError('Numerical floor too large')
    contrasts=[]
    for index,label in enumerate(labels[:5]):
        old=[groups[label][i]['kl_reference_to_changed'] for i in range(128)]
        new=[groups['joint_kfac'][i]['kl_reference_to_changed'] for i in range(128)]
        result=compare(old,new,20261014+index)
        # Gold NLL may be negative relative to teacher, so use paired bootstrap
        # directly; the relative-gain calculation in compare is not applicable.
        import random
        rng=random.Random(20261024+index)
        differences=[groups['joint_kfac'][i]['nll_difference']-groups[label][i]['nll_difference'] for i in range(128)]
        boot=sorted(sum(differences[rng.randrange(128)] for _ in range(128))/128 for _ in range(10000))
        result.update(reference=label,gold_nll_mean_delta=statistics.mean(differences),
            gold_nll_delta_ci95=[boot[249],boot[9749]])
        contrasts.append(result)
    largest=0
    for rank,index in enumerate(sorted(range(5),key=lambda i:contrasts[i]['sign_flip_p'])):
        largest=max(largest,min(1,(5-rank)*contrasts[index]['sign_flip_p']))
        contrasts[index]['holm_p']=largest
    means={label:statistics.mean(r['kl_reference_to_changed'] for r in groups[label].values()) for label in labels}
    best=min(labels[:5],key=lambda label:means[label])
    comparison=next(row for row in contrasts if row['reference']==best)
    gate=(comparison['mean_relative_gain']>=.1 and all(row['holm_p']<.05 and row['mean_delta']<0 for row in contrasts)
          and comparison['gold_nll_delta_ci95'][0]<=0)
    output.mkdir(parents=True,exist_ok=True)
    for name,records in [('quality.csv',summary['conditions']),('contrasts.csv',contrasts)]:
        fields=list(dict.fromkeys(k for row in records for k in row))
        with (output/name).open('w',newline='') as stream:
            writer=csv.DictWriter(stream,fieldnames=fields);writer.writeheader();writer.writerows(records)
    result=dict(status='PASS',case_count=128,tokens_per_condition=4096,rows=768,contrasts=contrasts,
        strongest_mean_baseline=best,passed_development_gate=gate,
        versions=summary['versions'],source_sha256=summary['source_sha256'],
        cases_sha256=frozen['cases_sha256'],controls_max_rms=summary['controls_max_rms'],
        prepare_wall_seconds=prep['wall_seconds'],evaluate_wall_seconds=summary['wall_seconds'],
        full_task_accuracy=False,gpu_hours=0,independent_validation_still_required=gate)
    (output/'validation.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--source',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True);args=p.parse_args();main(args.source,args.output)
