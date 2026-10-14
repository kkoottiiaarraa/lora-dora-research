import unittest
import torch
from transformers import Qwen3Config,Qwen3ForCausalLM
from peft import LoraConfig,get_peft_model
from lora_dora_study.precision_ablation import place_transformer,stream_dense,apply_dense_without_d,fingerprints,load_explicit_cpu
from lora_dora_study.fidelity_audit import without_d


def make(dtype):
    torch.manual_seed(33)
    cfg=Qwen3Config(vocab_size=48,hidden_size=32,intermediate_size=64,num_hidden_layers=1,
        num_attention_heads=4,num_key_value_heads=2,head_dim=8,attention_bias=False,tie_word_embeddings=False)
    cfg._attn_implementation='sdpa'
    model=get_peft_model(Qwen3ForCausalLM(cfg).to(dtype),LoraConfig(r=2,lora_alpha=4,
        target_modules=['q_proj','k_proj','v_proj','o_proj'],use_dora=True)).eval()
    with torch.no_grad():
        for module in model.modules():
            if hasattr(module,'lora_B') and 'default' in module.lora_B:
                module.lora_B['default'].weight.uniform_(-.02,.02)
                m=module.lora_magnitude_vector['default'].weight
                m.mul_(torch.linspace(.98,1.02,len(m)))
    return model.requires_grad_(False)


def run(model):
    with torch.inference_mode():return model(input_ids=torch.tensor([[2,4,8,3]]),use_cache=False).logits


class PrecisionAblationTests(unittest.TestCase):
    def test_fp32_placement_dense_and_restoration(self):
        model=make(torch.float32);original=run(model)
        place_transformer(model,'cpu',torch.float32)
        self.assertTrue(torch.equal(original,run(model)))
        with without_d(model):removed=run(model)
        self.assertGreater(float((original-removed).abs().max()),1e-7)
        self.assertTrue(torch.equal(original,run(model)))
        unscaled,_=stream_dense(model)
        self.assertTrue(torch.allclose(original,run(model),atol=2e-7,rtol=2e-6))
        apply_dense_without_d(model,unscaled)
        self.assertTrue(torch.allclose(removed,run(model),atol=2e-7,rtol=2e-6))

    def test_explicit_cpu_save_reload(self):
        import tempfile
        from pathlib import Path
        source=make(torch.float32)
        with tempfile.TemporaryDirectory() as folder:
            folder=Path(folder)
            torch.manual_seed(33)
            base=Qwen3ForCausalLM(source.get_base_model().config)
            base.save_pretrained(folder/'base')
            source.save_pretrained(folder/'adapter')
            reloaded=load_explicit_cpu(folder/'base',folder/'adapter',torch.float32)
            self.assertTrue(all(p.device.type=='cpu' and not p.is_meta for p in reloaded.parameters()))
            self.assertTrue(torch.equal(run(source),run(reloaded)))
            place_transformer(reloaded,'cpu',torch.float32)
            self.assertTrue(torch.equal(run(source),run(reloaded)))

    def test_offloaded_head_fp32_and_official_bytes(self):
        for dtype in [torch.float32,torch.bfloat16]:
            custom=place_transformer(make(dtype),'cpu',dtype)
            self.assertEqual(run(custom).dtype,torch.float32)
            self.assertTrue(torch.isfinite(run(custom)).all())
            stream_dense(custom);expected=fingerprints(custom)
            official=place_transformer(make(dtype),'cpu',dtype).merge_and_unload(safe_merge=True)
            self.assertEqual(expected,fingerprints(official))
            self.assertTrue(torch.equal(run(custom),run(official)))


if __name__=='__main__':unittest.main()
