"""Validate full-adapter screen and report every budget/method contrast."""
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
    state=json.loads((source/'state.json').read_text())
    capture=json.loads((source/'capture/summary.json').read_text())
    prep=json.loads((source/'prepare/summary.json').read_text())
    result=json.loads((source/'evaluate/summary.json').read_text())
    cases=json.loads((source/'cases.json').read_text())
    controls=json.loads((source/'evaluate/controls.json').read_text())
    storage=json.loads((source/'storage-audit.json').read_text())
    assert all(x['status']=='complete' and x['gpu_count']==0 for x in [state,capture,prep,result])
    assert capture['adapter_exact'] and result['adapter_exact']
    assert len(capture['modules'])==144 and len({r['name'] for r in capture['modules']})==144
    assert len(cases)==len({r['prompt_content_sha256'] for r in cases})==32
    assert sha(source/'cases.json')==capture['cases_sha256']==result['cases_sha256']
    keys={r['prompt_content_sha256'] for r in cases}
    for path in exclusions:
        assert keys.isdisjoint({r['prompt_content_sha256'] for r in json.loads(path.read_text())})
    assert all(r['train_index']>=232 and len(r['targets'])==32 for r in cases)
    costs={r['name']:sum(r['shape']) for r in capture['modules']}
    native=sum(r['native_elements'] for r in capture['modules'])
    assert native==prep['native_elements']==capture['native_elements']
    assert storage['source_dtype_counts']=={'F32':native}
    assert storage['saved_factor_shapes_counts_dtypes_finite_verified']
    assert storage['diagonals_equal_source_control']
    assert storage['calibration_test_first232_disjoint_verified']
    assert storage['factors_sha256']==prep['factors_sha256']
    for rank in [16,8]:
        budget=rank*sum(costs.values())
        assert prep['budgets'][str(rank)]==budget
        ranks=prep['structural_ranks'][str(rank)]
        assert set(ranks)==set(costs) and set(ranks.values())<={rank-1,rank}
        assert sum(ranks[r['name']]*costs[r['name']]+r['shape'][0] for r in capture['modules'])==budget
        for method in ['raw','weighted','structural']:
            assert prep['parameter_counts'][f'{method}_{rank}']==budget
            assert storage['actual_factor_elements'][f'{method}_{rank}']==budget
    assert max(r['rms'] for r in controls)==result['controls_max_rms']
    assert result['controls_max_rms']<.01*result['minimum_compression_rms']
    rows=[json.loads(line) for line in (source/'evaluate/per-case.jsonl').read_text().splitlines()]
    assert len(rows)==6*32
    by,quality={},[]
    labels={f'{m}_{r}' for m in ['raw','weighted','structural'] for r in [16,8]}
    assert {r['label'] for r in rows}==labels
    for label in sorted(labels):
        own=sorted([r for r in rows if r['label']==label],key=lambda r:r['case'])
        assert len(own)==32 and [r['case'] for r in own]==list(range(32))
        assert all(r['tokens']==32 and all(math.isfinite(v) for v in r.values()
                   if isinstance(v,(int,float))) for r in own)
        reported=next(r for r in result['conditions'] if r['label']==label)
        assert reported['status']=='complete' and reported['cases_completed']==32
        mean_kl=statistics.mean(r['kl_reference_to_changed'] for r in own)
        assert math.isclose(reported['mean_kl'],mean_kl,rel_tol=1e-12)
        by[label]=own
        count=prep['parameter_counts'][label]
        quality.append(dict(label=label,adapter_elements=count,fraction_of_source=count/native,
            fp32_tensor_payload_bytes=4*count,mean_kl=mean_kl,
            mean_nll_delta=statistics.mean(r['nll_difference'] for r in own),
            mean_reference_nll=statistics.mean(r['reference_nll'] for r in own),
            mean_rms=statistics.mean(r['rms'] for r in own),
            argmax_flips=sum(r['argmax_disagreements'] for r in own),positions=1024))
    for i in range(32):
        assert len({by[label][i]['reference_nll'] for label in labels})==1
    contrasts=[]
    for rank in [16,8]:
        for changed,reference in [('weighted','raw'),('structural','weighted'),('structural','raw')]:
            a,b=by[f'{changed}_{rank}'],by[f'{reference}_{rank}']
            d=[x['kl_reference_to_changed']-y['kl_reference_to_changed'] for x,y in zip(a,b)]
            nll=[x['nll_difference']-y['nll_difference'] for x,y in zip(a,b)]
            baseline=statistics.mean(r['kl_reference_to_changed'] for r in b)
            contrasts.append(dict(rank_budget=rank,changed=f'{changed}_{rank}',reference=f'{reference}_{rank}',
                kl_delta=statistics.mean(d),descriptive_kl_ci95=ci(d),
                relative_kl_delta=statistics.mean(d)/baseline if baseline else None,
                nll_delta=statistics.mean(nll),descriptive_nll_ci95=ci(nll),
                lower_kl_cases=sum(x<0 for x in d),higher_kl_cases=sum(x>0 for x in d)))
    baseline_signal={r['label']:(r['mean_kl']>=1e-4 or r['argmax_flips']/1024>=.01)
                     for r in quality if not r['label'].startswith('structural')}
    report=dict(status='validated',full_adapter=True,adapted_modules=144,questions=32,target_positions=1024,
        source_adapter_elements=native,contrasts=contrasts,baseline_screen_signal=baseline_signal,
        uncertainty='Exploratory whole-question percentile bootstrap10000 seed20261013; all six contrasts reported, no confirmatory multiplicity claim',
        scope='Full adapter, new posthoc-development train questions, teacher-forced prefixes; no GSM8K accuracy or latency measurement',
        format='Raw/W: ordinary fixed-base low-rank updates. Structural: fixed diagonal plus low-rank update; diagonal included in budget; not ordinary LoRA export.',
        versions=result['versions'],source_sha256=result['source_sha256'],
        storage_audit=storage,
        controls=dict(max_rms=result['controls_max_rms'],minimum_compression_rms=result['minimum_compression_rms']),
        resources=dict(gpu_hours=0,phases=state['phases'],peak_evaluate_rss_bytes=result['rss_bytes']),
        input_sha256={str(p.relative_to(source)):sha(p) for p in source.rglob('*') if p.is_file()})
    output.mkdir(parents=True,exist_ok=True)
    with (output/'quality.csv').open('w') as stream:
        writer=csv.DictWriter(stream,fieldnames=list(quality[0]));writer.writeheader();writer.writerows(quality)
    (output/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
    (output/'ranks.json').write_text(json.dumps(prep['structural_ranks'],indent=2)+'\n')
    print(json.dumps(dict(quality=quality,baseline_screen_signal=baseline_signal,contrasts=contrasts),indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--input',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--exclude-cases',type=Path,action='append',default=[]);a=p.parse_args()
    main(a.input,a.output,a.exclude_cases)
