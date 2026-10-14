"""CPU FP32 compression of full DoRA updates, with reversible module changes."""
from contextlib import contextmanager
import math

from lora_dora_study.rank_symmetry import effective_weight


def selected_modules(model, layers):
    result = {}
    for layer in layers:
        for leaf in ['v_proj', 'o_proj']:
            matches = [(n, m) for n, m in model.named_modules()
                       if n.endswith(f'layers.{layer}.self_attn.{leaf}')]
            if len(matches) != 1:
                raise ValueError('Missing or ambiguous selected module')
            name, module = matches[0]
            if not hasattr(module, 'use_dora') or not module.use_dora.get('default'):
                raise ValueError('Selected module must be native DoRA')
            if module.get_base_layer().bias is not None:
                raise ValueError('Bias-free V/O required')
            result[name] = module
    return result


@contextmanager
def scoped_gauge(model, layers, c):
    import torch
    if not math.isfinite(c) or c <= 0:
        raise ValueError('Positive finite scale required')
    restore = []
    try:
        with torch.no_grad():
            for name, module in selected_modules(model, layers).items():
                p = module.lora_magnitude_vector['default'].weight
                restore.append((p, p.detach().clone()))
                p.mul_(c if name.endswith('v_proj') else 1/c)
        yield
    finally:
        with torch.no_grad():
            for p, value in restore:
                p.copy_(value)


def decompose(base, value, rank):
    import torch
    if base.device.type != 'cpu' or value.device.type != 'cpu':
        raise ValueError('This screen is CPU only')
    if base.dtype != torch.float32 or value.dtype != torch.float32:
        raise ValueError('Require genuine FP32 weights')
    if rank < 1 or rank > min(value.shape):
        raise ValueError('Invalid compression rank')
    delta = value-base
    u, s, vh = torch.linalg.svd(delta, full_matrices=False)
    if not bool(s.isfinite().all()):
        raise FloatingPointError('Nonfinite singular values')
    root = s[:rank].sqrt()
    left, right = (u[:, :rank]*root).contiguous(), (root[:, None]*vh[:rank]).contiguous()
    energy = s.double().square()
    total = float(energy.sum())
    p = energy/total if total else energy
    entropy = float(-(p[p > 0]*p[p > 0].log()).sum())
    residual = float((delta.double()-(left@right).double()).square().sum())
    expected = float(energy[rank:].sum())
    if not math.isclose(residual, expected, rel_tol=2e-4, abs_tol=1e-8):
        raise ValueError('SVD residual disagrees with singular-value tail')
    ranks = {}
    for fraction in [.95, .99]:
        ranks[str(fraction)] = int(torch.searchsorted(energy.cumsum(0), fraction*total))+1 if total else 0
    info = dict(shape=list(value.shape), rank=rank, dense_update_elements=value.numel(),
        factor_elements=left.numel()+right.numel(), retained_energy=float(energy[:rank].sum())/total if total else 1.,
        entropy_nats=entropy, effective_rank=math.exp(entropy), energy_ranks=ranks,
        squared_residual=residual, expected_squared_residual=expected, singular_values=s.tolist())
    return dict(base=base.detach(), left=left.detach(), right=right.detach(), info=info)


def factorized_module(record):
    import torch
    import torch.nn.functional as F

    class FrozenBasePlusFactors(torch.nn.Module):
        def __init__(self):
            super().__init__()
            for name in ['base', 'left', 'right']:
                self.register_buffer(name, record[name])

        def forward(self, x):
            return F.linear(x, self.base) + F.linear(F.linear(x, self.right), self.left)

    return FrozenBasePlusFactors()


@contextmanager
def replacement(model, layers, kind, records=None):
    import torch
    restore = []
    try:
        for name, module in selected_modules(model, layers).items():
            if kind == 'factorized':
                new = factorized_module(records[name])
            elif kind in ['source_dense', 'compressed_dense']:
                if kind == 'source_dense':
                    _, value = effective_weight(module)
                else:
                    r = records[name]
                    value = r['base'] + r['left']@r['right']
                new = torch.nn.Linear(value.shape[1], value.shape[0], bias=False,
                                      device='cpu', dtype=torch.float32)
                with torch.no_grad():
                    new.weight.copy_(value)
                new.weight.requires_grad_(False)
            else:
                raise ValueError('Unknown replacement kind')
            parent, leaf = name.rsplit('.', 1)
            owner = model.get_submodule(parent)
            restore.append((owner, leaf, module))
            owner._modules[leaf] = new
        yield
    finally:
        for owner, leaf, module in reversed(restore):
            owner._modules[leaf] = module


def practical_gate(drift_rms, gauge_rms, compression_rms):
    if not all(math.isfinite(x) and x >= 0 for x in [drift_rms, gauge_rms, compression_rms]):
        raise ValueError('Finite nonnegative metrics required')
    return dict(passed=drift_rms > 10*gauge_rms and drift_rms > .2*compression_rms,
                drift_rms=drift_rms, gauge_rms=gauge_rms, compression_rms=compression_rms,
                drift_over_compression=drift_rms/compression_rms if compression_rms else None,
                criterion='drift > 10*gauge RMS AND drift > 20% original compression RMS; engineering screen')
