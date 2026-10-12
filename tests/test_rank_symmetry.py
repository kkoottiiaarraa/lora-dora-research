import importlib.util
import unittest

@unittest.skipUnless(importlib.util.find_spec('torch'), 'Requires PyTorch')
class RankSymmetryTests(unittest.TestCase):

    def test_svd_adaptive_rank_and_measured_activation_error(self):
        import torch
        from lora_dora_study.rank_symmetry import compressed_update, activation_error
        delta = torch.diag(torch.tensor([4.0, 2.0, 1.0, 0.5]))
        approximation, report = compressed_update(delta, energy=0.94)
        self.assertEqual(report['rank'], 2)
        self.assertAlmostEqual(report['retained_energy'], 20 / 21.25)
        error = activation_error(delta, approximation, torch.eye(4))
        self.assertAlmostEqual(error['relative_squared_error'], 1.25 / 21.25)
        full, _ = compressed_update(delta, rank=4)
        torch.testing.assert_close(full, delta)

    def test_actual_qwen3_qknorm_rope_gqa_vo_symmetry_and_dora_dense_fidelity(self):
        import torch
        from transformers import Qwen3Config, Qwen3ForCausalLM
        from peft import get_peft_model, LoraConfig
        from lora_dora_study.rank_symmetry import prepare
        torch.set_num_threads(2)
        for dora in [False, True]:
            torch.manual_seed(19)
            config = Qwen3Config(vocab_size=32, hidden_size=32, intermediate_size=64, num_hidden_layers=3, num_attention_heads=4, num_key_value_heads=2, head_dim=8)
            model = get_peft_model(Qwen3ForCausalLM(config), LoraConfig(r=2, lora_alpha=2, target_modules=['q_proj', 'k_proj', 'v_proj', 'o_proj'], use_dora=dora, task_type='CAUSAL_LM')).eval()
            with torch.no_grad():
                for name, p in model.named_parameters():
                    if 'lora_B' in name:
                        p.normal_(std=0.03)
                    if 'lora_magnitude_vector' in name:
                        p.mul_(1.1)
            inputs = dict(input_ids=torch.tensor([[1, 2, 3, 4, 5]]))
            with torch.inference_mode():
                before = model(**inputs).logits
            report = prepare(model, dict(intervention='vo_symmetry', rank=2, targets=['q_proj', 'k_proj', 'v_proj', 'o_proj'], calibration='synthetic'), inputs)
            with torch.inference_mode():
                after = model(**inputs).logits
            torch.testing.assert_close(before, after, atol=1e-06, rtol=1e-05)
            self.assertLess(report['dense_fidelity']['max_abs_logits_error'], 1e-06)
            self.assertLess(report['symmetry_logits_max_abs_error'], 1e-06)
            self.assertNotAlmostEqual(report['correlation_before'], report['correlation_joint_base_after'], places=5)

    def test_full_tiny_dora_rank_compression_and_lora_impact_control(self):
        import json
        import tempfile
        from pathlib import Path
        import torch
        from transformers import Qwen3Config, Qwen3ForCausalLM
        from peft import get_peft_model, LoraConfig
        from peft.tuners.lora.layer import LoraLayer
        from lora_dora_study.rank_symmetry import prepare
        torch.set_num_threads(2)
        reports = []
        with tempfile.TemporaryDirectory() as directory:
            manifest = Path(directory) / 'impact.json'
            for dora in [True, False]:
                torch.manual_seed(7)
                config = Qwen3Config(vocab_size=32, hidden_size=32, intermediate_size=64, num_hidden_layers=2, num_attention_heads=4, num_key_value_heads=2, head_dim=8)
                model = get_peft_model(Qwen3ForCausalLM(config), LoraConfig(r=2, lora_alpha=2, target_modules=['q_proj', 'k_proj', 'v_proj', 'o_proj'], use_dora=dora, task_type='CAUSAL_LM')).eval()
                with torch.no_grad():
                    for name, p in model.named_parameters():
                        if 'lora_B' in name:
                            p.normal_(std=0.03)
                        if 'lora_magnitude_vector' in name:
                            p.mul_(1.1)
                bases = {name: module.get_base_layer().weight.detach().clone() for name, module in model.named_modules() if isinstance(module, LoraLayer)}
                report = prepare(model, dict(intervention='rank_fixed' if dora else 'rank_lora_control', rank=2, targets=['q_proj', 'k_proj', 'v_proj', 'o_proj'], calibration='synthetic', impact_manifest=str(manifest)), dict(input_ids=torch.tensor([[1, 2, 3, 4, 5]])))
                for name, base in bases.items():
                    singular = torch.linalg.svdvals(model.get_submodule(name).weight.detach() - base)
                    self.assertLess(float(singular[2]), 1e-06)
                reports.append(report)
                if dora:
                    manifest.write_text(json.dumps(report))
            for a, b in zip(reports[0]['modules'], reports[1]['modules']):
                self.assertAlmostEqual(a['activation']['relative_squared_error'], b['activation']['relative_squared_error'], places=5)
if __name__ == '__main__':
    unittest.main()
