# Comparator amendment before any128case inference

14 October2026. Full candidate preparation is still running; none of its new
128case outputs exist. Candidate configuration/iterations/shrinkage stay fixed.
Original SPEC remains immutable for provenance.

Add two cheap native-DoRA comparators: native_m_input and native_m_kfac.
Use the same source-independent7/8ranks, and directional factors from the
fixed-D input-only or two-sided approximation, respectively. Preserve source
magnitudes m, recompute D using the norm of W0+the truncated direction.
This differs from retaining effective D while changing m implicitly.

Given fixed-D record D0 W0+LR, form U=D0^-1 LR, then
Dnew=m_source/rownorm(W0+U), and export Dnew W0+(Dnew D0^-1 L)R.
No optimizer/training/data selection, same exact5,898,240FP32elements.
Check source-magnitude reconstruction, row norms, finiteness and counts.
The exported representation is explicit affine form, with native-m semantics.

This is an obvious structural baseline, not a new algorithm. The DoRA forward
definition supplies its normalization; search for posthoc SVD/magnitude
retention did not establish a dedicated predecessor, which does not make
this comparator a novel contribution.

Now evaluate6conditions on the same128freshcases. Candidate-versus-baseline
family becomes5, including these2controls; use Holm across all5. Original
3contrast family may also be reported for traceability, but advancement
requires at least10% mean KL gain against the best of **all5** comparators,
paired evidence across the5contrasts and no concerning goldNLL tradeoff.
Do not inspect128case results to choose the comparator or alter the procedure.

Source reference: [DoRA](https://arxiv.org/abs/2402.09353).
Related literature found during this check:
[PermDoRA](https://arxiv.org/html/2606.11262v1) concerns multi-adapter composition
and weak geometric predictors. Its Eq.1 normalizes BA with a single Frobenius
scalar, which differs from native row-wise normalization of W0+BA in our
checkpoint; code was not audited. Do not conflate their formulation with ours,
or claim generic criticism of weight-space geometry as new.
