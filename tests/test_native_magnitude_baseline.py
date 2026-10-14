import unittest
import torch
from lora_dora_study.native_magnitude_baseline import retain_magnitude


class NativeMagnitudeTests(unittest.TestCase):
    def test_retains_row_norm_and_direction_at_same_storage(self):
        torch.manual_seed(41)
        base=torch.randn(5,4)
        original=base+torch.randn(5,4)*.1
        d=torch.linspace(.8,1.2,5)
        left=torch.randn(5,2)*.1;right=torch.randn(2,4)
        record=dict(left=left,right=right,row_scale=d)
        result,info=retain_magnitude(base,original,d,record)
        teacher_m=(d*original.norm(dim=1)).double()
        direction=base.double()+(left.double()/d.double()[:,None])@right.double()
        expected=direction*(teacher_m/direction.norm(dim=1))[:,None]
        deployed=base.double()*result['row_scale'].double()[:,None]+result['left'].double()@result['right'].double()
        torch.testing.assert_close(deployed,expected,rtol=1e-6,atol=1e-6)
        self.assertLess(info['maximum_relative_magnitude_error'],1e-6)
        self.assertEqual(sum(t.numel() for t in result.values()),23)


if __name__=='__main__':unittest.main()
