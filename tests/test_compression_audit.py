import importlib.util
import unittest

from lora_dora_study.compression_audit import practical_gate


class GateTests(unittest.TestCase):
    def test_strict_boundaries_and_zero_denominator(self):
        self.assertFalse(practical_gate(.2, .001, 1)['passed'])
        self.assertFalse(practical_gate(.21, .021, 1)['passed'])
        self.assertTrue(practical_gate(.21, .001, 1)['passed'])
        self.assertIsNone(practical_gate(0, 0, 0)['drift_over_compression'])
        for value in [float('nan'), float('inf'), -1]:
            with self.assertRaises(ValueError):practical_gate(value, 0, 1)


@unittest.skipUnless(importlib.util.find_spec('torch') and importlib.util.find_spec('peft'), 'Torch/PEFT required')
class ModelTests(unittest.TestCase):
    def test_diagonal_svd_matches_independent_optimum(self):
        import torch
        from lora_dora_study.compression_audit import decompose, factorized_module
        base = torch.eye(4)
        value = base+torch.diag(torch.tensor([.1, -.8, 2., .3]))
        r = decompose(base, value, 2)
        expected = base+torch.diag(torch.tensor([0., -.8, 2., 0.]))
        x = torch.arange(12, dtype=torch.float32).reshape(3, 4)/7
        torch.testing.assert_close(factorized_module(r)(x), x@expected.T)
        self.assertEqual(r['info']['factor_elements'], 16)
        self.assertAlmostEqual(r['info']['squared_residual'], .1, places=5)

    def test_scope_exception_and_full_rank_network_fidelity(self):
        import torch
        from test_fidelity_audit import TinyModelTests
        from lora_dora_study.compression_audit import scoped_gauge, selected_modules, replacement, decompose
        from lora_dora_study.rank_symmetry import effective_weight
        m = TinyModelTests().model()
        before = {k: v.clone() for k, v in m.state_dict().items()}
        x = torch.tensor([[1, 2, 3, 4]])
        with torch.inference_mode():
            original = m(x, use_cache=False).logits
            with scoped_gauge(m, [0], 1.005):
                self.assertTrue(all(torch.equal(v, m.state_dict()[k]) for k, v in before.items() if '.layers.1.' in k))
                torch.testing.assert_close(m(x, use_cache=False).logits, original, atol=2e-6, rtol=2e-5)
                records = {}
                for name, module in selected_modules(m, [0]).items():
                    base, value = effective_weight(module)
                    records[name] = decompose(base, value, min(value.shape))
                for kind in ['source_dense', 'compressed_dense', 'factorized']:
                    with replacement(m, [0], kind, records):
                        torch.testing.assert_close(m(x, use_cache=False).logits, original, atol=2e-6, rtol=2e-5)
                with self.assertRaisesRegex(RuntimeError, 'fixture'):
                    with replacement(m, [0], 'factorized', records):raise RuntimeError('fixture')
            self.assertTrue(all(torch.equal(v, m.state_dict()[k]) for k, v in before.items()))
            with self.assertRaisesRegex(RuntimeError, 'fixture'):
                with scoped_gauge(m, [0], .995):raise RuntimeError('fixture')
            self.assertTrue(all(torch.equal(v, m.state_dict()[k]) for k, v in before.items()))

    def test_factor_path_is_deployed_and_has_no_dense_update(self):
        import torch
        from unittest.mock import patch
        from lora_dora_study.compression_audit import decompose, factorized_module
        base = torch.eye(8)
        record = decompose(base, base+torch.diag(torch.arange(8, dtype=torch.float32)), 2)
        module = factorized_module(record)
        self.assertEqual({k: tuple(v.shape) for k, v in module.named_buffers()},
                         {'base': (8, 8), 'left': (8, 2), 'right': (2, 8)})
        self.assertFalse(list(module.parameters()))
        original = torch.nn.functional.linear
        with patch('torch.nn.functional.linear', wraps=original) as linear:
            module(torch.ones(1, 8))
            self.assertEqual(linear.call_count, 3)


if __name__ == '__main__':unittest.main()
