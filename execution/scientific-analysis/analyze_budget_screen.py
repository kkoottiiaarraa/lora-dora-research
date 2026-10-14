"""Validate compact CPU screen artifacts; exploratory paired comparisons only."""
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
import statistics

from analyze_compression_followup import ci


def main(source, output, exclusions):
    sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    prep = json.loads((source/'prepare/summary.json').read_text())
    summary = json.loads((source/'evaluate/summary.json').read_text())
    decisions = json.loads((source/'prepare/decisions.json').read_text())
    cases = json.loads((source/'prepare/cases.json').read_text())
    controls = json.loads((source/'evaluate/controls.json').read_text())
    storage = json.loads((source/'storage-audit.json').read_text())
    assert storage['selected_source_dtype_counts'] == {'F32': 993792}
    assert storage['source_tensor_payload_bytes'] == prep['native_elements']*4
    assert storage['compressed_tensor_payload_bytes'] == prep['factor_elements']*4
    assert storage['all_factor_shapes_dtypes_finite_and_counts_verified']
    assert storage['calibration_disjoint_verified']
    assert storage['factor_file_sha256'] == prep['factors_sha256']
    assert prep['status'] == summary['status'] == 'complete'
    assert prep['gpu_count'] == summary['gpu_count'] == 0 and summary['adapter_exact']
    assert sha(source/'prepare/cases.json') == prep['cases_sha256'] == summary['cases_sha256']
    assert sha(source/'prepare/decisions.json') == prep['decisions_sha256']
    keys = {r['prompt_content_sha256'] for r in cases}
    assert len(keys) == len(cases) == 16
    for path in exclusions:
        assert keys.isdisjoint({r['prompt_content_sha256'] for r in json.loads(path.read_text())})
    assert summary['controls_max_rms'] == max(r['rms'] for r in controls)
    assert summary['controls_max_rms'] < .01*summary['minimum_compression_rms']
    rows = [json.loads(x) for x in (source/'evaluate/per-case.jsonl').read_text().splitlines()]
    assert len(rows) == 192
    by, quality = {}, []
    for decision in decisions:
        label = decision['label']
        own = sorted([r for r in rows if r['label'] == label], key=lambda r:r['case'])
        assert len(own) == 16 and [r['case'] for r in own] == list(range(16))
        assert all(r['tokens'] == 32 and all(math.isfinite(v) for v in r.values()
                   if isinstance(v, (float, int))) for r in own)
        assert decision['factor_elements'] == prep['factor_elements'] == 491520
        assert all(type(r) is int and 0 <= r <= 32 for r in decision['ranks'].values())
        assert sum(r*storage['cost_per_rank'][n] for n,r in decision['ranks'].items()) == 491520
        reported = next(r for r in summary['conditions'] if r['label'] == label)
        assert reported['status'] == 'complete' and reported['cases_completed'] == 16
        mean_kl = statistics.mean(r['kl_reference_to_changed'] for r in own)
        assert math.isclose(mean_kl, reported['mean_kl'], rel_tol=1e-12)
        by[label] = own
        quality.append(dict(label=label, factor_elements=decision['factor_elements'],
            mean_kl=mean_kl, mean_nll_delta=statistics.mean(r['nll_difference'] for r in own),
            mean_rms=statistics.mean(r['rms'] for r in own),
            argmax_flips=sum(r['argmax_disagreements'] for r in own), positions=512))
    contrasts = []
    def compare(kind, changed, reference):
        a, b = by[changed], by[reference]
        d = [x['kl_reference_to_changed']-y['kl_reference_to_changed'] for x,y in zip(a,b)]
        nll = [x['nll_difference']-y['nll_difference'] for x,y in zip(a,b)]
        baseline = statistics.mean(x['kl_reference_to_changed'] for x in b)
        contrasts.append(dict(kind=kind, changed=changed, reference=reference,
            kl_delta=statistics.mean(d), descriptive_kl_ci95=ci(d),
            relative_kl_delta=statistics.mean(d)/baseline if baseline else None,
            nll_delta=statistics.mean(nll), descriptive_nll_ci95=ci(nll),
            lower_kl_cases=sum(x<0 for x in d), higher_kl_cases=sum(x>0 for x in d)))
    for method in ['svd', 'weighted']:
        for policy in ['fixed', 'allocated']:
            for c in [.995, 1.005]:
                compare('source_representation', f'{method}_{policy}_{c}', f'{method}_{policy}_1.0')
        compare('allocation', f'{method}_allocated_1.0', f'{method}_fixed_1.0')
    for policy in ['fixed', 'allocated']:
        compare('weighting', f'weighted_{policy}_1.0', f'svd_{policy}_1.0')
    ranks_changed = {}
    for method in ['svd', 'weighted']:
        own = [r for r in decisions if r['method'] == method and r['policy'] == 'allocated']
        ranks_changed[method] = len({tuple(sorted(r['ranks'].items())) for r in own}) > 1
    large_relative = any(abs(c['relative_kl_delta'] or 0) >= .2 for c in contrasts
                         if c['kind'] in ['source_representation', 'allocation'])
    tiny_absolute = all(r['mean_kl'] < 1e-5 and r['argmax_flips']/512 < .01 for r in quality)
    report = dict(status='validated', cases=16, target_positions=512, conditions=12,
        factor_elements=prep['factor_elements'], native_elements=prep['native_elements'],
        fraction_of_native_elements=prep['fraction_of_native_elements'],
        ranks_change_across_source_gauges=ranks_changed, contrasts=contrasts,
        relative_screen_signal=large_relative, tiny_absolute_effect_everywhere=tiny_absolute,
        candidate_design_warranted=large_relative and not tiny_absolute,
        uncertainty='Exploratory whole-case bootstrap10000 seed20261013; no multiplicity-adjusted confirmatory claims',
        scope='Six V/O modules; 16 new development train questions; teacher-forced prefixes, not GSM8K accuracy',
        versions=summary['versions'], source_sha256=summary['source_sha256'],
        storage_audit=storage,
        resources=dict(gpu_hours=0, prepare_wall_seconds=prep['wall_seconds'],
                       evaluate_wall_seconds=summary['wall_seconds'], cpu_threads=summary['cpu_threads'],
                       peak_evaluate_rss_bytes=summary['rss_bytes']),
        controls=dict(max_rms=summary['controls_max_rms'], min_compression_rms=summary['minimum_compression_rms']),
        input_sha256={str(p.relative_to(source)):sha(p) for p in source.rglob('*') if p.is_file()})
    output.mkdir(parents=True, exist_ok=True)
    with (output/'quality.csv').open('w') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(quality[0]))
        writer.writeheader();writer.writerows(quality)
    (output/'decisions.json').write_text(json.dumps(decisions, indent=2)+'\n')
    (output/'validation.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(dict(quality=quality, candidate_design_warranted=report['candidate_design_warranted'],
                         ranks_change_across_source_gauges=ranks_changed), indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--exclude-cases', type=Path, action='append', default=[])
    args = parser.parse_args()
    main(args.input, args.output, args.exclude_cases)
