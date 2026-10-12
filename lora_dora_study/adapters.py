"""Check saved keys and actual PEFT tensors, not just an adapter's label."""
from pathlib import Path


def verify_loaded_adapter(model, directory, expected_dora):
    import torch
    from peft import get_peft_model_state_dict
    from safetensors import safe_open
    from peft.tuners.lora.layer import LoraLayer
    loaded = get_peft_model_state_dict(model, adapter_name="default")
    path = Path(directory) / "adapter_model.safetensors"
    with safe_open(str(path), framework="pt", device="cpu") as saved:
        keys = set(saved.keys())
        if keys != set(loaded):
            raise ValueError("Adapter state mismatch: missing=" + str(sorted(keys-set(loaded))) +
                             " extra=" + str(sorted(set(loaded)-keys)))
        for key in sorted(keys):
            actual = loaded[key].detach().cpu()
            reference = saved.get_tensor(key)
            if actual.shape != reference.shape or not torch.isfinite(actual).all():
                raise ValueError("Invalid loaded adapter tensor: " + key)
            if not torch.equal(actual.float(), reference.float()):
                raise ValueError("Loaded adapter values differ from checkpoint: " + key)
    modules = []
    magnitude_count = sum("lora_magnitude_vector" in key for key in keys)
    for name, module in model.named_modules():
        if isinstance(module, LoraLayer):
            if bool(module.use_dora["default"]) != expected_dora:
                raise ValueError("Method differs from expected adapter: " + name)
            if not module.lora_B["default"].weight.count_nonzero().item():
                raise ValueError("Zero adapter B matrix: " + name)
            modules.append(dict(name=name, r=module.r["default"],
                                alpha=module.lora_alpha["default"],
                                scaling=module.scaling["default"],
                                use_dora=module.use_dora["default"]))
    if not modules or magnitude_count != (len(modules) if expected_dora else 0):
        raise ValueError("Adapter target/magnitude count mismatch")
    config = model.peft_config["default"]
    if config.modules_to_save or config.bias != "none" or config.fan_in_fan_out:
        raise ValueError("Unsupported nonstandard adapter config for this study")
    expected_targets = set(config.target_modules)
    actual_targets = {m["name"].rsplit(".", 1)[-1] for m in modules}
    layers = model.config.num_hidden_layers
    if actual_targets != expected_targets or len(modules) != layers * len(expected_targets):
        raise ValueError("Adapter target coverage mismatch")
    return dict(status="verified", saved_tensor_count=len(keys),
                exact_loaded_value_match=True, adapted_module_count=len(modules),
                magnitude_vector_count=magnitude_count, modules=modules)
