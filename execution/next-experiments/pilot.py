#!/usr/bin/env python3
"""One explicitly selected GPU, bounded pilot or separately authorized evaluation.

No scheduler, idle wait, GPU lease, downloads, or background continuation. The
default is a technical timing pilot, never a quality or full calibration claim.
"""
import argparse
import contextlib
import datetime
import hashlib
import importlib.metadata
import json
import math
import os
from pathlib import Path
import re
import resource
import signal
import sys
import threading
import time

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from lora_dora_study.benchmarks import score, user_content
from lora_dora_study.evaluation import sha256_file
from lora_dora_study.server import available_memory_bytes, gpu_snapshot, write_json


def reject_nonfinite_generation_scores(input_ids, scores):
    # Validate on CPU: diagnostics found unreliable device contents.
    if not bool(scores.detach().float().cpu().isfinite().all().item()):
        raise FloatingPointError("Nonfinite generation scores; stop instead of decoding invalid token 0")
    return scores


def arguments(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--gpu-uuid', required=True)
    p.add_argument('--task', choices=['gsm8k', 'mmlu', 'squadv2'], required=True)
    p.add_argument('--mode', choices=['controls', 'remove_d', 'nll'], required=True)
    p.add_argument('--condition', choices=['original', 'permuted', 'directional', 'remove_d', 'base', 'lora', 'dora'])
    p.add_argument('--output-dir', type=Path, required=True)
    p.add_argument('--stage', choices=['pilot', 'evaluate'], default='pilot')
    p.add_argument('--evaluation-authorized', action='store_true', help='Explicit future full-run authorization; never set for a pilot')
    p.add_argument('--budget-seconds', type=int)
    p.add_argument('--downloads', type=Path)
    p.add_argument('--dataset-manifest', type=Path)
    p.add_argument('--calibration-jsonl', type=Path)
    p.add_argument('--reference-predictions', type=Path)
    p.add_argument('--calibration-train', type=int)
    p.add_argument('--calibration-validation', type=int)
    p.add_argument('--seed', type=int, default=1729)
    p.add_argument('--pilot-cases', type=int, default=6)
    p.add_argument('--pilot-new-tokens', type=int, choices=[32, 64], default=32)
    p.add_argument('--timing-points', help='Forced counts <=128, same prompts; controls default 16,64,128, B default none')
    p.add_argument('--minimum-free-mib', type=int, default=8600)
    p.add_argument('--baseline-seconds', type=float, default=15)
    p.add_argument('--nll-segments', type=Path, help='JSON containing fixed segments and metadata, prepared on CPU')
    p.add_argument('--nll-pilot-segments', type=int, default=8)
    a = p.parse_args(argv)
    if not re.fullmatch(r'GPU-[A-Za-z0-9-]+', a.gpu_uuid):
        p.error('An explicit GPU UUID is required')
    if a.stage == 'evaluate' and (not a.evaluation_authorized or a.budget_seconds is None):
        p.error('Evaluation needs --evaluation-authorized and an explicit --budget-seconds')
    a.budget_seconds = a.budget_seconds or 900
    if not 1 <= a.budget_seconds <= (900 if a.stage == 'pilot' else 96*3600):
        p.error('Pilot budget must be <=900 seconds; evaluation budget <=96 GPU hours')
    if a.minimum_free_mib < 8600 or a.baseline_seconds < 15:
        p.error('Resource guard requires >=8600 MiB free and >=15 seconds baseline')
    a.calibration_train = a.calibration_train or (16 if a.stage == 'pilot' else 200)
    a.calibration_validation = a.calibration_validation or (8 if a.stage == 'pilot' else 32)
    if min(a.calibration_train, a.calibration_validation, a.pilot_cases) < 1:
        p.error('Sample counts must be positive')
    if a.stage == 'pilot' and (a.pilot_cases > 12 or a.calibration_train > 32 or a.calibration_validation > 16):
        p.error('Pilot caps: 12 generation cases, 32 calibration train, 16 validation')
    if a.stage == 'evaluate' and a.mode == 'controls' and (a.calibration_train < 200 or a.calibration_validation < 32):
        p.error('Full controls require >=200 train and >=32 disjoint validation calibration cases')
    a.condition = a.condition or {'controls': 'permuted', 'remove_d': 'remove_d', 'nll': 'dora'}[a.mode]
    allowed = {'controls': {'original', 'permuted', 'directional'}, 'remove_d': {'original', 'remove_d'}, 'nll': {'base', 'lora', 'dora', 'remove_d'}}
    if a.condition not in allowed[a.mode]:
        p.error('Condition does not belong to selected mode')
    if a.mode == 'controls' and not a.calibration_jsonl:
        if a.task != 'gsm8k':
            p.error('Non-GSM8K controls require explicit task training --calibration-jsonl')
        a.calibration_jsonl = ROOT/'datasets/gsm8k-train-calibration.jsonl'
    if a.mode == 'nll' and not a.nll_segments:
        p.error('NLL needs a fixed, previously prepared --nll-segments artifact')
    if not 1 <= a.nll_pilot_segments <= 16:
        p.error('NLL pilot needs 1..16 segments')
    a.timing_points = a.timing_points or ('16,64,128' if a.mode == 'controls' else 'none')
    try:
        a.timing_points = [] if a.timing_points == 'none' else [int(x) for x in a.timing_points.split(',')]
    except ValueError:
        p.error('Invalid timing points')
    if len(a.timing_points) > 3 or any(x < 1 or x > 128 for x in a.timing_points):
        p.error('At most three forced timing points, each <=128 tokens')
    a.downloads = a.downloads or ROOT/f'results/shadow_4b_{a.task}-downloads.json'
    a.dataset_manifest = a.dataset_manifest or ROOT/f'results/{a.task}-dataset.json'
    return a


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def read_rows(path):
    # JSONL uses literal LF records. Unicode U+2028/U+2029 can occur inside
    # valid JSON strings and must not be treated as record boundaries.
    return [json.loads(line) for line in Path(path).read_text().split('\n') if line]


def balanced_indices(lengths, count, response_lengths=None):
    """Deterministic prompt thirds; response-length halves within each if known."""
    if not lengths or count < 1:
        raise ValueError('Empty lengths or invalid sample count')
    order = sorted(range(len(lengths)), key=lambda i: (lengths[i], i))
    groups = [order[len(order)*q//3:len(order)*(q+1)//3] for q in range(3)]
    bins = []
    for group in groups:
        if response_lengths and all(i in response_lengths for i in group):
            group = sorted(group, key=lambda i: (response_lengths[i], i))
            bins.extend([group[:len(group)//2], group[len(group)//2:]])
        else:
            bins.append(group)
    chosen = []
    for round_index in range(max(len(lengths), count)):
        for group in bins:
            if not group:
                continue
            # Median first, then alternate towards each tail within each bin.
            candidates = [i for _, i in sorted(enumerate(group), key=lambda item: (abs(item[0]-(len(group)-1)/2), item[1]))]
            if round_index < len(candidates):
                chosen.append(candidates[round_index])
                if len(chosen) >= min(count, len(lengths)):
                    return chosen
    return chosen


def forecast(cases, lengths, response_lengths, full_token_limit):
    """Sensitivity scenarios, not an ETA fit: cache-free sequence cost grows."""
    def work(prompt, generated, power):
        return sum((prompt+step)**power for step in range(generated))
    measured = [c for c in cases if c['generated_tokens'] > 0 and not c.get('warmup')]
    if not measured:
        return {'available': False}
    result = {}
    for label, power in [('per_token_constant', 0), ('sequence_linear', 1), ('attention_quadratic', 2)]:
        rates = sorted(c['seconds']/work(c['input_tokens'], c['generated_tokens'], power) for c in measured)
        total_work = sum(work(min(length, 512), min(response_lengths.get(i, full_token_limit), full_token_limit), power) for i, length in enumerate(lengths))
        result[label] = dict(low_seconds=rates[0]*total_work, median_seconds=rates[len(rates)//2]*total_work, high_seconds=rates[-1]*total_work)
    return dict(available=True, scenarios=result, original_response_lengths_known=len(response_lengths),
                unknown_lengths_assumed=full_token_limit, full_dataset_cases=len(lengths),
                caveat='Timing sensitivity scenarios, not confidence intervals. use_cache=False recomputes growing full sequences; shared-GPU contention may change.')


def answerability_metrics(cases):
    result = {}
    for label, desired in [('answerable', True), ('unanswerable', False)]:
        subset = [case for case in cases if case['answerable'] == desired]
        if subset:
            result[label] = dict(count=len(subset), **{key: sum(c['metrics'][key] for c in subset)/len(subset) for key in ('exact', 'f1')})
    return result


class ResourceSampler:
    def __init__(self, path, uuid):
        self.path, self.uuid = path, uuid
        self.stop_event = threading.Event()
        self.error = None
        self.thread = threading.Thread(target=self.run, daemon=True)

    def sample(self):
        snapshot = gpu_snapshot()
        gpu = next(g for g in snapshot['gpus'] if g['uuid'] == self.uuid)
        processes = [p for p in snapshot['compute_processes'] if p['gpu_uuid'] == self.uuid]
        return dict(timestamp_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                    monotonic=time.monotonic(), gpu=gpu, processes=processes,
                    other_processes=[p for p in processes if p['pid'] != os.getpid()],
                    available_host_ram_bytes=available_memory_bytes())

    def run(self):
        with self.path.open('x') as output:
            while not self.stop_event.is_set():
                try:
                    row = self.sample()
                except Exception as error:
                    self.error = str(error)
                    row = dict(monotonic=time.monotonic(), error=self.error)
                output.write(json.dumps(row)+'\n')
                output.flush()
                self.stop_event.wait(2)

    def close(self):
        self.stop_event.set()
        if self.thread.ident is not None:
            self.thread.join(timeout=22)


def main(argv=None):
    a = arguments(argv)
    a.output_dir.mkdir(parents=True, exist_ok=False)
    report = dict(status='starting', stage=a.stage, full_evaluation=False, task=a.task,
                  mode=a.mode, condition=a.condition, gpu_uuid=a.gpu_uuid,
                  budget_seconds=a.budget_seconds, timestamp_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                  runner_sha256=sha256_file(Path(__file__)), seed=a.seed,
                  scope='Posthoc checkpoint intervention; no training-mechanism claim',
                  resource_policy='Explicitly authorized shared GPU; no waiting, lease, reservation, or process changes')
    report['source_sha256'] = {str(path.relative_to(ROOT)): sha256_file(path) for path in
        [ROOT/'scripts/series_worker.py', ROOT/'lora_dora_study/benchmarks.py', ROOT/'lora_dora_study/interventions.py',
         ROOT/'lora_dora_study/adapters.py', ROOT/'lora_dora_study/matched_controls.py', ROOT/'lora_dora_study/text_nll.py'] if path.exists()}
    summary = a.output_dir/'summary.json'
    write_json(summary, report)
    sampler = ResourceSampler(a.output_dir/'resources.jsonl', a.gpu_uuid)
    started = time.monotonic()

    def timeout_handler(signum, frame):
        raise TimeoutError('Explicit wall-clock budget exhausted')

    signal.signal(signal.SIGALRM, timeout_handler)
    signal.setitimer(signal.ITIMER_REAL, a.budget_seconds)

    def remaining():
        if time.monotonic()-started >= a.budget_seconds:
            raise TimeoutError('Explicit wall-clock budget exhausted')

    try:
        # Parse/verify CPU artifacts before paying GPU model-load costs.
        downloads = json.loads(a.downloads.read_text())
        paths = {role: item['snapshot_path'] for role, item in downloads['artifacts'].items()}
        if a.mode == 'nll':
            corpus = json.loads(a.nll_segments.read_text())
        else:
            manifest = json.loads(a.dataset_manifest.read_text())
            if manifest['max_input_tokens'] != 512 or sha256_file(manifest['path']) != manifest['jsonl_sha256']:
                raise ValueError('Dataset manifest/token cap/checksum mismatch')
            rows = read_rows(manifest['path'])
            if len(rows) != manifest['rows']:
                raise ValueError('Dataset row count mismatch')
            reference_rows = read_rows(a.reference_predictions) if a.reference_predictions else []
            if a.mode == 'controls':
                calibration_rows = read_rows(a.calibration_jsonl)
        sampler.thread.start()
        # No Torch imports until baseline and a fresh free-memory check pass.
        time.sleep(a.baseline_seconds)
        snapshot = sampler.sample()
        free = snapshot['gpu']['total_mib']-snapshot['gpu']['used_mib']
        ram = snapshot['available_host_ram_bytes']
        report['preload_resources'] = snapshot
        if sampler.error or free < a.minimum_free_mib or ram is None or ram < 12*1024**3:
            raise BlockingIOError('Fresh GPU free-memory / host RAM guard refused before Torch import')
        os.environ.update(CUDA_VISIBLE_DEVICES=a.gpu_uuid, OMP_NUM_THREADS='2', MKL_NUM_THREADS='2',
                          TOKENIZERS_PARALLELISM='false', HF_HUB_OFFLINE='1', TRANSFORMERS_OFFLINE='1')
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer, GenerationConfig
        from peft import PeftModel
        from lora_dora_study.adapters import verify_loaded_adapter
        from lora_dora_study.interventions import apply_intervention
        torch.set_num_threads(2)
        torch.set_num_interop_threads(1)
        torch.manual_seed(42)
        if not torch.cuda.is_bf16_supported():
            raise RuntimeError('BF16 required')
        torch.cuda.reset_peak_memory_stats()
        report['versions'] = {name: importlib.metadata.version(name) for name in ['torch', 'transformers', 'peft', 'safetensors', 'accelerate']}

        def timed(operation):
            remaining()
            torch.cuda.synchronize()
            begin = time.perf_counter()
            value = operation()
            torch.cuda.synchronize()
            return value, time.perf_counter()-begin

        def memory():
            return dict(peak_allocated_bytes=torch.cuda.max_memory_allocated(), peak_reserved_bytes=torch.cuda.max_memory_reserved(),
                        max_process_rss_bytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024,
                        available_host_ram_bytes=available_memory_bytes())

        report.update(artifacts=downloads['artifacts'], downloads_sha256=sha256_file(a.downloads), download_seconds=0,
                      download_note='Uses existing pinned snapshots; no downloads performed')
        tokenizer, report['tokenizer_load_seconds'] = timed(lambda: AutoTokenizer.from_pretrained(paths['base'], local_files_only=True, trust_remote_code=False))
        model, report['base_load_seconds'] = timed(lambda: AutoModelForCausalLM.from_pretrained(paths['base'], local_files_only=True,
            trust_remote_code=False, torch_dtype=torch.bfloat16, device_map={'': 'cuda:0'}, low_cpu_mem_usage=True, attn_implementation='sdpa'))
        role = a.condition if a.mode == 'nll' and a.condition in {'base', 'lora', 'dora'} else 'dora'
        if role != 'base':
            model, report['adapter_load_seconds'] = timed(lambda: PeftModel.from_pretrained(model, paths[role], local_files_only=True, is_trainable=False))
            report['adapter_validation'] = verify_loaded_adapter(model, paths[role], role == 'dora')
        model.eval()
        report['load_memory'] = memory()

        def inputs(ids):
            return dict(input_ids=torch.tensor([ids], device='cuda:0'), attention_mask=torch.ones((1, len(ids)), device='cuda:0', dtype=torch.long))

        def encode(row):
            prompt = tokenizer.apply_chat_template([dict(role='user', content=user_content(a.task, row))], tokenize=False,
                                                   add_generation_prompt=True, enable_thinking=False)
            ids = tokenizer(prompt, add_special_tokens=False)['input_ids']
            return dict(prompt_sha256=hashlib.sha256(prompt.encode()).hexdigest(), ids=ids[:512], original_input_tokens=len(ids))

        def forward(encoded):
            with torch.inference_mode(), torch.autocast(device_type='cuda', dtype=torch.bfloat16):
                return model(**inputs(encoded['ids']), use_cache=False).logits

        intervention = contextlib.nullcontext()
        if a.condition == 'remove_d':
            report['intervention'], report['intervention_seconds'] = timed(lambda: apply_intervention(model, 'remove_d', {'q_proj', 'k_proj', 'v_proj', 'o_proj'}))

        if a.mode == 'nll':
            from lora_dora_study.text_nll import evaluate_text_nll
            segments = corpus['segments']
            corpus_hash = hashlib.sha256(json.dumps(segments, separators=(',', ':')).encode()).hexdigest()
            if (corpus['metadata']['segment_count'] != len(segments) or
                    corpus['metadata']['token_segments_sha256'] != corpus_hash or
                    not 1 <= len(segments) <= 1024 or any(len(s) != 256 for s in segments)):
                raise ValueError('Fixed NLL corpus metadata/hash/shape mismatch')
            if a.stage == 'pilot':
                segments = segments[:a.nll_pilot_segments]
            report.update(corpus_metadata=corpus['metadata'], corpus_file_sha256=sha256_file(a.nll_segments), actual_segments_sha256=digest(segments), status='running')
            write_json(summary, report)
            with torch.autocast(device_type='cuda', dtype=torch.bfloat16):
                report['nll'] = evaluate_text_nll(model, segments, device='cuda:0', warmup_segments=1)
            report['full_evaluation'] = a.stage == 'evaluate'
            report['nll_full_corpus_segment_count'] = len(corpus['segments'])
            report['nll_forecast_seconds'] = report['nll']['elapsed_seconds']*len(corpus['segments'])/len(segments)
        else:
            encoded = [encode(row) for row in rows]
            response_lengths = {}
            if a.reference_predictions:
                for row in reference_rows:
                    index = int(row['test_row_index'])
                    if (not 0 <= index < len(rows) or row['input_ids_sha256'] != digest(encoded[index]['ids']) or
                            row['prompt_sha256'] != encoded[index]['prompt_sha256']):
                        raise ValueError('Accepted reference predictions differ in dataset/prompt/input token protocol')
                    response_lengths[index] = int(row['generated_tokens'])
                report['reference_predictions_sha256'] = sha256_file(a.reference_predictions)
            lengths = [x['original_input_tokens'] for x in encoded]
            indices = list(range(len(rows))) if a.stage == 'evaluate' else balanced_indices(lengths, a.pilot_cases, response_lengths)
            report.update(dataset=manifest, dataset_manifest_sha256=sha256_file(a.dataset_manifest), selected_indices=indices,
                          protocol=dict(do_sample=False, num_beams=1, use_cache=False, max_input_tokens=512, bf16_autocast=True,
                                        task_max_new_tokens=manifest['max_new_tokens'], batch_size=1))
            if a.mode == 'controls':
                from lora_dora_study.matched_controls import MatchedControls
                needed = a.calibration_train+a.calibration_validation
                if len(calibration_rows) < needed:
                    raise ValueError(f'Need {needed} distinct train calibration rows; only {len(calibration_rows)} available')
                calibration_rows = calibration_rows[:needed]
                # Check content rather than source IDs, which can overlap across splits.
                content = [digest(user_content(a.task, row)) for row in calibration_rows]
                test_content = {digest(user_content(a.task, row)) for row in rows}
                if len(set(content)) != needed or any(x in test_content for x in content):
                    raise ValueError('Calibration train/validation/test content overlap')
                calibration_inputs = [encode(row) for row in calibration_rows]
                controls, report['control_setup_seconds'] = timed(lambda: MatchedControls(model, seed=a.seed))
                reference, report['reference_forward_seconds'] = timed(lambda: forward(calibration_inputs[0]))
                zeros = {name: 0.0 for name in controls.modules}
                with controls.intervene('permuted', zeros):
                    hooked, elapsed = timed(lambda: forward(calibration_inputs[0]))
                report['zero_hook_fidelity'] = dict(exact_equal=bool(torch.equal(reference, hooked)),
                    max_abs_error=float((reference.float()-hooked.float()).abs().max()), seconds=elapsed)
                del reference, hooked
                if not report['zero_hook_fidelity']['exact_equal']:
                    raise ValueError('Zero intervention changed native reference logits')
                def calibrate():
                    with controls.calibrate() as cal:
                        for item in calibration_inputs[:a.calibration_train]:
                            remaining()
                            del_logits = forward(item)
                            del del_logits
                    return cal.report()
                calibration, report['calibration_train_seconds'] = timed(calibrate)
                # Correct realized BF16 perturbation strength using TRAIN inputs only.
                def refine():
                    with controls.calibrate(scales={k: dict(v) for k, v in calibration['scales'].items()}) as observed:
                        for item in calibration_inputs[:a.calibration_train]:
                            remaining()
                            logits = forward(item)
                            del logits
                    return observed.report()
                refinement, report['calibration_refinement_seconds'] = timed(refine)
                for kind, scales in calibration['scales'].items():
                    for name, scale in scales.items():
                        stats = refinement['modules'][name]
                        target, realized = stats['native_remove'], stats['realized'][kind]
                        if not math.isfinite(realized) or realized <= 0 or not math.isfinite(target):
                            raise ValueError('Invalid realized calibration energy')
                        scales[name] = scale * math.sqrt(target / realized)
                def validate():
                    with controls.calibrate(scales=calibration['scales']) as val:
                        for item in calibration_inputs[a.calibration_train:]:
                            remaining()
                            del_logits = forward(item)
                            del del_logits
                    return val.report()
                validation, report['calibration_validation_seconds'] = timed(validate)
                write_json(a.output_dir/'calibration.json', dict(train=calibration, refinement=refinement, validation=validation,
                    source_sha256=sha256_file(a.calibration_jsonl), train_count=a.calibration_train, validation_count=a.calibration_validation,
                    train_content_sha256=digest(content[:a.calibration_train]), validation_content_sha256=digest(content[a.calibration_train:]),
                    full_calibration=a.stage == 'evaluate', insufficiency='16/8 technical pilot is insufficient for full calibration transfer claims' if a.stage == 'pilot' else None))
                if a.condition != 'original':
                    intervention = controls.intervene(a.condition, calibration['scales'][a.condition])
            generation = GenerationConfig(do_sample=False, num_beams=1, use_cache=False,
                pad_token_id=tokenizer.pad_token_id if tokenizer.pad_token_id is not None else tokenizer.eos_token_id,
                eos_token_id=tokenizer.eos_token_id, bos_token_id=tokenizer.bos_token_id)
            report.update(status='running', generation_config=generation.to_dict())
            write_json(summary, report)
            cases, timing_cases = [], []
            def generate(index, token_limit, forced=False, warmup=False):
                item = encoded[index]
                kwargs = dict(max_new_tokens=token_limit)
                if forced:
                    kwargs['min_new_tokens'] = token_limit
                def operation():
                    with torch.inference_mode(), torch.autocast(device_type='cuda', dtype=torch.bfloat16):
                        return model.generate(**inputs(item['ids']), generation_config=generation, use_model_defaults=False, do_sample=False, logits_processor=[reject_nonfinite_generation_scores], **kwargs)
                generated, seconds = timed(operation)
                tokens = generated[0, len(item['ids']):]
                text = tokenizer.decode(tokens, skip_special_tokens=True)
                return dict(test_row_index=index, source_id=rows[index].get('id', index), input_tokens=len(item['ids']),
                    original_input_tokens=item['original_input_tokens'], prompt_truncated=item['original_input_tokens'] > len(item['ids']),
                    generated_tokens=len(tokens), seconds=seconds, token_limit=token_limit, forced_tokens=forced, warmup=warmup,
                    original_generated_tokens=response_lengths.get(index), input_ids_sha256=digest(item['ids']), prompt_sha256=item['prompt_sha256'],
                    text=text, metrics=score(a.task, text, rows[index]), answerable=bool(rows[index].get('answers', {}).get('text')) if a.task == 'squadv2' else None)
            with intervention:
                report['warmup'] = generate(indices[0], 2, warmup=True)
                write_json(summary, report)
                with (a.output_dir/'predictions.jsonl').open('x') as output:
                    for index in indices:
                        token_limit = manifest['max_new_tokens'] if a.stage == 'evaluate' else min(a.pilot_new_tokens, manifest['max_new_tokens'])
                        case = generate(index, token_limit)
                        cases.append(case)
                        output.write(json.dumps(case, ensure_ascii=False)+'\n'); output.flush()
                        report.update(predictions_completed=len(cases), inference_seconds=sum(x['seconds'] for x in cases), memory=memory())
                        write_json(summary, report)
                if a.stage == 'pilot':
                    quantile_indices = balanced_indices(lengths, 3)
                    with (a.output_dir/'length-timing.jsonl').open('x') as output:
                        for index in quantile_indices:
                            for token_limit in a.timing_points:
                                case = generate(index, token_limit, forced=True)
                                timing_cases.append(case)
                                output.write(json.dumps(case, ensure_ascii=False)+'\n'); output.flush()
            report['full_evaluation'] = a.stage == 'evaluate' and len(cases) == len(rows)
            report['metrics'] = {key: sum(c['metrics'][key] for c in cases)/len(cases) for key in cases[0]['metrics']}
            if a.task == 'squadv2':
                report['answerability_metrics'] = answerability_metrics(cases)
            report['quality_scope'] = 'Full frozen-protocol test evaluation' if report['full_evaluation'] else 'Technical pilot only; sample metrics do not estimate full quality'
            if a.stage == 'pilot':
                report['forecast'] = forecast(cases+timing_cases, lengths, response_lengths, manifest['max_new_tokens'])
        report.update(status='complete', memory=memory())
        return_code = 0
    except BaseException as error:
        status = 'guard_refused' if isinstance(error, BlockingIOError) else ('budget_exhausted' if isinstance(error, TimeoutError) else 'failed_needs_inspection')
        if 'out of memory' in str(error).lower():
            status = 'oom_clean_exit'
        report.update(status=status, error_type=type(error).__name__, error=str(error), full_evaluation=False)
        return_code = 75 if status == 'guard_refused' else 1
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        sampler.close()
        report.update(wall_seconds=time.monotonic()-started, resource_sampler_error=sampler.error)
        write_json(summary, report)
    return return_code


if __name__ == '__main__':
    sys.exit(main())
