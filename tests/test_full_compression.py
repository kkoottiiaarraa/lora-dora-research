import importlib.util
import unittest

from lora_dora_study.full_compression import structural_ranks


class BudgetTests(unittest.TestCase):
    def test_entire_adapter_equal_size_including_diagonal(self):
        shapes = {f'{i}.{leaf}': shape for i in range(36) for leaf, shape in
                  [('q', (4096, 2560)), ('k', (1024, 2560)),
                   ('v', (1024, 2560)), ('o', (2560, 4096))]}
        for rank in [8, 16]:
            ranks = structural_ranks(shapes, rank)
            self.assertEqual(set(ranks), set(shapes))
            self.assertTrue(set(ranks.values()) <= {rank-1, rank})
            self.assertEqual(sum(ranks[n]*sum(s)+s[0] for n,s in shapes.items()),
                             rank*sum(sum(s) for s in shapes.values()))
            self.assertEqual(ranks, structural_ranks(shapes, rank))


@unittest.skipUnless(importlib.util.find_spec('torch'), 'Torch required')
class StructuralTests(unittest.TestCase):
    def test_thin_weighted_optimum_and_full_rank(self):
        import torch
        from lora_dora_study.full_compression import thin_weighted_factors, module_from_record
        from lora_dora_study.weighted_compression import covariance_cholesky, weighted_factors
        torch.set_num_threads(2);torch.manual_seed(31)
        base = torch.randn(9, 10)
        a, b = torch.randn(9, 4), torch.randn(4, 10)
        scale = torch.rand(9)+.5
        a = a*scale[:, None]
        inputs = torch.randn(48, 10)
        chol, _ = covariance_cholesky(inputs)
        for rank in [2, 4]:
            factors, _ = thin_weighted_factors(a, b, chol, rank)
            left, right, _ = weighted_factors(a@b, chol, rank)
            torch.testing.assert_close(factors['left']@factors['right'], left@right, atol=3e-5, rtol=3e-5)
            if rank == 4:
                module = module_from_record(dict(base=base, row_scale=scale, **factors))
                expected = inputs@(scale[:,None]*base+a@b).T
                torch.testing.assert_close(module(inputs), expected, atol=3e-5, rtol=3e-5)

    def test_tiny_qwen_all_projections_and_exception_restore(self):
        import torch
        from transformers import Qwen3Config, Qwen3ForCausalLM
        from peft import LoraConfig, get_peft_model
        from lora_dora_study.full_compression import adapted_modules, replace_all
        torch.manual_seed(32)
        model = get_peft_model(Qwen3ForCausalLM(Qwen3Config(vocab_size=40, hidden_size=32,
            intermediate_size=64, num_hidden_layers=2, num_attention_heads=4,
            num_key_value_heads=2, head_dim=8)), LoraConfig(r=4, lora_alpha=8,
                use_dora=True, target_modules=['q_proj','k_proj','v_proj','o_proj'])).eval()
        records = {}
        with torch.no_grad():
            for name, module in adapted_modules(model).items():
                module.lora_B['default'].weight.normal_(std=.02)
                base=module.get_base_layer().weight
                a=module.lora_A['default'].weight;b=module.lora_B['default'].weight
                u=base+(b@a)*module.scaling['default']
                d=module.lora_magnitude_vector['default'].weight/u.norm(dim=1)
                records[name]=dict(left=b*module.scaling['default']*d[:,None],
                                   right=a, row_scale=d)
            ids=torch.tensor([[1,2,3,4]])
            before=model(ids).logits
            with replace_all(model, records):
                torch.testing.assert_close(model(ids).logits, before, atol=1e-6, rtol=1e-5)
            with self.assertRaises(RuntimeError):
                with replace_all(model, records): raise RuntimeError('restore')
            torch.testing.assert_close(model(ids).logits, before, atol=0, rtol=0)
            self.assertEqual(len(adapted_modules(model)), 8)


if __name__ == '__main__': unittest.main()
