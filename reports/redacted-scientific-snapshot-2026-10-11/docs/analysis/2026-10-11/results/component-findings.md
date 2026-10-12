# Global components and compression

Exploratory analysis after data collection. All effects condition on these fixed GSM8K checkpoints and 1319 test examples; no independent training replicates.

## Global radial components

| Intervention | Scorer | Change vs original PEFT DoRA [pointwise CI95] | Excludes loss >0.5 pp |
|---|---|---|---|
| gsm8k-base_magnitude-all | author_em | +0.910 pp [-0.303, +2.123] | True |
| gsm8k-base_magnitude-all | final_em | +0.910 pp [-0.303, +2.123] | True |
| gsm8k-remove_d-all | author_em | +0.986 pp [-0.227, +2.199] | True |
| gsm8k-remove_d-all | final_em | +0.910 pp [-0.227, +2.123] | True |

In this final checkpoint, removing the learned diagonal factor or replacing learned magnitude by base row norms does not show a material GSM8K accuracy loss at the stated pointwise 0.5 pp criterion. This is neither equivalence of generated functions nor a simultaneous guarantee. It does not show that magnitude was irrelevant during training, that a newly trained LoRA would reach the same solution, or that the retained BA alone explains why DoRA learned it. Learned A/B and their training history remain present.

## Compression relative to dense controls

| Intervention | Scorer | Change vs corresponding dense [pointwise CI95] |
|---|---|---|
| gsm8k-r32 | author_em | +0.682 pp [-0.455, +1.820] |
| gsm8k-r32 | final_em | +0.834 pp [-0.303, +1.971] |
| gsm8k-e95 | author_em | +0.758 pp [-0.455, +1.971] |
| gsm8k-e95 | final_em | +0.910 pp [-0.303, +2.123] |
| gsm8k-lora-matched-impact | author_em | +1.365 pp [+0.076, +2.654] |
| gsm8k-lora-matched-impact | final_em | +1.289 pp [+0.000, +2.578] |
| gsm8k-e99 | author_em | +0.303 pp [-0.758, +1.440] |
| gsm8k-e99 | final_em | +0.379 pp [-0.682, +1.516] |

Rank32 and E95 exclude an accuracy loss exceeding 0.5 pp pointwise under both scorers; E99 excludes a loss exceeding 1 pp but does not meet 0.5 pp. These statements concern dense references. All compression historical Holm p values exceed 0.05. Preserved accuracy does not mean preserved answers, and lack of significant harm alone is not equivalence.

Rank32 retains the leading 32 singular components of each full effective DoRA delta in its ideal FP32 approximation. Adding W0 and copying into BF16 weights may increase the algebraic rank of the actual materialized delta; that rank is unmeasured. This is not a tested same-rank trained LoRA. E95 has unweighted module rank median 21 (range 1–114); E99 median 303.5 (99–655). These ranks and energies are module summaries, not global model energies or independent experimental units. No correlation is fit across the three compression conditions.

All saved spectra in r32/E95/E99 describe the same input DoRA delta before truncation; their per-module hashes agree. spectral-entropy.csv reports 576 module/job rows with input and ideal pre-BF16 normalized squared-spectrum entropy H (natural logarithm) and exp(H). Ideal truncation uses the recorded kept rank; actual post-materialization spectra remain unmeasured. Matched uniform attenuation retains input normalized entropy and scales energy by (1-a)^2. These are descriptive geometric calculations, not a causal entropy experiment or 576 independent checkpoints.

The matched-control retained_energy field describes an intermediate rank32 SVD that is discarded before scalar attenuation. It must not be interpreted as the attenuated control retaining 100% of LoRA update energy. Analytic (1-attenuation)^2 fractions are exported separately and labelled before BF16 materialization.

No accepted saved diagnostic records learned D-I or learned magnitude minus base row norms, nor their activity in BF16. The numerical size of the removed factor is unavailable. These results therefore cannot establish that a substantially active factor was dispensable, or diagnose whether BF16 rounding attenuated its effect.

