"""Matched endpoint controls on unchanged, unmerged PEFT DoRA inference.

The native module forward always runs first. Hooks subtract FP32 actions and
cast once to the native output dtype. Scale zero returns the original tensor.
Calibration hooks never change outputs, so every module sees original-model
inputs. Only per-module vectors/scalar sums survive a forward; no activations
or dense correction matrices are retained. Eval-only, dense nn.Linear, one
active adapter; weights and autocast policy must stay fixed for this object's
lifetime. Native g is tapped from PEFT's own get_weight_norm, not re-created.
"""
from contextlib import contextmanager
from dataclasses import dataclass
import hashlib
import math

import torch
import torch.nn.functional as F

KINDS = ("radial", "permuted", "directional")


def row_permutation(name, rows, seed):
    """CPU permutation independent of module traversal/global RNG state."""
    digest = hashlib.sha256(f"{seed}:{name}".encode()).digest()
    generator = torch.Generator(device="cpu").manual_seed(int.from_bytes(digest[:8], "big") % (2**63))
    return torch.randperm(rows, generator=generator)


def matched_scale(reference_energy, control_energy):
    if not all(math.isfinite(v) and v >= 0 for v in (reference_energy, control_energy)):
        raise ValueError("Energies must be finite and nonnegative")
    if reference_energy == 0:
        return 0.0
    if control_energy == 0:
        raise ValueError("Cannot match positive radial energy with a zero control")
    return math.sqrt(reference_energy / control_energy)


@dataclass
class _ModuleState:
    module: object
    permutation: torch.Tensor
    ideal_g: torch.Tensor
    u_row_norm2: torch.Tensor
    l_row_norm2: torch.Tensor
    native_g: object = None
    arithmetic: object = None


