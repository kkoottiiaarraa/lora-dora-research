#!/usr/bin/env python3
"""Read-only acceptance of saved tensors, provenance and paired prefix rows.

Run on the compute server. No model load, inference, GPU or parameter updates.
Operational paths are accepted as arguments and omitted from the output.
"""
import argparse
import collections
import json
import math
import os
from pathlib import Path
import statistics
import sys

os.environ.update(CUDA_VISIBLE_DEVICES='', OMP_NUM_THREADS='2', MKL_NUM_THREADS='2')
REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))
from lora_dora_study.evaluation import sha256_file
from lora_dora_study.fidelity_audit import content_digest


def read(path):
    return json.loads(path.read_text())


def require(condition, message):
    if not condition:
        raise ValueError(message)


def main(root, output):
    import torch
    torch.set_num_threads(2)
    prep, evaluation = read(root/'prepare/summary.json'), read(root/'evaluate/summary.json')
    require(prep['status'] == evaluation['status'] == 'complete', 'Incomplete run')
    frozen = read(root/'evaluate/frozen.json')
    require(sha256_file(root/'evaluate/frozen.json') == evaluation['frozen_sha256'], 'Evaluation freeze changed')
    require(sha256_file(root/'prepare/frozen.json') == prep['frozen_sha256'], 'Preparation freeze changed')
    require(sha256_file(root/'prepare/factors.pt') == frozen['factors_sha256'], 'Primary factors changed')
    require(sha256_file(root/'native-m-baselines.pt') == frozen['native_baselines_sha256'], 'Native factors changed')
    for relative, digest in frozen['source_sha256'].items():
        require(sha256_file(REPO/relative) == digest, 'Source code changed: '+relative)
    manifest = read(root/'eval-manifest-private.json')
    parent = Path(manifest['full_root'])
    parent_manifest = read(parent/'manifest-private.json')
    original = Path(parent_manifest['parent_root'])
    original_manifest = read(original/'manifest-private.json')
    shapes = {row['name']: row['shape'] for row in read(parent/'capture/summary.json')['modules']}
    factors = torch.load(root/'prepare/factors.pt', map_location='cpu', weights_only=True)
    factors.update(torch.load(root/'native-m-baselines.pt', map_location='cpu', weights_only=True))
    labels = {'weighted_uniform', 'kfac_uniform', 'structural_kfac', 'joint_kfac', 'native_m_input', 'native_m_kfac'}
    require(set(factors) == labels, 'Unexpected conditions')
    counts = {}
    for label, records in factors.items():
        require(set(records) == set(shapes) and len(records) == 144, 'Module coverage')
        counts[label] = 0
        for name, record in records.items():
            required = {'left', 'right'} if label in {'weighted_uniform', 'kfac_uniform'} else {'left', 'right', 'row_scale'}
            require(set(record) == required, 'Unexpected factor keys')
            out_size, in_size = shapes[name]
            rank = record['left'].shape[1]
            require(record['left'].shape == (out_size, rank) and record['right'].shape == (rank, in_size), 'Factor shapes')
            require(rank == 8 if len(required) == 2 else rank in {7, 8}, 'Unexpected rank')
            if 'row_scale' in record:
                require(record['row_scale'].shape == (out_size,), 'Diagonal shape')
            for tensor in record.values():
                require(tensor.dtype == torch.float32 and bool(tensor.isfinite().all()), 'Nonfinite or wrong dtype')
                counts[label] += tensor.numel()
        require(counts[label] == 5898240 == frozen['factor_counts'][label], 'Actual storage mismatch')
    cases_path = root/'evaluate/cases.json'
    cases = read(cases_path)
    require(len(cases) == 128 and sha256_file(cases_path) == frozen['cases_sha256'], 'Case coverage/hash')
    failed_cases = root/'failed-native-reference-attempt-1/evaluate/cases.json'
    if failed_cases.exists():
        require(sha256_file(cases_path) == sha256_file(failed_cases), 'Technical retry changed questions')
    native_checks = read(root/'evaluate/native-reference-checks.json')
    require(len(native_checks) == 4 and all(r['bitwise_equal'] for r in native_checks), 'Native reference not accepted')
    old_paths = [Path(original_manifest['calibration_cases']), original/'validation-cases.json',
        Path(parent_manifest['anchored_root'])/'validation-cases.json',
        Path(parent_manifest['budget_root'])/'prepare/cases.json', parent/'cases.json',
        Path(manifest['radial_root'])/'cases.json', Path(manifest['allocation_root'])/'evaluate/cases.json']
    excluded = {r['prompt_content_sha256'] for path in old_paths for r in read(path)}
    datasets = {}
    for split in ['train', 'test']:
        item = original_manifest[split]
        require(sha256_file(Path(item['path'])) == item['sha256'], 'Dataset changed')
        datasets[split] = [json.loads(line) for line in Path(item['path']).read_text().splitlines()]
    excluded.update(content_digest(r) for r in datasets['test'] + datasets['train'][:232])
    digests = [r['prompt_content_sha256'] for r in cases]
    require(len(set(digests)) == 128 and not set(digests) & excluded, 'Case duplication/leakage')
    for case in cases:
        require(content_digest(datasets['train'][case['train_index']]) == case['prompt_content_sha256'], 'Question identity')
        require(len(case['targets']) == 32, 'Wrong target coverage')
    rows = [json.loads(line) for line in (root/'evaluate/per-case.jsonl').read_text().splitlines()]
    groups = collections.defaultdict(dict)
    for row in rows:
        require(row['case'] not in groups[row['label']], 'Duplicate row')
        require(row['tokens'] == 32 and all(math.isfinite(v) for v in row.values() if isinstance(v, (float, int))), 'Invalid metrics')
        groups[row['label']][row['case']] = row
    require(set(groups) == labels and len(rows) == 768, 'Wrong row coverage')
    for condition in evaluation['conditions']:
        records = groups[condition['label']]
        require(set(records) == set(range(128)), 'Case alignment')
        for key, metric in [('mean_kl', 'kl_reference_to_changed'), ('mean_nll_delta', 'nll_difference'), ('mean_rms', 'rms')]:
            require(math.isclose(statistics.mean(r[metric] for r in records.values()), condition[key], rel_tol=1e-12, abs_tol=1e-14), 'Summary mismatch')
        require(sum(r['argmax_disagreements'] for r in records.values()) == condition['argmax_disagreements'], 'Argmax summary')
    for index in range(128):
        require(len({groups[label][index]['reference_nll'] for label in labels}) == 1, 'Different native teacher')
    controls = read(root/'evaluate/controls.json')
    require(len(controls) == 2 and max(r['rms'] for r in controls) < .01*min(c['mean_rms'] for c in evaluation['conditions']), 'Numerical control floor')
    result = dict(status='PASS', conditions=6, modules_per_condition=144, cases=128,
        tokens_per_condition=4096, rows=768, actual_factor_elements=counts,
        actual_payload_bytes={k: v*4 for k, v in counts.items()}, finite_fp32_tensors=True,
        factor_hashes_match=True, source_hashes_match=True, cases_disjoint_from_previous_and_test=True,
        paired_native_teacher_identical=True, aggregates_recomputed=True, gpu_hours=0)
    output.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    main(args.root, args.output)
