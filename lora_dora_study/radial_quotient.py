"""Explicit scalar-gauge-invariant V/O radial intervention convention.

Centering is a choice of counterfactual, not a unique causal decomposition.
No optimization, state changes, model loading or training occurs here.
"""
import math


def coefficients(v_scale, o_scale, kind, gauge=1.):
    import torch
    if not math.isfinite(gauge) or gauge <= 0:
        raise ValueError('Positive finite scalar gauge required')
    v, o = v_scale.double()*gauge, o_scale.double()/gauge
    if any(x.ndim != 1 or not bool(x.isfinite().all()) or not bool((x > 0).all()) for x in [v, o]):
        raise ValueError('Positive finite row-scale vectors required')
    if kind == 'source':
        return v, o
    if kind == 'raw_v_off':
        return torch.ones_like(v), o
    if kind == 'raw_o_off':
        return v, torch.ones_like(o)
    if kind in ['pair_off', 'all_parts_off']:
        return torch.ones_like(v), torch.ones_like(o)
    vm, om = v.log().mean().exp(), o.log().mean().exp()
    if kind == 'v_shape_off':
        return torch.ones_like(v)*vm, o
    if kind == 'o_shape_off':
        return v, torch.ones_like(o)*om
    if kind == 'gain_off':
        return v/vm, o/om
    raise ValueError('Unknown intervention')
