# Radial activity: precision review and offline diagnostic definitions

Date: 2026-10-11. Scope: existing Qwen3-4B/GSM8K DoRA endpoint only;
This document specifies measurements; it does not claim numerical activity
results from the full checkpoint. Historical analysis and frozen code remain
unchanged.

## Main finding

The existing evaluation path does **not** compute its DoRA ratio in BF16.
Adapter parameters are FP32; the normalizer input and magnitude/normalizer
quotient are FP32. BF16 enters through autocast of linear operations and the
final output cast. Consequently, `BF16(g) == 1` measures a counterfactual
quotient rounding, not deployed radial inactivity. An FP32 or BF16 dense
reconstruction is also not a runtime-equivalent replacement for PEFT.

The cached base headers contain 398 BF16 tensors, including all 144 adapted
attention matrices. The cached DoRA header contains 432 F32 tensors. The
accepted full GSM8K DoRA
summary records `exact_loaded_value_match=true`, 144 adapted modules and
144 magnitude vectors. Configuration: r=32, alpha=32, scaling=1, no rank/alpha
patterns, no rsLoRA, no adapter bias, no extra saved modules, and
`fan_in_fan_out=false`. These are observations about the inspected artifacts,
not assumptions about other DoRA checkpoints.

## Installed implementation and actual evaluation arithmetic

Primary evidence is the inspected installed PEFT 0.17.1 source. Source locations
below are package-relative, so this review contains no access configuration.

| Source | Relevant behavior |
|---|---|
| `peft_model.py:378–389` | `from_pretrained` defaults `autocast_adapter_dtype=True`. |
| `peft_model.py:132–135,1401–1404` | Adapter promotion runs before checkpoint loading in the constructor, and again after loading. |
| `tuners/tuners_utils.py:353–394` | `_cast_adapter_dtype` promotes FP16/BF16 parameters in adapter dictionaries to FP32, including magnitude parameters. |
| `utils/save_and_load.py:517–524` | Normal loading copies into existing parameters; `assign=True` is the separate low-memory path. |
| `tuners/lora/layer.py:216–230` | A and B are linear layers; scaling is alpha/r or alpha/sqrt(r). |
| `tuners/lora/layer.py:757–780` | Base output is computed first; x is cast to A's dtype; variant dispatch is independent of `use_dora`; output returns to the base output dtype. |
| `tuners/lora/variants.py:110–129` | In evaluation, DoRA reuses the existing base output and disables dropout. |
| `tuners/lora/dora.py:30–35,73–99` | Identity-derived LoRA matrix, normalizer, detach, ratio and output correction, detailed below. |

The frozen study worker loads the base with `torch_dtype=torch.bfloat16`, loads
the adapter with default promotion, and evaluates in CUDA BF16 autocast:
[worker](../../../scripts/series_worker.py), lines 89–96 and 131–133.
[Adapter validation](../../../lora_dora_study/adapters.py) checks every loaded
adapter value against the saved tensor in FP32 exactly; initialization in the
base dtype therefore does not imply that the checkpoint was rounded to BF16
before promotion.

Under this path, with one unmerged adapter and no bias:

1. Base weights are BF16. Saved A, B and m, and loaded adapter parameters,
   are FP32. `Linear.forward` casts its adapter input x to FP32.
2. PEFT constructs a FP32 identity and computes `B(A(I)).T`. CUDA autocast
   casts the linear operands to BF16; both linear outputs are BF16. The result
   is a BF16 matrix, here called P. PEFT does not directly use FP32 `B @ A`
   in this unmerged forward path.
3. The base is explicitly converted to x's FP32 dtype. In
   `weight + scaling * P`, the scaled P is BF16 and addition to the FP32 base
   yields FP32. Here scaling=1, eliminating scalar-rounding ambiguity.
4. The row norm has FP32 output, explicitly converted back to its FP32 matrix
   dtype. The ratio `g = m / n` and `g - 1` are FP32. The normalizer and the
   matrix used only for its computation are detached from gradients. Detach
   changes gradients, not the endpoint norm value, and does not freeze the norm
   across optimizer steps or calls.
