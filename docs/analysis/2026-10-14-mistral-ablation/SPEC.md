# Conditional Mistral8case screen, fixed before weights/outputs

14 October2026. Motivation: Qwen fresh64 confirmed raw V/O ablation KL-ordering
reversal, but secondary gold-NLL relevance remains uncertain. Do not launch a
large Qwen generation study on this basis. One bounded second-architecture
screen tests empirical prevalence, not just the known algebraic symmetry.
This is not replication of the failed joint compression candidate.

## Source and provenance

- Base mistralai/Mistral-7B-v0.1, already downloaded, revision
  27d67f1b5f57dc0953326b2601d68371d40ea8da. Verify both tensor shard hashes
  against HF blob names or pinned HF metadata before loading.
- DoRA fzzhang/mistralv1_dora_r32_25e5_e05, revision
  f27c212d9067b676e50db989d99c6b90bcf491a4; file SHA256
  b03e743d22a0ca0106d6a2c1b6feff250b24dd4a233a2e216d0870aa3dc2981a.
  Public, BF16 saved480tensors/160targets, rank32/alpha64. Load FP32 and
  verify every saved value after exact BF16-to-FP32 cast. Targets q/k/v/o
  ANDgate_proj,32layers. Gate remains unchanged during V/O interventions.
- Author card declares seed0/lr2.5e-5/5epochs, datasetNone. Author project
  [Spectral Adapter2024](https://github.com/pilancilab/spectral_adapter),
  pinned3c182800f7854b156d63a3f1282713429bbf4942, uses GSM8K and
  `question: QUESTION answer: ANSWER`, but defaults rank8/alpha16/2epochs
  differ from this checkpoint. Training dataset/base revision/seed execution
  are not verified. Do not claim controlled training comparison or author
  benchmark reproduction. This is not the SORA2025 paper by name association.
- Author DoRA forward inspected: row norm of W0+sBA (dim1); this matches
  the inference formula used here. Custom spectral flags in config are false.
  Do not import or execute the author training code or install its environment.

## Procedure and stop rule

No new model training or GPU; CPU16, FP32SDPA. Dedicated existing environment.
Download only the94MBadapter and any missing lightweight tokenizer metadata
on compute host, max2workers. All weights/tensors stay there.

First8eligible questions among the frozen Qwen fresh64 list, matched by train
index/content. Use author-style plain prefix, BOS from tokenizer; tokenize
full prefix+gold answer with offsets and select first32answer tokens. This
avoids boundary-tokenization mismatch. No chat template or5-shot accuracy
claim. Inputs/cases/source/hash manifest frozen before first native output.

Same10conditions as Qwen screen: raw V/O×c=.995/1/1.005, v_shape_off,
o_shape_off,gain_off at1,and pair_off once. Same relative row-centering rule.
Verify160native modules/480tensors and all r/alpha/scaling. Source native
first4case repeats must be bitwise equal. Convert all160targets to a common
dense execution path (including unchangedgate), retain32V/O pairs. Cache8
dense source references. Controls:8native/dense,8source-gauge,24centered-gauge
on first4cases. Require maxcontrolRMS<1%minimuminterventionRMS; source restored
bitwise on one case after all swaps. Save finite80rows/256tokens per condition.

Advance only on the same screen gate: raw V/O mean-KL ordering reversal over
fixed modest gauges and contrast range>10%maxrawKL, OR a raw gold-NLL mean
sign reversal with range>.001nat/token. Numerical controls must pass. No p
claims from8exploratory cases. Negative is retained; no new c/layer selection.
Positive motivates a separately frozen fresh64confirmation, not automatic
full generation. Protected20min runtime, failed attempt saved/no GPU hold.

This is an independent trained artifact/architecture, not multiple training
seeds, and does not by itself establish B-level novelty or useful accuracy.
General implementation invariance and gauge audits have prior work described
in ../2026-10-14-ablation-commutation/PRIOR.md.
