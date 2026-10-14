#!/usr/bin/env python3
"""Predeclared paired confirmation on64fresh questions, stdlib only."""
import argparse
import collections
import csv
import hashlib
import json
import math
from pathlib import Path
import random
import statistics


def paired(differences, seed):
    rng = random.Random(seed)
    n, draws = len(differences), 10000
    mean = statistics.mean(differences)
    boot = sorted(sum(differences[rng.randrange(n)] for _ in range(n))/n for _ in range(draws))
    observed = abs(mean)
    exceed = sum(abs(sum(x*(1 if rng.getrandbits(1) else -1) for x in differences)/n) >= observed for _ in range(draws))
    return dict(mean_delta=mean, ci95=[boot[249], boot[9749]], ci97_5=[boot[124], boot[9874]],
        sign_flip_p=(1+exceed)/(draws+1), positive_cases=sum(x > 0 for x in differences),
        negative_cases=sum(x < 0 for x in differences))


def main(source, output):
    read = lambda name: json.loads((source/name).read_text())
    summary, frozen = read('summary.json'), read('frozen.json')
    if summary['status'] != 'complete':
        raise ValueError('Incomplete validation')
    for filename, digest in [('frozen.json', summary['frozen_sha256']), ('cases.json', frozen['cases_sha256'])]:
        if hashlib.sha256((source/filename).read_bytes()).hexdigest() != digest:
            raise ValueError('Immutable input changed')
    native = read('native-checks.json')
    if len(native) != 4 or not all(row['bitwise_equal'] for row in native):
        raise ValueError('Native reference')
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
    if len(rows) != 640 or set(groups) != expected or any(set(g) != set(range(64)) for g in groups.values()):
        raise ValueError('Coverage/alignment')
    conditions = {(c['kind'], c['gauge']): c for c in summary['conditions']}
    for key, group in groups.items():
        for dest, metric in [('mean_kl', 'kl_reference_to_changed'), ('mean_nll_delta', 'nll_difference'), ('mean_rms', 'rms')]:
            if not math.isclose(statistics.mean(row[metric] for row in group.values()), conditions[key][dest], rel_tol=1e-12, abs_tol=1e-14):
                raise ValueError('Summary mismatch')
    controls = read('controls.json')
    if len(controls) != 36 or max(r['rms'] for r in controls) >= .01*min(c['mean_rms'] for c in conditions.values() if c['mean_rms'] > 0):
        raise ValueError('Numerical controls')
    contrasts = []
    for metric in ['kl_reference_to_changed', 'nll_difference']:
        for gauge in [.995, 1.005]:
            differences = [groups['raw_v_off', gauge][i][metric]-groups['raw_o_off', gauge][i][metric] for i in range(64)]
            contrasts.append(dict(metric=metric, gauge=gauge, **paired(differences, 20261014+len(contrasts))))
    largest = 0
    for rank, index in enumerate(sorted(range(4), key=lambda i: contrasts[i]['sign_flip_p'])):
        largest = max(largest, min(1, (4-rank)*contrasts[index]['sign_flip_p']))
        contrasts[index]['holm_p'] = largest
    primary = contrasts[:2]
    confirmed = (primary[0]['ci97_5'][0] > 0 and primary[1]['ci97_5'][1] < 0
                 and all(c['holm_p'] < .05 for c in primary))
    output.mkdir(parents=True, exist_ok=True)
    for filename, records in [('fresh-quality.csv', summary['conditions']), ('fresh-contrasts.csv', contrasts)]:
        with (output/filename).open('w', newline='') as stream:
            writer = csv.DictWriter(stream, fieldnames=list(dict.fromkeys(k for row in records for k in row)))
            writer.writeheader()
            writer.writerows(records)
    result = dict(status='PASS', cases=64, rows=640, tokens_per_condition=2048,
        primary_reversal_confirmed=confirmed, contrasts=contrasts, primary_family_size=4,
        controls_max_rms=max(r['rms'] for r in controls), controls=controls,
        cases_sha256=frozen['cases_sha256'], exclusions_sha256=frozen['exclusions_sha256'],
        source_sha256=summary['source_sha256'], versions=summary['versions'],
        wall_seconds=summary['wall_seconds'], gpu_hours=0, full_task_accuracy=False,
        training_mechanism_identified=False, conference_level_established=False)
    (output/'fresh-validation.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps({k: v for k, v in result.items() if k not in ['controls', 'source_sha256', 'versions']}, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    main(args.source, args.output)
