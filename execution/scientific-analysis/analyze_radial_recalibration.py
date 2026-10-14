"""One prospective primary radial-calibration comparison, all baselines shown."""
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
import statistics

from analyze_compression_followup import ci


def main(source,output,exclusions):
    sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    summary=json.loads((source/'summary.json').read_text())
    frozen=json.loads((source/'frozen.json').read_text())
    cases=json.loads((source/'cases.json').read_text())
    controls=json.loads((source/'controls.json').read_text())
    diagnostics=json.loads((source/'diagnostics.json').read_text())
    audit=json.loads((source/'factor-audit.json').read_text())
    assert summary['status']=='complete' and summary['adapter_exact'] and summary['gpu_count']==0
    assert frozen['frozen_before_validation'] and sha(source/'frozen.json')==summary['frozen_sha256']
    assert sha(source/'cases.json')==frozen['cases_sha256']==summary['cases_sha256']
    assert frozen['factor_elements']==5898240 and frozen['rank_budget']==8
    assert audit['factors_sha256']==frozen['candidate_sha256']
    assert audit['directions_bitwise_unchanged'] and audit['all_shapes_counts_finite_verified']
    assert audit['calibration_test_first232_disjoint_verified']
    assert len(cases)==len({r['prompt_content_sha256'] for r in cases})==64
    keys={r['prompt_content_sha256'] for r in cases}
    for path in exclusions:
        assert keys.isdisjoint({r['prompt_content_sha256'] for r in json.loads(path.read_text())})
    assert len(diagnostics)==144
    assert all(r['weighted_loss_after']<=r['weighted_loss_before']*(1+1e-7)+1e-12 for r in diagnostics)
    rows=[json.loads(line) for line in (source/'per-case.jsonl').read_text().splitlines()]
    assert len(rows)==4*64
    labels=['raw_8','weighted_8','structural_8','recalibrated_8'];by={};quality=[]
    assert {r['label'] for r in rows}==set(labels)
    for label in labels:
        own=sorted([r for r in rows if r['label']==label],key=lambda r:r['case'])
        assert len(own)==64 and [r['case'] for r in own]==list(range(64))
        assert all(r['tokens']==32 and all(math.isfinite(v) for v in r.values()
                   if isinstance(v,(int,float))) for r in own)
        reported=next(r for r in summary['conditions'] if r['label']==label)
        assert reported['status']=='complete' and reported['cases_completed']==64
        mean_kl=statistics.mean(r['kl_reference_to_changed'] for r in own)
        assert math.isclose(mean_kl,reported['mean_kl'],rel_tol=1e-12)
        by[label]=own
        quality.append(dict(label=label,adapter_elements=5898240,fp32_tensor_payload_bytes=4*5898240,
            mean_kl=mean_kl,mean_nll_delta=statistics.mean(r['nll_difference'] for r in own),
            mean_rms=statistics.mean(r['rms'] for r in own),
            argmax_flips=sum(r['argmax_disagreements'] for r in own),positions=2048))
    for i in range(64):assert len({by[label][i]['reference_nll'] for label in labels})==1
    floor=max(r['rms'] for r in controls)
    assert floor==summary['controls_max_rms']<.01*min(r['mean_rms'] for r in summary['conditions'])
    contrasts=[]
    for reference in ['structural_8','weighted_8','raw_8']:
        a,b=by['recalibrated_8'],by[reference]
        delta=[x['kl_reference_to_changed']-y['kl_reference_to_changed'] for x,y in zip(a,b)]
        nll=[x['nll_difference']-y['nll_difference'] for x,y in zip(a,b)]
        baseline=statistics.mean(r['kl_reference_to_changed'] for r in b)
        gain=-statistics.mean(delta)/baseline
        interval=ci(delta)
        contrasts.append(dict(kind='primary' if reference=='structural_8' else 'secondary',
            changed='recalibrated_8',reference=reference,kl_delta=statistics.mean(delta),
            kl_ci95=interval,relative_kl_gain=gain,nll_delta=statistics.mean(nll),
            descriptive_nll_ci95=ci(nll),lower_kl_cases=sum(d<0 for d in delta),
            higher_kl_cases=sum(d>0 for d in delta),
            benefit_screen_passed=gain>=.1 and interval[1]<0))
    total_before=sum(r['weighted_loss_before'] for r in diagnostics)
    total_after=sum(r['weighted_loss_after'] for r in diagnostics)
    report=dict(status='validated',questions=64,target_positions=2048,adapted_modules=144,
        adapter_elements=5898240,primary=contrasts[0],contrasts=contrasts,
        better_mean_than_both_ordinary_baselines=all(c['relative_kl_gain']>0 for c in contrasts[1:]),
        calibration=dict(total_local_gain=1-total_after/total_before,
            median_module_local_gain=statistics.median(r['relative_local_gain'] for r in diagnostics),
            max_diagonal_change=max(r['max_abs_diagonal_change'] for r in diagnostics)),
        uncertainty='One frozen primary comparison, paired whole-question percentile bootstrap10000 seed20261013 CI95; secondary exploratory, no task-accuracy inference',
        scope='64 new posthoc-validation train questions; source adaptation may have seen them. Not GSM8K test accuracy.',
        resources=dict(gpu_hours=0,prepare_wall_seconds=summary['prepare_seconds'],
            total_wall_seconds=summary['wall_seconds'],evaluation_cpu_threads=16,peak_rss_bytes=summary['rss_bytes']),
        versions=summary['versions'],source_sha256=summary['source_sha256'],
        input_sha256={str(p.relative_to(source)):sha(p) for p in source.rglob('*') if p.is_file()})
    output.mkdir(parents=True,exist_ok=True)
    with (output/'quality.csv').open('w') as stream:
        writer=csv.DictWriter(stream,fieldnames=list(quality[0]));writer.writeheader();writer.writerows(quality)
    (output/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(quality=quality,primary=report['primary'],contrasts=contrasts,
                         calibration=report['calibration']),indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--input',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--exclude-cases',type=Path,action='append',default=[]);a=p.parse_args()
    main(a.input,a.output,a.exclude_cases)
