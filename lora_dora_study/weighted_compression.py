"""Closed-form activation-weighted update compression; no training or fitting labels."""
import math


def covariance_cholesky(inputs, ridge=.001):
    import torch
    x = inputs.double()
    covariance = x.T@x/len(x)
    regularizer = ridge*float(covariance.diag().mean())
    if not math.isfinite(regularizer) or regularizer <= 0:
        raise ValueError('Degenerate activation covariance')
    covariance.diagonal().add_(regularizer)
    return torch.linalg.cholesky(covariance), regularizer


def weighted_factors(delta, cholesky, rank=32):
    import torch
    # ||(delta-R)L||_F, LL^T = E[xx^T]+lambda I.
    scaled = (delta.double()@cholesky).float()
    u, s, vh = torch.linalg.svd(scaled, full_matrices=False)
    root = s[:rank].sqrt()
    left = (u[:, :rank]*root).contiguous()
    weighted_right = root[:, None]*vh[:rank]
    right = torch.linalg.solve_triangular(cholesky.T, weighted_right.double().T, upper=True).T.float().contiguous()
    if not bool(left.isfinite().all() and right.isfinite().all()):
        raise FloatingPointError('Nonfinite weighted factors')
    residual = ((delta.double()-(left@right).double())@cholesky).square().sum()
    expected = s[rank:].double().square().sum()
    if not math.isclose(float(residual), float(expected), rel_tol=.003, abs_tol=1e-8):
        raise ValueError('Weighted optimality check failed')
    return left, right, dict(weighted_squared_residual=float(residual),
                            expected_squared_tail=float(expected), rank=rank)
