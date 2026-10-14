#!/usr/bin/env python3
"""Independent lightweight acceptance of byte-baseline comparisons; stdlib only."""
import argparse
import collections
import csv
import hashlib
import json
import math
from pathlib import Path
import random
import statistics
from analyze_allocation_diagnosis import compare,interval


def main(source,output):
    summary=json.loads((source/'summary.json').read_text())
    frozen=json.loads((source/'frozen.json').read_text())
    if summary['status']!='complete' or not summary['adapter_exact']:
        raise ValueError('Incomplete/invalid native source')
    digest=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
    if digest(source/'frozen.json')!=summary['frozen_sha256']:
        raise ValueError('Frozen metadata changed')
    if digest(source/'cases.json')!=frozen['cases_sha256']:
        raise ValueError('Cases changed')
    cases=json.loads((source/'cases.json').read_text());n=len(cases)
    if n not in [8,128] or len({c['prompt_content_sha256'] for c in cases})!=n:
        raise ValueError('Case coverage')
    if any(len(c['targets'])!=32 for c in cases):raise ValueError('Target coverage')
    if n==128 and digest(source/'cache-index.json')!=frozen['cache_index_sha256']:
        raise ValueError('Cached source metadata changed')
    rows=[json.loads(l) for l in (source/'per-case.jsonl').read_text().splitlines()]
    groups=collections.defaultdict(dict)
    labels=['kfac_fp32_r8','structural_fp16_r15','structural_int8_r30']
    for row in rows:
        if row['case'] in groups[row['label']]:raise ValueError('Duplicate row')
        if row['tokens']!=32 or any(not math.isfinite(row[key]) for key in ['kl_reference_to_changed','nll_difference','rms','reference_nll','changed_nll']):
            raise ValueError('Invalid metrics')
        if abs(row['changed_nll']-row['reference_nll']-row['nll_difference'])>1e-12:
            raise ValueError('NLL identity changed')
        groups[row['label']][row['case']]=row
    if set(groups)!=set(labels) or len(rows)!=3*n or any(set(g)!=set(range(n)) for g in groups.values()):
        raise ValueError('Misaligned conditions')
    native=json.loads((source/'native-checks.json').read_text())
    if len(native)!=(8 if n==128 else 4) or not all(r['bitwise_equal'] for r in native):
        raise ValueError('Source reload failed')
    controls=json.loads((source/'controls.json').read_text())
    if len(controls)!=4:raise ValueError('Control coverage')
    floor=max(c['rms'] for c in controls)
    quality=[]
    for label in labels:
        own=list(groups[label].values())
        result=dict(label=label,cases=n,tokens=n*32,mean_kl=statistics.mean(r['kl_reference_to_changed'] for r in own),
            mean_nll_delta=statistics.mean(r['nll_difference'] for r in own),mean_rms=statistics.mean(r['rms'] for r in own),
            argmax_disagreements=sum(r['argmax_disagreements'] for r in own),**frozen['storage'][label])
        stored=next(c for c in summary['conditions'] if c['label']==label)
        for key in ['mean_kl','mean_nll_delta','mean_rms']:
            if not math.isclose(result[key],stored[key],rel_tol=1e-12,abs_tol=1e-14):
                raise ValueError('Summary mismatch')
        if result['payload_bytes']>23592960 or result.get('total_file_bytes',0)>23592960:
            raise ValueError('Byte cap failed')
        quality.append(result)
    if floor>=.01*min(r['mean_rms'] for r in quality):raise ValueError('Numerical floor too large')
    archive_audit=json.loads((output/'storage-audit.json').read_text())
    if archive_audit['status']!='PASS' or archive_audit['source_adapter']['tensor_count']!=432:
        raise ValueError('Independent archive audit failed')
    for label in labels[1:]:
        actual=archive_audit['archives'][label];expected=frozen['storage'][label]
        if any(actual[key]!=expected[key] for key in ['payload_bytes','sha256','total_file_bytes']):
            raise ValueError('Independent file audit mismatch')
    contrasts=[]
    if n==128:
        for index,label in enumerate(labels[1:]):
            old=[groups[labels[0]][i]['kl_reference_to_changed'] for i in range(n)]
            new=[groups[label][i]['kl_reference_to_changed'] for i in range(n)]
            result=compare(old,new,20261014+index)
            differences=[groups[label][i]['nll_difference']-groups[labels[0]][i]['nll_difference'] for i in range(n)]
            rng=random.Random(20261114+index)
            bootstrap=[sum(differences[rng.randrange(n)] for _ in range(n))/n for _ in range(10000)]
            result.update(label=label,gold_nll_mean_delta=statistics.mean(differences),gold_nll_ci95=interval(bootstrap))
            contrasts.append(result)
        largest=0
        for rank,index in enumerate(sorted(range(2),key=lambda i:contrasts[i]['sign_flip_p'])):
            largest=max(largest,min(1,(2-rank)*contrasts[index]['sign_flip_p']))
            contrasts[index]['holm_p']=largest
    output.mkdir(parents=True,exist_ok=True)
    prefix='development-' if n==128 else 'screen-'
    for filename,records in [('quality.csv',quality),('contrasts.csv',contrasts)]:
        if not records:continue
        with (output/(prefix+filename)).open('w',newline='') as stream:
            writer=csv.DictWriter(stream,fieldnames=list(dict.fromkeys(k for r in records for k in r)))
            writer.writeheader();writer.writerows(records)
    accepted=dict(status='PASS',cases=n,rows=len(rows),tokens_per_condition=n*32,
        quality=quality,contrasts=contrasts,controls_max_rms=floor,cases_sha256=frozen['cases_sha256'],
        source_sha256=summary['source_sha256'],versions=summary['versions'],artifacts=summary['artifacts'],
        wall_seconds=summary['wall_seconds'],rss_bytes=summary['rss_bytes'],gpu_hours=0,
        source_tensor_count=432,full_task_accuracy=False,new_independent_test=False,new_algorithm=False,
        runtime_vram_or_speed_measured=False,conference_level_established=False,
        storage_archive_audit_still_required=False,
        source_storage=archive_audit['source_adapter'],
        input_sha256={p.name:digest(p) for p in source.iterdir() if p.is_file() and p.suffix in ['.json','.jsonl']})
    (output/(prefix+'validation.json')).write_text(json.dumps(accepted,indent=2)+'\n')
    print(json.dumps({k:accepted[k] for k in ['status','cases','rows','contrasts','wall_seconds']},indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--source',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();main(a.source,a.output)
