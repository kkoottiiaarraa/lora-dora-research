"""Small CPU checks against actual installed PEFT, no downloaded fixtures."""
import copy
import math
import unittest

import torch
from peft import LoraConfig, get_peft_model

from lora_dora_study.matched_controls import MatchedControls, matched_scale, row_permutation


class TinyModel(torch.nn.Module):
    def __init__(self, dtype=torch.float32):
        super().__init__()
        self.q_proj = torch.nn.Linear(7, 5, bias=True, dtype=dtype)

    def forward(self, x):
        return self.q_proj(x)


def fixture(dtype=torch.float32):
    torch.manual_seed(741)
    model = get_peft_model(TinyModel(dtype), LoraConfig(
        r=3, lora_alpha=4, lora_dropout=0.2, target_modules=["q_proj"], use_dora=True)).eval()
    module = model.base_model.model.q_proj
    with torch.no_grad():
        module.lora_A["default"].weight.normal_(std=0.2)
        module.lora_B["default"].weight.normal_(std=0.15)
        module.lora_magnitude_vector["default"].weight.mul_(torch.tensor([0.8, 1.1, 0.95, 1.2, 1.05]))
    x = torch.randn(2, 4, 7).to(dtype)
    return model, module, x


class MatchedControlsTests(unittest.TestCase):
    def test_permutation_reproducible_independent_of_global_rng(self):
        first = row_permutation("layer.q", 97, 1729)
        torch.rand(100)
        self.assertTrue(torch.equal(first, row_permutation("layer.q", 97, 1729)))
        self.assertFalse(torch.equal(first, row_permutation("layer.k", 97, 1729)))
        self.assertEqual(sorted(first.tolist()), list(range(97)))

    def test_scalar_match_and_degenerate_cases(self):
        self.assertEqual(matched_scale(9, 4), 1.5)
        self.assertEqual(matched_scale(0, 0), 0)
        for reference, control in ((1, 0), (-1, 1), (1, float("nan"))):
            with self.assertRaises(ValueError):
                matched_scale(reference, control)

    def test_fp32_algebra_bias_excluded_calibration_scale_native_remove(self):
        model, module, x = fixture()
        controls = MatchedControls(model, row_chunk=2, token_chunk=3)
        name = next(iter(controls.modules))
        magnitude = module.lora_magnitude_vector["default"]
        had_instance_norm = "get_weight_norm" in magnitude.__dict__
        with torch.no_grad():
            original = model(x)
            with controls.calibrate() as calibration:
                calibrated = model(x)
            self.assertTrue(torch.equal(original, calibrated))
            self.assertEqual("get_weight_norm" in magnitude.__dict__, had_instance_norm)
            state = controls.modules[name]
            weight = module.get_base_layer().weight.float()
            low_rank = module.lora_B["default"].weight @ module.lora_A["default"].weight * module.scaling["default"]
            direction = weight + low_rank
            gminus = state.native_g - 1
            actions = controls.actions(name, x)
            torch.testing.assert_close(actions["radial"], x @ (direction * gminus[:, None]).T)
            torch.testing.assert_close(actions["permuted"], x @ (direction * gminus[state.permutation, None]).T)
            torch.testing.assert_close(actions["directional"], x @ low_rank.T)
            # The copied installed PEFT dispatcher provides an independent native
            # remove_D target, including bias and native output casting.
            removed = copy.deepcopy(model)
            removed_module = removed.base_model.model.q_proj
            removed_module.use_dora["default"] = False
            removed_module.lora_variant.pop("default")
            native_energy = (original.double() - removed(x).double()).square().sum().item()
            report = calibration.report()
            stats = report["modules"][name]
            self.assertAlmostEqual(stats["native_remove"], native_energy, places=8)
            self.assertEqual(stats["tokens"], 8)
            for kind in ("permuted", "directional"):
                scale = report["scales"][kind][name]
                self.assertAlmostEqual(scale * scale * stats[kind], native_energy, places=8)
            with controls.intervene("permuted", {name: 0.7}):
                changed = model(x)
            torch.testing.assert_close(changed, original - 0.7 * actions["permuted"])

    def test_bf16_zero_path_native_capture_and_heldout_rounding(self):
        model, module, x = fixture(torch.bfloat16)
        controls = MatchedControls(model, row_chunk=2, token_chunk=3)
        name = next(iter(controls.modules))
        with torch.no_grad(), torch.autocast("cpu", dtype=torch.bfloat16):
            original = model(x)
            # A fresh object can run no-op prior to calibration: tap captures g
            # without changing PEFT's returned norm or native module output.
            with controls.intervene("permuted", {name: 0.0}):
                self.assertTrue(torch.equal(original, model(x)))
            with controls.calibrate() as calibration:
                self.assertTrue(torch.equal(original, model(x)))
            report = calibration.report()
            removed = copy.deepcopy(model)
            removed_module = removed.base_model.model.q_proj
            removed_module.use_dora["default"] = False
            removed_module.lora_variant.pop("default")
            actual_energy = (original.float() - removed(x).float()).double().square().sum().item()
            self.assertEqual(report["modules"][name]["native_remove"], actual_energy)
            validation_x = x * 0.7
            with controls.calibrate(scales=report["scales"]) as validation:
                model(validation_x)
            val = validation.report()
            for kind in ("permuted", "directional"):
                self.assertGreaterEqual(val["modules"][name]["rounding_error"][kind], 0)
                with controls.intervene(kind, report["scales"][kind]):
                    changed = model(validation_x)
                actual_delta = model(validation_x).float() - changed.float()
                expected_energy = actual_delta.double().square().sum().item()
                self.assertAlmostEqual(val["modules"][name]["realized"][kind], expected_energy, places=8)
            self.assertEqual(val["applied_scales"], report["scales"])
            self.assertTrue(all(math.isfinite(v) for kind in report["scales"].values() for v in kind.values()))
        # Reusing captured coefficients with a different norm path is rejected.
        with controls.calibrate():
            with self.assertRaisesRegex(ValueError, "arithmetic changed"):
                model(x)
        self.assertFalse(controls._busy)

    def test_reject_training_overlapping_context_and_missing_activations(self):
        model, _, x = fixture()
        with self.assertRaises(ValueError):
            MatchedControls(model.train())
        controls = MatchedControls(model.eval())
        with controls.calibrate() as calibration:
            with self.assertRaises(RuntimeError):
                with controls.calibrate():
                    pass
        with self.assertRaisesRegex(ValueError, "No original-model"):
            calibration.report()
        with self.assertRaises(ValueError):
            with controls.intervene("permuted", {}):
                pass
        with controls.calibrate():
            model(x)
        self.assertFalse(controls._busy)


if __name__ == "__main__":
    torch.set_num_threads(2)
    unittest.main()
