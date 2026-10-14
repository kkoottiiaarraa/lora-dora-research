# Full fixed-base affine recompression: one bounded candidate

14 October2026. Authorized autonomous research, no agents/new-model training.
Candidate is motivated by a frozen4module calibration prototype:5joint block
cycles reduce fixed-D two-sided local error25.54%, aggregate ratio to ordinary
rank8two-sided error0.7928. This is not a full matched-budget or task-quality
result. Previous D-only method failed its practical gate; changing L/R changes
the optimization problem and is the reason for this next test.

Nearest priors: KFAC-SVD/OBD for two-sided weighting; EoRA for residual
compensation; SigmaScale for learned scaling; ChainDoRA for compact direction.
Block least-squares and transpose correction are known. Exact novelty of this
posthoc affine DoRA application is unestablished. Do not claim first method
or a B-level contribution merely from positive local reconstruction.

## Procedure fixed before full outputs

Qwen3-4B/GSM8K, all144q/k/v/o modules, original fixed W0. Same64calibration
questions/32positions used in existing activation capture. Gather empirical
output-gradient covariance G using summed gold-prefix CE, no parameter grads
or updates. G uses0.3shrinkage. Input C uses existing64case covariance and
ridge0.001, identical for all input-only/two-sided methods. No token clipping
or trimming. This is OBD/KFAC-style metric adaptation, not full author replication.

Four main conditions, all exactly5,898,240FP32elements:

1. weighted_uniform: existing input-only full-Delta W-SVD, rank8.
2. kfac_uniform: full Delta with proper two-sided SVD, rank8.
3. structural_kfac: retain sourceD and weighted directional rank7/8 using the
   existing score-independent whole-adapter assignment, counting D.
4. joint_kfac: same ranks/storage as3,5fixed block cycles jointly fitting D and
   L/R under tr(G E C E^T), starting from sourceD. Export FP32 factors.

For fixed D, low-rank step is exact metric SVD; for fixed L/R, D is the exact
coupled linear solve with H=G elementwise(W0 C W0^T). Monotone surrogate descent
does not imply global optimality or task accuracy. Tiny independent design-matrix
least-squares and metric-tail/monotonicity tests passed before real prototype.

Capture CPU16, preparation CPU8, inference CPU16, one sequential worker per
phase; existing diagnostic may overlap capture. Check available RAM before
loading model. Preparation saves per-module checkpoints/hashes and progress.
No GPU needed for prefixes. Initial phase limits90min capture/120min prepare;
an overrun triggers investigation, not arbitrary candidate truncation.

## Evaluation and decisions

128new development train questions, excluding all old calibration, development,
validation and test content, including64allocation-diagnostic questions.
Freeze cases/factors/procedure before new model outputs. Last32gold-prefix
positions per case, full vocabulary teacher KL primary; gold NLL and argmax
changes secondary. CPUFP32 source load/native reference and factorized/dense
controls checked. Floor <1% of smallest compression RMS.

Primary candidate contrasts: joint_kfac versus structural_kfac, kfac_uniform
and weighted_uniform (family3, Holm-adjusted paired sign-flip tests). Whole
question bootstrap10000, seed20261014; intervals descriptive. Advance only
if candidate improves mean KL by at least10% against the strongest mean
baseline, with convincing paired evidence and no concerning gold NLL tradeoff.
Do not tune iterations/shrinkage using these outputs. This is a development
gate; positive result requires independent answer-generation evaluation and
attribution control with joint input-only objective, then another ready pair.
Negative result closes this fixed candidate rather than a parameter grid.

If capture/preparation fails technically, fix and record the attempt without
using failed quality outputs for choices. Existing successful source artifacts
remain immutable. Operational paths/private data stay outside Git.
