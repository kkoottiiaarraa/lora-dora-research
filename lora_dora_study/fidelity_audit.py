"""Fixed-prefix fidelity measurements and reversible DoRA gauge interventions."""
from contextlib import contextmanager
import hashlib
import json
import math


def content_digest(row):
    from lora_dora_study.benchmarks import user_content
    return hashlib.sha256(user_content('gsm8k', row).encode()).hexdigest()


def select_cases(train, test, count=64, skip=232):
    excluded = {content_digest(r) for r in train[:skip]} | {content_digest(r) for r in test}
    selected = []
    for i, row in enumerate(train[skip:], skip):
        h = content_digest(row)
        if h not in excluded:
            selected.append((i, row))
            excluded.add(h)
            if len(selected) == count:
                break
    if len(selected) != count:
        raise ValueError('Insufficient distinct train-only examples')
    return selected


@contextmanager
def magnitude_gauge(model, scale):
    import torch
    if not math.isfinite(scale) or scale <= 0:
        raise ValueError('Positive finite gauge scale required')
    restore = []
    counts = {'v_proj': 0, 'o_proj': 0}
    try:
        with torch.no_grad():
            for name, module in model.named_modules():
                leaf = name.rsplit('.', 1)[-1]
                if leaf not in counts or not hasattr(module, 'lora_magnitude_vector'):
                    continue
                if module.get_base_layer().bias is not None:
                    raise ValueError('Bias-free V/O required')
                if not module.use_dora.get('default', False):
                    raise ValueError('Original DoRA required for magnitude gauge')
                p = module.lora_magnitude_vector['default'].weight
                restore.append((p, p.detach().clone()))
                p.mul_(scale if leaf == 'v_proj' else 1/scale)
                counts[leaf] += 1
        if not counts['v_proj'] or counts['v_proj'] != counts['o_proj']:
            raise ValueError('Incomplete V/O gauge coverage')
        yield counts
    finally:
        with torch.no_grad():
            for p, original in restore:
                p.copy_(original)


@contextmanager
def without_d(model):
    restore = []
    try:
        for module in model.modules():
            if hasattr(module, 'use_dora') and module.use_dora.get('default', False):
                variant = module.lora_variant.pop('default')
                restore.append((module, variant))
                module.use_dora['default'] = False
        if not restore:
            raise ValueError('No DoRA adapters')
        yield
    finally:
        for module, variant in restore:
            module.use_dora['default'] = True
            module.lora_variant['default'] = variant


def metrics(reference, changed, targets):
    """Exact full-vocabulary metrics on CPU; no top-k KL approximation."""
    import torch
    import torch.nn.functional as F
    a, b = reference.double(), changed.double()
    if a.shape != b.shape or a.ndim != 2:
        raise ValueError('Require aligned [target tokens, vocabulary] logits')
    if not torch.isfinite(a).all() or not torch.isfinite(b).all():
        raise FloatingPointError('Nonfinite CPU-read-back logits')
    d = b-a
    la, lb = a.log_softmax(-1), b.log_softmax(-1)
    top = a.topk(2, dim=-1).values
    margin = top[:, 0]-top[:, 1]
    target = torch.tensor(targets, dtype=torch.long)
    nlla = -la.gather(1, target[:, None]).mean()
    nllb = -lb.gather(1, target[:, None]).mean()
    return dict(tokens=len(targets), max_abs=float(d.abs().max()), rms=float(d.square().mean().sqrt()),
        kl_reference_to_changed=float((la.exp()*(la-lb)).sum(-1).mean()),
        argmax_disagreements=int((a.argmax(-1)!=b.argmax(-1)).sum()),
        mean_reference_margin=float(margin.mean()),
        positions_with_margin_below_twice_max_error=int((margin<=2*d.abs().amax(-1)).sum()),
        reference_nll=float(nlla), changed_nll=float(nllb), nll_difference=float(nllb-nlla))


