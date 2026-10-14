"""Reversible final-checkpoint radial counterfactuals, not training interventions."""
from contextlib import contextmanager


def components(module):
    import torch
    if not module.use_dora.get('default',False) or module.get_base_layer().bias is not None:
        raise ValueError('Expected native bias-free DoRA')
    with torch.no_grad():
        base=module.get_base_layer().weight.detach().float()
        direction=base+(module.lora_B['default'].weight.detach().float()@module.lora_A['default'].weight.detach().float())*module.scaling['default']
        norm=direction.norm(dim=1);base_norm=base.norm(dim=1);m=module.lora_magnitude_vector['default'].weight.detach().float()
        if any(not bool(t.isfinite().all()) or not bool((t>0).all()) for t in [norm,base_norm,m]):
            raise ValueError('Positive finite radial decomposition required')
        d=m/norm;learned=m/base_norm;normalization=base_norm/norm;gain=d.log().mean().exp()
        return dict(norm=norm,base_norm=base_norm,m=m.clone(),d=d,learned=learned,normalization=normalization,
            gain=gain,shape=d/gain)


def target_magnitude(parts,condition):
    if condition=='base_magnitude':return parts['base_norm']
    if condition=='learned_only':return parts['learned']*parts['norm']
    if condition=='scalar_d':return parts['gain']*parts['norm']
    if condition=='centered_d':return parts['m']/parts['gain']
    raise ValueError('Unknown radial counterfactual')


@contextmanager
def intervention(model,condition):
    import torch
    restore=[]
    try:
        with torch.no_grad():
            for module in model.modules():
                if hasattr(module,'use_dora') and module.use_dora.get('default',False):
                    p=module.lora_magnitude_vector['default'].weight;restore.append((p,p.detach().clone()))
                    p.copy_(target_magnitude(components(module),condition))
        if not restore:raise ValueError('No native DoRA modules')
        yield
    finally:
        with torch.no_grad():
            for p,original in restore:p.copy_(original)
