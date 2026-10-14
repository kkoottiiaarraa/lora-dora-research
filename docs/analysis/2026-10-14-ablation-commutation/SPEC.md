# Bounded screen: DoRA V/O ablations and scalar gauge

14 October2026. Frozen before outputs. No agents/new training/GPU required.
Previous joint compression candidate failed its gate and is closed. This is
a different question about interpretation of endpoint interventions, not a
compression-parameter sweep. Closest prior and limitations: PRIOR.md.

## Algebra and intervention

For each of36attention blocks, source matrices are `D_V U_V` and `D_O U_O`,
`U=W0+sBA`, with strictly positive D. Scale magnitudes V by c and O by1/c;
W0/A/B/r stay fixed. Source and joint removeD-VO functions are invariant in
exact arithmetic. Q/K and all other weights stay unchanged.

Ordinary removeD-V sets D_V to1 but leaves gauged D_O/c. Its branch becomes
1/c times the ungauged removeD-V branch. Ordinary removeD-O analogously
becomes c times its original branch. This is a change of intervention, not
an inference bug or proof that training claims are false.

One explicit invariant decomposition, not claimed unique: let
`mu_V=mean(log D_V)`, `mu_O=mean(log D_O)`, centered scales
`barD=D/exp(mu)`, and branch gain `g=exp(mu_V+mu_O)`.
Under the scalar gauge, mu_V gains logc and mu_O loses logc; centered
scales and g are invariant. Three interventions:

- v_shape_off: replace D_V by its geometric mean, keep D_O.
- o_shape_off: replace D_O by its geometric mean, keep D_V.
- gain_off: divide each D by its geometric mean.

Removing all three yields joint removeD-VO. Other homogeneous choices of
centering also define invariant questions; this is not intrinsic uniqueness
or invariance under every possible network reparameterization.

## Fixed screen

Same Qwen3-4B/GSM8K source/revisions and first8OLD calibration questions,
32gold continuation predictions each. This is exploratory local screening,
not new validation, task accuracy or training-seed evidence. CPU16FP32SDPA.

Conditions: raw removeD-V and removeD-O at c=.995/1/1.005 (6conditions),
three centered interventions at c=1, joint removeD-VO once. Total10×8rows.
No dense no-op repeated full evaluations. Verify source gauges and centered
interventions at both nonunit c on first4cases only. Joint endpoint weights
must be exactly unchanged by gauge; algebra/tinyGQA test accompanies this.

Load native source, verify exact adapter144 and four cached native references
bitwise. Convert effective weights to a common dense FP32 execution path.
Measure native/dense floor separately; use dense source as primary teacher
for all conditions. Controls must be <1% smallest nonzero intervention RMS;
do not weaken this criterion if it fails. Freeze source hashes/cases before
outputs. Save finite per-case metrics, row-scale summaries and errors.

Advance only if within the preselected modest gauges (a) mean teacher-KL
ordering of raw V/O ablations reverses and the contrast range exceeds10% of
the largest mean raw KL, OR (b) a raw ablation gold-NLL mean changes sign
with range>0.001nat/token. Additionally effects must exceed100times the
numerical RMS control floor and invariant controls pass. This is an
engineering effect gate, not a significance test; publish all conditions.

Positive requires a fresh matched64case validation of the same contrast and
an invariant intervention, then task-quality/another architecture if useful.
Negative closes this fixed screen; no search over c, layers or per-block c
to manufacture a reversal. Protected runtime15min; failures stop/save
without holding GPUs. Record actual CPU wall time and GPU0hours.
