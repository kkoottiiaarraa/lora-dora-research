#!/usr/bin/env python3
"""Apply the fixed128 Mistral endpoint-sign protocol, without further fitting."""
import argparse
import collections
import csv
import hashlib
import json
import math
from pathlib import Path
import random
import statistics


def estimate(values, seed, test=True):
    rng = random.Random(seed)
    n = len(values)
    mean = statistics.mean(values)
    boot = sorted(sum(values[rng.randrange(n)] for _ in range(n))/n for _ in range(10000))
    result = dict(mean=mean, ci95=[boot[249], boot[9749]], ci98_75=[boot[62], boot[9937]],
        positive_cases=sum(x > 0 for x in values), negative_cases=sum(x < 0 for x in values))
    if test:
        count = sum(abs(sum(x*(1 if rng.getrandbits(1) else -1) for x in values)/n) >= abs(mean) for _ in range(10000))
        result['sign_flip_p'] = (1+count)/10001
    return result


def main(source, output):
    read = lambda name: json.loads((source/name).read_text())
    summary, frozen = read('summary.json'), read('frozen.json')
    if summary['status'] != 'complete':
        raise ValueError('Incomplete validation')
    if summary['verified_native_modules'] != 160 or summary['verified_saved_tensors'] != 480:
        raise ValueError('Incomplete adapter')
    for filename, expected in [('frozen.json', summary['frozen_sha256']), ('cases.json', frozen['cases_sha256'])]:
        if hashlib.sha256((source/filename).read_bytes()).hexdigest() != expected:
            raise ValueError('Immutable input changed')
    native = read('native-checks.json')
    if len(native) != 4 or not all(x['bitwise_equal'] for x in native):
        raise ValueError('Native reference')
    rows = [json.loads(line) for line in (source/'per-case.jsonl').read_text().splitlines()]
    groups = collections.defaultdict(dict)
    for row in rows:
        key = (row['kind'], row['gauge'])
        if row['case'] in groups[key] or row['tokens'] != 32 or not all(math.isfinite(x) for x in row.values() if isinstance(x, (float, int))):
            raise ValueError('Duplicate/invalid metric')
        groups[key][row['case']] = row
    expected = {(kind, gauge) for kind in ['raw_v_off', 'raw_o_off'] for gauge in [.995, 1.005]}
    expected |= {(kind, 1.) for kind in ['v_shape_off', 'o_shape_off', 'gain_off', 'pair_off']}
    if len(rows) != 1024 or set(groups) != expected or any(set(x) != set(range(128)) for x in groups.values()):
        raise ValueError('Coverage/alignment')
    conditions = {(x['kind'], x['gauge']): x for x in summary['conditions']}
    for key, group in groups.items():
        for dest, metric in [('mean_kl', 'kl_reference_to_changed'), ('mean_nll_delta', 'nll_difference'), ('mean_rms', 'rms')]:
            if not math.isclose(statistics.mean(x[metric] for x in group.values()), conditions[key][dest], rel_tol=1e-12, abs_tol=1e-14):
                raise ValueError('Summary mismatch')
    controls = read('controls.json')
    if len(controls) != 36 or max(x['rms'] for x in controls) >= .01*min(x['mean_rms'] for x in conditions.values() if x['mean_rms'] > 0):
        raise ValueError('Numerical controls')
    case_audit = json.loads((output/'fresh-case-audit.json').read_text())
    if case_audit['status'] != 'PASS' or case_audit['cases'] != 128 or case_audit['cases_sha256'] != frozen['cases_sha256']:
        raise ValueError('Independent case audit missing or mismatched')
    tests = []
    for kind, gauge, direction in [('raw_v_off', .995, 1), ('raw_v_off', 1.005, -1), ('raw_o_off', .995, -1), ('raw_o_off', 1.005, 1)]:
        values = [groups[kind, gauge][i]['nll_difference'] for i in range(128)]
        tests.append(dict(kind=kind, gauge=gauge, expected_sign=direction,
            **estimate(values, 20261014+len(tests))))
    largest = 0
    for rank, index in enumerate(sorted(range(4), key=lambda i: tests[i]['sign_flip_p'])):
        largest = max(largest, min(1, (4-rank)*tests[index]['sign_flip_p']))
        tests[index]['holm_p'] = largest
    supported = {}
    for kind in ['raw_v_off', 'raw_o_off']:
        selected = [x for x in tests if x['kind'] == kind]
        supported[kind] = all(x['holm_p'] < .05 and (x['ci98_75'][0] > 0 if x['expected_sign'] > 0 else x['ci98_75'][1] < 0) for x in selected)
    secondary = []
    for index, kind in enumerate(['raw_v_off', 'raw_o_off']):
        values = [groups[kind, .995][i]['nll_difference']-groups[kind, 1.005][i]['nll_difference'] for i in range(128)]
        secondary.append(dict(kind=kind, comparison='NLL(.995)-NLL(1.005)', primary=False,
            **estimate(values, 20261024+index, test=False)))
    output.mkdir(parents=True, exist_ok=True)
    for filename, records in [('fresh-quality.csv', summary['conditions']), ('fresh-nll-tests.csv', tests), ('fresh-gauge-responses.csv', secondary)]:
        with (output/filename).open('w', newline='') as stream:
            writer = csv.DictWriter(stream, fieldnames=list(dict.fromkeys(k for row in records for k in row)))
            writer.writeheader()
            writer.writerows(records)
    result = dict(status='PASS', cases=128, rows=1024, tokens_per_condition=4096,
        primary_supported_pairs=supported, primary_sign_reversal_confirmed=any(supported.values()),
        primary_tests=tests, secondary_gauge_responses=secondary, primary_family_size=4,
        controls_max_rms=max(x['rms'] for x in controls), controls=controls,
        cases_sha256=frozen['cases_sha256'], exclusions_sha256=frozen['exclusions_sha256'],
        source_sha256=summary['source_sha256'], versions=summary['versions'],
        artifact_provenance=read('artifact-provenance.json'),
        wall_seconds=summary['wall_seconds'], rss_bytes=summary['rss_bytes'], gpu_hours=0,
        full_task_accuracy=False, author_benchmark_reproduced=False,
        training_mechanism_identified=False, conference_level_established=False)
    (output/'fresh-validation.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps({k: v for k, v in result.items() if k not in ['controls', 'source_sha256', 'versions', 'artifact_provenance']}, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    main(args.source, args.output)
