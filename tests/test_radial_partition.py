import unittest
import torch
from peft import LoraConfig,get_peft_model
from lora_dora_study.radial_partition import components,intervention,target_magnitude


class Fixture(torch.nn.Module):
    def __init__(self):
        super().__init__();self.proj=torch.nn.Linear(5,4,bias=False)
    def forward(self,x):return self.proj(x)


class RadialPartitionTests(unittest.TestCase):
    def fixture(self):
        torch.manual_seed(78);m=get_peft_model(Fixture(),LoraConfig(r=2,lora_alpha=4,target_modules=['proj'],use_dora=True))
        with torch.no_grad():
            layer=m.base_model.model.proj;layer.lora_B['default'].weight.normal_(0,.08)
            layer.lora_magnitude_vector['default'].weight.mul_(torch.tensor([.85,1.03,1.12,.94]))
        return m.eval(),layer

    def test_decomposition_and_distinct_counterfactuals(self):
        model,layer=self.fixture();p=components(layer)
        torch.testing.assert_close(p['learned']*p['normalization'],p['d'])
        torch.testing.assert_close(p['gain']*p['shape'],p['d'])
        torch.testing.assert_close(target_magnitude(p,'base_magnitude')/p['norm'],p['normalization'])
        torch.testing.assert_close(target_magnitude(p,'learned_only')/p['norm'],p['learned'])
        self.assertFalse(torch.allclose(p['learned'],p['normalization']))
        x=torch.randn(3,5);original=model(x).detach().clone();m0=layer.lora_magnitude_vector['default'].weight.detach().clone()
        for condition in ['base_magnitude','learned_only','scalar_d','centered_d']:
            with intervention(model,condition):self.assertFalse(torch.equal(model(x),original))
            self.assertTrue(torch.equal(layer.lora_magnitude_vector['default'].weight,m0));self.assertTrue(torch.equal(model(x),original))
        with self.assertRaises(RuntimeError):
            with intervention(model,'centered_d'):raise RuntimeError('deliberate caller failure')
        self.assertTrue(torch.equal(layer.lora_magnitude_vector['default'].weight,m0))

    def test_scalar_and_shape_under_source_rescaling(self):
        model,layer=self.fixture();p=components(layer)
        with torch.no_grad():layer.lora_magnitude_vector['default'].weight.mul_(1.4)
        q=components(layer)
        torch.testing.assert_close(q['shape'],p['shape'])
        torch.testing.assert_close(q['gain'],p['gain']*1.4)
        torch.testing.assert_close(target_magnitude(q,'centered_d'),target_magnitude(p,'centered_d'))
        torch.testing.assert_close(target_magnitude(q,'scalar_d'),target_magnitude(p,'scalar_d')*1.4)


if __name__=='__main__':unittest.main()