class MatchedControls:
    """Construct once; collect training calibration, validate, then intervene.

    ``with controls.calibrate() as cal: model(...)``; ``cal.report()`` yields
    ``scales[kind][module_name]``. Pass that unchanged mapping to
    ``calibrate(scales=...)`` on disjoint validation prompts and to
    ``intervene(kind, scales[kind])``. Data split/provenance and acceptance
    thresholds belong to the runner. Calibration weights tokens equally;
    use batch=1 without padding (padding masks are not inferred by hooks).
    """
    def __init__(self, model, targets=("q_proj", "k_proj", "v_proj", "o_proj"),
                 adapter="default", seed=1729, row_chunk=1024, token_chunk=128):
        from peft.tuners.lora.layer import Linear
        if model.training or row_chunk < 1 or token_chunk < 1:
            raise ValueError("Require eval model and positive chunk sizes")
        self.model, self.adapter, self.seed = model, adapter, seed
        self.row_chunk, self.token_chunk = row_chunk, token_chunk
        self.modules = {}
        self._busy = False
        with torch.no_grad():
            for name, module in model.named_modules():
                if not isinstance(module, Linear) or name.rsplit(".", 1)[-1] not in targets:
                    continue
                if (module.merged or module.disable_adapters or module.fan_in_fan_out or
                    module.active_adapters != [adapter] or not module.use_dora.get(adapter, False) or
                    not isinstance(module.get_base_layer(), torch.nn.Linear) or
                    module.get_base_layer().weight.__class__ is not torch.nn.Parameter):
                    raise ValueError(f"Unsupported dense single-adapter DoRA module: {name}")
                a = module.lora_A[adapter].weight.detach().float().cpu()
                b = module.lora_B[adapter].weight.detach().float().cpu()
                weight = module.get_base_layer().weight
                norms, lnorms = [], []
                with torch.autocast("cpu", enabled=False):
                    for start in range(0, weight.shape[0], row_chunk):
                        low_rank = (b[start:start + row_chunk] @ a) * module.scaling[adapter]
                        direction = weight[start:start + row_chunk].detach().float().cpu() + low_rank
                        norms.append(direction.square().sum(1))
                        lnorms.append(low_rank.square().sum(1))
                norm2 = torch.cat(norms)
                if not torch.isfinite(norm2).all() or (norm2 <= 0).any():
                    raise ValueError(f"Invalid direction row norms in {name}")
                ideal_g = module.lora_magnitude_vector[adapter].weight.detach().float().cpu() / norm2.sqrt()
                self.modules[name] = _ModuleState(module, row_permutation(name, weight.shape[0], seed),
                                                  ideal_g, norm2, torch.cat(lnorms))
        if not self.modules:
            raise ValueError("No DoRA targets matched")

    def _check_module(self, state):
        module = state.module
        if module.training or module.merged or module.disable_adapters or module.active_adapters != [self.adapter]:
            raise ValueError("DoRA state changed after controls were constructed")

    @contextmanager
    def _hooks(self, hook):
        if self._busy:
            raise RuntimeError("Control contexts cannot overlap")
        self._busy = True
        handles, restore = [], []
        try:
            for name, state in self.modules.items():
                self._check_module(state)
                magnitude = state.module.lora_magnitude_vector[self.adapter]
                # Preserve whether the method originally existed in the instance
                # dictionary; restoring only a bound method would leave a shadow.
                previous = magnitude.__dict__.get("get_weight_norm")
                original = magnitude.get_weight_norm
                def tap(*args, _original=original, _state=state, _magnitude=magnitude, **kwargs):
                    norm = _original(*args, **kwargs)
                    device = norm.device.type
                    signature = (device, str(norm.dtype), torch.is_autocast_enabled(device),
                                 str(torch.get_autocast_dtype(device)))
                    if _state.arithmetic is not None and _state.arithmetic != signature:
                        raise ValueError("Autocast/norm arithmetic changed since native g capture")
                    if _state.native_g is None:
                        _state.native_g = (_magnitude.weight.detach() / norm.detach()).float().cpu()
                        if not torch.isfinite(_state.native_g).all():
                            raise ValueError("Native PEFT radial coefficients are nonfinite")
                        _state.arithmetic = signature
                    return norm
                magnitude.get_weight_norm = tap
                restore.append((magnitude, previous))
                handles.append(state.module.register_forward_hook(
                    lambda module, inputs, output, _name=name: hook(_name, inputs[0], output)))
            yield
        finally:
            for handle in handles:
                handle.remove()
            for magnitude, previous in restore:
                if previous is None:
                    del magnitude.get_weight_norm
                else:
                    magnitude.get_weight_norm = previous
            self._busy = False

    def actions(self, name, x, kinds=KINDS):
        """FP32 ideal linear actions using actual captured native PEFT g.

        Bias is excluded. FP32 matmul order differs from PEFT and is measured
        against native remove_D during calibration. Call in no_grad mode.
        """
        state = self.modules[name]
        if state.native_g is None:
            raise RuntimeError("Capture native g with an original forward first")
        if any(kind not in KINDS for kind in kinds):
            raise ValueError("Unknown control")
        module, adapter = state.module, self.adapter
        self._check_module(state)
        with torch.autocast(x.device.type, enabled=False):
            x32 = x.float()
            a = module.lora_A[adapter].weight.detach().float()
            b = module.lora_B[adapter].weight.detach().float()
            low_rank = F.linear(F.linear(x32, a), b) * module.scaling[adapter]
            result = {}
            if "directional" in kinds:
                result["directional"] = low_rank
            if "radial" in kinds or "permuted" in kinds:
                weight = module.get_base_layer().weight
                direction = torch.empty_like(low_rank)
                for start in range(0, weight.shape[0], self.row_chunk):
                    direction[..., start:start + self.row_chunk] = (
                        F.linear(x32, weight[start:start + self.row_chunk].detach().float()) +
                        low_rank[..., start:start + self.row_chunk])
                gminus = (state.native_g - 1).to(x.device)
                if "radial" in kinds:
                    result["radial"] = direction * gminus
                if "permuted" in kinds:
                    result["permuted"] = direction * gminus[state.permutation.to(x.device)]
        return result

    @contextmanager
    def calibrate(self, scales=None):
        """Observe original forwards only; optional fixed scales audit casting."""
        calibration = Calibration(self, scales)
        with torch.no_grad(), self._hooks(calibration.observe):
            yield calibration

    @contextmanager
    def intervene(self, kind, scales):
        """Subtract c*control from native output, with one final dtype cast."""
        if kind not in KINDS or set(scales) != set(self.modules):
            raise ValueError("Require a supported kind and exactly one scale per module")
        if any(not math.isfinite(c) or c < 0 for c in scales.values()):
            raise ValueError("Scales must be finite and nonnegative")
        def hook(name, x, output):
            scale = scales[name]
            if scale == 0:
                return output
            flat_x = x.reshape(-1, x.shape[-1])
            flat_y = output.reshape(-1, output.shape[-1])
            changed = torch.empty_like(flat_y)
            for start in range(0, len(flat_x), self.token_chunk):
                stop = start + self.token_chunk
                action = self.actions(name, flat_x[start:stop], (kind,))[kind]
                changed[start:stop] = (flat_y[start:stop].float() - scale * action).to(output.dtype)
            return changed.reshape(output.shape)
        with torch.no_grad(), self._hooks(hook):
            yield