def convert_custom(model):
    import torch
    from lora_dora_study.rank_symmetry import effective_weight
    modules = [(name, module) for name, module in model.named_modules()
               if hasattr(module, 'use_dora') and module.use_dora.get('default', False)]
    with torch.no_grad():
        for name, module in modules:
            _, value = effective_weight(module)
            base = module.get_base_layer()
            linear = torch.nn.Linear(value.shape[1], value.shape[0], bias=base.bias is not None,
                                     device=value.device, dtype=base.weight.dtype)
            linear.weight.copy_(value)
            if base.bias is not None:
                linear.bias.copy_(base.bias)
            parent, leaf = name.rsplit('.', 1)
            model.get_submodule(parent)._modules[leaf] = linear


def projection_fingerprints(model):
    """All deployed attention-projection bytes; canonical names survive merge."""
    import torch
    result={}
    for name,module in model.named_modules():
        if 'layers.' in name and name.rsplit('.',1)[-1] in {'q_proj','k_proj','v_proj','o_proj'}:
            if not isinstance(module,torch.nn.Linear):
                raise ValueError('Expected dense deployed projections')
            key=name[name.index('layers.'):]
            value=module.weight.detach().cpu().contiguous()
            h=hashlib.sha256(str((list(value.shape),str(value.dtype))).encode())
            h.update(value.view(torch.uint8).numpy().tobytes())
            result[key]=h.hexdigest()
    if len(result)!=model.config.num_hidden_layers*4:
        raise ValueError('Incomplete dense fingerprint coverage')
    return result


def small_geometry(model, output_dir):
    """CPU only, three preselected layers; no full-model SVD grid."""
    import csv
    import torch
    from lora_dora_study.rank_symmetry import effective_weight
    rows = []
    with torch.inference_mode():
        for layer in [0, 17, 35]:
            named = dict(model.named_modules())
            selected = {}
            for leaf in ['v_proj', 'o_proj']:
                matches = [(n, m) for n, m in named.items() if n.endswith(f'layers.{layer}.self_attn.{leaf}')]
                if len(matches) != 1:
                    raise ValueError('Missing selected module')
                name, module = matches[0]
                base, value = effective_weight(module)
                selected[leaf] = (base, value)
                for c in [.995, 1., 1.005]:
                    scale = c if leaf == 'v_proj' else 1/c
                    delta = value*scale-base
                    singular = torch.linalg.svdvals(delta)
                    energy = singular.double().square()
                    p = energy/energy.sum()
                    h = float(-(p[p>0]*p[p>0].log()).sum())
                    rows.append(dict(module=name,c=c,entropy=h,effective_rank=math.exp(h),
                                     update_frobenius=float(energy.sum().sqrt()),
                                     calculation='FP32 weights, CPU SVD; ideal pre-BF16 matrix'))
            # Independent FP64 V/O block check, including GQA replication.
            v, o = selected['v_proj'][1].double(), selected['o_proj'][1].double()
            x = torch.linspace(-.1,.1,v.shape[1],dtype=torch.float64)[None,:]
            heads=model.config.num_key_value_heads; groups=model.config.num_attention_heads//heads
            def block(vw, ow):
                z=torch.nn.functional.linear(x,vw).reshape(1,heads,-1)
                z=z.repeat_interleave(groups,dim=1).flatten(1)
                return torch.nn.functional.linear(z,ow)
            y=block(v,o)
            for c in [.995,1.005,2.]:
                changed=block(v*c,o/c)
                relative=float((y-changed).norm()/y.norm().clamp_min(1e-30))
                if relative>1e-10:
                    raise ValueError('FP64 module identity failed')
                rows.append(dict(module=f'layer.{layer}.vo_fp64',c=c,relative_output_error=relative))
    fields=list(dict.fromkeys(k for r in rows for k in r))
    with open(output_dir/'geometry.csv','w') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
    return rows
