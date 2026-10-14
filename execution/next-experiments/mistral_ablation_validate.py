#!/usr/bin/env python3
"""Fixed128 fresh Mistral gold-NLL validation, CPU FP32, no training."""
import argparse
from contextlib import contextmanager
import datetime
import importlib.metadata
import json
import os
from pathlib import Path
import resource
import signal
import sys
import time

os.environ.update(CUDA_VISIBLE_DEVICES='', OMP_NUM_THREADS='16', MKL_NUM_THREADS='16',
    OPENBLAS_NUM_THREADS='16', HF_HUB_OFFLINE='0', TRANSFORMERS_OFFLINE='1',
    TOKENIZERS_PARALLELISM='false')
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from lora_dora_study.server import write_json, available_memory_bytes
from lora_dora_study.evaluation import sha256_file


def main(root):
    start = time.monotonic()
    summary = dict(status='running', phase='setup', conditions=[], gpu_count=0,
        training=False, started_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
    def save():
        summary.update(wall_seconds=time.monotonic()-start,
            rss_bytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024)
        write_json(root/'summary.json', summary)
    def deadline(signum, frame):
        raise TimeoutError('Bounded ablation screen deadline')
    signal.signal(signal.SIGALRM, deadline)
    signal.setitimer(signal.ITIMER_REAL, 5400)
    save()
    try:
        manifest = json.loads((root/'manifest-private.json').read_text())
        for relative, digest in manifest['source_sha256'].items():
            if sha256_file(ROOT/relative) != digest:
                raise ValueError('Frozen source changed: '+relative)
        from huggingface_hub import snapshot_download, HfApi
        download_start = time.monotonic()
        base_path = Path(snapshot_download(manifest['base']['repo_id'], revision=manifest['base']['revision'],
            cache_dir=manifest['hub_cache'], allow_patterns=['config.json', 'tokenizer*', 'special_tokens_map.json', '*.model'],
            max_workers=2, token=False))
        adapter_path = Path(snapshot_download(manifest['dora']['repo_id'], revision=manifest['dora']['revision'],
            cache_dir=manifest['hub_cache'], allow_patterns=['adapter_config.json', 'adapter_model.safetensors', 'README.md'],
            max_workers=2, token=False))
        summary['download_seconds'] = time.monotonic()-download_start
        verification_start = time.monotonic()
        adapter_sha = sha256_file(adapter_path/'adapter_model.safetensors')
        if adapter_sha != manifest['dora']['weights_sha256']:
            raise ValueError('Adapter weight hash mismatch')
        weight_files = sorted(base_path.glob('*.safetensors'))
        if len(weight_files) != 2:
            raise ValueError('Expected two base shards')
        verified = {}
        metadata = None
        for path in weight_files:
            expected = path.resolve().name
            if len(expected) != 64 or any(c not in '0123456789abcdef' for c in expected):
                if metadata is None:
                    metadata = HfApi().model_info(manifest['base']['repo_id'], revision=manifest['base']['revision'], files_metadata=True, token=False)
                sibling = next(x for x in metadata.siblings if x.rfilename == path.name)
                expected = sibling.lfs['sha256'] if isinstance(sibling.lfs, dict) else sibling.lfs.sha256
            observed = sha256_file(path)
            if observed != expected:
                raise ValueError('Base shard checksum mismatch')
            verified[path.name] = observed
        summary['weight_verification_seconds'] = time.monotonic()-verification_start
        config = json.loads((adapter_path/'adapter_config.json').read_text())
        if config['r'] != 32 or config['lora_alpha'] != 64 or not config['use_dora']:
            raise ValueError('Adapter config changed')
        if set(config['target_modules']) != {'q_proj', 'k_proj', 'v_proj', 'o_proj', 'gate_proj'}:
            raise ValueError('Target config changed')
        if config.get('spectral_top') or config.get('spectral_bottom') or config.get('use_rslora'):
            raise ValueError('Unsupported spectral/rank-scaling variant')
        write_json(root/'artifact-provenance.json', dict(base=dict(repo_id=manifest['base']['repo_id'],
            revision=manifest['base']['revision'], verified_shards_sha256=verified),
            dora=dict(repo_id=manifest['dora']['repo_id'], revision=manifest['dora']['revision'],
            weights_sha256=adapter_sha, storage_dtype='bfloat16'), execution_dtype='float32',
            author_training_provenance_confirmed=False, author_benchmark_reproduced=False))
        old = dict(versions=manifest['versions'], artifacts=dict(base=dict(snapshot_path=str(base_path)), dora=dict(snapshot_path=str(adapter_path))))
        screen = Path(manifest['screen_root'])
        if sha256_file(screen/'cases.json') != manifest['screen_cases_sha256']:
            raise ValueError('Old Mistral questions changed')
        cal = json.loads((screen/'cases.json').read_text())
        parent = Path(manifest['full_root'])
        fm = json.loads((parent/'manifest-private.json').read_text())
        original = Path(fm['parent_root'])
        qm = json.loads((original/'manifest-private.json').read_text())
        datasets = {}
        for split in ['train', 'test']:
            if sha256_file(Path(qm[split]['path'])) != qm[split]['sha256']:
                raise ValueError('Dataset changed')
            datasets[split] = [json.loads(line) for line in Path(qm[split]['path']).read_text().splitlines()]
        from lora_dora_study.fidelity_audit import content_digest
        excluded = {content_digest(row) for row in datasets['train'][:232]+datasets['test']}
        for path in [Path(qm['calibration_cases']), original/'validation-cases.json',
            Path(fm['anchored_root'])/'validation-cases.json', Path(fm['budget_root'])/'prepare/cases.json',
            parent/'cases.json', Path(manifest['radial_root'])/'cases.json',
            Path(manifest['allocation_root'])/'evaluate/cases.json', Path(manifest['affine_root'])/'evaluate/cases.json',
            Path(manifest['qwen_validation_root'])/'cases.json', screen/'cases.json']:
            excluded |= {item['prompt_content_sha256'] for item in json.loads(path.read_text())}
        import hashlib
        exclusions_sha256 = hashlib.sha256(json.dumps(sorted(excluded)).encode()).hexdigest()
        from transformers import AutoTokenizer
        tokenizer = AutoTokenizer.from_pretrained(base_path, local_files_only=True, trust_remote_code=False)
        cases = []
        for index, row in enumerate(datasets['train']):
            digest = content_digest(row)
            if digest in excluded:
                continue
            prefix = 'question: '+row['question']+' answer: '
            encoded = tokenizer(prefix+row['answer'], add_special_tokens=True, return_offsets_mapping=True)
            boundary = next(i for i, (a, b) in enumerate(encoded['offset_mapping']) if b > len(prefix))
            targets = encoded['input_ids'][boundary:boundary+32]
            if boundary > 512 or len(targets) != 32:
                continue
            cases.append(dict(train_index=index, prompt_content_sha256=digest,
                input_ids=encoded['input_ids'][:boundary+31], targets=targets, prompt_tokens=boundary))
            excluded.add(digest)
            if len(cases) == 128:
                break
        if len(cases) != 128:
            raise ValueError('Insufficient fresh eligible cases')
        write_json(root/'cases.json', cases)
        import torch
        from transformers import AutoModelForCausalLM
        from peft import PeftModel
        from lora_dora_study.adapters import verify_loaded_adapter
        from lora_dora_study.fidelity_audit import convert_custom, metrics
        from lora_dora_study.radial_quotient import coefficients
        torch.set_num_threads(16)
        torch.set_num_interop_threads(1)
        torch.manual_seed(20261014)
        torch.set_float32_matmul_precision('highest')
        versions = {k: importlib.metadata.version(k) for k in old['versions']}
        if versions != old['versions']:
            raise ValueError('Versions changed')
        if available_memory_bytes() < 64*1024**3:
            raise BlockingIOError('Need64GiB available RAM')
        summary.update(versions=versions, source_sha256=manifest['source_sha256'], cpu_threads=16)
        write_json(root/'frozen.json', dict(cases_sha256=sha256_file(root/'cases.json'),
            source_sha256=manifest['source_sha256'], gauges=[.995, 1.005], cases=128, exclusions_sha256=exclusions_sha256,
            dataset_sha256={key: qm[key]['sha256'] for key in ['train', 'test']},
            before_outputs=True, exploration_only=False))
        summary['frozen_sha256'] = sha256_file(root/'frozen.json')
        model = AutoModelForCausalLM.from_pretrained(old['artifacts']['base']['snapshot_path'],
            local_files_only=True, trust_remote_code=False, torch_dtype=torch.float32,
            device_map={'': 'cpu'}, low_cpu_mem_usage=True, attn_implementation='sdpa')
        model = PeftModel.from_pretrained(model, old['artifacts']['dora']['snapshot_path'],
            local_files_only=True, is_trainable=False).eval()
        model.requires_grad_(False)
        check = verify_loaded_adapter(model, old['artifacts']['dora']['snapshot_path'], True)
        if not check['exact_loaded_value_match'] or check['adapted_module_count'] != 160:
            raise ValueError('Adapter mismatch')
        if any(x['r'] != 32 or x['alpha'] != 64 or x['scaling'] != 2 for x in check['modules']):
            raise ValueError('Loaded rank/alpha/scaling mismatch')
        summary['verified_native_modules'] = 160
        summary['verified_saved_tensors'] = check['saved_tensor_count']
        if any(p.dtype != torch.float32 or p.device.type != 'cpu' for p in model.parameters()):
            raise ValueError('Execution mode changed')
        def logits(case):
            ids = torch.tensor([case['input_ids']], dtype=torch.long)
            with torch.inference_mode():
                y = model(input_ids=ids, attention_mask=torch.ones_like(ids),
                    use_cache=False, logits_to_keep=32).logits[0].detach().cpu()
            if y.shape[0] != 32 or not bool(y.isfinite().all()):
                raise FloatingPointError('Invalid logits')
            return y
        native = [torch.load(screen/'native-logit-cache'/f'original-{i}.pt', map_location='cpu', weights_only=True) for i in range(4)]
        native_checks = []
        for i, case in enumerate(cal[:4]):
            observed = logits(case)
            native_checks.append(dict(case=i, bitwise_equal=torch.equal(observed, native[i]),
                **metrics(native[i], observed, case['targets'])))
            write_json(root/'native-checks.json', native_checks)
            if not native_checks[-1]['bitwise_equal']:
                torch.save(observed, root/f'native-reference-failed-{i}.pt')
                raise ValueError('Old Mistral native reference changed on case '+str(i))
        pairs = {}
        for name, module in model.named_modules():
            leaf = name.rsplit('.', 1)[-1]
            if leaf not in ['v_proj', 'o_proj'] or not hasattr(module, 'use_dora'):
                continue
            if not module.use_dora.get('default') or module.get_base_layer().bias is not None:
                raise ValueError('Expected bias-free DoRA V/O')
            b = module.get_base_layer().weight.detach()
            u = b+(module.lora_B['default'].weight@module.lora_A['default'].weight)*module.scaling['default']
            d = module.lora_magnitude_vector['default'].weight.detach()/u.norm(dim=1)
            if not bool((d > 0).all()):
                raise ValueError('Positive D required for chosen decomposition')
            pairs.setdefault(name.rsplit('.', 1)[0], {})[leaf] = dict(name=name, u=u.detach(), d=d)
        if len(pairs) != 32 or any(set(pair) != {'v_proj', 'o_proj'} for pair in pairs.values()):
            raise ValueError('Pair coverage')
        rowscale = []
        for name, pair in pairs.items():
            row = dict(module=name)
            for leaf, record in pair.items():
                logs = record['d'].double().log()
                row[leaf] = dict(log_mean=float(logs.mean()), log_std=float(logs.std(unbiased=False)),
                    minimum=float(record['d'].min()), maximum=float(record['d'].max()))
            rowscale.append(row)
        write_json(root/'row-scales.json', rowscale)
        convert_custom(model)
        model.eval()
        model.requires_grad_(False)

        @contextmanager
        def intervention(kind, gauge=1.):
            restore = []
            try:
                for pair in pairs.values():
                    dv, do = coefficients(pair['v_proj']['d'], pair['o_proj']['d'], kind, gauge)
                    for leaf, scale in [('v_proj', dv), ('o_proj', do)]:
                        record = pair[leaf]
                        module = model.get_submodule(record['name'])
                        restore.append((module, module.weight))
                        module.weight = torch.nn.Parameter(scale.float()[:, None]*record['u'], requires_grad=False)
                yield
            finally:
                for module, weight in reversed(restore):
                    module.weight = weight

        cache = root/'logit-cache'
        cache.mkdir()
        controls = []
        for i, case in enumerate(cal[:4]):
            controls.append(dict(kind='native_to_dense', case=i,
                **metrics(native[i], logits(case), case['targets'])))
        for i, case in enumerate(cases):
            y = logits(case)
            torch.save(y, cache/f'dense-source-{i}.pt')
            summary.update(phase='dense_reference', cases_completed=i+1)
            save()
        for gauge in [.995, 1.005]:
            with intervention('source', gauge):
                for i, case in enumerate(cases[:4]):
                    reference = torch.load(cache/f'dense-source-{i}.pt', weights_only=True, map_location='cpu')
                    controls.append(dict(kind='source_gauge', gauge=gauge, case=i,
                        **metrics(reference, logits(case), case['targets'])))
        conditions = [(kind, gauge) for kind in ['raw_v_off', 'raw_o_off'] for gauge in [.995, 1.005]]
        conditions += [(kind, 1.) for kind in ['v_shape_off', 'o_shape_off', 'gain_off', 'pair_off']]
        for kind, gauge in conditions:
            condition = dict(kind=kind, gauge=gauge, status='running', cases_completed=0)
            summary['conditions'].append(condition)
            summary['phase'] = 'conditions'
            rows = []
            with intervention(kind, gauge):
                for i, case in enumerate(cases):
                    reference = torch.load(cache/f'dense-source-{i}.pt', map_location='cpu', weights_only=True)
                    y = logits(case)
                    row = dict(kind=kind, gauge=gauge, case=i, **metrics(reference, y, case['targets']))
                    with (root/'per-case.jsonl').open('a') as stream:
                        stream.write(json.dumps(row)+'\n')
                    if kind in ['v_shape_off', 'o_shape_off', 'gain_off'] and i < 4:
                        torch.save(y, cache/f'{kind}-{i}.pt')
                    rows.append(row)
                    condition['cases_completed'] = i+1
                    save()
            condition.update(status='complete', mean_kl=sum(r['kl_reference_to_changed'] for r in rows)/128,
                mean_nll_delta=sum(r['nll_difference'] for r in rows)/128,
                mean_rms=sum(r['rms'] for r in rows)/128,
                argmax_disagreements=sum(r['argmax_disagreements'] for r in rows))
            save()
        for kind in ['v_shape_off', 'o_shape_off', 'gain_off']:
            for gauge in [.995, 1.005]:
                with intervention(kind, gauge):
                    for i, case in enumerate(cases[:4]):
                        reference = torch.load(cache/f'{kind}-{i}.pt', map_location='cpu', weights_only=True)
                        controls.append(dict(kind=kind+'_gauge', gauge=gauge, case=i,
                            **metrics(reference, logits(case), case['targets'])))
        write_json(root/'controls.json', controls)
        source = torch.load(cache/'dense-source-0.pt', map_location='cpu', weights_only=True)
        if not torch.equal(source, logits(cases[0])):
            raise ValueError('Interventions did not restore source')
        floor = max(r['rms'] for r in controls)
        effect = min(c['mean_rms'] for c in summary['conditions'] if c['mean_rms'] > 0)
        if floor >= .01*effect:
            raise ValueError('Numerical floor exceeds1% of smallest effect')
        if sha256_file(root/'frozen.json') != summary['frozen_sha256']:
            raise ValueError('Frozen configuration changed')
        summary.update(status='complete', phase='complete', controls_max_rms=floor,
            minimum_effect_rms=effect, full_task_accuracy=False, exploration_only=False)
        save()
    except Exception as exc:
        summary.update(status='failed', error=repr(exc))
        save()
        raise
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=Path, required=True)
    args = parser.parse_args()
    main(args.root)
