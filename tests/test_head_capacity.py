import unittest
import torch
from lora_dora_study.head_capacity import analyze


class HeadCapacityTests(unittest.TestCase):
    def test_diagonal_rotation_has_real_extra_output_directions(self):
        base=torch.tensor([[1.,0.],[0.,1.],[1.,0.],[0.,1.],[0.,0.],[0.,0.]],dtype=torch.float64)
        x=torch.eye(2,dtype=torch.float64)
        d=torch.tensor([1.,1.,2.,3.,1.,1.],dtype=torch.float64)
        result=analyze(base,d[:,None]*base,x,1)
        self.assertGreater(result['tail_energy'],.1)
        b=torch.tensor([[1.],[2.],[3.],[4.],[5.],[6.]],dtype=torch.float64)
        a=torch.tensor([[.2,.3]],dtype=torch.float64)
        lora=analyze(base,base+b@a,x,1)
        self.assertLess(lora['tail_fraction_source'],1e-28)
        self.assertLess(analyze(base,2*base,x,1)['outside_fraction_source'],1e-28)

    def test_gauge_and_independent_dense_output_spectrum(self):
        torch.manual_seed(9)
        base=torch.randn(8,3,dtype=torch.float64)
        source=torch.rand(8,1,dtype=torch.float64)*base
        x=torch.randn(11,3,dtype=torch.float64)
        observed=analyze(base,source,x,1)
        q,_=torch.linalg.qr(base,mode='reduced')
        dense=(source-q@(q.T@source))@x.T/(len(x)**.5)
        expected=torch.linalg.svdvals(dense)
        self.assertAlmostEqual(observed['tail_energy'],float(expected[1:].square().sum()),places=11)
        for c in [.995,1.005,2.]:
            transformed=analyze(base,source/c,x*c,1)
            self.assertAlmostEqual(observed['tail_energy'],transformed['tail_energy'],places=11)
            self.assertAlmostEqual(observed['source_energy'],transformed['source_energy'],places=11)


if __name__=='__main__':unittest.main()
