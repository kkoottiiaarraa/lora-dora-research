# Real-covariance probe: technical lead, not a new compression method

14 October2026, frozen before real covariance outputs. Motivation and pinned
author-code audit: [LEMS audit](../../literature/2026-10-14-lems-code-audit.md).
The exact extracted author function has a100-case FP64 synthetic witness.
Standard Fisher/SVD weighting is known (KFAC-SVD, GFWSVD, OBD, FACTS).

Use CPU FP32 source Qwen3-4B/GSM8K, original frozen DoRA, no parameter updates.
First8of the existing64calibration cases, last32gold-prefix positions each.
Collect output-gradient Gram for12preselected q/k/v/o projections at layers
0,17,35. Backpropagate summed CE; parameters have requires_grad=False, an
embedding activation is the gradient leaf. This empirical gradient covariance
is a proxy, not exact model Fisher. No new validation cases consumed.

Build G and C from matching256gradient/input tokens. LEMS-like shrinkage
row0.3/column0.1, **no token trimming/clipping**. This is an isolated convention
probe, not full reproduction. For full Delta and rank8 compare transforms
Lg Delta Lc (pinned-code convention) and Lg^T Delta Lc (standard metric).
De-whiten and measure the same objective tr(E^T G E C). Check optimum equals
spectral tail, finite tensors, source hashes/native reference/gradient coverage.

Report ratios and covariance gaps on all12modules. No task-quality claim,
no inference intervention and no novel-method claim. If meaningful at real
covariances, later independently evaluate outputs before considering this
a useful methodological result. If negligible, close this lead.
