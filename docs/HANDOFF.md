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
The user confirmed the Finland VM is connected to Tailscale (Ubuntu 24.04.4 LTS,
accept-dns/routes off). They installed the relay and returned a successful SSH
banner. Endpoint: 100.105.205.79:2222, relayed to 185.185.59.19:22.
Service: lora-dora-ssh-relay.service; SSH banner:
SSH-2.0-OpenSSH_9.6p1 Ubuntu-3ubuntu13.19. This proves the VM-local relay, not
SSH host identity/authentication or cloud access. The agent has not executed
any remote command. No GPU diagnosis or model restoration has run.

The user also supplied screenshots of the published cloud environment with
Tailscale marked Configured. Its UI has **no separate TCP/IP/CIDR field**;
do not repeat the earlier mistaken request to find one. This original cloud
task still has vpn_configured=false and empty TCP grants. The official docs
say updated published configurations apply to new tasks while existing tasks
keep their state. First inspect a new task started from the published setup.
Runtime CONNECT requires VPN + TCP grant; do not assume Internet=Unrestricted
adds that grant. If the fresh environment has none, report the platform policy
gap and request its supported configuration flow; do not bypass it.

Branch: `research/prepare-checkpoint-study`. Cloud workspace:
`/workspace/lora-dora-research`. Clone into a new directory on the server.
The restored cloud environment should use the same branch and ordinary SSH
commands to operate a new server-side checkout. Read `docs/REMOTE_ACCESS.md`.
Full public inventory is `checkpoint_inventory.json`; first pinned pilot is
`configs/shadow_qwen3_4b_gsm8k.json` with about 8.25 GB selected downloads.

Prepared: research protocol, metadata manifest, eight pinned GSM8K test examples,
NumPy weight algebra, read-only server probe, checksum-verified downloader and
bounded pilot scripts. Ten CPU tests pass. GPU execution and package compatibility
still need validation on real hardware. No measured quality gap or mechanism
has been established by us. Raw third-party downloads are ignored, not vendored.

## Next authorized steps

1. Read the root context, inventory, protocol and AGENTS.md. Before any server
   work, inspect /etc/codex/network-policy.json and current environment status.
   Confirm that this is the updated VPN-configured environment and use the
   permitted CONNECT workflow for 100.105.205.79:2222 if the grant exists.
   Do not attempt a denied route. SSH username: kotelnikovni. Credentials were
   supplied in the original chat and deliberately not saved in Git; a new task
   may need the user to provide authentication after transport is verified.
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
