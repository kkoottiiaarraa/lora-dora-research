"""Explicit effective weights, adaptive SVD compression and exact V/O symmetry.

All decompositions use FP32. No optimizer, no fitting to evaluation answers.
"""
import math

def effective_weight(module):
    import torch
    base=module.get_base_layer().weight.detach().float()
    update=module.lora_B['default'].weight.float() @ module.lora_A['default'].weight.float()
    update=update*module.scaling['default']
    value=base+update
    if module.use_dora['default']:
        value=value*(module.lora_magnitude_vector['default'].weight.float()/value.norm(dim=1))[:,None]
    return base,value.detach()

def compressed_update(delta, rank=None, energy=None):
    import torch
    if (rank is None)==(energy is None):raise ValueError('Choose rank or energy')
    u,s,vh=torch.linalg.svd(delta.float(),full_matrices=False)
    if energy is not None:
        if not 0<energy<=1:raise ValueError('Energy outside (0,1]')
        cumulative=s.square().cumsum(0)
        k=int(torch.searchsorted(cumulative,energy*cumulative[-1]).item())+1 if cumulative[-1]>0 else 0
    else:
        if rank<0:raise ValueError('Negative rank')
        k=min(rank,len(s))
    approximation=(u[:,:k]*s[:k])@vh[:k]
    total=float(s.square().sum())
    return approximation,dict(rank=k,shape=list(delta.shape),spectrum=s.cpu().tolist(),
        retained_energy=float(s[:k].square().sum())/total if total else 1.)

def activation_error(delta, approximation, inputs):
    import torch
    x=inputs.to(device=delta.device,dtype=torch.float32)
    numerator=float((x@(delta-approximation).T).square().sum())
    denominator=float((x@delta.T).square().sum())
    return dict(squared_output_error=numerator,original_update_output_energy=denominator,
                relative_squared_error=numerator/denominator if denominator else None,
                calibration_tokens=len(x))

def magnitude_direction(base, value):
    import torch
    # Mean absolute row magnitude change and mean (1-cosine) per layer.
    magnitude=(value.norm(dim=1)-base.norm(dim=1)).abs().mean()
    direction=(1-torch.nn.functional.cosine_similarity(base,value,dim=1)).mean()
    return dict(magnitude=float(magnitude),direction=float(direction))

def pearson(rows):
    import torch
    if len(rows)<2:return None
    x=torch.tensor([r['magnitude'] for r in rows],dtype=torch.float64)
    y=torch.tensor([r['direction'] for r in rows],dtype=torch.float64)
    x=x-x.mean();y=y-y.mean()
    denominator=x.norm()*y.norm()
    return float(x@y/denominator) if denominator else None

