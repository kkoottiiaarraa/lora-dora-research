#!/usr/bin/env python3
"""Fresh64 V/O attribution validation, CPU FP32, no training."""
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
    OPENBLAS_NUM_THREADS='16', HF_HUB_OFFLINE='1', TRANSFORMERS_OFFLINE='1',
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
        raise TimeoutError('Fresh ablation validation deadline')
    signal.signal(signal.SIGALRM, deadline)
    signal.setitimer(signal.ITIMER_REAL, 1800)
    save()
    try:
        manifest = json.loads((root/'manifest-private.json').read_text())
        for relative, digest in manifest['source_sha256'].items():
            if sha256_file(ROOT/relative) != digest:
                raise ValueError('Frozen source changed: '+relative)
        parent = Path(manifest['full_root'])
        original = Path(json.loads((parent/'manifest-private.json').read_text())['parent_root'])
        old = json.loads((original/'manifest-private.json').read_text())
        calpath = Path(old['calibration_cases'])
        if sha256_file(calpath) != old['calibration_cases_sha256']:
            raise ValueError('Calibration changed')
        cal = json.loads(calpath.read_text())
        from lora_dora_study.fidelity_audit import content_digest
        from lora_dora_study.benchmarks import user_content
        from transformers import AutoTokenizer
        fm = json.loads((parent/'manifest-private.json').read_text())
        datasets = {}
        for split in ['train', 'test']:
            item = old[split]
            if sha256_file(Path(item['path'])) != item['sha256']:
                raise ValueError('Dataset changed')
            datasets[split] = [json.loads(line) for line in Path(item['path']).read_text().splitlines()]
        excluded = {content_digest(row) for row in datasets['train'][:232]+datasets['test']}
        excluded |= {case['prompt_content_sha256'] for case in cal}
        for path in [original/'validation-cases.json', Path(fm['anchored_root'])/'validation-cases.json',
            Path(fm['budget_root'])/'prepare/cases.json', parent/'cases.json',
            Path(manifest['radial_root'])/'cases.json',
            Path(manifest['allocation_root'])/'evaluate/cases.json',
            Path(manifest['affine_root'])/'evaluate/cases.json']:
            excluded |= {case['prompt_content_sha256'] for case in json.loads(path.read_text())}
        import hashlib
        excluded_hash = hashlib.sha256(json.dumps(sorted(excluded)).encode()).hexdigest()
        tokenizer = AutoTokenizer.from_pretrained(old['artifacts']['base']['snapshot_path'],
            local_files_only=True, trust_remote_code=False)
        cases = []
        for index, row in enumerate(datasets['train']):
            digest = content_digest(row)
            if digest in excluded:
                continue
            prompt = tokenizer.apply_chat_template([dict(role='user', content=user_content('gsm8k', row))],
                tokenize=False, add_generation_prompt=True, enable_thinking=False)
            ids = tokenizer(prompt, add_special_tokens=False)['input_ids']
            targets = tokenizer(row['answer'], add_special_tokens=False)['input_ids'][:32]
            if len(ids) > 512 or len(targets) < 32:
                continue
            cases.append(dict(train_index=index, prompt_content_sha256=digest,
                input_ids=ids+targets[:-1], targets=targets))
            excluded.add(digest)
            if len(cases) == 64:
                break
        if len(cases) != 64:
            raise ValueError('Insufficient fresh cases')
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
            source_sha256=manifest['source_sha256'], gauges=[.995, 1., 1.005], cases=64,
            exclusions_sha256=excluded_hash, dataset_sha256={k: old[k]['sha256'] for k in ['train', 'test']},
            before_outputs=True, exploration_only=False))
        summary['frozen_sha256'] = sha256_file(root/'frozen.json')
        model = AutoModelForCausalLM.from_pretrained(old['artifacts']['base']['snapshot_path'],
            local_files_only=True, trust_remote_code=False, torch_dtype=torch.float32,
            device_map={'': 'cpu'}, low_cpu_mem_usage=True, attn_implementation='sdpa')
        model = PeftModel.from_pretrained(model, old['artifacts']['dora']['snapshot_path'],
            local_files_only=True, is_trainable=False).eval()
        model.requires_grad_(False)
        check = verify_loaded_adapter(model, old['artifacts']['dora']['snapshot_path'], True)
        if not check['exact_loaded_value_match'] or check['adapted_module_count'] != 144:
            raise ValueError('Adapter mismatch')
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
        native = [torch.load(original/'capture/logit-cache'/f'original-{i}.pt',
            map_location='cpu', weights_only=True) for i in range(4)]
        native_checks = []
        for i in range(4):
            observed = logits(cal[i])
            native_checks.append(dict(case=i, bitwise_equal=torch.equal(observed, native[i]),
                **metrics(native[i], observed, cal[i]['targets'])))
            write_json(root/'native-checks.json', native_checks)
            if not native_checks[-1]['bitwise_equal']:
                torch.save(observed, root/f'native-failed-{i}.pt')
                raise ValueError('Native reference changed on case '+str(i))
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
        if len(pairs) != 36 or any(set(pair) != {'v_proj', 'o_proj'} for pair in pairs.values()):
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
        conditions = [(kind, gauge) for kind in ['raw_v_off', 'raw_o_off'] for gauge in [.995, 1., 1.005]]
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
            condition.update(status='complete', mean_kl=sum(r['kl_reference_to_changed'] for r in rows)/64,
                mean_nll_delta=sum(r['nll_difference'] for r in rows)/64,
                mean_rms=sum(r['rms'] for r in rows)/64,
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