class Calibration:
    def __init__(self, controls, scales):
        self.controls, self.scales = controls, scales
        if scales is not None:
            for kind, values in scales.items():
                if kind not in KINDS or set(values) != set(controls.modules):
                    raise ValueError("Validation scales do not match all target modules")
                if any(not math.isfinite(c) or c < 0 for c in values.values()):
                    raise ValueError("Invalid validation scale")
        self.sums = {name: dict(tokens=0, calls=0, radial=0.0, permuted=0.0, directional=0.0,
                               native_remove=0.0, radial_vs_native_remove_error=0.0,
                               realized={}, rounding_error={}) for name in controls.modules}

    @staticmethod
    def _energy(value):
        # FP64 scalar accumulation, bounded per-token chunk temporary.
        return value.double().square().sum().item()

    def observe(self, name, x, output):
        control = self.controls
        module, adapter = control.modules[name].module, control.adapter
        stats = self.sums[name]
        stats["calls"] += 1
        flat_x, flat_y = x.reshape(-1, x.shape[-1]), output.reshape(-1, output.shape[-1])
        stats["tokens"] += len(flat_x)
        # Native remove_D diagnostic uses the same low-rank casting/scaling
        # order as PEFT Linear.forward with its DoRA dispatcher disabled.
        native_base = module.get_base_layer()(x)
        adapter_x = module._cast_input_dtype(x, module.lora_A[adapter].weight.dtype)
        native_lora = module.lora_B[adapter](module.lora_A[adapter](adapter_x))
        native_remove = (native_base + native_lora * module.scaling[adapter]).to(output.dtype)
        native_delta = (output.float() - native_remove.float()).reshape(flat_y.shape)
        for start in range(0, len(flat_x), control.token_chunk):
            stop = start + control.token_chunk
            actions = control.actions(name, flat_x[start:stop])
            original = flat_y[start:stop].float()
            for kind, action in actions.items():
                stats[kind] += self._energy(action)
            stats["native_remove"] += self._energy(native_delta[start:stop])
            stats["radial_vs_native_remove_error"] += self._energy(actions["radial"] - native_delta[start:stop])
            if self.scales is not None:
                for kind, scales in self.scales.items():
                    ideal_delta = actions[kind] * scales[name]
                    changed = (original - ideal_delta).to(output.dtype).float()
                    actual_delta = original - changed
                    stats["realized"][kind] = stats["realized"].get(kind, 0.0) + self._energy(actual_delta)
                    stats["rounding_error"][kind] = stats["rounding_error"].get(kind, 0.0) + self._energy(actual_delta - ideal_delta)
        # Returning None explicitly preserves every original module output.
        return None

    def report(self):
        scales = {kind: {} for kind in ("permuted", "directional")}
        modules = {}
        for name, stats in self.sums.items():
            if stats["calls"] == 0:
                raise ValueError(f"No original-model calibration activations for {name}")
            state = self.controls.modules[name]
            gminus = state.native_g - 1
            modules[name] = dict(stats)
            modules[name]["native_arithmetic"] = state.arithmetic
            modules[name]["native_g_vs_ideal_fp32_g_max_abs"] = (state.native_g - state.ideal_g).abs().max().item()
            modules[name]["weight_frobenius_squared"] = {
                "radial": (gminus.double().square() * state.u_row_norm2.double()).sum().item(),
                "permuted": (gminus[state.permutation].double().square() * state.u_row_norm2.double()).sum().item(),
                "directional": state.l_row_norm2.double().sum().item()}
            modules[name]["radial_vs_native_remove_relative_rms"] = (
                math.sqrt(stats["radial_vs_native_remove_error"] / stats["native_remove"])
                if stats["native_remove"] else None)
            for kind in scales:
                scales[kind][name] = matched_scale(stats["native_remove"], stats[kind])
        return dict(seed=self.controls.seed, modules=modules, scales=scales,
                    applied_scales=self.scales,
                    energy_target="actual native DoRA minus native remove_D output, on original-model inputs",
                    numeric_path="native PEFT output minus FP32 action, cast once to native dtype",
                    limitations=["Scale zero is exact; nonzero paths differ from native remove_D ordering.",
                                 "Native g and weights require fixed autocast/eval inference policy.",
                                 "Token-weighted unpadded calibration; split/test isolation is runner responsibility."])
