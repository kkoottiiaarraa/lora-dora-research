"""Real PEFT CPU integration on a tiny random Qwen3, never downloaded weights."""
import importlib.util
import tempfile
import unittest


@unittest.skipUnless(importlib.util.find_spec("torch") and importlib.util.find_spec("peft"),
                     "GPU-host venv dependencies required")
class AdapterLoadingTests(unittest.TestCase):
    def test_saved_adapter_roundtrip_and_corruption_detection(self):
        import torch
        from transformers import Qwen3Config, Qwen3ForCausalLM
        from peft import LoraConfig, PeftModel, get_peft_model
        from lora_dora_study.adapters import verify_loaded_adapter
        torch.set_num_threads(2)
        config = Qwen3Config(vocab_size=32, hidden_size=32, intermediate_size=64,
                            num_hidden_layers=2, num_attention_heads=4,
                            num_key_value_heads=2, head_dim=8)
        for dora in (False, True):
            with self.subTest(dora=dora), tempfile.TemporaryDirectory() as directory:
                base = Qwen3ForCausalLM(config)
                original = {k: v.clone() for k, v in base.state_dict().items()}
                model = get_peft_model(base, LoraConfig(r=2, lora_alpha=2,
                    target_modules=["q_proj", "v_proj"], use_dora=dora,
                    task_type="CAUSAL_LM"))
                with torch.no_grad():
                    for name, parameter in model.named_parameters():
                        if "lora_B" in name:
                            parameter.normal_(std=.03)
                model.save_pretrained(directory)
                fresh = Qwen3ForCausalLM(config)
                fresh.load_state_dict(original)
                loaded = PeftModel.from_pretrained(fresh, directory).eval()
                report = verify_loaded_adapter(loaded, directory, dora)
                self.assertEqual(report["adapted_module_count"], 4)
                self.assertEqual(report["saved_tensor_count"], 12 if dora else 8)
                inputs = torch.tensor([[1, 2, 3]])
                with torch.inference_mode():
                    before = loaded(inputs).logits
                    merged = loaded.merge_and_unload(safe_merge=True)
                    torch.testing.assert_close(before, merged(inputs).logits, atol=1e-6, rtol=1e-5)
                # Reload and prove the validator catches a silently changed tensor.
                fresh = Qwen3ForCausalLM(config)
                fresh.load_state_dict(original)
                loaded = PeftModel.from_pretrained(fresh, directory)
                with torch.no_grad():
                    next(p for n, p in loaded.named_parameters() if "lora_B" in n).add_(1)
                with self.assertRaises(ValueError):
                    verify_loaded_adapter(loaded, directory, dora)


if __name__ == "__main__":
    unittest.main()
