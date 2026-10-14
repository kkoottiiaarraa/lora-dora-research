# Conditional replication notes

Do not launch replication before the full candidate has passed its development
gate and the next question is clear. Current candidate is on Qwen3-4B/GSM8K.
Other already evaluated task adapters on the same base can test task transfer;
they do not constitute a second architecture or new training seeds.

One architecture reserve: public `fzzhang/mistralv1_{lora,dora}_r32_25e5_e05`,
base `mistralai/Mistral-7B-v0.1`. Configs re-read at pinned inventory revisions:

- LoRA revision `e64c0f1a3a1d65bb3c529264cbb672c95b7db8d5`,
  [config](https://huggingface.co/fzzhang/mistralv1_lora_r32_25e5_e05/resolve/e64c0f1a3a1d65bb3c529264cbb672c95b7db8d5/adapter_config.json).
- DoRA revision `f27c212d9067b676e50db989d99c6b90bcf491a4`,
  [config](https://huggingface.co/fzzhang/mistralv1_dora_r32_25e5_e05/resolve/f27c212d9067b676e50db989d99c6b90bcf491a4/adapter_config.json).
- Both rank32/alpha64, bias none, use_rslora false. use_dora differs as expected.
- Targets include **gate_proj as well as q/k/v/o**. The current attention-only
  adapted_modules helper intentionally rejects this extra target. It cannot
  be reused blindly, and gate storage must not be omitted from claimed savings.
- Pinned DoRA safetensors header checked through two HTTP206range requests,
  with no tensor payload downloaded:480tensors, allBF16,46,923,776elements,
  93,847,552payloadbytes. This differs from the current Qwen FP32 adapter.
  A quarter-element **FP32** export would retain about half the source bytes,
  not a quarter. Specify storage dtype and account for unchanged modules.

For a bounded transfer study either support every target explicitly, or compress
only attention while keeping gate unchanged and report the **whole-adapter**
budget including unchanged gate. These answer different questions. Full
gate output-gradient covariance and coupled diagonal solve are more expensive;
estimate actual shapes before committing to that workload.

Per-checkpoint training dataset/provenance remain unresolved in inventory.
Never present this as a controlled LoRA-vs-DoRA training comparison. Compression
fidelity against each checkpoint can still be measured; downstream task quality
requires confirmed tokenizer/prompt and a native baseline. No new weights were
downloaded by this config audit and no Mistral job launched.
