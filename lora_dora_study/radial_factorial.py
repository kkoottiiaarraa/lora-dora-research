"""Explicit reference-dependent radial counterfactuals, not training causes."""

CONDITIONS=('native','remove_d','reset_m_fp32','remove_n_fp32','reset_m_rounded','remove_n_rounded')

def radial_scale(magnitude,direction_norm,base_norm,condition,rounded_dtype):
    import torch
    if condition not in CONDITIONS:raise ValueError('Unknown condition')
    if any(not bool(x.isfinite().all())or not bool((x>0).all())for x in [magnitude,direction_norm,base_norm]):raise ValueError('Positive finite norms required')
    reference=base_norm.to(rounded_dtype).float()if condition.endswith('rounded')else base_norm
    if condition=='native':return magnitude/direction_norm
    if condition=='remove_d':return torch.ones_like(magnitude)
    if condition.startswith('reset_m'):return reference/direction_norm
    return magnitude/reference
