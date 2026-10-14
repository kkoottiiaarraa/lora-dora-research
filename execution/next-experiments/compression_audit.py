#!/usr/bin/env python3
"""Bounded CPU FP32 pilot followed by the approved Qwen compression screen."""
import argparse
import csv
import datetime
import importlib.metadata
import json
import os
from pathlib import Path
import resource
import signal
import sys
import time

os.environ.update(CUDA_VISIBLE_DEVICES='', OMP_NUM_THREADS='4', MKL_NUM_THREADS='4',
                  OPENBLAS_NUM_THREADS='4', TOKENIZERS_PARALLELISM='false',
                  HF_HUB_OFFLINE='1', TRANSFORMERS_OFFLINE='1')
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from lora_dora_study.server import available_memory_bytes, write_json
from lora_dora_study.evaluation import sha256_file
from lora_dora_study.fidelity_audit import metrics
from lora_dora_study.rank_symmetry import effective_weight
from lora_dora_study.compression_audit import selected_modules, scoped_gauge, decompose, replacement, practical_gate


def main(args):
    args.output.mkdir(parents=True, exist_ok=False)
    start = time.monotonic()
    def deadline(signum, frame):raise TimeoutError('CPU screen budget exhausted')
    signal.signal(signal.SIGALRM, deadline)
    signal.setitimer(signal.ITIMER_REAL, args.budget_seconds)
    summary = dict(status='starting', timestamp_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        scope='Exploratory train-prefix compression screen; not benchmark accuracy or training',
        device='cpu', dtype='float32', cpu_threads=4, gpu_hours=0, full_evaluation=False,
        rank=32, scales=[1., .995, 1.005], conditions=[], stages=[], budget_seconds=args.budget_seconds,
        runner_sha256=sha256_file(Path(__file__)))
    def save():
        summary.update(wall_seconds=time.monotonic()-start,
                       max_process_rss_bytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024)
        write_json(args.output/'summary.json', summary)
    save()
    try:
        manifest = json.loads(args.manifest.read_text())
        for rel, expected in manifest['source_sha256'].items():
            if sha256_file(ROOT/rel) != expected:raise ValueError('Source changed: '+rel)
        summary['source_sha256'] = manifest['source_sha256']
        if available_memory_bytes() < 64*1024**3:
            raise BlockingIOError('Need 64 GiB available CPU RAM before loading')
        source = Path(manifest['source_audit'])
        prior = json.loads((source/'qwen-cpu/summary.json').read_text())
        for rel, expected in manifest['input_sha256'].items():
            if sha256_file(source/rel) != expected:raise ValueError('Input changed: '+rel)
        assert prior['status'] == 'complete' and prior['dtype'] == 'torch.float32'
        cases_path = source/'cases.json'
        assert sha256_file(cases_path) == prior['cases_sha256']
        cases = json.loads(cases_path.read_text())
        assert len(cases) == 64 and all(len(c['targets']) == 32 for c in cases)
        assert len({c['prompt_content_sha256'] for c in cases}) == 64
        summary['cases_sha256'] = sha256_file(cases_path)
        summary['reference_summary_sha256'] = sha256_file(source/'qwen-cpu/summary.json')
        summary['input_sha256'] = manifest['input_sha256']
        summary['artifacts'] = prior['artifacts']
        import torch
        from transformers import AutoModelForCausalLM
        from peft import PeftModel
        from lora_dora_study.adapters import verify_loaded_adapter
        torch.set_num_threads(4);torch.set_num_interop_threads(1);torch.manual_seed(20261013)
        torch.backends.cuda.matmul.allow_tf32 = False
        torch.backends.cudnn.allow_tf32 = False
        summary['versions'] = {k: importlib.metadata.version(k) for k in ['torch', 'transformers', 'peft', 'safetensors', 'accelerate']}
        if summary['versions'] != prior['versions']:raise ValueError('Reference software versions changed')
        paths = {k: v['snapshot_path'] for k, v in manifest['artifacts'].items()}
        if any({key: manifest['artifacts'][k][key] for key in ['repo_id', 'revision']} != prior['artifacts'][k] for k in prior['artifacts']):
            raise ValueError('Reference checkpoint revisions changed')
        t = time.monotonic()
        model = AutoModelForCausalLM.from_pretrained(paths['base'], local_files_only=True,
            trust_remote_code=False, torch_dtype=torch.float32, device_map={'': 'cpu'},
            low_cpu_mem_usage=True, attn_implementation='sdpa')
        model = PeftModel.from_pretrained(model, paths['dora'], local_files_only=True, is_trainable=False).eval()
        model.requires_grad_(False)
        valid = verify_loaded_adapter(model, paths['dora'], True)
        if not valid['exact_loaded_value_match'] or valid['adapted_module_count'] != 144:
            raise ValueError('Incomplete or mismatched loaded adapter')
        if model.config.num_hidden_layers != 36 or model.config.attention_bias:
            raise ValueError('Unexpected model configuration')
        if any(p.dtype != torch.float32 or p.device.type != 'cpu' for p in model.parameters()):
            raise ValueError('Unexpected parameter dtype or device')
        summary['load_seconds'] = time.monotonic()-t
        summary['adapter_exact_match'] = True
        cache = args.output/'logit-cache';cache.mkdir()
        comparisons, svd_cache = [], {}

        def logits(case):
            x = torch.tensor([case['input_ids']], dtype=torch.long)
            with torch.inference_mode():
                y = model(input_ids=x, attention_mask=torch.ones_like(x), use_cache=False,
                          logits_to_keep=len(case['targets'])).logits[0].detach().cpu()
            if not bool(y.isfinite().all()) or y.shape[0] != len(case['targets']):
                raise FloatingPointError('Nonfinite or misaligned logits')
            return y

        def cached(label, i):
            if label.endswith('/native_1.0'):label = 'original'
            if label == 'original':
                folder = cache if summary['reference_cache_policy'] == 'recomputed' else source/'qwen-cpu/logit-cache'
            else:folder = cache
            return torch.load(folder/f'{label}-{i}.pt', map_location='cpu', weights_only=True)

        exact = []
        for i in range(4):
            expected = torch.load(source/f'qwen-cpu/logit-cache/original-{i}.pt', map_location='cpu', weights_only=True)
            exact.append(torch.equal(logits(cases[i]), expected))
        summary['reference_first4_bitwise_equal'] = exact
        summary['reference_cache_policy'] = 'reused_same_versions_coefficients_inputs' if all(exact) else 'recomputed'
        if not all(exact):
            for i, case in enumerate(cases):torch.save(logits(case), cache/f'original-{i}.pt')
        save()

        def run(stage, condition, count, reference, store=False, extra_references=None, reuse_original=False):
            begin = time.monotonic()
            label = stage+'/'+condition
            record = dict(stage=stage, condition=condition, status='running', cases_completed=0, count=count,
                          execution='reused_validated_original_cache' if reuse_original else 'forward')
            summary['conditions'].append(record);save()
            for i, case in enumerate(cases[:count]):
                y = cached('original', i) if reuse_original else logits(case)
                if store and not reuse_original:
                    target = cache/f'{label}-{i}.pt';target.parent.mkdir(exist_ok=True)
                    torch.save(y, target)
                refs = dict(extra_references or {})
                refs[condition] = reference
                for metric_label, ref_label in refs.items():
                    row = dict(stage=stage, condition=metric_label, case=i, **metrics(cached(ref_label, i), y, case['targets']))
                    comparisons.append(row)
                    with (args.output/'per-case.jsonl').open('a') as f:f.write(json.dumps(row)+'\n')
                record.update(cases_completed=i+1, elapsed_seconds=time.monotonic()-begin)
                record['forecast_seconds_for_condition'] = record['elapsed_seconds']*count/(i+1)
                save()
            record.update(status='complete', elapsed_seconds=time.monotonic()-begin);save()

        def average(stage, condition):
            values = [r['rms'] for r in comparisons if r['stage'] == stage and r['condition'] == condition]
            if not values:raise ValueError('Missing comparison: '+condition)
            return sum(values)/len(values)

        def stage(name, layers, count):
            stage_start = time.monotonic()
            record = dict(stage=name, layers=layers, cases=count, status='running', technical_checks=[], practical_gates={})
            summary['stages'].append(record);save()
            baseline = name+'/compressed_1.0'
            for c in [1., .995, 1.005]:
                scale = str(c);native_label = 'native_'+scale
                with scoped_gauge(model, layers, c), torch.inference_mode():
                    run(name, native_label, count, 'original', store=True, reuse_original=c == 1.)
                    with replacement(model, layers, 'source_dense'):
                        run(name, 'dense_'+scale, count, name+'/'+native_label)
                    gauge_error = average(name, native_label)
                    dense_error = average(name, 'dense_'+scale)
                    floor = .01*prior['aggregates']['remove_d']['mean_rms']
                    if max(gauge_error, dense_error) > floor:
                        raise ValueError('Source gauge/dense FP32 fidelity failed before compression')
                    records = {}
                    for module_name, module in selected_modules(model, layers).items():
                        key = (module_name, c)
                        if key not in svd_cache:
                            begin = time.monotonic()
                            base, value = effective_weight(module)
                            decomposition = decompose(base, value, 32)
                            decomposition['info'].update(module=module_name, c=c, seconds=time.monotonic()-begin)
                            decomposition['info'].update(
                                source_adapter_rank=module.r['default'],
                                source_adapter_elements=sum(p.numel() for p in [module.lora_A['default'].weight,
                                    module.lora_B['default'].weight, module.lora_magnitude_vector['default'].weight]),
                                source_magnitude_elements=module.lora_magnitude_vector['default'].weight.numel(),
                                storage_caveat='Base shared conceptually; rank32 target mostly removes magnitudes versus native rank32 DoRA, not a large adapter-size reduction')
                            svd_cache[key] = decomposition
                            write_json(args.output/'spectra.json', [r['info'] for r in svd_cache.values()])
                        records[module_name] = svd_cache[key]
                    with replacement(model, layers, 'factorized', records):
                        extras = {'compressed_drift_'+scale: baseline} if c != 1. else None
                        run(name, 'compressed_'+scale, count, 'original', store=True, extra_references=extras)
                    with replacement(model, layers, 'compressed_dense', records):
                        run(name, 'dense_factor_check_'+scale, 4, name+'/compressed_'+scale)
                    factor_error = average(name, 'dense_factor_check_'+scale)
                    compression_effect = average(name, 'compressed_'+scale)
                    if factor_error > max(1e-5, .01*compression_effect):
                        raise ValueError('Factorized versus dense compression fidelity failed')
                    record['technical_checks'].append(dict(c=c, gauge_rms=gauge_error, source_dense_rms=dense_error,
                        factor_dense_rms=factor_error, passed=True))
                    if c != 1.:
                        record['practical_gates'][scale] = practical_gate(average(name, 'compressed_drift_'+scale),
                            gauge_error, average(name, 'compressed_1.0'))
                verify_loaded_adapter(model, paths['dora'], True)
                save()
            record.update(status='complete', wall_seconds=time.monotonic()-stage_start,
                          practical_screen_passed=any(v['passed'] for v in record['practical_gates'].values()))
            save()

        stage('pilot', [0], 4)
        summary['pilot_technical_passed'] = True;save()
        stage('screen', [0, 17, 35], 64)
        fields = list(comparisons[0])
        with (args.output/'metrics.csv').open('w') as stream:
            writer = csv.DictWriter(stream, fieldnames=fields);writer.writeheader();writer.writerows(comparisons)
        aggregates = []
        for stage_name, condition in sorted({(r['stage'], r['condition']) for r in comparisons}):
            rows = [r for r in comparisons if r['stage'] == stage_name and r['condition'] == condition]
            aggregates.append(dict(stage=stage_name, condition=condition, cases=len(rows), tokens=sum(r['tokens'] for r in rows),
                mean_rms=sum(r['rms'] for r in rows)/len(rows), mean_kl=sum(r['kl_reference_to_changed'] for r in rows)/len(rows),
                mean_nll_difference=sum(r['nll_difference'] for r in rows)/len(rows),
                max_abs=max(r['max_abs'] for r in rows), argmax_disagreements=sum(r['argmax_disagreements'] for r in rows)))
        summary.update(status='complete', aggregates=aggregates, svd_count=len(svd_cache),
            practical_screen_passed=summary['stages'][-1]['practical_screen_passed'],
            interpretation='Engineering effect-size screen only; no article-level novelty or heldout quality conclusion')
        save()
    except Exception as exc:
        summary.update(status='failed', error=repr(exc));save();raise
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--budget-seconds', type=int, default=14400)
    main(parser.parse_args())
