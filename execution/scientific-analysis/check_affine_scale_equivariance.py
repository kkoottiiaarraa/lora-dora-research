#!/usr/bin/env python3
"""Tiny algebra/code check; no model, data selection or quality experiment.

Checks a known homogeneity property of the existing affine solver. Its utility
and novelty do not follow from this numerical check.
"""
import argparse
import json
import os
from pathlib import Path
import sys

os.environ.update(CUDA_VISIBLE_DEVICES='', OMP_NUM_THREADS='2', MKL_NUM_THREADS='2')
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))


def main(output):
    import torch
    from lora_dora_study.affine_compression import alternating_affine, weighted_rank_factors
    torch.set_num_threads(2)
    torch.manual_seed(20261014)

    def positive(size):
        a = torch.randn(size, size, dtype=torch.float64)
        return a@a.T + torch.eye(size, dtype=torch.float64)

    modules = {}
    for name, rows, columns in [('v', 6, 8), ('o', 8, 6)]:
        base = torch.randn(rows, columns, dtype=torch.float64)
        diagonal = 1 + .03*torch.randn(rows, dtype=torch.float64)
        target = diagonal[:, None]*base + .03*torch.randn(rows, 3, dtype=torch.float64)@torch.randn(3, columns, dtype=torch.float64)
        modules[name] = dict(base=base, target=target, diagonal=diagonal,
            row=positive(rows), column=positive(columns))

    def compress(data, method, scale):
        b, t = data['base'], data['target']*scale
        # Transported metrics for V and O give the same transformed objective.
        g = data['row']/(scale*scale) if data is modules['v'] else data['row']
        c = data['column'] if data is modules['v'] else data['column']/(scale*scale)
        gl, cl = torch.linalg.cholesky(g), torch.linalg.cholesky(c)
        if method == 'joint':
            record, _ = alternating_affine(b, t, data['diagonal']*scale, g, cl, 2, iterations=5)
            return record['row_scale'].double()[:, None]*b + record['left'].double()@record['right'].double()
        d = data['diagonal']*scale if method == 'fixed_d' else torch.ones_like(data['diagonal'])
        left, right, _ = weighted_rank_factors(t-d[:, None]*b, gl, cl, 2)
        return d[:, None]*b + left@right

    results = []
    for method in ['joint', 'fixed_d', 'full_delta']:
        original = {name: compress(data, method, 1.) for name, data in modules.items()}
        product = original['o']@original['v']
        for scale in [.995, 1.005, 2.]:
            changed = {name: compress(data, method, scale if name == 'v' else 1/scale)
                       for name, data in modules.items()}
            matrix_error = max(float((changed[name] - original[name]*(scale if name == 'v' else 1/scale)).norm()/original[name].norm()) for name in modules)
            function_error = float((changed['o']@changed['v'] - product).norm()/product.norm())
            results.append(dict(method=method, scale=scale,
                relative_weight_equivariance_error=matrix_error,
                relative_composition_error=function_error))
            if method in ['joint', 'fixed_d'] and max(matrix_error, function_error) > 1e-5:
                raise ValueError('Affine scalar equivariance failed')
    result = dict(status='PASS', synthetic=True, model_inference=False, gpu_hours=0,
        rank=2, joint_cycles=5, joint_export_dtype='float32',
        fixed_d_and_full_delta_math_dtype='float64',
        same_budget_quality_comparison=False, rows=results,
        novelty_established=False, task_utility_established=False)
    output.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    main(args.output)
