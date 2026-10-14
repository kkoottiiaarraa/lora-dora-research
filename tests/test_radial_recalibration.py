import importlib.util
import unittest


@unittest.skipUnless(importlib.util.find_spec('torch'),'Torch required')
class RadialTests(unittest.TestCase):
    def test_recovers_known_diagonal_and_no_extra_storage(self):
        import torch
        from lora_dora_study.radial_recalibration import recalibrate
        torch.set_num_threads(2);torch.manual_seed(43)
        base=torch.randn(7,9);left=torch.randn(7,3);right=torch.randn(3,9)
        d=torch.linspace(.8,1.2,7);target=d.double()[:,None]*base.double()+left.double()@right.double()
        record=dict(left=left,right=right,row_scale=torch.ones(7))
        result,info=recalibrate(base,target,torch.randn(60,9),record)
        torch.testing.assert_close(result['row_scale'],d,atol=2e-7,rtol=2e-7)
        self.assertLess(info['weighted_loss_after'],1e-11)
        self.assertEqual(sum(t.numel() for t in result.values()),sum(t.numel() for t in record.values()))

    def test_direct_whitened_solution_and_target_scaling_equivariance(self):
        import torch
        from lora_dora_study.radial_recalibration import recalibrate
        from lora_dora_study.weighted_compression import covariance_cholesky
        torch.manual_seed(44)
        base=torch.randn(6,8);target=base+torch.randn(6,8)*.1;inputs=torch.randn(70,8)
        record=dict(left=torch.randn(6,2)*.1,right=torch.randn(2,8),row_scale=torch.ones(6))
        result,info=recalibrate(base,target,inputs,record)
        chol,_=covariance_cholesky(inputs)
        bl=base.double()@chol;residual=(target.double()-record['left'].double()@record['right'].double())@chol
        expected=(bl*residual).sum(1)/bl.square().sum(1)
        torch.testing.assert_close(result['row_scale'].double(),expected,atol=1e-7,rtol=1e-7)
        c=1.005
        transformed=dict(left=record['left'].double()*c,right=record['right'],row_scale=record['row_scale'].double()*c)
        again,_=recalibrate(base,target.double()*c,inputs*c,transformed)
        torch.testing.assert_close(again['row_scale'],result['row_scale']*c,atol=2e-7,rtol=2e-7)
        self.assertLessEqual(info['weighted_loss_after'],info['weighted_loss_before'])


if __name__=='__main__':unittest.main()
