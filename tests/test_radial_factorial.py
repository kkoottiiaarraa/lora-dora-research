import unittest

class FactorialTest(unittest.TestCase):
    def test_factorization_and_rounded_initialization(self):
        import torch
        from lora_dora_study.radial_factorial import radial_scale
        torch.manual_seed(13);w=torch.randn(7,9);u=w+.1*torch.randn(7,9);a=w.norm(dim=1);n=u.norm(dim=1);m=a.to(torch.bfloat16).float()
        s=lambda c:radial_scale(m,n,a,c,torch.bfloat16)
        self.assertTrue(torch.allclose(s('reset_m_fp32')*s('remove_n_fp32'),s('native'),atol=1e-7))
        self.assertTrue(torch.equal(s('reset_m_rounded'),s('native')))
        self.assertTrue(torch.equal(s('remove_n_rounded'),s('remove_d')))

    def test_global_vo_counterfactuals_preserve_scalar_gauge(self):
        import torch
        from lora_dora_study.radial_factorial import CONDITIONS,radial_scale
        torch.manual_seed(17);torch.set_num_threads(2)
        # Fixed attention mixing includes a GQA-like duplicated V head.
        x=torch.randn(5,6);v=torch.randn(4,6);o=torch.randn(6,8);mix=torch.randn(5,5).softmax(-1)
        av=v.norm(dim=1)*1.03;ao=o.norm(dim=1)*.97;nv=v.norm(dim=1);no=o.norm(dim=1);mv=av*torch.linspace(.9,1.1,4);mo=ao*torch.linspace(.9,1.1,6)
        def branch(c,mode):
            sv=radial_scale(mv*c,nv,av,mode,torch.bfloat16);so=radial_scale(mo/c,no,ao,mode,torch.bfloat16)
            z=mix@(x@(sv[:,None]*v).T);return torch.cat([z,z],dim=1)@(so[:,None]*o).T
        for condition in CONDITIONS:
            self.assertTrue(torch.allclose(branch(1,condition),branch(1.005,condition),atol=4e-6,rtol=1e-5),condition)

if __name__=='__main__':unittest.main()
