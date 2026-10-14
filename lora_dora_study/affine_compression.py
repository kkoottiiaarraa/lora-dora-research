"""Known block least-squares for fixed-base diagonal-plus-low-rank approximation.

This is an exploratory solver, not a claim of a novel optimization principle.
The row metric couples the diagonal coefficients; output covariance and all
calibration choices must be frozen separately from evaluation.
"""


def weighted_rank_factors(target, row_cholesky, column_cholesky, rank):
    import torch
    if not 0 <= rank <= min(target.shape):
        raise ValueError('Invalid rank')
    transformed = row_cholesky.T@target.double()@column_cholesky
    u, s, vh = torch.linalg.svd(transformed, full_matrices=False)
    left = torch.linalg.solve_triangular(row_cholesky.T,
        u[:, :rank]*s[:rank].sqrt(), upper=True)
    right = torch.linalg.solve_triangular(column_cholesky.T,
        (s[:rank].sqrt()[:, None]*vh[:rank]).T, upper=True).T
    return left, right, float(s[rank:].square().sum())


def diagonal_system(base, row_metric, column_cholesky):
    """H = G elementwise (W0 C W0^T), exact Hessian up to factor2."""
    import torch
    whitened = base.double()@column_cholesky
    hessian = row_metric*(whitened@whitened.T)
    return whitened, torch.linalg.cholesky(hessian)


def fit_diagonal(base_whitened, target_minus_update_whitened, row_metric, hessian_cholesky):
    import torch
    rhs = ((row_metric@target_minus_update_whitened)*base_whitened).sum(1)
    return torch.cholesky_solve(rhs[:, None], hessian_cholesky)[:, 0]


def objective(base, target, diagonal, left, right, row_cholesky, column_cholesky):
    error = target.double()-diagonal[:, None]*base.double()-left@right
    return float((row_cholesky.T@error@column_cholesky).square().sum())


def alternating_affine(base, target, initial_diagonal, row_metric, column_cholesky,
                       rank, iterations=5):
    """Five fixed block cycles; no labels, gradients, optimizer, validation tuning.

    For fixed D, low-rank step is globally optimal for the quadratic metric.
    For fixed L/R, D step is a coupled exact linear solve. Global joint
    optimality, end-to-end fidelity and task improvements do not follow.
    """
    import torch
    if type(iterations) is not int or iterations <= 0:
        raise ValueError('Positive fixed iteration count required')
    b, t = base.double(), target.double()
    d = initial_diagonal.double().clone()
    row_cholesky = torch.linalg.cholesky(row_metric)
    bw, hchol = diagonal_system(b, row_metric, column_cholesky)
    tw = t@column_cholesky
    history=[]
    for index in range(iterations):
        left,right,tail=weighted_rank_factors(t-d[:, None]*b,row_cholesky,column_cholesky,rank)
        before=objective(b,t,d,left,right,row_cholesky,column_cholesky)
        d=fit_diagonal(bw,tw-left@(right@column_cholesky),row_metric,hchol)
        after=objective(b,t,d,left,right,row_cholesky,column_cholesky)
        if not bool(d.isfinite().all()) or float(d.abs().min())<1e-6:
            raise FloatingPointError('Degenerate diagonal')
        tolerance=1e-8*max(before,1e-20)
        if abs(before-tail)>tolerance or after>before+tolerance:
            raise ValueError('Exact block objective check failed')
        if history and before>history[-1]['after_diagonal']+tolerance:
            raise ValueError('Alternating objective increased')
        history.append(dict(iteration=index+1,after_low_rank=before,after_diagonal=after))
    return dict(left=left.float().contiguous(),right=right.float().contiguous(),
                row_scale=d.float().contiguous()),history
