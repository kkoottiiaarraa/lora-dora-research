#!/usr/bin/env python3
"""Bounded CPU screen reusing frozen factors; no new SVD, training or GPU use."""
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

os.environ.update(CUDA_VISIBLE_DEVICES='', OMP_NUM_THREADS='4', MKL_NUM_THREADS='4',
                  OPENBLAS_NUM_THREADS='4', HF_HUB_OFFLINE='1', TRANSFORMERS_OFFLINE='1',
                  TOKENIZERS_PARALLELISM='false')
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from lora_dora_study.evaluation import sha256_file
from lora_dora_study.server import write_json, available_memory_bytes


def main(root, phase):
    start = time.monotonic()
    out = root / phase
    out.mkdir(exist_ok=False)
    status = dict(status='running', phase=phase, training=False, gpu_count=0,
                  started_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(), conditions=[])

    def save():
        status.update(wall_seconds=time.monotonic()-start,
                      rss_bytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024)
        write_json(out/'summary.json', status)

    def deadline(signum, frame): raise TimeoutError('Bounded budget screen exhausted')
    signal.signal(signal.SIGALRM, deadline)
    signal.setitimer(signal.ITIMER_REAL, 600 if phase == 'prepare' else 3600)
    save()
    try:
        m = json.loads((root/'manifest-private.json').read_text())
        parent = Path(m['parent_root'])
        previous = json.loads((parent/'manifest-private.json').read_text())
        for rel, digest in m['source_sha256'].items():
            if sha256_file(ROOT/rel) != digest: raise ValueError('Frozen source changed: '+rel)
        import torch
        torch.set_num_threads(4 if phase == 'prepare' else 16)
        torch.set_num_interop_threads(1)
        torch.manual_seed(20261013)
        torch.set_float32_matmul_precision('highest')
        versions = {k: importlib.metadata.version(k) for k in previous['versions']}
        if versions != previous['versions']: raise ValueError('Software changed')
        status.update(versions=versions, cpu_threads=torch.get_num_threads(), source_sha256=m['source_sha256'])
        from lora_dora_study.compression_audit import selected_modules, replacement, scoped_gauge
        from lora_dora_study.fidelity_audit import metrics, content_digest
        from lora_dora_study.rank_budget import allocate
        layers = [0, 17, 35]
        if phase == 'prepare':
            if available_memory_bytes() < 8*1024**3: raise BlockingIOError('Need 8GiB for caches')
            prepared = json.loads((parent/'prepare/summary.json').read_text())
            capture = json.loads((parent/'capture/summary.json').read_text())
            if prepared['status'] != 'complete' or capture['status'] != 'complete':
                raise ValueError('Parent incomplete')
            if sha256_file(parent/'prepare/factors.pt') != prepared['factors_sha256']:
                raise ValueError('Frozen factors changed')
            if sha256_file(parent/'capture/matrices.pt') != capture['matrices_sha256']:
                raise ValueError('Frozen matrices changed')
            matrices = torch.load(parent/'capture/matrices.pt', map_location='cpu', weights_only=True)
            existing = torch.load(parent/'prepare/factors.pt', map_location='cpu', weights_only=True)
            costs = {name: sum(r['base'].shape) for name, r in matrices.items()}
            budget = sum(costs.values())*16
            native_elements = sum(r['source_adapter_elements'] for r in matrices.values())
            if budget >= .51*native_elements: raise ValueError('Not materially smaller than source')
            factors, decisions = {}, []
            for method in ['svd', 'weighted']:
                for c in [1., .995, 1.005]:
                    source = existing[method+'_'+str(c)]
                    spectra = {}
                    for name, pair in source.items():
                        # Left columns = U sqrt(sigma) for both cached procedures.
                        left = pair['left'].double()
                        singular = left.square().sum(0)
                        gram = left.T@left
                        off_diagonal_relative = float((gram-torch.diag(singular)).norm()/gram.norm())
                        if off_diagonal_relative > 1e-5:
                            raise ValueError('Cached left columns are not orthogonal')
                        if not bool((singular[:-1] >= singular[1:]*(1-1e-5)).all()):
                            raise ValueError('Cached factors not nested in spectral order')
                        # Sort only tiny roundoff inversions; SVD order above verified.
                        spectra[name] = singular.square().sort(descending=True).values.tolist()
                    allocation, gain = allocate(spectra, costs, budget)
                    for policy, ranks in [('fixed', {n: 16 for n in source}), ('allocated', allocation)]:
                        label = method+'_'+policy+'_'+str(c)
                        clipped = {n: dict(left=p['left'][:, :ranks[n]].clone(),
                                           right=p['right'][:ranks[n]].clone()) for n, p in source.items()}
                        count = sum(v['left'].numel()+v['right'].numel() for v in clipped.values())
                        if count != budget: raise ValueError('Unequal factor budgets')
                        factors[label] = clipped
                        decisions.append(dict(label=label, method=method, policy=policy, source_c=c,
                                              ranks=ranks, factor_elements=count,
                                              retained_proxy_energy=sum(sum(spectra[n][:ranks[n]]) for n in ranks)))
            torch.save(factors, out/'factors.pt')
            write_json(out/'decisions.json', decisions)
            # New screen inputs fixed before any scores, including no reuse of earlier validations.
            from transformers import AutoTokenizer
            from lora_dora_study.benchmarks import user_content
            calpath = Path(previous['calibration_cases'])
            if sha256_file(calpath) != previous['calibration_cases_sha256']: raise ValueError('Cal changed')
            excluded = {r['prompt_content_sha256'] for r in json.loads(calpath.read_text())}
            for path in [parent/'validation-cases.json', Path(m['anchored_root'])/'validation-cases.json']:
                excluded |= {r['prompt_content_sha256'] for r in json.loads(path.read_text())}
            train = [json.loads(x) for x in Path(previous['train']['path']).read_text().splitlines()]
            test = [json.loads(x) for x in Path(previous['test']['path']).read_text().splitlines()]
            for label in ['train', 'test']:
                if sha256_file(Path(previous[label]['path'])) != previous[label]['sha256']:
                    raise ValueError('Dataset changed')
            excluded |= {content_digest(r) for r in train[:232]+test}
            tokenizer = AutoTokenizer.from_pretrained(previous['artifacts']['base']['snapshot_path'],
                                                      local_files_only=True, trust_remote_code=False)
            cases = []
            for index, row in enumerate(train):
                digest = content_digest(row)
                if digest in excluded: continue
                text = tokenizer.apply_chat_template([dict(role='user', content=user_content('gsm8k', row))],
                    tokenize=False, add_generation_prompt=True, enable_thinking=False)
                ids = tokenizer(text, add_special_tokens=False)['input_ids']
                targets = tokenizer(row['answer'], add_special_tokens=False)['input_ids'][:32]
                if len(ids) > 512 or len(targets) < 32: continue
                cases.append(dict(train_index=index, prompt_content_sha256=digest,
                                  input_ids=ids+targets[:-1], targets=targets))
                excluded.add(digest)
                if len(cases) == 16: break
            if len(cases) != 16: raise ValueError('Insufficient screen cases')
            write_json(out/'cases.json', cases)
            status.update(status='complete', factor_elements=budget, native_elements=native_elements,
                fraction_of_native_elements=budget/native_elements, decisions=decisions,
                factors_sha256=sha256_file(out/'factors.pt'), cases_sha256=sha256_file(out/'cases.json'),
                decisions_sha256=sha256_file(out/'decisions.json'), case_count=len(cases))
            save()
            return

        if available_memory_bytes() < 64*1024**3: raise BlockingIOError('Need 64GiB RAM')
        prep = json.loads((root/'prepare/summary.json').read_text())
        if prep['status'] != 'complete': raise ValueError('Preparation incomplete')
        for name, key in [('cases.json', 'cases_sha256'), ('factors.pt', 'factors_sha256'),
                          ('decisions.json', 'decisions_sha256')]:
            if sha256_file(root/'prepare'/name) != prep[key]: raise ValueError('Prepared artifact changed')
        factors = torch.load(root/'prepare/factors.pt', map_location='cpu', weights_only=True)
        cases = json.loads((root/'prepare/cases.json').read_text())
        from transformers import AutoModelForCausalLM
        from peft import PeftModel
        from lora_dora_study.adapters import verify_loaded_adapter
        model = AutoModelForCausalLM.from_pretrained(previous['artifacts']['base']['snapshot_path'],
            local_files_only=True, trust_remote_code=False, torch_dtype=torch.float32,
            device_map={'': 'cpu'}, low_cpu_mem_usage=True, attn_implementation='sdpa')
        model = PeftModel.from_pretrained(model, previous['artifacts']['dora']['snapshot_path'],
                                         local_files_only=True, is_trainable=False).eval()
        model.requires_grad_(False)
        check = verify_loaded_adapter(model, previous['artifacts']['dora']['snapshot_path'], True)
        if not check['exact_loaded_value_match'] or check['adapted_module_count'] != 144:
            raise ValueError('Adapter load mismatch')
        if any(p.dtype != torch.float32 or p.device.type != 'cpu' for p in model.parameters()):
            raise ValueError('Unexpected dtype/device')
        status.update(adapter_exact=True, load_seconds=time.monotonic()-start,
                      case_count=len(cases), factor_elements=prep['factor_elements'])
        def logits(case):
            ids = torch.tensor([case['input_ids']], dtype=torch.long)
            with torch.inference_mode():
                y = model(input_ids=ids, attention_mask=torch.ones_like(ids), use_cache=False,
                          logits_to_keep=32).logits[0].detach().float().cpu()
            if y.shape[0] != 32 or not bool(y.isfinite().all()): raise FloatingPointError('Invalid logits')
            return y
        cal = json.loads(Path(previous['calibration_cases']).read_text())
        for i in range(4):
            cached = torch.load(parent/'capture/logit-cache'/f'original-{i}.pt', weights_only=True,
                                map_location='cpu')
            if not torch.equal(logits(cal[i]), cached): raise ValueError('Reference execution changed')
        cache = out/'logit-cache'
        cache.mkdir()
        for i, case in enumerate(cases):
            torch.save(logits(case), cache/f'original-{i}.pt')
            status.update(current='reference', cases_completed=i+1)
            save()
        controls = []
        for c in [1., .995, 1.005]:
            with scoped_gauge(model, layers, c):
                with replacement(model, layers, 'source_dense'):
                    for i in range(2):
                        reference = torch.load(cache/f'original-{i}.pt', weights_only=True)
                        controls.append(dict(kind='source_dense', c=c, case=i,
                                             **metrics(reference, logits(cases[i]), cases[i]['targets'])))
        first = next(iter(factors))
        def records(label):
            return {n: dict(base=mod.get_base_layer().weight.detach(), **factors[label][n])
                    for n, mod in selected_modules(model, layers).items()}
        dense_check = []
        with replacement(model, layers, 'factorized', records(first)):
            for i in range(2): dense_check.append(logits(cases[i]))
        with replacement(model, layers, 'compressed_dense', records(first)):
            for i in range(2):
                row = metrics(dense_check[i], logits(cases[i]), cases[i]['targets'])
                controls.append(dict(kind='factorized_vs_dense', case=i, **row))
        write_json(out/'controls.json', controls)
        early_effect = sum(metrics(torch.load(cache/f'original-{i}.pt', weights_only=True),
                                   dense_check[i], cases[i]['targets'])['rms'] for i in range(2))/2
        if max(r['rms'] for r in controls) >= .01*early_effect:
            raise ValueError('Early control floor >=1% compression effect')
        rows = []
        for label in factors:
            record = dict(label=label, status='running', cases_completed=0)
            status['conditions'].append(record)
            save()
            with replacement(model, layers, 'factorized', records(label)):
                for i, case in enumerate(cases):
                    y = logits(case)
                    reference = torch.load(cache/f'original-{i}.pt', weights_only=True, map_location='cpu')
                    row = dict(label=label, case=i, **metrics(reference, y, case['targets']))
                    rows.append(row)
                    with (out/'per-case.jsonl').open('a') as stream: stream.write(json.dumps(row)+'\n')
                    record['cases_completed'] = i+1
                    save()
            own = [r for r in rows if r['label'] == label]
            record.update(status='complete', mean_kl=sum(r['kl_reference_to_changed'] for r in own)/len(own),
                mean_nll_delta=sum(r['nll_difference'] for r in own)/len(own),
                mean_rms=sum(r['rms'] for r in own)/len(own),
                argmax_disagreements=sum(r['argmax_disagreements'] for r in own))
            save()
        floor = max(r['rms'] for r in controls)
        min_effect = min(r['mean_rms'] for r in status['conditions'])
        if floor >= .01*min_effect: raise ValueError('Control floor >=1% compression effect')
        status.update(status='complete', controls_max_rms=floor, minimum_compression_rms=min_effect,
                      full_task_accuracy=False, cases_sha256=prep['cases_sha256'])
        save()
    except Exception as exc:
        status.update(status='failed', error=repr(exc))
        save()
        raise
    finally: signal.setitimer(signal.ITIMER_REAL, 0)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--phase', choices=['prepare', 'evaluate'], required=True)
    args = parser.parse_args()
    main(args.root, args.phase)
