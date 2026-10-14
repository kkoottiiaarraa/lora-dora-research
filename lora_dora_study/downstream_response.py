"""Fixed-downstream counterfactuals; no claims of unique causal attribution."""


def frozen_residual(source_final, source_local, changed_local):
    if source_final.shape != source_local.shape or source_local.shape != changed_local.shape:
        raise ValueError('Aligned residual shapes required')
    return source_final + (changed_local-source_local)


def attenuation(actual_kl, frozen_kl):
    import math
    if frozen_kl <= 0:
        return None
    return 1-math.sqrt(max(actual_kl, 0.)/frozen_kl)


def rms_denominator(hidden, epsilon):
    return (hidden.float().square().mean(-1, keepdim=True)+epsilon).sqrt()


def source_denominator_logits(dynamic_logits, changed_hidden, source_hidden, epsilon):
    # A bias-free linear head makes the final RMSNorm denominator a scalar per token.
    return dynamic_logits*(rms_denominator(changed_hidden,epsilon)/rms_denominator(source_hidden,epsilon))
