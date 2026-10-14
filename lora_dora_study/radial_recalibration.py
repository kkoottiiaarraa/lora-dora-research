"""Closed-form projection of truncation error onto the scaled frozen base."""


def recalibrate(base, target, inputs, record, ridge_fraction=.001):
    """Minimize ||(target-diag(d)base-LR)C^(1/2)||_F with fixed L/R.

    C=X^T X/n + lambda I. Each d has an independent scalar least-squares
    solution. No labels, optimizer, gradient steps or added parameters.
    """
    import torch
    b,w,x=base.double(),target.double(),inputs.double()
    left,right=record['left'].double(),record['right'].double()
    old=record['row_scale'].double()
    ridge=ridge_fraction*float(x.square().mean())
    if ridge<=0:raise ValueError('Degenerate covariance')
    by=x@b.T
    residual_y=x@w.T-by*old-(x@right.T)@left.T
    residual_w=w-old[:,None]*b-left@right
    numerator=(residual_y*by).mean(0)+ridge*(residual_w*b).sum(1)
    denominator=by.square().mean(0)+ridge*b.square().sum(1)
    if not bool((denominator>0).all()):raise ValueError('Degenerate base row')
    continuous=old+numerator/denominator
    deployed=continuous.float()
    if not bool(deployed.isfinite().all()) or float(deployed.abs().min())<1e-6:
        raise FloatingPointError('Degenerate recalibrated diagonal')
    delta=deployed.double()-old
    before=float(residual_y.square().sum()/len(x)+ridge*residual_w.square().sum())
    after_y=residual_y-by*delta
    after_w=residual_w-delta[:,None]*b
    after=float(after_y.square().sum()/len(x)+ridge*after_w.square().sum())
    if after>before*(1+1e-7)+1e-12:raise ValueError('Closed-form objective increased')
    return dict(left=record['left'],right=record['right'],row_scale=deployed),dict(
        ridge=ridge,weighted_loss_before=before,weighted_loss_after=after,
        relative_local_gain=(before-after)/before if before else 0.,
        max_abs_diagonal_change=float(delta.abs().max()),
        mean_abs_diagonal_change=float(delta.abs().mean()),
        ideal_projection_improvement=float((numerator.square()/denominator).sum()))
