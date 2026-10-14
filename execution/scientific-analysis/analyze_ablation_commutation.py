#!/usr/bin/env python3
"""Accept a frozen eight-old-case screen and apply its predeclared effect gate."""
import argparse
import collections
import csv
import hashlib
import json
import math
from pathlib import Path
import statistics


def main(source, output):
    read = lambda name: json.loads((source/name).read_text())
    summary, frozen = read('summary.json'), read('frozen.json')
    if summary['status'] != 'complete':
        raise ValueError('Incomplete screen')
    if hashlib.sha256((source/'frozen.json').read_bytes()).hexdigest() != summary['frozen_sha256']:
        raise ValueError('Freeze changed')
    if hashlib.sha256((source/'cases.json').read_bytes()).hexdigest() != frozen['cases_sha256']:
        raise ValueError('Cases changed')
    native = read('native-checks.json')
    if len(native) != 4 or not all(row['bitwise_equal'] for row in native):
        raise ValueError('Native reference not accepted')
    rows = [json.loads(line) for line in (source/'per-case.jsonl').read_text().splitlines()]
    groups = collections.defaultdict(dict)
    for row in rows:
        key = (row['kind'], row['gauge'])
        if row['case'] in groups[key] or row['tokens'] != 32:
            raise ValueError('Duplicate/invalid row')
        if not all(math.isfinite(v) for v in row.values() if isinstance(v, (float, int))):
            raise ValueError('Nonfinite metric')
        groups[key][row['case']] = row
    expected = {(kind, gauge) for kind in ['raw_v_off', 'raw_o_off'] for gauge in [.995, 1., 1.005]}
    expected |= {(kind, 1.) for kind in ['v_shape_off', 'o_shape_off', 'gain_off', 'pair_off']}
    if len(rows) != 80 or set(groups) != expected or any(set(g) != set(range(8)) for g in groups.values()):
        raise ValueError('Coverage/alignment')
    conditions = {(c['kind'], c['gauge']): c for c in summary['conditions']}
    for key, group in groups.items():
        for dest, metric in [('mean_kl', 'kl_reference_to_changed'), ('mean_nll_delta', 'nll_difference'), ('mean_rms', 'rms')]:
            if not math.isclose(statistics.mean(row[metric] for row in group.values()), conditions[key][dest], rel_tol=1e-12, abs_tol=1e-14):
                raise ValueError('Summary mismatch')
    controls = read('controls.json')
    if len(controls) != 40:
        raise ValueError('Control coverage')
    floor = max(row['rms'] for row in controls)
    if floor >= .01*min(c['mean_rms'] for c in conditions.values() if c['mean_rms'] > 0):
        raise ValueError('Numerical floor')
    contrasts = []
    for gauge in [.995, 1., 1.005]:
        v, o = conditions['raw_v_off', gauge], conditions['raw_o_off', gauge]
        contrasts.append(dict(gauge=gauge, v_mean_kl=v['mean_kl'], o_mean_kl=o['mean_kl'],
            v_minus_o_kl=v['mean_kl']-o['mean_kl'],
            v_mean_nll_delta=v['mean_nll_delta'], o_mean_nll_delta=o['mean_nll_delta']))
    differences = [c['v_minus_o_kl'] for c in contrasts]
    raw_kl = [conditions[k]['mean_kl'] for k in expected if k[0].startswith('raw_')]
    reversal = min(differences) < 0 < max(differences)
    kl_gate = reversal and max(differences)-min(differences) > .1*max(raw_kl)
    nll_changes = {}
    for kind in ['raw_v_off', 'raw_o_off']:
        values = [conditions[kind, gauge]['mean_nll_delta'] for gauge in [.995, 1., 1.005]]
        nll_changes[kind] = dict(minimum=min(values), maximum=max(values),
            sign_change=min(values) < 0 < max(values), range=max(values)-min(values))
    nll_gate = any(c['sign_change'] and c['range'] > .001 for c in nll_changes.values())
    output.mkdir(parents=True, exist_ok=True)
    for filename, records in [('quality.csv', summary['conditions']), ('gauge-contrasts.csv', contrasts)]:
        with (output/filename).open('w', newline='') as stream:
            writer = csv.DictWriter(stream, fieldnames=list(dict.fromkeys(k for row in records for k in row)))
            writer.writeheader()
            writer.writerows(records)
    result = dict(status='PASS', cases=8, rows=80, tokens_per_condition=256,
        exploration_only=True, full_task_accuracy=False, significance_test=False,
        passed_screen_gate=kl_gate or nll_gate, kl_ranking_reversal=reversal,
        kl_contrast_range=max(differences)-min(differences), kl_gate=kl_gate,
        gold_nll_changes=nll_changes, gold_nll_gate=nll_gate,
        controls_max_rms=floor, controls=controls,
        source_sha256=summary['source_sha256'], cases_sha256=frozen['cases_sha256'],
        versions=summary['versions'], wall_seconds=summary['wall_seconds'], gpu_hours=0)
    (output/'validation.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps({k: v for k, v in result.items() if k not in ['controls', 'source_sha256', 'versions']}, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    main(args.source, args.output)
