"""Full fixed-base adapter compression controls. No optimizer or training."""
from contextlib import contextmanager
import random

from lora_dora_study.rank_budget import allocate


def adapted_modules(model):
    result = {n: m for n, m in model.named_modules()
              if hasattr(m, 'use_dora') and m.use_dora.get('default')}
    if not result:
        raise ValueError('No native DoRA modules')
    for name, module in result.items():
        if module.get_base_layer().bias is not None:
            raise ValueError('Bias-free projections required')
        if name.rsplit('.', 1)[-1] not in ['q_proj', 'k_proj', 'v_proj', 'o_proj']:
            raise ValueError('Unexpected target module')
    return result


def structural_ranks(shapes, reference_rank, seed=20261013):
    """Ranks r-1/r; count every radial scalar and match ordinary LoRA-r size.

    Among feasible near-uniform assignments maximize sum of directional ranks.
    Fixed seeded order breaks ties without using data or scores.
    """
    names = sorted(shapes)
    random.Random(seed).shuffle(names)
    mapping = {f'{i:04}': name for i, name in enumerate(names)}
    costs = {k: sum(shapes[name]) for k, name in mapping.items()}
    diagonal_elements = sum(shapes[name][0] for name in names)
    base_elements = (reference_rank-1)*sum(costs.values()) + diagonal_elements
    budget = reference_rank*sum(costs.values())
    if reference_rank < 2 or base_elements > budget:
        raise ValueError('Near-uniform structural budget infeasible')
    extra, _ = allocate({k: [1.] for k in mapping}, costs, budget-base_elements)
    ranks = {mapping[k]: reference_rank-1+extra[k] for k in mapping}
    actual = sum(ranks[n]*sum(shapes[n])+shapes[n][0] for n in names)
    if actual != budget:
        raise ValueError('Structural storage budget mismatch')
    return ranks


def thin_weighted_factors(left_source, right_source, cholesky, rank):
    """Whiten/SVD a low-rank product with exact thin QR, no dense target SVD."""
    import torch
    if not 0 < rank <= min(left_source.shape[1], right_source.shape[0]):
        raise ValueError('Invalid structural rank')
    ql, rl = torch.linalg.qr(left_source.double(), mode='reduced')
    qr, rr = torch.linalg.qr((right_source.double()@cholesky).T, mode='reduced')
    u, s, vh = torch.linalg.svd(rl@rr.T, full_matrices=False)
    root = s[:rank].sqrt()
    left = ((ql@u[:, :rank])*root).float().contiguous()
    weighted_right = root[:, None]*(vh[:rank]@qr.T)
    right = torch.linalg.solve_triangular(cholesky.T, weighted_right.T, upper=True).T.float().contiguous()
    if not bool(left.isfinite().all() and right.isfinite().all()):
        raise FloatingPointError('Nonfinite structural factors')
    return dict(left=left, right=right), dict(rank=rank,
        ideal_weighted_squared_tail=float(s[rank:].square().sum()), singular_values=s.tolist())


def module_from_record(record):
    import torch
    import torch.nn.functional as F

    class FrozenAdapter(torch.nn.Module):
        def __init__(self):
            super().__init__()
            for key in ['base', 'left', 'right', 'row_scale']:
                if key in record:
                    self.register_buffer(key, record[key])

        def forward(self, x):
            y = F.linear(x, self.base)
            if hasattr(self, 'row_scale'):
                y = y*self.row_scale
            return y+F.linear(F.linear(x, self.right), self.left)

    return FrozenAdapter()


@contextmanager
def replace_all(model, records, dense=False):
    import torch
    restore = []
    try:
        modules = adapted_modules(model)
        if set(modules) != set(records):
            raise ValueError('Must replace every adapted projection exactly once')
        for name, source in modules.items():
            record = dict(base=source.get_base_layer().weight.detach(), **records[name])
            if dense:
                weight = record['base']
                if 'row_scale' in record:
                    weight = weight*record['row_scale'][:, None]
                weight = weight+record['left']@record['right']
                new = torch.nn.Linear(weight.shape[1], weight.shape[0], bias=False,
                                      device='cpu', dtype=torch.float32)
                with torch.no_grad(): new.weight.copy_(weight)
                new.requires_grad_(False)
            else:
                new = module_from_record(record)
            parent, leaf = name.rsplit('.', 1)
            owner = model.get_submodule(parent)
            restore.append((owner, leaf, source))
            owner._modules[leaf] = new
        yield
    finally:
        for owner, leaf, source in reversed(restore):
            owner._modules[leaf] = source
