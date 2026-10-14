#!/usr/bin/env python3
"""Known spectral allocation diagnostic over previously captured full DoRA."""
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
                  OPENBLAS_NUM_THREADS='4', HF_HUB_OFFLINE='1',
                  TRANSFORMERS_OFFLINE='1', TOKENIZERS_PARALLELISM='false')
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from lora_dora_study.server import write_json, available_memory_bytes
from lora_dora_study.evaluation import sha256_file


def prepare(root, parent, capture, summary, save):
    import torch
    from lora_dora_study.weighted_compression import covariance_cholesky
    from lora_dora_study.full_compression import thin_weighted_factors, structural_ranks
    from lora_dora_study.rank_budget import allocate

    costs = {item['name']: sum(item['shape']) for item in capture['modules']}
    shapes = {item['name']: item['shape'] for item in capture['modules']}
    diagonal_cost = sum(shape[0] for shape in shapes.values())
    budget = 8 * sum(costs.values())
    maximum = {'weighted': {}, 'structural': {}}
    spectra = {'weighted': {}, 'structural': {}}
    diagnostics = []
    uniform_structural = structural_ranks(shapes, 8)
    for index, item in enumerate(capture['modules']):
        path = parent/'capture'/item['file']
        if sha256_file(path) != item['sha256']:
            raise ValueError('Capture changed')
        data = torch.load(path, map_location='cpu', weights_only=True)
        name = item['name']
        chol, ridge = covariance_cholesky(data['inputs'])
        delta = data['value'] - data['base']
        scaled = (delta.double() @ chol).float()
        u, s, vh = torch.linalg.svd(scaled, full_matrices=False)
        k = 32
        left = (u[:, :k]*s[:k].sqrt()).contiguous()
        right = torch.linalg.solve_triangular(chol.T,
                    (s[:k].sqrt()[:, None]*vh[:k]).double().T, upper=True).T.float().contiguous()
        maximum['weighted'][name] = dict(left=left, right=right)
        spectra['weighted'][name] = s[:k].double().square().tolist()
        residual = ((delta.double()-(left@right).double()) @ chol).square().sum()
        tail = s[k:].double().square().sum()
        relative = abs(float(residual-tail))/max(float(tail), 1e-20)
        if relative > .003:
            raise ValueError('Weighted rank32 objective mismatch')
        struct, info = thin_weighted_factors(
            data['b'].double()*data['scaling']*data['row_scale'].double()[:, None],
            data['a'], chol, 32)
        struct['row_scale'] = data['row_scale'].clone()
        maximum['structural'][name] = struct
        spectra['structural'][name] = [v*v for v in info['singular_values']]
        teacher = data['value'].double()@chol
        diagnostics.append(dict(module=name, shape=item['shape'], ridge=ridge,
            weighted_total=float(s.double().square().sum()),
            weighted_tail_beyond32=float(tail),
            structural_total=sum(spectra['structural'][name]),
            teacher_output_energy=float(teacher.square().sum()),
            numerical_tail_relative_error=relative))
        summary.update(modules_completed=index+1, phase='prepare_spectra')
        save()
        del data, delta, scaled, u, s, vh, teacher, chol
    factors = {}
    allocations = {}
    for method in maximum:
        available = budget - (diagonal_cost if method == 'structural' else 0)
        ranks, gain = allocate(spectra[method], costs, available)
        uniform = uniform_structural if method == 'structural' else {n: 8 for n in costs}
        uniform_gain = sum(sum(spectra[method][n][:uniform[n]]) for n in costs)
        if gain + 1e-8*max(gain, 1) < uniform_gain:
            raise ValueError('Allocation proxy worse than feasible uniform')
        for suffix, mapping in [('uniform', uniform), ('allocated', ranks)]:
            label = method+'_'+suffix
            records = {}
            for name, rank in mapping.items():
                src = maximum[method][name]
                record = dict(left=src['left'][:, :rank].clone(), right=src['right'][:rank].clone())
                if method == 'structural':
                    record['row_scale'] = src['row_scale'].clone()
                if not all(bool(t.isfinite().all()) for t in record.values()):
                    raise FloatingPointError('Invalid factors')
                records[name] = record
            count = sum(t.numel() for rec in records.values() for t in rec.values())
            if count != budget:
                raise ValueError('Actual factor budget mismatch')
            allocations[label] = dict(ranks=mapping, factor_elements=count,
                retained_local_energy=sum(sum(spectra[method][n][:mapping[n]]) for n in costs))
            factors[label] = records
    for row in diagnostics:
        n = row['module']
        for label, alloc in allocations.items():
            method = label.split('_')[0]
            rank = alloc['ranks'][n]
            row[label+'_rank'] = rank
            row[label+'_local_loss'] = row[method+'_total']-sum(spectra[method][n][:rank])
    torch.save(factors, root/'factors.pt')
    write_json(root/'diagnostics.json', diagnostics)
    write_json(root/'allocations.json', allocations)
    write_json(root/'spectra.json', spectra)
    frozen = dict(factors_sha256=sha256_file(root/'factors.pt'),
        allocations_sha256=sha256_file(root/'allocations.json'),
        spectra_sha256=sha256_file(root/'spectra.json'),
        calibration_source_sha256=sha256_file(parent/'capture/summary.json'),
        frozen_before_new_inference=True, factor_elements=budget, maximum_rank=32)
    write_json(root/'frozen.json', frozen)
    summary.update(status='complete', phase='prepare_complete', factor_elements=budget,
                   frozen_sha256=sha256_file(root/'frozen.json'))
    save()


def main(root):
    start = time.monotonic()
    summary = dict(status='running', phase='prepare', gpu_count=0, training=False,
                   started_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
    def save():
        summary.update(wall_seconds=time.monotonic()-start,
                       rss_bytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024)
        write_json(root/'prepare-summary.json', summary)
    def timeout(signum, frame):
        raise TimeoutError('Allocation preparation deadline')
    signal.signal(signal.SIGALRM, timeout)
    signal.setitimer(signal.ITIMER_REAL, 3600)
    save()
    try:
        manifest = json.loads((root/'manifest-private.json').read_text())
        for rel, digest in manifest['source_sha256'].items():
            if sha256_file(ROOT/rel) != digest:
                raise ValueError('Frozen source changed: '+rel)
        import torch
        torch.set_num_threads(4)
        torch.set_num_interop_threads(1)
        torch.manual_seed(20261014)
        torch.set_float32_matmul_precision('highest')
        parent = Path(manifest['full_root'])
        capture = json.loads((parent/'capture/summary.json').read_text())
        if capture['status'] != 'complete' or len(capture['modules']) != 144:
            raise ValueError('Incomplete source capture')
        versions = {k: importlib.metadata.version(k) for k in capture['versions']}
        if versions != capture['versions']:
            raise ValueError('Versions changed')
        if available_memory_bytes() < 16*1024**3:
            raise BlockingIOError('Need 16 GiB available RAM')
        summary.update(versions=versions, source_sha256=manifest['source_sha256'], cpu_threads=4)
        prepare(root, parent, capture, summary, save)
    except Exception as exc:
        summary.update(status='failed', error=repr(exc)); save(); raise
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=Path, required=True)
    args = parser.parse_args()
    main(args.root)
