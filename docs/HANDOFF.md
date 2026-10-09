# Continuation after cloud environment replacement

## Current state

The user is investigating why DoRA sometimes beats LoRA, primarily using
already trained matched checkpoints. They prefer mathematical/posthoc analysis
over training because GPU time is limited. Audit found ten main candidate pairs
and reserve Mistral/PeRL series; this is not runtime validation of all pairs.

The user's server reportedly has seven RTX A4000 cards (16 GiB each). Actual
hardware, utilization, CUDA/PyTorch and model load times have **not been checked**:
the cloud executor has HTTPS but no configured VPN/TCP access. No SSH command
has run on the server. The other existing repository must not be modified.

The user confirmed that the agent must remain in the cloud. They considered
server-local Codex CLI and then cancelled that route. Do not install an agent
on the GPU server. The agreed access path is cloud Tailscale VPN to the user's
Finland VM, which relays one TCP port to the GPU server's existing OpenSSH.
There is no sudo permission on the GPU server; none is required for this relay.
The user sees the Tailscale option in Codex Cloud settings. They confirmed the
Finland VM is connected to Tailscale (Ubuntu 24.04.4 LTS, accept-dns/routes off).
Its SSH relay and cloud VPN/TCP grants still need completing. The agent has not
executed any remote command. `scripts/setup_ssh_relay.py` is prepared for the
user to install the relay on their own VM, not on the GPU server.

Branch: `research/prepare-checkpoint-study`. Cloud workspace:
`/workspace/lora-dora-research`. Clone into a new directory on the server.
The restored cloud environment should use the same branch and ordinary SSH
commands to operate a new server-side checkout. Read `docs/REMOTE_ACCESS.md`.
Full public inventory is `checkpoint_inventory.json`; first pinned pilot is
`configs/shadow_qwen3_4b_gsm8k.json` with about 8.25 GB selected downloads.

Prepared: research protocol, metadata manifest, eight pinned GSM8K test examples,
NumPy weight algebra, read-only server probe, checksum-verified downloader and
bounded pilot scripts. CPU tests pass. GPU execution and package compatibility
still need validation on real hardware. No measured quality gap or mechanism
has been established by us. Raw third-party downloads are ignored, not vendored.

## Next authorized steps

1. Read the root context, inventory, protocol and AGENTS.md.
2. Run `python3 scripts/server_preflight.py --output results/preflight.json`.
   Report actual utilization of all GPUs, available RAM and disk. Inspect
   compatible Python/Torch/CUDA without dumping other users' command lines.
3. Prepare an isolated venv, reuse compatible system Torch if appropriate,
   install pinned research dependencies locally. GPU scheduler rules take
   precedence over idle heuristics. Do not alter the other checkout.
4. Download only the first public 4B pair, directly into server-local cache,
   verify revisions/hashes and adapter configurations. No training.
5. Pilot base, LoRA and DoRA serially on one idle GPU, batch=1. Save actual
   load timings, peak allocated/reserved VRAM, process RSS and generation speed.
   Then assess whether two or three independent GPU workers are feasible.
   Max three concurrently; do not use occupied cards or stop any other job.
6. Give the user a measured time/resource estimate, distinguishing download,
   cold/warm load, adapter attachment, inference and analysis. Do not extrapolate
   complete evaluation time from a single token or ignore longer context costs.
7. Fix runtime issues, verify merge fidelity, reproduce full evaluation before
   explaining a checkpoint quality difference. Retain negative-control pairs
   and author-score inconsistency in the Shadow GSM8K tables.

User communications are in Russian. Progress autonomously on these authorized
steps and give concise updates. Ask only for genuinely missing access or scope.
