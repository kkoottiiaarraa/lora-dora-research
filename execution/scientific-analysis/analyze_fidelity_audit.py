"""Aggregate a completed audit using stdlib only; publish no operational metadata."""
import argparse
import csv
import hashlib
import json
import math
import random
from pathlib import Path
import statistics


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_csv(path, rows):
    with path.open('w') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main(source, output):
    output.mkdir(parents=True, exist_ok=True)
    hashes = {'analysis_script': digest(Path(__file__))}
    summaries, tables, checks, effects, nll_intervals = {}, [], [], {}, {}
    cases_path = source / 'cases.json'
    cases = json.loads(cases_path.read_text())
    assert len(cases) == 64
    assert len({r['prompt_content_sha256'] for r in cases}) == 64
    assert all(r['train_index'] >= 232 and len(r['targets']) == 32 for r in cases)
    hashes['cases.json'] = digest(cases_path)
    for phase in ['gpu', 'cpu']:
        folder = source / ('qwen-' + phase)
        summary = json.loads((folder / 'summary.json').read_text())
        rows = [json.loads(line) for line in (folder / 'per-case.jsonl').read_text().splitlines()]
        with (folder / 'metrics.csv').open() as stream:
            csv_rows = list(csv.DictReader(stream))
        assert len(csv_rows) == len(rows)
        for a, b in zip(rows, csv_rows):
            for key, value in a.items():
                assert b[key] == str(value)
        assert summary['status'] == 'complete'
        assert summary['cases_sha256'] == hashes['cases.json']
        for key in ['custom_dense_projection_sha256', 'official_dense_projection_sha256']:
            assert len(summary[key]) == 144
        assert summary['custom_dense_projection_sha256'] == summary['official_dense_projection_sha256']
        assert all(r['exact_adapter_match'] and r['modules'] == 144 for r in summary['loads'])
        removal = summary['aggregates']['remove_d']['mean_rms']
        effects[phase] = {r['case']: r for r in rows if r['condition'] == 'remove_d'}
        values = [effects[phase][i]['nll_difference'] for i in range(64)]
        rng = random.Random(20261013)
        samples = sorted(statistics.mean(rng.choices(values, k=64)) for _ in range(6000))
        nll_intervals[phase] = dict(mean=statistics.mean(values), percentile95=[samples[149], samples[5849]])
        for condition, aggregate in summary['aggregates'].items():
            subset = [r for r in rows if r['condition'] == condition]
            expected = 4 if condition in ['repeat_original', 'official_minus_custom'] or condition.startswith('remove-gauge') else 64
            assert len(subset) == aggregate['cases'] == expected
            assert sorted(r['case'] for r in subset) == list(range(expected))
            for key, field in [('mean_rms', 'rms'), ('mean_nll_delta', 'nll_difference'), ('mean_kl', 'kl_reference_to_changed')]:
                assert math.isclose(statistics.mean(r[field] for r in subset), aggregate[key], rel_tol=1e-12, abs_tol=1e-15)
            assert sum(r['tokens'] for r in subset) == aggregate['tokens']
            assert sum(r['argmax_disagreements'] for r in subset) == aggregate['argmax_disagreements']
            assert max(r['max_abs'] for r in subset) == aggregate['max_abs']
            assert all(r['argmax_disagreements'] <= r['positions_with_margin_below_twice_max_error'] for r in subset)
            for r in subset:
                assert all(math.isfinite(v) for v in r.values() if isinstance(v, (int, float)))
            if expected == 4:
                assert aggregate['max_abs'] == aggregate['mean_rms'] == 0
            tables.append(dict(phase=phase, condition=condition, **aggregate,
                               rms_over_remove_d=aggregate['mean_rms'] / removal))
        if phase == 'cpu':
            assert summary['geometry_gate']['passed']
            for scale, ratio in summary['geometry_gate']['ratios'].items():
                assert math.isclose(summary['aggregates']['gauge_' + scale]['mean_rms'] / removal, ratio, rel_tol=1e-12)
                assert ratio <= .01
        summaries[phase] = summary
        for name in ['summary.json', 'metrics.csv', 'per-case.jsonl']:
            hashes['qwen-' + phase + '/' + name] = digest(folder / name)
        checks.append(phase + ': completeness, finite metrics, independent aggregates, exact merge weights, adapter match, margin bound: PASS')
    assert all(summaries['gpu'][key] == summaries['cpu'][key] for key in ['artifacts', 'versions', 'cases_sha256', 'runner_sha256', 'helper_sha256'])
    geometry_path = source / 'qwen-cpu/geometry.csv'
    with geometry_path.open() as stream:
        geometry = list(csv.DictReader(stream))
    spectra = [r for r in geometry if r['entropy']]
    blocks = [r for r in geometry if r['relative_output_error']]
    assert len(spectra) == 18 and len(blocks) == 9
    geometry_comparisons = []
    for module in sorted({r['module'] for r in spectra}):
        selected = {float(r['c']): r for r in spectra if r['module'] == module}
        assert set(selected) == {.995, 1., 1.005}
        base = selected[1.]
        for scale, row in sorted(selected.items()):
            entropy, erank = float(row['entropy']), float(row['effective_rank'])
            assert math.isclose(math.exp(entropy), erank, rel_tol=1e-12)
            geometry_comparisons.append(dict(module=module[module.index('layers.'):], c=scale,
                entropy_nats=entropy, effective_rank=erank,
                entropy_delta_nats=entropy-float(base['entropy']),
                effective_rank_ratio=erank/float(base['effective_rank']),
                update_norm_ratio=float(row['update_frobenius'])/float(base['update_frobenius'])))
    assert all(float(row['relative_output_error']) < 1e-10 for row in blocks)
    hashes['qwen-cpu/geometry.csv'] = digest(geometry_path)
    interactions = next(r for r in summaries['cpu']['conditions'] if r['condition'] == 'remove_d')['ablation_path_interaction']
    assert len(interactions) == 64
    interaction_rms = statistics.mean(r['rms'] for r in interactions)
    cpu_squared = statistics.mean(r['rms'] ** 2 for r in effects['cpu'].values())
    gpu_squared = statistics.mean(r['rms'] ** 2 for r in effects['gpu'].values())
    interaction_squared = statistics.mean(r['rms'] ** 2 for r in interactions)
    # Same case lengths and vocabulary: squared RMS values recover the pooled dot product.
    cosine = (cpu_squared + gpu_squared - interaction_squared) / (2 * math.sqrt(cpu_squared * gpu_squared))
    assert -1.0000001 <= cosine <= 1.0000001
    result = dict(status='validated', case_count=64, target_positions=2048,
        entropy_definition='p_i=sigma_i^2/sum_j(sigma_j^2); H=-sum_i p_i log(p_i)',
        effective_rank_definition='exp(H); not algebraic rank or adapter rank',
        geometry_scope='six preselected matrices, FP32 reconstruction, no BF16 spectra',
        fp64_block_max_relative_error=max(float(r['relative_output_error']) for r in blocks),
        fp64_block_scope='one deterministic input per selected V/O pair, not full attention evaluation',
        mean_ablation_path_interaction_rms=interaction_rms,
        interaction_over_fp32_remove_d_rms=interaction_rms / summaries['cpu']['aggregates']['remove_d']['mean_rms'],
        pooled_ablation_path_cosine=cosine,
        pooled_rms=dict(cpu_remove_d=math.sqrt(cpu_squared), gpu_remove_d=math.sqrt(gpu_squared), interaction=math.sqrt(interaction_squared)),
        exploratory_nll_intervals=nll_intervals,
        interval_method='6000 percentile bootstrap resamples of 64 whole train cases; seed 20261013; no heldout accuracy claim or multiplicity claim',
        path_comparison_caveat='dtype AND backend differ; no precision-only causality',
        metadata={key: summaries['cpu'][key] for key in ['artifacts', 'versions', 'runner_sha256', 'helper_sha256', 'cases_sha256']},
        resources={phase: {key: d[key] for key in ['wall_seconds', 'max_process_rss_bytes', 'peak_allocated_bytes', 'peak_reserved_bytes'] if key in d} for phase, d in summaries.items()},
        checks=checks, input_sha256=hashes)
    write_csv(output / 'fidelity.csv', tables)
    write_csv(output / 'geometry-comparisons.csv', geometry_comparisons)
    write_csv(output / 'fp64-block-checks.csv', [dict(module=r['module'], c=r['c'], relative_output_error=r['relative_output_error']) for r in blocks])
    (output / 'validation.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({key: value for key, value in result.items() if key not in ['metadata', 'input_sha256']}, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, required=True, help='Private completed thesis-audit directory')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    main(args.input, args.output)