5. The actual low-rank activation output `z = B(A(x))` is BF16 under autocast.
   Let y0 be the BF16 base output. The correction is evaluated in the written
   order: `(g-1)*y0 + (g*z)*scaling`. FP32 g promotes these products and sums to
   FP32. PEFT adds this correction to y0 and casts the final result to the
   base output dtype, BF16.

These dtype deductions use the inspected PEFT source plus the version-pinned
[PyTorch 2.5.1 CUDA autocast registrations](https://github.com/pytorch/pytorch/blob/v2.5.1/aten/src/ATen/autocast_mode.cpp#L155)
and [operation policies](https://github.com/pytorch/pytorch/blob/v2.5.1/aten/src/ATen/autocast_mode.h#L717).
`linear` is in the lower-precision policy; norm operations include FP32 policies.
The actual CUDA tensor values have not been measured by this review.

scalar times BF16 -> BF16; FP32 plus BF16 -> FP32; its norm -> FP32; FP32 m
divided by that norm -> FP32; FP32 g times a BF16 vector -> FP32. It loaded no
checkpoint and called no model/PEFT forward.

The advanced dense calibration in `rank_symmetry.prepare` is a separate path:
it runs outside the generation autocast context. Its FP32 adapter GEMMs and
its dense conversion must not be used as evidence for generation-time BF16
equivalence.

## Three families of measurements

Use W0 in [out,in] orientation, after the study's base dtype conversion;
saved FP32 A, B and m; and the verified scaling s. Reject non-finite values,
nonpositive normalization denominators and unsupported configuration instead
of silently replacing them. Record nonpositive m explicitly: m is an
unconstrained parameter and positivity must be checked, not assumed.

### A. Ideal endpoint geometry, with a reference precision check

Replicate the frozen reconstruction in explicit FP32 outside autocast:

```
L = s * (B.float() @ A.float())
U = W0.float() + L
n = row_norm(U)
n0 = row_norm(W0.float())
g = m.float() / n
WD = g[:,None] * U
delta = WD - W0.float()
```

Report these as `ideal_fp32`, not PEFT runtime weights. On deterministic row
blocks, repeat products, norms and ratios in FP64 to quantify FP32 reference
error. An inexpensive all-row FP64 reduction of the FP32 U detects norm-only
error, but does not replace a FP64 B@A reference. Label those two checks
separately. If all-row FP64 multiplication is affordable, use it as the common
reference rather than a sampled uncertainty claim.

Keep three different quantities distinct:

| Quantity | Meaning |
|---|---|
| `g-1 = (m-n)/n` | Endpoint diagonal departure from identity, conditional on A/B and chosen norm arithmetic. |
| `m-n0`, `(m-n0)/n0` | Endpoint residual from a specified base norm; not established parameter movement during training. |
| `n-n0`, `(n-n0)/n0` | Norm change from the low-rank direction update before DoRA normalization. |

For each, report signed mean, mean absolute value, RMS, median/p90/p95/p99/max
absolute value, negative/zero/positive counts, and counts above disclosed
relative thresholds, such as 1e-5/1e-4/1e-3/1e-2. Preserve exact-zero counts
separately from tolerance-defined activity. Give both pooled row summaries and
equal-module summaries; unequal projection dimensions otherwise change the
weighting. Row counts are descriptive, not independent experimental repeats.

The diagonal term `R0 = (g-1)[:,None]*W0` is not the full removal perturbation.
Define `T = g[:,None]*L`, so `delta = R0 + T`. Measure squared Frobenius
energies of R0, T, delta, L, and the signed cross term `2<R0,T>`.
Report `||R0||/||L||`, `||R0||/||delta||`, with undefined denominators explicit;
the second need not be <=1 because components can cancel. Energy fractions
must not be presented as additive percentages unless the cross term is shown.

The ideal endpoint interventions have useful independent identities:

```
E_removeD = WD-U = (g-1)[:,None]*U
||E_removeD[i]|| = |m[i]-n[i]|
W_baseMagnitude = (n0/n)[:,None]*U
||WD[i]-W_baseMagnitude[i]|| = |m[i]-n0[i]|
```

Use these identities to validate implementation, allowing measured FP32
rounding error and testing against FP64. They require no SVD. They also show
why a nontrivial D does not by itself establish that learned magnitude updates
were necessary: even m equal to the base norm generally yields g != 1 after
A/B changes U's norm. Norms/Frobenius energies describe weights, not benchmark
importance or activation-weighted effect.

### B. Explicit rounding counterfactuals

Keep names that identify the actual operation:

| Measurement | Definition |
|---|---|
| Quotient rounded | `Q_bf16(m/n)`; number with result exactly 1. |
| Operands rounded, FP32 division | `Q_bf16(m).float()/Q_bf16(n).float()`. |
| BF16 operands and quotient | BF16 division of separately rounded m and n. |
| Dense weight rounding | `Q_bf16(WD)` versus `Q_bf16(U)`. |

These counterfactuals are unequal in general. The deployed path above uses
none of the first three as its ratio. Compare activity counts and sign changes
across them, and report `||g_variant-g_reference||` and norm-relative errors.
Use actual casts/`nextafter`, not a symmetric `abs(g-1)<eps` rule. The BF16
neighbors of 1 are 0.99609375 and 1.0078125; nearest-even rounding to 1 has
asymmetric bounds approximately 0.998046875 and 1.00390625, including ties
according to the implementation's tie rule. FP32 quotient rounding to exactly
1 is another distinct event and should be compared with the FP64 ratio.

For dense rounding, report changed entries, changed rows, per-module change
fractions, max absolute change and squared Frobenius change; compare results
after both matrices have been cast, then promoted for subtraction. Cross-tab
`Q_bf16(g)==1` with whether the corresponding BF16 dense row changed. A small
ratio can cross a weight rounding boundary, and a nonunit ratio can leave a
rounded dense row unchanged. Neither equality test establishes the equality
of PEFT outputs, which use separate base and low-rank branches.


product output; then form `V = W0.float() + s*P` in the same dtype and order
as `get_weight_norm`. Compute FP32 row norms and FP32 `m/n`. Call the results

The shortcut `P = BF16(B_bf16 @ A_bf16)` assumes the first identity projection
deterministic small selection of identity column blocks, without constructing
a full identity or calling a module/model forward. Record exact elementwise
agreement and shape/dtype. Avoid silently replacing the two-stage product by
`BF16(B_fp32 @ A_fp32)`, which rounds after multiplying unrounded operands.

Compare surrogate P with FP32 B@A, then n and g with their ideal counterparts.
Report distributions of `n_surrogate/n_ideal-1`, `g_surrogate-g_ideal`, counts
of sign/threshold/identity classifications changed, and separately the
effect of using FP32 versus FP64 reductions of the same V. This attributes
normalizer differences to operand/output rounding and reduction precision.

selection. Block size can also change a kernel. Validate a few row blocks
agreement with the algebra does not certify CUDA identity reconstruction,
activation GEMMs or final output rounding. Do not build a surrogate merged
matrix and call it the deployed PEFT model. Actual output/activity validation
would need a later separately scoped measurement of PEFT intermediate dtypes,
norms, g and outputs on selected modules and inputs.

## Can norm precision alone make m look active or inactive?

Yes, under a specified numerical definition. The installed initializer forms
the norm from the current base-plus-initial-update tensor, then casts the norm
to that tensor's dtype (`dora.py:37–64`). BF16 initialization can therefore
store a BF16-rounded base norm even if the parameter is subsequently promoted
to FP32. Comparing an unchanged initialized value with a FP32/FP64 base norm
can create a nonzero residual solely from rounding. Conversely, rounding both
operands or their quotient can erase a small nonzero residual. A changing
normalizer can make g active even with fixed m.

Compare m against (i) FP64 norm of the actual cached base values, (ii) FP32
norm primitive. Record exact equality, absolute/relative residual, sign flips
and threshold crossing. Include how many m values themselves lie exactly on
the BF16 lattice. Comparisons (iii) and (iv) are initialization proxies; any
differences between them are reduction/output-precision effects to report.

The authors' training PEFT revision, initialization dtype/ordering, exact
training base snapshot and optimizer trajectory are not established by this
endpoint. Therefore none of these proxies identifies the actual initial m,
proves m never changed, proves m received zero gradients, or identifies a
training mechanism. The historical `base_magnitude` intervention specifically
copies the **FP32 current-base norm** into m; it is not an established reset to
the authors' original initialized parameter.

The historical `remove_d` intervention clears both `use_dora` and the variant
dispatcher. This removes normalizer/magnitude arithmetic entirely and uses the
ordinary PEFT additive branch. At ideal precision it is W0+sBA with the
DoRA-trained factors. Its finite-precision output is a separate arithmetic
path, so weight-difference measurements do not isolate its entire measured
benchmark effect from arithmetic effects.

## Streaming implementation and acceptance recommendations

Read safetensors headers and the base index first. Match every A/B/m key to
exactly one base key, verify 36 layers x four projections =144 modules,
dimensions, rank/scaling/configuration, revisions and source digests. Preserve
cached storage dtype and a separate intended evaluation dtype in provenance.

Slice one base matrix by output rows, corresponding B rows and m entries;
retain only that module's small A. Compute products and all accumulators in
row blocks, then release tensors. Do not use `get_tensor` on a whole multi-GB
row scalars/compact tables, not full reconstructed weights. Exact quantiles of
the few hundred thousand row scalars are feasible and should be distinguished
from approximate streaming quantiles. Use a declared deterministic block size.

Meaningful acceptance checks are:

1. Cached revision/file hashes, header dtype/shape inventory and complete key
   mapping; no unexpected modules, bias or quantization.
2. `delta == R0+T`, energy/cross-term identity, and row-norm intervention
   identities against a deterministic FP64 reference. Report numeric residuals
   and precision-justified tolerances, rather than arbitrary pass thresholds.
3. Counterexamples with m=n, m=n0, L=0 and quotient values on both sides of BF16
   rounding boundaries. These distinguish normalization activity from baseline
   magnitude residuals and catch asymmetric rounding mistakes.
4. Primitive dtype assertions for each surrogate stage; two-stage identity
   product versus shortcut on deterministic selected blocks; block-size checks.
5. Global accumulators equal the sum of module accumulators; per-projection
   tables carry denominators; rerunning selected modules reproduces row scalars.
6. A manifest records source and input hashes, Python/Torch/safetensors versions,
   thread caps, dtype definitions, block sizes and every unavailable validation.

This stage can establish how much radial structure the endpoint contains under
specified arithmetic, and whether coarse rounding summaries were misleading.
It cannot establish deployed functional inactivity, actual delta rank after
BF16, necessity during training, independent-LoRA attainability or a DoRA
quality advantage.

## Follow-up recommendation: bounded CUDA normalizer control

endpoint geometry and the stated rounding counterfactuals. It is insufficient
by itself for the central claim that a given proportion of deployed CUDA
ratios is exactly or materially different from 1. A numerical error bound
has not supplied such a bound. For a CUDA ratio claim, run the following small
activity.

the same installed versions and BF16 autocast settings as the study. Keep only
one module's W0/A/B/m and scratch tensors on the device. Reproduce the full
identity-based two linear operations using tensor primitives, without loading
the transformer or invoking any module/model forward:

```
# W0: BF16; A, B, m: FP32; s: verified scalar, here 1
with torch.inference_mode(), torch.autocast("cuda", dtype=torch.bfloat16):
    identity = torch.eye(A.shape[1], device="cuda", dtype=A.dtype)
    first = torch.nn.functional.linear(identity, A)
    P_cuda = torch.nn.functional.linear(first, B).T
    V_cuda = W0.to(A.dtype) + s * P_cuda.detach()
    n_cuda = torch.linalg.norm(V_cuda, dim=1).to(V_cuda.dtype).detach()
    g_cuda = m / n_cuda
```

Here `F.linear` is a tensor primitive, not a model forward or inference on
examples. Preserve the full identity and GEMM shapes: splitting them or using
direct B@A changes the kernel problem. This control does not need a
calibration prompt, tokenizer, generation, activation tensors, full model,

Before a future launch, estimate peak live tensor memory from actual header
must be reported separately. Release module tensors between iterations; do not
change product shapes merely to force an already-failed budget. Existing
resource/preflight constraints still apply; this design authorizes no launch.

The minimum recorded measurements are:

1. All 144 module keys/shapes/scaling, input hashes, package/source hashes,
   device architecture/driver, and current TF32/BF16 reduced-precision
   reduction/autocast flags. Record rather than silently changing flags; the
   historical process flags were not captured, limiting exact replay claims.
2. Actual dtypes of identity, first product, P, V, n and g for every shape
   family. Expected values are FP32/BF16/BF16/FP32/FP32/FP32.
   max/quantiles/RMS absolute g discrepancy, relative n discrepancy, exact
   `g==1` counts, sign changes of `g-1`, and crossings of every declared
   activity threshold. Compare margin to threshold with observed discrepancy;
   disclose borderline rows rather than rounding them into a headline count.
   module, without storing full matrices. This separates normalizer reduction
   differences from BF16 product differences. Retain the resulting row scalars;
5. Repeat a deterministic selection covering each shape family and the rows
   nearest activity thresholds, checking g reproducibility. Record peak
   elapsed time. Summaries must reconcile to module/row denominators.

This would directly measure the normalizer and FP32 g under the recorded CUDA
tensor path. It would close the major device-arithmetic gap for radial ratio
activity, including a check of the identity reconstruction. It would **not**
measure the activation branch B(A(x)), final output rounding, layer/model
functional differences, downstream benchmark quality, BF16 delta rank, or
training necessity. Even nonunit g does not prove a nonzero output change on
given inputs; even identical g across devices does not validate the existing
dense conversion. The result should be described as a normalizer-path control,
not PEFT model or historical evaluation equivalence.

## Inspected source digests

Installed PEFT source SHA256:

```
07d514fd057d8aa9ec7b89bec3f3fbd04862951c1a8ff73153e833096481ecf5  tuners/lora/dora.py
39e2f6908c9f3faf4d2de2b6ecfdf44c96d2cae67b8155ed1b51bc67fb25b734  tuners/lora/layer.py
c477a90d68caa2d3d2ffa22266f32ad3ab1767f01d84250e5242f1fc29f202c2  tuners/lora/variants.py
d5b6a92d8f0b5325951519e81d2ed9debcba6ace1028e887958dd5e5188be66a  tuners/tuners_utils.py
2307ebeb101baff53b19ce5a0f109885d99b64ab147d67cba19719b6097c3e10  peft_model.py
849282f01e69b7055cc499e67f279cde3f489421aea212f59f701f45755de26b  utils/save_and_load.py
```

Study source SHA256:

```
8f902d0ff539cf11d2743f98648a07c4015dd20f484f110ee6fbe97e97f61f9a  scripts/series_worker.py
4f91f9d1e20873cb0354517646ef6e84bd8447db14989cec88d9219c7f558729  lora_dora_study/adapters.py
68b7582f33ace776902ad98df1e6b3238b7bf047a42e29ecf757ac3ac24a4e54  lora_dora_study/interventions.py
d50047efc0bc82778a511300d89a2555d462a7be95794fa23dfbb601d9132079  lora_dora_study/rank_symmetry.py
```

Inspected cached revisions: base `1cfa9a7208912126459214e8b04321603b3df60c`;
DoRA `07f6a59c2ab6b36b1cecb5feb66187638202521d`. The accepted primary run
summary is `results/first-series-greedy/jobs/gsm8k-quality-greedy/full-dora-attempt-1/summary.json`.
