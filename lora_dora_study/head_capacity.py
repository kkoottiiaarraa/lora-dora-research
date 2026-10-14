"""Elementary head-output rank obstruction, measured on fixed empirical inputs."""


def analyze(base, source, inputs, rank):
    import torch
    base,source,inputs=base.double(),source.double(),inputs.double()
    if base.shape!=source.shape or inputs.ndim!=2 or inputs.shape[1]!=base.shape[1]:
        raise ValueError('Unaligned head data')
    if not 0<=rank<base.shape[1] or len(inputs)==0:
        raise ValueError('Nontrivial rank/input count required')
    if not all(bool(t.isfinite().all()) for t in [base,source,inputs]):
        raise FloatingPointError('Nonfinite head inputs')
    q,r=torch.linalg.qr(base,mode='reduced')
    if float(r.diag().abs().min())<1e-12*float(base.norm()):
        raise ValueError('Base head not numerically full-column-rank')
    outside=source-q@(q.T@source)
    covariance=inputs.T@inputs/len(inputs)
    eigenvalues,vectors=torch.linalg.eigh((covariance+covariance.T)*.5)
    if float(eigenvalues.min()) < -1e-10*max(float(eigenvalues.max()),1e-30):
        raise FloatingPointError('Empirical covariance not PSD')
    square_root=(vectors*eigenvalues.clamp_min(0).sqrt())@vectors.T
    singular=torch.linalg.svdvals(outside@square_root)
    energy=float((source@square_root).square().sum())
    outside_energy=float(singular.square().sum())
    tail=float(singular[rank:].square().sum())
    return dict(source_energy=energy,outside_energy=outside_energy,tail_energy=tail,
        tail_fraction_source=tail/energy if energy else 0.,
        tail_fraction_outside=tail/outside_energy if outside_energy else 0.,
        outside_fraction_source=outside_energy/energy if energy else 0.,
        singular_values=singular.tolist(),
        base_projection_relative_floor=float((base-q@(q.T@base)).norm()/base.norm()))


def action_error(reference,changed,inputs):
    import torch
    x=inputs.double();d=changed.double()-reference.double()
    c=x.T@x/len(x)
    return float(((d@c)*d).sum().clamp_min(0))
