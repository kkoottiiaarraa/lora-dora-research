"""Accept the frozen calibration/validation comparison; stdlib-only analysis."""
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
import random
import statistics


def ci(values, alpha=.05):
    mean=statistics.mean(values)
    if max(values)==min(values):return [mean,mean]
    rng=random.Random(20261013)
    draws=sorted(statistics.mean(rng.choices(values,k=len(values))) for _ in range(10000))
    return [draws[max(0,int(10000*alpha/2)-1)],draws[int(10000*(1-alpha/2))-1]]


def main(source,output):
    output.mkdir(parents=True,exist_ok=True)
    state=json.loads((source/'state.json').read_text())
    assert state['status']=='complete'
    d=json.loads((source/'evaluate/summary.json').read_text())
    capture=json.loads((source/'capture/summary.json').read_text())
    prepare=json.loads((source/'prepare/summary.json').read_text())
    selection=json.loads((source/'selection.json').read_text())
    val=json.loads((source/'validation-cases.json').read_text())
    assert d['status']==capture['status']==prepare['status']=='complete'
    assert capture['cases_completed']==64 and prepare['modules']==6
    assert selection['frozen_before_validation']
    sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    assert sha(source/'selection.json')==d['selection_sha256']
    assert sha(source/'validation-cases.json')==selection['validation_cases_sha256']==capture['validation_cases_sha256']
    assert len(val)==len({r['prompt_content_sha256'] for r in val})==64
    rows=[json.loads(x) for x in (source/'evaluate/per-case.jsonl').read_text().splitlines()]
    with (source/'evaluate/metrics.csv').open() as f:csvrows=list(csv.DictReader(f))
    assert len(rows)==len(csvrows)
    assert all(all(b[k]==str(v) for k,v in a.items()) for a,b in zip(rows,csvrows))
    by={};summary=[]
    for split,label in sorted({(r['split'],r['label']) for r in rows}):
        r=sorted([r for r in rows if r['split']==split and r['label']==label],key=lambda r:r['case'])
        assert len(r)==64 and [x['case'] for x in r]==list(range(64))
        assert all(x['tokens']==32 for x in r)
        assert all(math.isfinite(v) for x in r for v in x.values() if isinstance(v,(int,float)))
        by[split,label]=r
        summary.append(dict(split=split,label=label,mean_kl=statistics.mean(x['kl_reference_to_changed'] for x in r),
            mean_nll_delta=statistics.mean(x['nll_difference'] for x in r),mean_rms=statistics.mean(x['rms'] for x in r),
            argmax_flips=sum(x['argmax_disagreements'] for x in r)))
    assert len([k for k in by if k[0]=='calibration'])==6
    assert set(d['validation_evaluated_labels'])=={k[1] for k in by if k[0]=='validation'}
    for record in d['conditions']:
        assert record['status']=='complete' and record['cases_completed']==64
        actual=statistics.mean(r['kl_reference_to_changed'] for r in by[record['split'],record['label']])
        assert math.isclose(actual,record['mean_kl'],rel_tol=1e-12)
    for method in ['svd','weighted']:
        options=[method+'_'+str(c) for c in [1.,.995,1.005]]
        best=min(options,key=lambda l:(statistics.mean(r['kl_reference_to_changed'] for r in by['calibration',l]),l!=method+'_1.0'))
        assert best==selection['chosen'][method]
    contrasts=[]
    targets=[('primary',selection['chosen']['weighted'],'weighted_1.0'),
             ('secondary_weighting','weighted_1.0','svd_1.0'),
             ('secondary_matched_search',selection['chosen']['weighted'],selection['chosen']['svd'])]
    for kind,changed,reference in targets:
        a,b=by['validation',changed],by['validation',reference]
        delta=[x['kl_reference_to_changed']-y['kl_reference_to_changed'] for x,y in zip(a,b)]
        ndelta=[x['nll_difference']-y['nll_difference'] for x,y in zip(a,b)]
        baseline=statistics.mean(x['kl_reference_to_changed'] for x in b)
        interval=ci(delta);gain=-statistics.mean(delta)/baseline if baseline else None
        contrasts.append(dict(kind=kind,changed=changed,reference=reference,
            same_condition=changed==reference,kl_difference=statistics.mean(delta),kl_ci95=interval,kl_ci97_5_family2=ci(delta,.025),
            relative_kl_gain=gain,nll_difference=statistics.mean(ndelta),nll_ci95=ci(ndelta),
            lower_kl_cases=sum(x<0 for x in delta),higher_kl_cases=sum(x>0 for x in delta),
            benefit_screen_passed=gain is not None and gain>=.1 and ci(delta,.025)[1]<0))
    with (output/'quality.csv').open('w') as f:
        w=csv.DictWriter(f,fieldnames=list(summary[0]));w.writeheader();w.writerows(summary)
    report=dict(status='validated',selection=selection,contrasts=contrasts,
        inference_scope='64 new train questions not used for posthoc method selection; not unseen by original training and not test accuracy',
        uncertainty='paired whole-case percentile bootstrap10000 seed20261013; family2 with separate anchored primary: additional97.5% intervals; secondary descriptive',
        resources=state['phases'],execution={p:dict(device=x.get('device','cpu'),threads=x.get('cpu_threads'),wall_seconds=x['wall_seconds']) for p,x in [('capture',capture),('prepare',prepare),('evaluate',d)]},
        metadata={k:d[k] for k in ['versions','source_sha256']},
        input_sha256={str(p.relative_to(source)):sha(p) for p in source.rglob('*') if p.is_file()})
    (output/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:report[k] for k in ['status','selection','contrasts','execution']},indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--input',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();main(a.input,a.output)
