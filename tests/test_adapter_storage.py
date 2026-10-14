import unittest
import torch
from lora_dora_study.adapter_storage import thin_factors, encode, decode, payload_bytes


class AdapterStorageTests(unittest.TestCase):
    def test_full_rank_roundtrip_and_cost(self):
        torch.manual_seed(17)
        left, right = torch.randn(9, 3), torch.randn(3, 11)
        d = torch.rand(9) + .5
        l, r = thin_factors(left, right, 3)
        self.assertTrue(torch.allclose(l @ r, left @ right, atol=2e-6, rtol=2e-6))
        for mode, factor_bytes, scale_bytes in [('fp16', 2, 0), ('int8', 1, 24)]:
            rec = encode(l, r, d, mode)
            got = decode(rec)
            self.assertTrue(torch.equal(got['row_scale'], d))
            error = (got['left'] @ got['right'] - left @ right).norm() / (left @ right).norm()
            self.assertLess(float(error), .02)
            self.assertEqual(payload_bytes({'x': rec}), (9*3+3*11)*factor_bytes+9*4+scale_bytes)

    def test_zero_components_and_optimal_truncation(self):
        left = torch.diag(torch.tensor([4., 2., 1.]))
        right = torch.eye(3)
        l, r = thin_factors(left, right, 2)
        self.assertAlmostEqual(float((left @ right-l @ r).square().sum()), 1., places=5)
        rec = encode(torch.zeros(3, 2), torch.zeros(2, 4), torch.ones(3), 'int8')
        got = decode(rec)
        self.assertEqual(float(got['left'].abs().sum()+got['right'].abs().sum()), 0.)
        self.assertTrue(torch.isfinite(rec['left_scale']).all())

    def test_reject_overflow_and_incomplete_scale(self):
        with self.assertRaises(FloatingPointError):
            encode(torch.full((3, 2), 1e10), torch.ones(2, 4), torch.ones(3), 'fp16')
        rec = encode(torch.ones(3, 2), torch.ones(2, 4), torch.ones(3), 'int8')
        del rec['right_scale']
        with self.assertRaises(ValueError):
            decode(rec)


if __name__ == '__main__':
    unittest.main()