def prepare(model,job,calibration_inputs):
    import torch
    from peft.tuners.lora.layer import LoraLayer
    method=job['intervention']
    modules={n:m for n,m in model.named_modules() if isinstance(m,LoraLayer)
             and n.rsplit('.',1)[-1] in job['targets']}
    if not modules:raise ValueError('No adapted attention modules')
    captured={};hooks=[]
    def capture(name):
        def hook(module,arguments):
            if name not in captured:
                captured[name]=arguments[0].detach().reshape(-1,arguments[0].shape[-1])[:128].cpu()
        return hook
    for name,module in modules.items():hooks.append(module.register_forward_pre_hook(capture(name)))
    with torch.inference_mode():
        before=model(**calibration_inputs).logits.float()
    for hook in hooks:hook.remove()
    records=[];weights={}
    with torch.no_grad():
        for name,module in modules.items():
            base,value=effective_weight(module)
            # CPU storage avoids holding a second entire model in VRAM.
            weights[name]=(base.cpu(),value.cpu())
            linear=torch.nn.Linear(value.shape[1],value.shape[0],bias=module.get_base_layer().bias is not None,
                                   device=value.device,dtype=module.get_base_layer().weight.dtype)
            linear.weight.copy_(value)
            if linear.bias is not None:linear.bias.copy_(module.get_base_layer().bias)
            parent,leaf=name.rsplit('.',1)
            model.get_submodule(parent)._modules[leaf]=linear
        modules.clear();del module,base,value,linear
        torch.cuda.empty_cache() if torch.cuda.is_available() else None
        dense=model(**calibration_inputs).logits.float()
        fidelity=dict(max_abs_logits_error=float((before-dense).abs().max()),
                      argmax_agreement=float((before.argmax(-1)==dense.argmax(-1)).float().mean()))
        symmetry_before=[];symmetry_after=[];fixed_base_after=[]
        for name,(base_cpu,value_cpu) in weights.items():
            linear=model.get_submodule(name)
            base=base_cpu.to(linear.weight.device);value=value_cpu.to(linear.weight.device)
            delta=value-base
            item=dict(module=name,adapter_rank=job.get('rank',32))
            if method in {'rank_fixed','rank_energy','rank_lora_control'}:
                approximation,details=compressed_update(delta,rank=job.get('rank',32) if method!='rank_energy' else None,
                                                         energy=job.get('energy') if method=='rank_energy' else None)
                item.update(details)
                if method=='rank_lora_control':
                    # Match DoRA's measured per-module output perturbation using
                    # attenuation of LoRA's update, retaining its rank <= r.
                    import json
                    from pathlib import Path
                    target=json.loads(Path(job['impact_manifest']).read_text())
                    target=next(r for r in target['modules'] if r['module']==name)
                    relative=target['activation']['relative_squared_error']
                    if relative is None:raise ValueError('Undefined matched impact')
                    attenuation=math.sqrt(relative)
                    approximation=delta*(1-attenuation)
                    item['attenuation']=attenuation
                    item['control']='Matched relative activation error; attenuation retains LoRA rank'
                item['activation']=activation_error(delta,approximation,captured[name])
                linear.weight.copy_(base+approximation)
            elif method=='vo_symmetry':
                layer=int(name.split('.layers.')[1].split('.')[0])
                scale=[.5,1.,2.][layer%3]
                leaf=name.rsplit('.',1)[-1]
                factor=scale if leaf=='v_proj' else 1/scale if leaf=='o_proj' else 1.
                linear.weight.mul_(factor)
                if linear.bias is not None and leaf=='v_proj':linear.bias.mul_(factor)
                if leaf=='v_proj':
                    symmetry_before.append(magnitude_direction(base,value))
                    symmetry_after.append(magnitude_direction(base*factor,value*factor))
                    fixed_base_after.append(magnitude_direction(base,value*factor))
                item.update(scale=factor,
                    joint_base_rank_preserved=True,
                    same_fixed_base_rank_preserved='not guaranteed; (c-1)W0 can have full rank')
            elif method!='dense_reference':raise ValueError('Unknown advanced intervention')
            records.append(item)
            del base,value,delta
        after=model(**calibration_inputs).logits.float()
    result=dict(method=method,modules=records,dense_fidelity=fidelity,
                calibration_source=job['calibration'],calibration_tokens=calibration_inputs['input_ids'].shape[1],
                interpretation='Final-checkpoint intervention, not a training-trajectory causal claim')
    if method=='vo_symmetry':
        error=float((dense-after).abs().max())
        result.update(symmetry_logits_max_abs_error=error,
                      symmetry_argmax_agreement=float((dense.argmax(-1)==after.argmax(-1)).float().mean()),
                      statistic_definition='Across layers: mean absolute row norm change versus mean 1-cosine, V projections',
                      correlation_before=pearson(symmetry_before),correlation_joint_base_after=pearson(symmetry_after),
                      correlation_fixed_base_after=pearson(fixed_base_after),
                      layer_statistics=dict(before=symmetry_before,joint_base_after=symmetry_after,fixed_base_after=fixed_base_after))
        if not torch.allclose(dense,after,atol=.05,rtol=.01):
            raise RuntimeError('V/O symmetry failed numerical logit preservation: '+str(error))
    return result
