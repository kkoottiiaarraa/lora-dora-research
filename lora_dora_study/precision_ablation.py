"""Small execution helpers for matched ablations; no new DoRA kernel."""


def place_transformer(model, device, dtype):
    """Keep lookup/head on CPU FP32 and move transformer without Accelerate offload."""
    import torch
    import torch.nn.functional as F
    core = model.get_base_model()
    if any(hasattr(m, '_hf_hook') for m in core.modules()):
        raise ValueError('Unexpected dispatch hooks; explicit placement required')
    embed = core.model.embed_tokens
    head = core.lm_head

    class Lookup(torch.nn.Module):
        def __init__(self):
            super().__init__()
            self.weight = torch.nn.Parameter(embed.weight.detach().float().cpu(), requires_grad=False)
            self.padding_idx = embed.padding_idx
        def forward(self, ids):
            return F.embedding(ids.cpu(), self.weight, self.padding_idx).to(device=device, dtype=dtype)

    class Head(torch.nn.Module):
        def __init__(self):
            super().__init__()
            self.weight = torch.nn.Parameter(head.weight.detach().float().cpu(), requires_grad=False)
        def forward(self, hidden):
            return F.linear(hidden.to(device='cpu', dtype=torch.float32), self.weight)

    core.model.embed_tokens = Lookup()
    core.lm_head = Head()
    core.model.layers.to(device)
    core.model.norm.to(device)
    core.model.rotary_emb.to(device)
    # PEFT adapter parameters remain FP32; base and norms retain load dtype.
    return model


def projection_names(model):
    return [name for name,m in model.named_modules() if hasattr(m,'use_dora') and 'default' in m.use_dora]


def stream_dense(model):
    """Same FP32 effective_weight convention as the existing converter, bounded VRAM."""
    import torch
    from lora_dora_study.rank_symmetry import effective_weight
    names = projection_names(model)
    if not names:
        raise ValueError('No adapted projections')
    unscaled = {}
    scales = {}
    with torch.no_grad():
        for name in names:
            module = model.get_submodule(name)
            base = module.get_base_layer()
            if base.bias is not None:
                raise ValueError('Bias-free required')
            _, value = effective_weight(module)
            direction = base.weight.detach().float() + (
                module.lora_B['default'].weight.float() @ module.lora_A['default'].weight.float())*module.scaling['default']
            d = module.lora_magnitude_vector['default'].weight.float()/direction.norm(dim=1)
            unscaled[name] = direction.detach().cpu()
            scales[name] = d.detach().cpu()
            linear = torch.nn.Linear(value.shape[1], value.shape[0], bias=False,
                device=base.weight.device, dtype=base.weight.dtype)
            linear.weight.copy_(value)
            linear.requires_grad_(False)
            parent,leaf = name.rsplit('.',1)
            model.get_submodule(parent)._modules[leaf] = linear
            del module,base,value,direction,d,linear
    return unscaled, scales


def apply_dense_without_d(model, unscaled):
    import torch
    with torch.no_grad():
        for name, weight in unscaled.items():
            module = model.get_submodule(name)
            module.weight.copy_(weight)


def fingerprints(model):
    import hashlib
    import torch
    records={}
    for name,module in model.named_modules():
        if name.rsplit('.',1)[-1] in {'q_proj','k_proj','v_proj','o_proj'} and isinstance(module,torch.nn.Linear):
            key=name[name.index('layers.'):]
            t=module.weight.detach().cpu().contiguous()
            h=hashlib.sha256(str((list(t.shape),str(t.dtype))).encode())
            h.update(t.view(torch.uint8).numpy().tobytes());records[key]=h.hexdigest()
    return records


def load_explicit_cpu(base_path, adapter_path, dtype):
    """Do not let PEFT infer a second device map when CUDA is visible."""
    from transformers import AutoModelForCausalLM
    from peft import PeftModel
    model = AutoModelForCausalLM.from_pretrained(base_path,local_files_only=True,
        trust_remote_code=False,torch_dtype=dtype,device_map=None,low_cpu_mem_usage=True,
        attn_implementation='sdpa')
    model = PeftModel.from_pretrained(model,adapter_path,local_files_only=True,
        is_trainable=False,torch_device='cpu',device_map={'':'cpu'}).eval()
    model.requires_grad_(False)
    if any(p.device.type!='cpu' or p.is_meta for p in model.parameters()):
        raise ValueError('Explicit CPU loader did not materialize every parameter')
    return model
