"""Compatibility check: Qwen2 biased projections, native DoRA versus dense math."""
import unittest

class Qwen2BiasTest(unittest.TestCase):
    def test_biased_native_and_dense_match(self):
        import torch
        from transformers import Qwen2Config,Qwen2ForCausalLM
        from peft import LoraConfig,get_peft_model
        from lora_dora_study.fidelity_audit import convert_custom,without_d
        torch.manual_seed(7);torch.set_num_threads(2)
        config=Qwen2Config(vocab_size=37,hidden_size=16,intermediate_size=24,num_hidden_layers=2,num_attention_heads=2,num_key_value_heads=1)
        model=get_peft_model(Qwen2ForCausalLM(config).float(),LoraConfig(r=2,lora_alpha=4,use_dora=True,target_modules=['q_proj','k_proj','v_proj','o_proj','gate_proj','up_proj','down_proj'])).eval()
        directions={}
        with torch.no_grad():
            for name,m in model.named_modules():
                if not hasattr(m,'use_dora'):continue
                m.lora_B['default'].weight.normal_(std=.02);m.lora_magnitude_vector['default'].weight.mul_(1.07)
                if m.get_base_layer().bias is not None:m.get_base_layer().bias.normal_(std=.03)
                directions[name]=m.get_base_layer().weight+(m.lora_B['default'].weight@m.lora_A['default'].weight)*m.scaling['default']
            ids=torch.tensor([[1,2,3,4]]);native=model(ids).logits
            with without_d(model):removed=model(ids).logits
            convert_custom(model);dense=model(ids).logits
            self.assertTrue(torch.allclose(native,dense,atol=2e-7,rtol=1e-5))
            for name,w in directions.items():model.get_submodule(name).weight.copy_(w)
            self.assertTrue(torch.allclose(removed,model(ids).logits,atol=2e-7,rtol=1e-5))

if __name__=='__main__':unittest.main()
