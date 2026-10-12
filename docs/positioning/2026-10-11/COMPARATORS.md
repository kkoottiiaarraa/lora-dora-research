# Accepted-paper comparators and novelty boundary

Checked 2026-10-11. Six papers below have acceptance verified from official proceedings or TMLR publication records. A seventh close critical comparator has author-reported workshop acceptance corroborated by a workshop-branded paper; its decision page was inaccessible. Venue examples demonstrate contribution types and evidential choices, not universal acceptance thresholds or chances.

**Our comparison baseline:** accepted local analysis plus radial FINDINGS: three task-specific Qwen3-4B LoRA/DoRA pairs, fixed public checkpoints rather than independent training seeds; active-radial diagnostics on one GSM8K checkpoint; posthoc component/rank interventions; no established DoRA quality advantage. The 144 matrices are observations within one model, not 144 independent replications. The potentially distinctive observation is measurable posthoc radial change with close mean task accuracy, separating training and inference roles. Its novelty is narrower than “removing adaptation components preserves quality.”

## 1. LoRA vs Full Fine-tuning: An Illusion of Equivalence — NeurIPS 2025 main

**Status:** [official proceedings](https://papers.nips.cc/paper_files/paper/2025/hash/ff541950d1e885af90f523571564a401-Abstract-Conference.html) explicitly says Main Conference Track. An older ICLR 2025 submission PDF is not the acceptance record.

**Contribution/evidence:** a spectral definition of intruder dimensions distinguishes LoRA and full-FT solutions even at comparable target accuracy. The [author text, v3](https://arxiv.org/html/2410.21228v3), §§3–5/Appendices L–P, covers RoBERTa-base on six classification tasks, LLaMA/LLaMA-2 on chat/math/code; rank, scaling, learning-rate and definition-sensitivity checks; a five-seed MNLI check; and six-task continual learning. Crucially, §5 scales the highest-ranked intruder in each matrix after training while measuring task accuracy and pretraining loss. A neighboring singular direction of similar singular value is the comparison control. Intruder attenuation can preserve task performance while improving forgetting, whereas the comparison intervention behaves differently. The accepted abstract also states the intervention result.

**Implication for ours (assessment):** a precise coordinate definition plus a discriminating intervention can be a main-conference empirical contribution. Generic posthoc attenuation with preserved task quality is occupied. Our radial intervention needs a specificity control and independent replication; comparable update norm alone does not establish a special role for D. We lack their second behavioral axis, retention/generalization, that makes removal useful beyond preserving a mean score.

**Version caution:** the proceedings PDF fetched during this audit appears earlier than the accepted abstract/arXiv v3. Intervention details above are attributed to v3, not silently to that PDF.

## 2. LoRA Learns Less and Forgets Less — TMLR, August 2024

**Status:** the [publication PDF](https://openreview.net/pdf?id=aloEru2qCG) is indexed with the TMLR August 2024 publication header; the [official OpenReview author publication record](https://openreview.net/profile?id=~Mansheej_Paul1) identifies Accepted by TMLR. Direct forum access was browser-challenged.

**Contribution/evidence:** the [author text, v2](https://arxiv.org/html/2405.09673v2), §§3–4/Appendices A–C, maps learning/forgetting trade-offs rather than introducing another adapter. Llama-2-7B is studied on math/code in instruction-FT and continued-pretraining regimes, with ranks 16/64/256, duration sweeps and learning-rate searches. Controls include base/full-FT, off-domain evaluation, weight-decay/dropout, generation diversity and full-FT update SVD. Tülu instruction-tuning is an explicit boundary where LoRA can match full-FT. Model-family breadth is limited; strength comes from regime/control breadth rather than a universal model law.

**Implication for ours (assessment):** empirical clarification is a legitimate contribution, but this does not make a three-checkpoint comparison equally strong. “DoRA advantage not established here” cannot become “DoRA does not help”: unknown training selection and absent retraining prevent the tuned-method comparison this paper performs. More summaries of the same weights do not replace controlled regime variation.

## 3. Decoupling Angles and Strength in Low-rank Adaptation — ICLR 2025 conference

**Status:** [official ICLR proceedings](https://proceedings.iclr.cc/paper_files/paper/2025/hash/3379ce104189b72d5f7baaa03ae81329-Abstract-Conference.html), not a workshop. DeLoRA is the method name; the proceedings title omits that prefix.

**Contribution/evidence:** [author text](https://arxiv.org/html/2503.18225v1), §§2–3/Appendices B–D, derives normalized/scaled low-rank updates to decouple adaptation strength and angles. It combines design ablations, image generation, GLUE and LLaMA-2 instruction tuning with learning-rate robustness and prolonged-training checks. DreamBooth uses 30 subjects/three seeds after selection on three subjects; GLUE uses separate selection/evaluation splits and five seeds. Some baselines are borrowed from prior papers. Appendix C/Table 10 already tests **training DoRA with fixed magnitude**: similar small-scale image-generation scores, but no DeLoRA-like robustness gain.

**Implication for ours (assessment):** “magnitude can be fixed with little quality change” is prior art in training. Our posthoc removal of the full radial factor from a trained checkpoint is a different intervention; exact formulas must carry that distinction. The endpoint result does not test DeLoRA’s training-robustness claim or establish equally effective DoRA training without magnitude learning.

## 4. Parameter Efficient Fine-tuning via Explained Variance Adaptation — NeurIPS 2025 main

**Status:** [official proceedings](https://papers.nips.cc/paper_files/paper/2025/hash/41d33bd41fd44bd9dba0e092047cf213-Abstract-Conference.html) explicitly says Main Conference Track. Earlier author versions use “One Initialization to Rule them All”; that is not a separate accepted paper.

**Contribution/evidence:** EVA initializes LoRA from activation singular directions and reallocates a fixed rank budget; the accepted abstract adds an expected-gradient-signal justification. The [author version/supplement](https://arxiv.org/html/2410.07170v3), §3/Appendices C–I, evaluates language generation/understanding, image classification and reinforcement learning. Concrete breadth includes two encoders on eight GLUE tasks and VTAB-1K’s 19 datasets. Controls include equal-rank budgets and whitening, random rotation/permutation, and redistribution ablations; five-seed GLUE summaries are reported. These distinguish direction, scale and allocation at initialization.

**Implication for ours (assessment):** the elementary operation, activation SVD, is not the entire novelty; it connects a justified choice to training behavior under controlled budgets. Endpoint weight geometry neither reproduces EVA initialization nor tests its gradient claim. Radial-specific interpretation needs alternatives matching relevant scale while changing direction/structure. Endpoint correlation identifies less than these ablations.

## 5. How Much is Too Much? Exploring LoRA Rank Trade-offs for Retaining Knowledge and Domain Robustness — Findings, IJCNLP–AACL 2025

**Status:** [ACL Anthology](https://aclanthology.org/2025.findings-ijcnlp.58/) labels Venue: Findings and ID 2025.findings-ijcnlp.58. The volume title is confusing; this is not an NLP main-track comparator.

**Contribution/evidence:** [paper](https://aclanthology.org/2025.findings-ijcnlp.58.pdf), §§3–5/Tables 1–3, extends rank/performance/forgetting comparison to Llama-3.1-8B-Instruct and Qwen-2.5-7B-Instruct. It trains on GSM8K/MMLU/MedMCQA, sweeps ranks 8–128, and includes MathQA/legal-QA transfer plus spectral/attention analysis. Base, LoRA and full-SFT baselines are compared. Most training hyperparameters are held constant rather than optimized separately per method. I did not verify independent-seed uncertainty in the inspected results; this is not a uniformly ideal evaluation template.

**Implication for ours (assessment):** a bounded empirical extension can reach Findings without a new adapter, but this example varies model family, trained rank and transfer domain. Ours has finer paired interventions but narrower independent coverage. This acceptance does not establish that our current evidence suffices there. A precise posthoc DoRA question is more distinctive than another general rank/accuracy sweep.

## 6. Fine-tuning Happens in Tiny Subspaces: Exploring Intrinsic Task-specific Subspaces of Pre-trained Language Models — ACL 2023 main, long paper

**Status:** [official Anthology](https://aclanthology.org/2023.acl-long.95/), Volume 1: Long Papers; not Findings. This is a geometry/PEFT comparator rather than a direct DoRA predecessor.

**Contribution/evidence:** [paper](https://aclanthology.org/2023.acl-long.95.pdf), §4/Tables 1–3, uncovers task subspaces through principal directions of training trajectories. BERT-base and RoBERTa-base are studied across eight GLUE tasks, averaging five seeds. It tests same-task and transferred/unified subspaces and compares full training, frozen encoders and random subspaces. Outlier-dimension ablations compare disabling selected dimensions with random dimensions and find strong task-specific sensitivity.

**Implication for ours (assessment):** geometry becomes informative when the chosen subspace predicts intervention effects better than an alternative. Tiny-subspace/spectral concentration alone are longstanding observations. Our endpoint intervention is distinct, but singular values and correlations add limited conceptual novelty without predicting why this component is removable while alternatives are not. Training-trajectory subspace dimension, matrix rank and radial norm are different objects.

## 7. Learning Rate Matters: Vanilla LoRA May Suffice for LLM Fine-tuning — ICML 2026 workshops, author-reported acceptance

**Status boundary:** [official author repository](https://github.com/yuang-lee/lr-matters-lora) announces HiLD and CoLoRAI acceptance on 2026-07-06. The [OpenReview PDF](https://openreview.net/pdf?id=fQ79zHBsjm) is HiLD 2026-branded; the [organizer website](https://sites.google.com/view/hidimlearning/home) verifies that workshop’s ICML 2026 identity. I could not read the decision/presentation subtype because the forum was browser-challenged. This is author-supported workshop acceptance, never ICML main acceptance.

**Contribution/evidence:** [author text, v2](https://arxiv.org/html/2602.04998v2), §§3–4/Appendices A/D–I, audits hyperparameter practices and re-evaluates vanilla LoRA plus nine variants, including DoRA. Searches vary learning rate, batch size, rank and duration over four task types and model sizes 0.6B–13B. Qwen/Gemma experiments use three independent runs. Hessian analysis links optimal learning-rate ranges to curvature. The critical result concerns peak-performance similarity under tested searches, not universal inferiority of variants.

**Implication for ours (assessment):** “LoRA and DoRA can have similar quality” has close precedent with much broader optimized training evidence. Our possible value is the endpoint component test and its boundaries. Workshop status does not imply weak controls or a trivial computational study, and is not a low-bar guarantee for our work.

## Nearby preprints restricting novelty without an established venue precedent

- [LoRA-Squeeze: Simple and Effective Post-Tuning and In-Tuning Compression of LoRA Modules](https://arxiv.org/abs/2602.10993), 2026: high-source-rank training followed by SVD compression, including posthoc and rank-annealing variants; abstract reports 13 text and 10 vision-language tasks. No accepted venue verified. Generic high-rank-then-compress is not a new framing for our rank32/E95 result. The separate claims recheck covers exact overlap and sophisticated-variant exclusions.
- [Shortcuts in the Tail: Debiasing via Post-Hoc Spectral Compression of Fine-Tuning Updates](https://arxiv.org/abs/2606.07596), 2026: abstract reports three instruction-tuned models/four classification benchmarks and top-/bottom-/random-component plus matched-rank-LoRA controls. The [OpenReview PDF](https://openreview.net/pdf?id=4ZSmSVsUjI) is workshop-branded; acceptance not independently verified. It is relevant conceptual competition for useful posthoc compression without an accepted-status claim.

## Assessment of the remaining scientific distinction

A compact empirical or critical idea can support publication when independent variation, useful behavioral endpoints and discriminating controls carry it. Our fixed-checkpoint arithmetic and paired-score accounting improve credibility but do not create those missing distinctions.

The unresolved contribution is whether **DoRA’s radial factor is active yet selectively dispensable at inference across independently trained/adapted checkpoints**, while retaining the claimed task/retention trade-off. Current data establish one active GSM8K endpoint with close mean accuracy, not “selectively” or independent replication. Removing D changes answers, so preserved mean accuracy is not unchanged function. Comparable-strength alternative perturbations matter particularly given Intruder’s neighboring-direction and EVA’s direction/scale controls. A training-mechanism claim needs training evidence; an endpoint paper can remain narrower but must state the boundary.

