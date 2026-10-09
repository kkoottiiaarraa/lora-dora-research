# Research execution constraints

Read `LORA_DORA_RESEARCH_CONTEXT.md`, `CHECKPOINT_INVENTORY_2026-10-09.md`,
`docs/RESEARCH_PROTOCOL.md`, and `docs/HANDOFF.md` before continuing.

- This is a new isolated research checkout. Do not modify the user's other
  repository, other environments, or other users' processes.
- Work on already trained public checkpoints; no training requested.
- Maximum three GPUs simultaneously across all research jobs. Start with one.
  Inspect nvidia-smi immediately before launching. Avoid a GPU with an existing
  compute process, >1024 MiB used, or >10% utilization. Unknown probe state
  means do not launch. Cooperative locks do not reserve GPUs from other users.
- If this server has a scheduler or allocation rules, follow them before these
  idle-GPU heuristics. Do not stop or evict any existing process.
- Use a dedicated venv and cache. Inspect the existing CUDA/PyTorch version
  before installing dependencies. Never change global packages or use sudo
  for this research. Keep downloads out of Git, cap download workers at two.
- First pilot is Qwen3-4B/GSM8K, BF16, batch=1, short context, no quantization.
  Restrict each pilot worker to one GPU via CUDA_VISIBLE_DEVICES before importing
  Torch. CPU workers/threads initially two. Report download, load and inference
  timings separately. Measure actual VRAM and host RAM before adding workers.
- GPU scripts have not yet been runtime verified. Validate on the first pilot,
  record dependency versions and any fixes. Do not call a syntax check an
  inference success; do not call eight smoke examples a quality evaluation.
- Preserve source revisions and unknown training metadata. Include both positive
  and negative DoRA-vs-LoRA comparisons. A final checkpoint intervention is not
  proof of a training mechanism; a weight correlation is not itself causality.
- Never save passwords, auth keys or account tokens in research files/reports.
  Do not inspect unrelated credentials or print full process command lines.
- Latest access decision: the user cancelled the HTTPS API/Cloudflare route and
  is considering Codex CLI on their Finland VM. The CLI may run there; the GPU
  server runs ordinary research scripts only. See docs/VM_CLI.md. No CLI or API
  has been installed remotely by this cloud agent. Keep VM memory use small:
  one CLI session, code and small reports only; download/load weights on GPU host.
