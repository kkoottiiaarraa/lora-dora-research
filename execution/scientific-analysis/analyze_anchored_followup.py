"""Validate the additional anchored procedure and its untouched question split."""
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
import statistics

from analyze_compression_followup import ci


def main(source,generic,calibration,output):
    output.mkdir(parents=True,exist_ok=True)
    sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    d=json.loads((source/'summary.json').read_text());selection=json.loads((source/'selection.json').read_text())
    m=json.loads((source/'manifest-private.json').read_text())
    assert d['status']=='complete' and selection['frozen_before_validation']
    assert sha(source/'selection.json')==d['selection_sha256']
    assert sha(source/'validation-cases.json')==selection['validation_cases_sha256']==d['validation_cases_sha256']
    assert sha(calibration)==m['calibration_cases_sha256']
    questions=[json.loads(p.read_text()) for p in [calibration,generic/'validation-cases.json',source/'validation-cases.json']]
    sets=[{r['prompt_content_sha256'] for r in group} for group in questions]
    assert all(len(s)==64 for s in sets) and len(set.union(*sets))==192
    assert max(d['ideal_fp64_canonical_relative_errors'].values())<=1e-12
    rows=[json.loads(x) for x in (source/'per-case.jsonl').read_text().splitlines()]
    by={};quality=[]
    for split,label in sorted({(r['split'],r['label']) for r in rows}):
        r=sorted([r for r in rows if r['split']==split and r['label']==label],key=lambda r:r['case'])
        assert len(r)==64 and [x['case'] for x in r]==list(range(64))
        assert all(x['tokens']==32 and all(math.isfinite(v) for v in x.values() if isinstance(v,(int,float))) for x in r)
        by[split,label]=r
        quality.append(dict(split=split,label=label,mean_kl=statistics.mean(x['kl_reference_to_changed'] for x in r),
            mean_nll_delta=statistics.mean(x['nll_difference'] for x in r),mean_rms=statistics.mean(x['rms'] for x in r),
            argmax_flips=sum(x['argmax_disagreements'] for x in r)))
    assert len([k for k in by if k[0]=='calibration'])==3
    assert set(selection['validation_labels'])=={k[1] for k in by if k[0]=='validation'}
    for r in d['conditions']:
        assert r['status']=='complete' and r['cases_completed']==64
        actual=statistics.mean(x['kl_reference_to_changed'] for x in by[r['split'],r['label']])
        assert math.isclose(actual,r['mean_kl'],rel_tol=1e-12)
    options=['anchor_1.0','anchor_0.995','anchor_1.005']
    best=min(options,key=lambda label:(statistics.mean(r['kl_reference_to_changed'] for r in by['calibration',label]),label!='anchor_1.0'))
    assert best==selection['chosen']
    comparisons=[('primary','weighted_1.0'),('secondary_canonical_only','anchor_1.0'),('secondary_raw','svd_1.0')]
    if selection.get('generic_selection'):
        comparisons.append(('secondary_matched_search',selection['generic_selection']['chosen']['weighted']))
    contrasts=[]
    for kind,reference in comparisons:
        a,b=by['validation',best],by['validation',reference]
        delta=[x['kl_reference_to_changed']-y['kl_reference_to_changed'] for x,y in zip(a,b)]
        nll=[x['nll_difference']-y['nll_difference'] for x,y in zip(a,b)]
        baseline=statistics.mean(x['kl_reference_to_changed'] for x in b)
        corrected=ci(delta,.025)
        gain=-statistics.mean(delta)/baseline if baseline else None
        contrasts.append(dict(kind=kind,changed=best,reference=reference,same_condition=best==reference,
            kl_difference=statistics.mean(delta),kl_ci95=ci(delta),kl_ci97_5_family2=corrected,
            relative_kl_gain=gain,nll_difference=statistics.mean(nll),nll_ci95=ci(nll),
            lower_kl_cases=sum(x<0 for x in delta),higher_kl_cases=sum(x>0 for x in delta),
            benefit_screen_passed=gain is not None and gain>=.1 and corrected[1]<0))
    with (output/'anchored-quality.csv').open('w') as f:
        w=csv.DictWriter(f,fieldnames=list(quality[0]));w.writeheader();w.writerows(quality)
    report=dict(status='validated',selection=selection,contrasts=contrasts,wall_seconds=d['wall_seconds'],
        anchor_scales=d['anchor_scales'],ideal_fp64_canonical_relative_errors=d['ideal_fp64_canonical_relative_errors'],
        validation_disjoint_question_count=192,
        inference_scope='new train holdout for posthoc method selection, not unseen original-training data or task accuracy',
        uncertainty='paired whole-question bootstrap10000 seed20261013; family2 primary CIs97.5; secondary exploratory',
        parameters='rank32 in six V/O matrices, factor budget983040 elements, native adapter993792; no measured latency advantage',
        source_sha256=d['source_sha256'],versions=d['versions'],
        artifacts={k:{z:v[z] for z in ['repo_id','revision']} for k,v in m['artifacts'].items()},
        input_sha256={str(p.relative_to(source)):sha(p) for p in source.rglob('*') if p.is_file()})
    (output/'anchored-validation.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:report[k] for k in ['status','selection','contrasts','wall_seconds','anchor_scales']},indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--input',type=Path,required=True);p.add_argument('--generic',type=Path,required=True)
    p.add_argument('--calibration-cases',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();main(a.input,a.generic,a.calibration_cases,a.output)