## Exploratory direct comparison against original PEFT DoRA

After observing the dense-conversion shift, six direct paired contrasts were added to the execution spec before computation. They use their own 50,000-resample bootstrap and Holm family of six; original pointwise criteria are not inferred by adding historical CI endpoints.

| Intervention | Scorer | Direct change, pp | CI95, pp | Holm (6) | Excludes loss >0.5 pp |
|---|---|---|---|---|---|
| gsm8k-r32 | author_em | +0.152 | [-0.986, +1.289] | 1 | False |
| gsm8k-r32 | final_em | +0.152 | [-0.986, +1.289] | 1 | False |
| gsm8k-e95 | author_em | +0.227 | [-0.910, +1.365] | 1 | False |
| gsm8k-e95 | final_em | +0.227 | [-0.910, +1.365] | 1 | False |
| gsm8k-e99 | author_em | -0.227 | [-1.365, +0.910] | 1 | False |
| gsm8k-e99 | final_em | -0.303 | [-1.440, +0.834] | 1 | False |

Against original PEFT DoRA, r32 and E95 exclude a loss exceeding 1 pp pointwise, but cannot exclude 0.5 pp. E99 only meets the 2 pp criterion. Thus the stronger dense-relative 0.5 pp statement does not directly transfer to the original adapter.

## Limited calibration matching and sensitivity contrast

Per-module relative squared activation perturbation matches closely on one training prompt (54 tokens), using each original checkpoint’s own activations. Absolute perturbations, perturbation directions, combined network effects and test-distribution errors are not matched. Saved dense_fidelity measures adapter-to-dense conversion before compression or attenuation; no final compressed fidelity is certified.

| Scorer | (r32−denseD)−(matchedL−denseL), pp | CI95, pp | raw p | Holm (2) |
|---|---|---|---|---|
| author_em | -0.682 | [-2.350, +0.986] | 0.447271 | 0.894542 |
| final_em | -0.455 | [-2.123, +1.213] | 0.623028 | 0.894542 |

The new four-run contrast uses aligned source IDs, prompt/input hashes and scorer, common-index empirical bootstrap (50,000; fixed spec seeds), percentile CI and centered two-sided bootstrap p. It compares sensitivity under this restricted matching, not a pure causal rank effect. Neither scorer establishes a difference in sensitivity.

## Descriptive saved-spectrum summaries

The following are unweighted medians across 144 modules. The same DoRA input is repeated for three operations; no module-level hypothesis test or cross-condition correlation is used.

| Operation | Input H (nats) | Ideal H (nats) | Input exp(H) | Ideal exp(H) | Ideal retained energy fraction |
|---|---|---|---|---|---|
| gsm8k-r32 | 1.771339 | 1.393077 | 5.878717 | 4.027252 | 0.963051 |
| gsm8k-e95 | 1.771339 | 1.348287 | 5.878717 | 3.850838 | 0.950686 |
| gsm8k-e99 | 1.771339 | 1.661713 | 5.878717 | 5.268325 | 0.990017 |
| gsm8k-lora-matched-impact | 1.340191 | 1.340191 | 3.819787 | 3.819787 | 0.913346 |

Lower ideal entropy and near-preserved accuracy here constrain the necessity of the removed ideal spectral tail in this construction. They do not isolate entropy from energy, singular-vector changes, BF16 materialization, or movement toward the base weights, and do not establish an entropy cause of training success.

## Multiplicity and practical criteria

All 40 saved contrasts and their literal historical estimates/CI/p are retained. Global Holm across all 40 raw p leaves 0 contrasts below 0.05; this sensitivity analysis does not replace historical families or account for the full adaptive research process.

The 0.5/1/2 pp columns test lower_CI > −δ using existing pointwise intervals. They are thresholds for excluding specified accuracy losses, not formal simultaneous noninferiority, two-sided mathematical equivalence, function equivalence, or training uncertainty.


Inputs and independent checks are recorded in component-validation.json; source metadata and scope details are in matched-control-limitations.json. New output manifest is coordinated by the main analysis agent.

