import unittest
import torch
from lora_dora_study.radial_quotient import coefficients


class RadialQuotientTests(unittest.TestCase):
    def setUp(self):
        torch.manual_seed(20261014)
        self.v = torch.randn(6, 8, dtype=torch.float64)
        self.o = torch.randn(8, 12, dtype=torch.float64)
        self.dv = torch.randn(6, dtype=torch.float64).mul(.1).exp()
        self.do = torch.randn(8, dtype=torch.float64).mul(.1).exp()
        self.x = torch.randn(5, 8, dtype=torch.float64)
        self.p = torch.randn(4, 5, 5, dtype=torch.float64).softmax(-1)

    def block(self, kind, gauge):
        v, o = coefficients(self.dv, self.do, kind, gauge)
        values = (self.x@(v[:, None]*self.v).T).reshape(5, 2, 3).repeat_interleave(2, dim=1)
        context = torch.einsum('hts,shd->thd', self.p, values).reshape(5, 12)
        return context@(o[:, None]*self.o).T

    def test_corrected_and_endpoints_invariant_with_gqa(self):
        for kind in ['source', 'pair_off', 'v_shape_off', 'o_shape_off', 'gain_off']:
            original = self.block(kind, 1.)
            for gauge in [.995, 1.005, 2.]:
                self.assertTrue(torch.allclose(original, self.block(kind, gauge), atol=1e-12, rtol=1e-12))

    def test_raw_interventions_have_predicted_asymmetric_scale(self):
        for gauge in [.995, 1.005, 2.]:
            self.assertTrue(torch.allclose(self.block('raw_v_off', gauge), self.block('raw_v_off', 1.)/gauge, atol=1e-12, rtol=1e-12))
            self.assertTrue(torch.allclose(self.block('raw_o_off', gauge), self.block('raw_o_off', 1.)*gauge, atol=1e-12, rtol=1e-12))

    def test_all_parts_off_and_domain(self):
        a = coefficients(self.dv, self.do, 'all_parts_off')
        b = coefficients(self.dv, self.do, 'pair_off')
        self.assertTrue(all(torch.equal(x, y) for x, y in zip(a, b)))
        with self.assertRaises(ValueError):
            coefficients(-self.dv, self.do, 'gain_off')


if __name__ == '__main__':
    unittest.main()
