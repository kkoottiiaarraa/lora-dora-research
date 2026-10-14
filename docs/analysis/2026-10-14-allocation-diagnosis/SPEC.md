# Allocation versus approximation: diagnostic, not a new algorithm

Frozen before new inference, 14 October 2026. Scope: Qwen3-4B/GSM8K,
all 144 adapted projections, fixed W0, CPU FP32, no training or new agents.
Study uses existing captured calibration inputs (64 questions).

Question: does redistributing a fixed adapter budget by the **known local
activation-weighted objective** improve functional fidelity? Does this differ
between ordinary low-rank Delta and fixed-D directional compression?

Four conditions, all exactly 5,898,240 FP32 elements:

- weighted_uniform: full Delta, rank8 everywhere;
- weighted_allocated: same per-module weighted SVD, ranks0..32, exact
  sum r_l*(out_l+in_l) budget, maximize retained weighted spectral energy;
- structural_uniform: existing score-independent r7/8 allocation, D counted;
- structural_allocated: same fixed original D and directional weighted SVD,
  ranks0..32, same budget including every D scalar.

Use existing exact allocator. This is a cost-aware adaptation of known
spectral allocation, not a claim of novelty or a replication of PARA/LEMS.
No factors or allocation scores selected using inference validation.
Rank0 allowed; source32 cap fixed in advance. It limits the ordinary-delta
class too; any conclusion is conditional on this cap.

Preparation: one module at a time, CPU4. Validate finite factors, shapes,
actual counts, hashes, local weighted residuals against spectral tails.
Report by Q/K/V/O and depth: local loss, rank distribution, teacher output
energy and absolute tail contribution. Exact local allocation cannot worsen
the corresponding summed calibration objective versus the feasible uniform
assignment. It need not improve teacher KL or task accuracy.

Inference: CPU16 if adequate available RAM; use 64 new development train
questions, excluding all previous calibration/development/validation/test
content. Last32 gold-prefix positions/question, full vocabulary teacher KL,
gold NLL and argmax changes. No claims of task accuracy. Freeze case/factor
hashes before outputs. Native source validation on4 old reference cases;
factorized-vs-dense controls on2 new cases. Floor <1% compression RMS.

Primary diagnostic contrasts allocated minus uniform within each class;
paired question bootstrap10000, seed20261014, Holm correction of2 paired
sign-flip tests; intervals descriptive. Practical signal: at least10% mean
KL decrease. This development experiment selects a direction; any proposed
new method later needs independent validation and answer-generation testing.

Interpretation rules:
- Local proxy improves and KL worsens: proxy allocation mismatch; not proof
  all adaptive rank allocation fails. Compare calibrated/influence-aware prior.
- KL improves materially: allocation explains part of loss; not new algorithm.
- No material improvement: not proof approximation dominates, since only
  one allocation proxy and one cap have been tested.
- Structural/full-Delta comparison at identical actual storage is secondary.

No automatic broad hyperparameter grid. No Mistral until a useful specific
effect or corrective candidate justifies replication.
