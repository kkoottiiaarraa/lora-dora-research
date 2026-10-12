"""Posthoc magnitude/direction interventions; no optimizer or training."""


def apply_intervention(model, method, targets):
    import torch
    from peft.tuners.lora.layer import LoraLayer
    if method == "none":
        return dict(method=method, modules=[])
    if method not in {"base_magnitude", "remove_d"}:
        raise ValueError("Intervention not numerically validated")
    changed = []
    with torch.no_grad():
        for name, module in model.named_modules():
            if not isinstance(module, LoraLayer) or name.rsplit(".", 1)[-1] not in targets:
                continue
            if not module.use_dora["default"]:
                raise ValueError("Magnitude intervention requires DoRA")
            if method == "remove_d":
                module.use_dora["default"] = False
                # PEFT 0.17 dispatches forward through lora_variant, independently
                # of use_dora. Remove the DoRA dispatcher to obtain W0 + sBA.
                module.lora_variant.pop("default", None)
            else:
                magnitude = module.lora_magnitude_vector["default"].weight
                magnitude.copy_(module.get_base_layer().weight.detach().float().norm(dim=1).to(magnitude))
            changed.append(name)
    if not changed:
        raise ValueError("No intervention targets matched")
    return dict(method=method, targets=sorted(targets), modules=changed,
                interpretation="Role in final checkpoint, not proof of a training mechanism")
