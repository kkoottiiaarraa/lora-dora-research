# GSM8K radial-activity read-only inventory — 2026-10-11


## Resources

80 logical CPUs; load averages 24.30/26.96/28.87. MemTotal 791159732 kB, MemAvailable 502945816 kB. Repository filesystem total 99602705072128 bytes, used 5279411892224, free 89323183902720. Instantaneous RTX A4000 snapshots, all 16376 MiB total:

|GPU|utilization %|used MiB|
|---|---:|---:|
|0|0|5856|
|1|42|7314|
|2|0|8102|
|3|36|8582|
|4|98|2510|
|5|77|8586|
|6|73|8584|

These are observations, not reservations or estimates of job safety.

## Pinned original weights

Manifest: `/path/to/user-user/lora-dora-series/results/shadow_4b_gsm8k-downloads.json`.
Cache root: `/path/to/user-user/.cache/lora-dora-research/huggingface/`.

|Role|Exact directory beneath cache root|
|---|---|
|base|`models--Qwen--Qwen3-4B/snapshots/1cfa9a7208912126459214e8b04321603b3df60c`|
|DoRA|`models--shadow-llm--Qwen3-4B-GSM8k-DoRA/snapshots/07f6a59c2ab6b36b1cecb5feb66187638202521d`|
|LoRA|`models--shadow-llm--Qwen3-4B-GSM8k-LoRA/snapshots/83f1d1515f410cd3df48e808ae2071e39a06faf1`|

Base `config.json` 726 bytes: 36 layers, hidden size 2560, intermediate size 9728, 32 attention heads, 8 KV heads, head dimension128, tied embeddings, declared bfloat16. `model.safetensors.index.json` 32819 bytes,398 keys, metadata total_size8044936192. All398 tensor headers BF16.

|Base shard|file bytes|header bytes|tensor count|
|---|---:|---:|---:|
|model-00001-of-00003.safetensors|3957900840|20000|174|
|model-00002-of-00003.safetensors|3987450520|25232|219|
|model-00003-of-00003.safetensors|99630640|552|5|

Both adapters: r32, alpha32, scaling alpha/r=1, fan_in_fan_out=false, bias=none, use_rslora=false, no rank/alpha patterns. DoRA config875 bytes/use_dora=true; LoRA config876 bytes/use_dora=false. Original disk adapter tensors are **F32**, including DoRA m; this differs from deployment BF16 and must be retained in native-precision analysis.

|Adapter file|file bytes|header bytes|tensor count|
|---|---:|---:|---:|
|DoRA adapter_model.safetensors|95684080|58856|432|
|LoRA adapter_model.safetensors|94410616|38768|288|

All144 modules verified: layers0–35 × {q_proj,k_proj,v_proj,o_proj}. DoRA144 A +144 B +144 magnitude vectors; LoRA144 A +144 B. Disk key stem `base_model.model.model.layers.{layer}.self_attn.{projection}`; suffixes `.lora_A.weight`, `.lora_B.weight`, `.lora_magnitude_vector` (m has **no `.weight` suffix**). Runtime PEFT may add `.default`; it is absent from disk.

|Projection|base W [out,in]|A|B|m|
|---|---|---|---|---|
|q|[4096,2560]|[32,2560]|[4096,32]|[4096]|
|k|[1024,2560]|[32,2560]|[1024,32]|[1024]|
|v|[1024,2560]|[32,2560]|[1024,32]|[1024]|
|o|[2560,4096]|[32,4096]|[2560,32]|[2560]|

Map adapter stem to base key by removing prefix `base_model.model.` and appending `.weight`. Index lookup succeeds for all144 modules:64 in shard1,80 in shard2,0 in shard3. Use index mapping rather than inferring shard from layer. Combined m length313344; do not average module summaries as if rows had equal counts.

## Existing small diagnostics and calibration

Original profiler root `/path/to/user-user/lora-dora-profiling/interventions-direct/`:

- `gsm8k-remove_d-all/intervention.json` 8372 bytes: keys method,targets,modules,interpretation;144 module names. No D, m, base norms, or BF16 activity arrays/statistics.
- `gsm8k-dense-dora/intervention.json` 15751 bytes: method,modules,dense_fidelity,calibration_source,calibration_tokens,interpretation. Module records contain module,adapter_rank only. Dense fidelity max_abs_logits_error1.34375,argmax_agreement0.9814814925193787;54 calibration tokens. This is original PEFT→dense fidelity, not the new radial activity measurement.
- Accepted analysis `execution/scientific-analysis/build_components.py` explicitly records unavailable D−I, learned m minus base norms, and BF16 activity. Original diagnostic fields do not answer point1.

Calibration source exists: `/path/to/user-user/lora-dora-series/datasets/gsm8k-train-calibration.jsonl`,4166206 bytes,7473 lines; JSON records include question,answer. First question begins Natalia sold clips; original diagnostic used first line with128 token cap and actual54 tokens. This is an available input for an authorized future forward check, not saved per-module activations. No existing per-module calibration activations were established by this inventory.

Missing quantities to compute: native F32 m and A/B with BF16 base promoted to F32; row norms of U=W0+sBA; D=m/norm_rows(U); D−1 distributions and learned m−norm_rows(W0); native radial delta versus learned update; deployed dtype reconstruction and elementwise BF16 change/rounding statistics. Safetensors header inspection establishes shapes/dtypes, not numerical values or activity. New analysis must state arithmetic/casting order and distinguish original native adapter precision from PEFT deployment behavior.
