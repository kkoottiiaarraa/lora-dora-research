import unittest
import torch
from lora_dora_study.affine_compression import (
    diagonal_system,fit_diagonal,weighted_rank_factors,alternating_affine)


class AffineMathTests(unittest.TestCase):
    def test_coupled_diagonal_matches_explicit_design_least_squares(self):
        torch.manual_seed(31)
        base=torch.randn(4,3,dtype=torch.float64)
        target=torch.randn(4,3,dtype=torch.float64)
        a=torch.randn(4,4,dtype=torch.float64);g=a@a.T+torch.eye(4,dtype=torch.float64)
        a=torch.randn(3,3,dtype=torch.float64);c=a@a.T+torch.eye(3,dtype=torch.float64)
        gl,cl=torch.linalg.cholesky(g),torch.linalg.cholesky(c)
        bw,h=diagonal_system(base,g,cl)
        solution=fit_diagonal(bw,target@cl,g,h)
        design=[]
        for i in range(4):
            v=torch.zeros(4,dtype=torch.float64);v[i]=1
            design.append((gl.T@(v[:,None]*base)@cl).flatten())
        design=torch.stack(design,dim=1)
        reference=torch.linalg.lstsq(design,(gl.T@target@cl).flatten()).solution
        torch.testing.assert_close(solution,reference,rtol=1e-10,atol=1e-10)

    def test_weighted_svd_metric_tail_and_alternating_descent(self):
        torch.manual_seed(32)
        b=torch.randn(5,4,dtype=torch.float64);t=torch.randn(5,4,dtype=torch.float64)
        a=torch.randn(5,5,dtype=torch.float64);g=a@a.T+torch.eye(5,dtype=torch.float64)
        a=torch.randn(4,4,dtype=torch.float64);cl=torch.linalg.cholesky(a@a.T+torch.eye(4,dtype=torch.float64))
        gl=torch.linalg.cholesky(g)
        left,right,tail=weighted_rank_factors(t,gl,cl,2)
        torch.testing.assert_close((gl.T@(t-left@right)@cl).square().sum(),torch.tensor(tail,dtype=torch.float64))
        record,history=alternating_affine(b,t,torch.ones(5,dtype=torch.float64),g,cl,2,iterations=5)
        losses=[row['after_diagonal'] for row in history]
        self.assertTrue(all(a>=b-1e-10 for a,b in zip(losses,losses[1:])))
        self.assertEqual(record['left'].numel()+record['right'].numel()+record['row_scale'].numel(),23)


if __name__=='__main__':unittest.main()
