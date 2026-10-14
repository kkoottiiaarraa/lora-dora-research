import importlib.util
import unittest


@unittest.skipUnless(importlib.util.find_spec('torch'), 'Torch required')
class WeightedTests(unittest.TestCase):
    def test_whitening_orientation_and_weighted_optimum(self):
        import torch
        from lora_dora_study.weighted_compression import covariance_cholesky, weighted_factors
        torch.set_num_threads(2);torch.manual_seed(19)
        x=torch.randn(60,8);x[:,3]=x[:,0]*2+x[:,3]*.01
        delta=torch.randn(7,8)
        l,ridge=covariance_cholesky(x)
        left,right,info=weighted_factors(delta,l,3)
        u,s,vh=torch.linalg.svd(delta,full_matrices=False)
        raw=(u[:,:3]*s[:3])@vh[:3]
        def loss(a):return float(((delta.double()-a.double())@l).square().sum())
        self.assertLessEqual(loss(left@right),loss(raw)+1e-5)
        covariance=x.double().T@x.double()/len(x)+torch.eye(8,dtype=torch.float64)*ridge
        torch.testing.assert_close(l@l.T,covariance)
        self.assertLessEqual(abs(info['weighted_squared_residual']-info['expected_squared_tail']),.003*info['expected_squared_tail'])

    def test_full_rank_and_scalar_activation_rescaling(self):
        import torch
        from lora_dora_study.weighted_compression import covariance_cholesky, weighted_factors
        torch.manual_seed(21)
        x=torch.randn(50,6);delta=torch.randn(5,6)
        l,_=covariance_cholesky(x)
        a,b,_=weighted_factors(delta,l,5)
        torch.testing.assert_close(a@b,delta,atol=2e-6,rtol=2e-5)
        a,b,_=weighted_factors(delta,l,2)
        aa,bb,_=weighted_factors(delta,l*1.005,2)
        torch.testing.assert_close(a@b,aa@bb,atol=3e-6,rtol=3e-5)


if __name__=='__main__':unittest.main()
