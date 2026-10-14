# Fresh64 validation fixed after the8old-case screen

14 October2026, before fresh outputs. Screen passed its predefined KL-ordering
reversal gate; raw gold-NLL signs did not reverse. Do not retune c/layers.
This validation tests the same10conditions and the same row-centering convention.
No new algorithm, optimizer, training or GPU is introduced.

Select64previously unused eligible GSM8K train questions, excluding all test,
first232train, old calibration/development/validation, allocation64, radial64
and affine128 content hashes. Sequential selection, prompt<=512tokens and
at least32gold answer tokens, as in prior matched evaluations. Freeze cases,
all exclusions digest, dataset hashes and code before outputs. Author checkpoint
may have seen train questions; this is independent of our screen, not proof of
unseen-source-training generalization. CPU16FP32SDPA, no parameter updates.

Four cached OLD native cases must match bitwise. After common dense conversion,
native/dense controls use those4oldcases. New64dense source outputs are primary
references. Conditions are6raw(V/O×.995/1/1.005), three centered single-part
interventions at1, and pair_off once.10×64=640rows/2048positions per condition.
Source and centered gauge checks at both nonunit c on first4newcases only:
36controls in total including4oldnative/dense. Require floor<1%smallest effect,
restoration bitwise on one new source case, finite metrics and source coverage.

Primary confirmation: paired question KL contrasts V_off−O_off at c=.995 and
c=1.005 retain respectively positive and negative means, and both are supported
after multiple correction. Prespecify two gold-NLL contrasts at the same c as
secondary, without substituting NLL for a failed KL endpoint. Use two-sided
paired sign-flip10000 and Holm across **all4**contrasts, bootstrap10000questions.
Show97.5%individual KL intervals (Bonferroni for2) as descriptive intervals;
do not equate them with training-seed uncertainty. Require both primary Holm
p<.05 and opposite endpoint intervals excluding0 for confirmation. Publish
baseline c=1and all corrected conditions regardless of confirmation.

The three centered questions are invariant to this scalar V/O gauge, but their
single-ablation effects need not sum because of interactions. They are not
unique causal parts, and we do not add a Shapley/all-coalition grid here.
No criterion on these outputs selects a new centering, c or layer subset.

Positive confirmation motivates a specific next test of decision/task-quality
relevance and a ready second architecture. It alone is not B-level evidence.
If uncertain/negative, preserve it and stop this frozen contrast before further
expansion. Protected runtime30minutes; technical failures save/stop without
holding GPUs, and can be repaired without choosing by quality outputs.
