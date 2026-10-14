#!/usr/bin/env python3
"""A byte-matched storage baseline screen, reusing fixed CPU reference infrastructure."""
import argparse
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
    started = time.monotonic()
    summary = dict(status='running', phase='setup', conditions=[], gpu_count=0,
        training=False, started_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
    def save():
        summary.update(wall_seconds=time.monotonic()-started,
            rss_bytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024)
        write_json(root/'summary.json', summary)
    def timeout(signum, frame):
        raise TimeoutError('Byte-budget screen deadline')
    signal.signal(signal.SIGALRM, timeout)
    signal.setitimer(signal.ITIMER_REAL, 1800)
    save()
    try:
        manifest = json.loads((root/'manifest-private.json').read_text())
        for rel, digest in manifest['source_sha256'].items():
            if sha256_file(ROOT/rel) != digest:
                raise ValueError('Frozen source changed: '+rel)
        full = Path(manifest['full_root'])
        original = Path(json.loads((full/'manifest-private.json').read_text())['parent_root'])
        old = json.loads((original/'manifest-private.json').read_text())
        capture = json.loads((full/'capture/summary.json').read_text())
        affine = Path(manifest['affine_root'])
        prep = json.loads((affine/'prepare/frozen.json').read_text())
        if capture['status'] != 'complete' or len(capture['modules']) != 144:
            raise ValueError('Capture incomplete')
        if sha256_file(affine/'prepare/factors.pt') != prep['factors_sha256']:
            raise ValueError('Existing KFAC factors changed')
        calpath = Path(old['calibration_cases'])
        if sha256_file(calpath) != old['calibration_cases_sha256']:
            raise ValueError('Calibration changed')
        cal = json.loads(calpath.read_text())
        cases = cal[:8]
        if len(cases) != 8 or any(len(c['targets']) != 32 for c in cases):
            raise ValueError('Fixed case coverage')
        write_json(root/'cases.json', cases)
        import torch
        from safetensors.torch import save_file, load_file
        from transformers import AutoModelForCausalLM
        from peft import PeftModel
        from lora_dora_study.adapters import verify_loaded_adapter
        from lora_dora_study.adapter_storage import thin_factors, encode, decode, payload_bytes
        from lora_dora_study.full_compression import replace_all
        from lora_dora_study.fidelity_audit import metrics
        torch.set_num_threads(16)
        torch.set_num_interop_threads(1)
        torch.manual_seed(20261014)
        torch.set_float32_matmul_precision('highest')
        versions = {k: importlib.metadata.version(k) for k in old['versions']}
        if versions != old['versions']:
            raise ValueError('Versions changed')
        if available_memory_bytes() < 64*1024**3:
            raise BlockingIOError('Need64GiB available RAM')
        summary.update(versions=versions, cpu_threads=16, source_sha256=manifest['source_sha256'],
            artifacts={k:{j:v[j] for j in ('repo_id','revision')} for k,v in old['artifacts'].items()},
            payload_budget_bytes=23592960, new_method=False)
        all_factors = torch.load(affine/'prepare/factors.pt', map_location='cpu', weights_only=True)
        factors = dict(kfac_fp32_r8=all_factors['kfac_uniform'])
        del all_factors
        packed = {'structural_fp16_r15':{}, 'structural_int8_r30':{}}
        native = {}
        for index, item in enumerate(capture['modules']):
            path = full/'capture'/item['file']
            if sha256_file(path) != item['sha256']:
                raise ValueError('Source capture changed')
            data = torch.load(path, map_location='cpu', weights_only=True)
            name = item['name']
            source_left = (data['row_scale'][:,None]*data['b'])*data['scaling']
            source_right = data['a']
            native[name] = dict(left=source_left.contiguous(), right=source_right.contiguous(),
                                row_scale=data['row_scale'].clone())
            # SVD of the same effective branch, independently truncated at the fixed ranks.
            l30, r30 = thin_factors(source_left, source_right, 30)
            packed['structural_int8_r30'][name] = encode(l30, r30, data['row_scale'], 'int8')
            packed['structural_fp16_r15'][name] = encode(l30[:,:15], r30[:15], data['row_scale'], 'fp16')
            summary.update(phase='encode', modules_completed=index+1)
            save()
            del data
        if any(len(records) != 144 for records in packed.values()):
            raise ValueError('Storage coverage')
        storage = {'kfac_fp32_r8':dict(payload_bytes=payload_bytes(factors['kfac_fp32_r8']), rank=8)}
        for label, records in packed.items():
            tensors = {name+'.'+key:t for name, rec in records.items() for key,t in rec.items()}
            archive = root/(label+'.safetensors')
            save_file(tensors, str(archive))
            config = root/(label+'.json')
            write_json(config, dict(format='fixed_D_plus_LR_v1', base_unchanged=True,
                rank=15 if 'fp16' in label else 30, storage_mode='fp16' if 'fp16' in label else 'int8',
                quantization='symmetric_RTN_latent_components' if 'int8' in label else None,
                execution='decode_to_FP32; no low-bit runtime claim'))
            reread = load_file(str(archive), device='cpu')
            if set(reread) != set(tensors) or any(not torch.equal(reread[k],v) for k,v in tensors.items()):
                raise ValueError('Serialized tensor roundtrip changed')
            decoded = {}
            for name, rec in records.items():
                decoded[name] = decode({k:reread[name+'.'+k] for k in rec})
            factors[label] = decoded
            entry = dict(payload_bytes=payload_bytes(records), archive_bytes=archive.stat().st_size,
                config_bytes=config.stat().st_size, sha256=sha256_file(archive),
                config_sha256=sha256_file(config), tensor_count=len(tensors),
                dtypes=sorted({str(t.dtype) for t in tensors.values()}))
            entry['total_file_bytes'] = entry['archive_bytes']+entry['config_bytes']
            if entry['payload_bytes'] > 23592960 or entry['total_file_bytes'] > 23592960:
                raise ValueError('Byte budget exceeded')
            storage[label] = entry
        if storage['kfac_fp32_r8']['payload_bytes'] != 23592960:
            raise ValueError('Reference storage changed')
        write_json(root/'storage.json', storage)
        write_json(root/'frozen.json', dict(cases_sha256=sha256_file(root/'cases.json'),
            source_sha256=manifest['source_sha256'], storage=storage,
            before_new_outputs=True, exploration_only=True))
        summary['frozen_sha256'] = sha256_file(root/'frozen.json')
        summary.update(phase='load', storage=storage)
        save()
        model = AutoModelForCausalLM.from_pretrained(old['artifacts']['base']['snapshot_path'],
            local_files_only=True, trust_remote_code=False, torch_dtype=torch.float32,
            device_map={'':'cpu'}, low_cpu_mem_usage=True, attn_implementation='sdpa')
        model = PeftModel.from_pretrained(model, old['artifacts']['dora']['snapshot_path'],
            local_files_only=True, is_trainable=False).eval()
        model.requires_grad_(False)
        check = verify_loaded_adapter(model, old['artifacts']['dora']['snapshot_path'], True)
        if not check['exact_loaded_value_match'] or check['adapted_module_count'] != 144:
            raise ValueError('Adapter mismatch')
        if any(p.dtype != torch.float32 or p.device.type != 'cpu' for p in model.parameters()):
            raise ValueError('Execution mode changed')
        summary['adapter_exact'] = True
        def logits(case):
            ids = torch.tensor([case['input_ids']], dtype=torch.long)
            with torch.inference_mode():
                y = model(input_ids=ids, attention_mask=torch.ones_like(ids), use_cache=False,
                    logits_to_keep=32).logits[0].detach().cpu()
            if y.shape[0] != 32 or not bool(y.isfinite().all()):
                raise FloatingPointError('Invalid logits')
            return y
        references = []
        native_checks = []
        for i, case in enumerate(cases):
            y = logits(case)
            references.append(y)
            if i < 4:
                old_y = torch.load(original/'capture/logit-cache'/f'original-{i}.pt',
                    map_location='cpu', weights_only=True)
                native_checks.append(dict(case=i, bitwise_equal=torch.equal(y, old_y),
                    **metrics(old_y, y, case['targets'])))
                write_json(root/'native-checks.json', native_checks)
                if not torch.equal(y, old_y):
                    raise ValueError('Native source reference changed')
        controls = []
        with replace_all(model, native):
            for i, case in enumerate(cases[:4]):
                controls.append(dict(case=i, **metrics(references[i], logits(case), case['targets'])))
        write_json(root/'controls.json', controls)
        floor = max(r['rms'] for r in controls)
        for label, records in factors.items():
            condition = dict(label=label, status='running', cases_completed=0)
            summary['conditions'].append(condition)
            summary['phase'] = 'conditions'
            save()
            rows = []
            with replace_all(model, records):
                for i, case in enumerate(cases):
                    row = dict(label=label, case=i, **metrics(references[i], logits(case), case['targets']))
                    with (root/'per-case.jsonl').open('a') as stream:
                        stream.write(json.dumps(row)+'\n')
                    rows.append(row)
                    condition['cases_completed'] = i+1
                    save()
            condition.update(status='complete', mean_kl=sum(r['kl_reference_to_changed'] for r in rows)/8,
                mean_nll_delta=sum(r['nll_difference'] for r in rows)/8,
                mean_rms=sum(r['rms'] for r in rows)/8,
                argmax_disagreements=sum(r['argmax_disagreements'] for r in rows))
            save()
        if floor >= .01*min(c['mean_rms'] for c in summary['conditions']):
            raise ValueError('Control floor exceeds1%effect')
        if not torch.equal(logits(cases[0]), references[0]):
            raise ValueError('Source not restored')
        baseline = summary['conditions'][0]['mean_kl']
        improvements = {c['label']:1-c['mean_kl']/baseline for c in summary['conditions'][1:]}
        summary.update(status='complete', phase='complete', controls_max_rms=floor,
            improvements_vs_fp32_kfac=improvements, byte_frontier_gate=any(v >= .2 for v in improvements.values()),
            full_task_accuracy=False, conference_level_established=False)
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
    main(parser.parse_args().root)
