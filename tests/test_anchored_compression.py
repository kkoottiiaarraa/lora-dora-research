import importlib.util
import unittest


@unittest.skipUnless(importlib.util.find_spec('torch'),'Torch required')
class AnchorTests(unittest.TestCase):
    def test_independent_layer_gauges_and_scaled_covariance(self):
        import torch
        from lora_dora_study.anchored_compression import anchors,canonical_values
        torch.manual_seed(31)
        m={}
        for layer in [0,1]:
            for leaf in ['v_proj','o_proj']:
                m[f'layers.{layer}.{leaf}']=dict(base=torch.randn(8,8,dtype=torch.float64),value=torch.randn(8,8,dtype=torch.float64))
        transformed={}
        scales={'layers.0':.995,'layers.1':1.005}
        for name,r in m.items():
            c=scales[name.rsplit('.',1)[0]]
            transformed[name]=dict(base=r['base'],value=r['value']*(c if name.endswith('v_proj') else 1/c))
        a,b=canonical_values(m),canonical_values(transformed)
        for name in a:torch.testing.assert_close(a[name],b[name],atol=1e-12,rtol=1e-12)
        for layer,c in scales.items():
            self.assertAlmostEqual(anchors(transformed)[layer]*c,anchors(m)[layer],places=12)
            covariance=torch.eye(8,dtype=torch.float64)
            torch.testing.assert_close(covariance*anchors(m)[layer]**2,
                covariance*c*c*anchors(transformed)[layer]**2)


if __name__=='__main__':unittest.main()
