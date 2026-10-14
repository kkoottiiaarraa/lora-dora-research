#!/usr/bin/env python3
"""Small independent stdlib-only paired analysis of allocation outputs."""
import argparse
import collections
import csv
import hashlib
import json
from pathlib import Path
import random
import statistics


def interval(values):
    values=sorted(values)
    return [values[int(.025*(len(values)-1))],values[int(.975*(len(values)-1))]]


def compare(original, changed, seed):
    differences=[b-a for a,b in zip(original,changed)]
    rng=random.Random(seed);boots=[];relative=[];null=[]
    n=len(differences);observed=abs(statistics.mean(differences))
    for _ in range(10000):
        ids=[rng.randrange(n) for _ in range(n)]
        old=sum(original[i] for i in ids)/n
        new=sum(changed[i] for i in ids)/n
        boots.append(new-old);relative.append(1-new/old)
        null.append(abs(sum(d*(1 if rng.getrandbits(1) else -1) for d in differences)/n))
    return dict(mean_delta=statistics.mean(differences),delta_ci95=interval(boots),
        mean_relative_gain=1-statistics.mean(changed)/statistics.mean(original),
        relative_gain_ci95=interval(relative),
        sign_flip_p=(1+sum(x>=observed for x in null))/10001,
        cases_improved=sum(d<0 for d in differences),cases_worsened=sum(d>0 for d in differences))


def main(source,destination):
    summary=json.loads((source/'evaluate/summary.json').read_text())
    prep=json.loads((source/'prepare-summary.json').read_text())
    if summary['status']!='complete' or prep['status']!='complete':
        raise ValueError('Workers incomplete')
    rows=[json.loads(line) for line in (source/'evaluate/per-case.jsonl').read_text().splitlines()]
    by_label=collections.defaultdict(dict)
    for row in rows:
        if row['case'] in by_label[row['label']]:raise ValueError('Duplicate case')
        by_label[row['label']][row['case']]=row
    if len(rows)!=256 or len(by_label)!=4 or any(set(own)!=set(range(64)) for own in by_label.values()):
        raise ValueError('Missing aligned rows')
    frozen=json.loads((source/'evaluate/frozen.json').read_text())
    casebytes=(source/'evaluate/cases.json').read_bytes()
    if hashlib.sha256(casebytes).hexdigest()!=frozen['cases_sha256']:raise ValueError('Case hash mismatch')
    cases=json.loads(casebytes)
    if len({case['prompt_content_sha256'] for case in cases})!=64:raise ValueError('Duplicate prompts')
    if any(len(case['targets'])!=32 for case in cases):raise ValueError('Wrong token coverage')
    if any(v!=5898240 for v in frozen['factor_counts'].values()):raise ValueError('Unequal budgets')
    if summary['controls_max_rms']>=.01*min(c['mean_rms'] for c in summary['conditions']):
        raise ValueError('Fidelity control failed')
    contrasts=[]
    for index,method in enumerate(['weighted','structural']):
        old=[by_label[method+'_uniform'][i]['kl_reference_to_changed'] for i in range(64)]
        new=[by_label[method+'_allocated'][i]['kl_reference_to_changed'] for i in range(64)]
        contrasts.append(dict(method=method,**compare(old,new,20261014+index)))
    largest=0
    for rank,index in enumerate(sorted(range(2),key=lambda i:contrasts[i]['sign_flip_p'])):
        largest=max(largest,min(1,(2-rank)*contrasts[index]['sign_flip_p']))
        contrasts[index]['holm_p']=largest
    diagnostics=json.loads((source/'diagnostics.json').read_text())
    allocation=json.loads((source/'allocations.json').read_text())
    budget_rows=[]
    for label,record in allocation.items():
        actual=sum((sum(row['shape'])*record['ranks'][row['module']]
            +(row['shape'][0] if label.startswith('structural') else 0)) for row in diagnostics)
        if actual!=5898240:raise ValueError('Rank-derived budget mismatch')
        for projection in ['q_proj','k_proj','v_proj','o_proj']:
            group=[row for row in diagnostics if row['module'].endswith('.'+projection)]
            ranks=[record['ranks'][row['module']] for row in group]
            if len(group)!=36:raise ValueError('Module coverage changed')
            budget_rows.append(dict(label=label,projection=projection,modules=36,
                mean_rank=statistics.mean(ranks),min_rank=min(ranks),max_rank=max(ranks),
                rank_zero_count=ranks.count(0),summed_local_loss=sum(row[label+'_local_loss'] for row in group)))
    destination.mkdir(parents=True,exist_ok=True)
    for name,records in [('quality.csv',summary['conditions']),('allocation.csv',budget_rows),('contrasts.csv',contrasts)]:
        fields=list(dict.fromkeys(k for row in records for k in row))
        with (destination/name).open('w',newline='') as stream:
            writer=csv.DictWriter(stream,fieldnames=fields);writer.writeheader();writer.writerows(records)
    validation=dict(status='PASS',case_count=64,tokens_per_condition=2048,rows=256,
        cases_sha256=frozen['cases_sha256'],source_sha256=summary['source_sha256'],
        contrasts=contrasts,controls_max_rms=summary['controls_max_rms'],
        bootstrap_question_resamples=10000,primary_family_size=2,
        inference_wall_seconds=summary['wall_seconds'],prepare_wall_seconds=prep['wall_seconds'],
        versions=summary['versions'],gpu_hours=0,full_task_accuracy=False,
        limitation='Development comparison; not training-seed uncertainty or answer-generation accuracy.')
    (destination/'validation.json').write_text(json.dumps(validation,indent=2))
    print(json.dumps(dict(conditions=summary['conditions'],contrasts=contrasts),indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--source',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True);args=p.parse_args();main(args.source,args.output)
