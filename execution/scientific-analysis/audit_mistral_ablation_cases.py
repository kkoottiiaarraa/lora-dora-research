#!/usr/bin/env python3
"""Read-only independent question/token/exclusion audit; Mistral128 whole-text tokenization; no model or GPU."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import sys

os.environ.update(CUDA_VISIBLE_DEVICES='', OMP_NUM_THREADS='2', MKL_NUM_THREADS='2',
    HF_HUB_OFFLINE='1', TRANSFORMERS_OFFLINE='1', TOKENIZERS_PARALLELISM='false')
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from lora_dora_study.evaluation import sha256_file
from lora_dora_study.fidelity_audit import content_digest
from lora_dora_study.benchmarks import user_content


def main(root, output):
    read = lambda p: json.loads(p.read_text())
    manifest = read(root/'manifest-private.json')
    parent = Path(manifest['full_root'])
    fm = read(parent/'manifest-private.json')
    original = Path(fm['parent_root'])
    old = read(original/'manifest-private.json')
    datasets = {}
    for split in ['train', 'test']:
        if sha256_file(Path(old[split]['path'])) != old[split]['sha256']:
            raise ValueError('Dataset changed')
        datasets[split] = [json.loads(line) for line in Path(old[split]['path']).read_text().splitlines()]
    excluded = {content_digest(row) for row in datasets['train'][:232]+datasets['test']}
    paths = [Path(old['calibration_cases']), original/'validation-cases.json',
        Path(fm['anchored_root'])/'validation-cases.json', Path(fm['budget_root'])/'prepare/cases.json',
        parent/'cases.json', Path(manifest['radial_root'])/'cases.json',
        Path(manifest['allocation_root'])/'evaluate/cases.json', Path(manifest['affine_root'])/'evaluate/cases.json',
        Path(manifest['qwen_validation_root'])/'cases.json', Path(manifest['screen_root'])/'cases.json']
    excluded |= {case['prompt_content_sha256'] for path in paths for case in read(path)}
    frozen = read(root/'frozen.json')
    digest = hashlib.sha256(json.dumps(sorted(excluded)).encode()).hexdigest()
    if digest != frozen['exclusions_sha256']:
        raise ValueError('Exclusions changed')
    cases = read(root/'cases.json')
    content = {case['prompt_content_sha256'] for case in cases}
    if len(cases) != 128 or len(content) != 128 or content & excluded:
        raise ValueError('Wrong coverage or leakage')
    if sha256_file(root/'cases.json') != frozen['cases_sha256']:
        raise ValueError('Question file changed')
    from transformers import AutoTokenizer
    tokenizer = AutoTokenizer.from_pretrained(Path(manifest['hub_cache'])/('models--'+manifest['base']['repo_id'].replace('/', '--'))/'snapshots'/manifest['base']['revision'],
        local_files_only=True, trust_remote_code=False)
    for case in cases:
        row = datasets['train'][case['train_index']]
        if content_digest(row) != case['prompt_content_sha256']:
            raise ValueError('Question identity')
        prefix = 'question: '+row['question']+' answer: '
        encoded = tokenizer(prefix+row['answer'], add_special_tokens=True, return_offsets_mapping=True)
        boundary = next(i for i, (a, b) in enumerate(encoded['offset_mapping']) if b > len(prefix))
        targets = encoded['input_ids'][boundary:boundary+32]
        if boundary > 512 or len(targets) != 32 or case['prompt_tokens'] != boundary or case['targets'] != targets or case['input_ids'] != encoded['input_ids'][:boundary+31]:
            raise ValueError('Tokenization/continuation mismatch')
    result = dict(status='PASS', cases=128, excluded_content_hashes=len(excluded),
        exclusions_sha256=digest, cases_sha256=frozen['cases_sha256'],
        all_question_identities_verified=True, all_input_and_target_tokens_rebuilt=True,
        no_prior_or_test_content_overlap=True, model_loaded=False, gpu_hours=0)
    output.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    main(args.root, args.output)
