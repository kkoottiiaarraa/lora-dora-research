# Mistral128 fresh NLL confirmation, frozen before new outputs

14 October2026. The8case screen did NOT replicate Qwen KL-ordering reversal.
It passed its predeclared alternative gold-NLL sign-change gate. This is a
different, explicitly named confirmation hypothesis; retain both outcomes.

## Fixed questions and workload

Choose128eligible GSM8Ktrain questions not in any prior/calibration/test
content sets, including Qwen affine128 and Qwen fresh64. Mistral screen8
are a subset of Qwen fresh64 and are excluded. Same author-style plain
prefix and whole-string offset/BOS tokenization,32gold answer tokens,
prompt<=512. Save content/token hashes and exclusions digest before outputs.
Training exposure of these questions by the original checkpoint is unknown.

n=128 is fixed using the pilot variance before new outputs: rough normal
80%power estimates for4Bonferroni tests are112for O_off .995 and38for O_off
1.005;64would be weak. V_off .995 estimate260exceeds this bounded budget.
Pilot n8variance estimates are uncertain;128does not guarantee confirmation.
Do not extend n or choose another c if the result is uncertain/negative.

Eight full conditions, saving two unnecessary raw c=1evaluations:
raw V_off/O_off at.995/1.005 (4), centered Vshape/Oshape/gain at1 (3),
pair_off once(1).1024rows,4096positions per condition. The c=1raw values
remain8case exploration and are not mixed into128case estimates.

Same pinned base/adapter/source formula and all160native targets including
unchanged gate. Existing20minscreen is terminal before this worker starts.
CPU16FP32SDPA, no optimizer/GPU. Four cached OLD Mistral native examples
must reload bitwise. Dense conversion once;128newdense source references.
Controls4oldnative/dense +8newsourcegauges +24newcenteredgauges=36,
maxRMS<1%minimumeffect, restoredsourcebitwise. Protected90min deadline.

## Primary hypothesis and decision

Four two-sided paired sign-flip tests against0 for per-question gold NLL
condition−source (10000draws), Holm across all4:

- V_off .995 positive; V_off1.005 negative.
- O_off .995 negative; O_off1.005 positive.

At least one complete prespecified V or O pair must have the expected signs,
both Holm p<.05, and descriptive98.75%question-bootstrap intervals excluding0
in the expected directions.10000resamples, seed20261014. Publish all4tests,
both successful/unsuccessful pairs, all8conditions and corrected controls.
No substitution of a gauge difference for failed endpoint signs.

Also report gauge-to-gauge NLL differences with descriptive intervals, and
KL V/O ordering, without promoting them to a failed primary gate. This is
gold-prefix probability, not generated-answer accuracy or a training mechanism.
Centering gives an invariant convention, not unique causal truth/additivity.

Positive is evidence that a harmful/helpful NLL conclusion is representation
dependent on this checkpoint. Before B-level claims still require nearest-prior
comparison and useful decision/task relevance. Negative/uncertain closes this
fixed confirmation; no c/layer/sample-size search and no automatic generation.
