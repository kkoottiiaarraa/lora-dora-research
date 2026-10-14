import unittest
import torch
from lora_dora_study.downstream_response import frozen_residual, source_denominator_logits


class DownstreamTests(unittest.TestCase):
    def test_frozen_branches_match_explicit_residual_execution(self):
        source = torch.tensor([[1.,2.]])
        native_branch = torch.tensor([[.3,-.2]])
        changed_branch = torch.tensor([[-.1,.5]])
        later_branches = [torch.tensor([[.2,.1]]),torch.tensor([[-.4,.3]])]
        source_final = source+native_branch+sum(later_branches)
        explicit = source+changed_branch+sum(later_branches)
        observed = frozen_residual(source_final,native_branch,changed_branch)
        torch.testing.assert_close(observed,explicit)

    def test_norm_partition_with_anisotropic_gamma_and_rectangular_head(self):
        source=torch.tensor([[1.,2.],[-.2,.7]])
        changed=source+torch.tensor([[.2,-.1],[.3,.1]])
        gamma=torch.tensor([.7,1.3]);head=torch.tensor([[1.,.2],[-.1,.4],[.3,-.5]])
        epsilon=.01
        dynamic=(changed*gamma/(changed.square().mean(-1,keepdim=True)+epsilon).sqrt())@head.T
        observed=source_denominator_logits(dynamic,changed,source,epsilon)
        independent=(changed*gamma/(source.square().mean(-1,keepdim=True)+epsilon).sqrt())@head.T
        torch.testing.assert_close(observed,independent)


if __name__=='__main__':unittest.main()
