# Research continuation

## Current decision (2026-10-09)

The user cancelled the proposed HTTPS research API/Cloudflare route as too
complicated. They now want to assess Codex CLI on their own Finland VM, which
would operate the GPU server through ordinary SSH. This supersedes the earlier
preference to keep the agent exclusively in Codex Cloud. Do not install an agent
on the shared GPU server. See `docs/VM_CLI.md` for feasibility, measurement limits
and the small setup procedure.

The Finland VM is Ubuntu 24.04.4 LTS, 1 vCPU, 2 GB RAM, 32 GB NVMe, 500 Mbps.
User-confirmed public IP: 2.26.67.204; Tailscale IP: 100.105.205.79.
TCP ports 80/443 are occupied by docker-proxy (IPv4 and IPv6); container identity
and actual VPN CPU/RAM use are unknown. Do not modify those containers or VPN.
Root credentials were supplied in the chat and intentionally not stored here.
No SSH authentication or command from this agent has succeeded on either host.
No remote CLI/API installation, model download or GPU pilot has occurred.

The cloud executor uses the inherited HTTP/HTTPS proxy. This original task has
vpn_configured=false and empty TCP grants; proxy:8088 refuses connections.
The user also tested a fresh published task: vpn_configured=true, still empty
TCP grants and refused listener. There is no confirmed UI field for TCP grants.
Do not ask them to repeat that test or contact Support: they rejected that route.
The working VM-local SSH relay at 100.105.205.79:2222 to 185.185.59.19:22 proves
only VM-local TCP forwarding and an SSH banner, not cloud access or authentication.
The hostname vm2093721.vds.chsl.one was NXDOMAIN in public DNS during this session.

Cancelled HTTP drafts were never committed, pushed or deployed. They are archived
outside Git at /tmp/lora-dora-cancelled-http-api-20261009 in this cloud executor.
No installer or Cloudflare service was created. Their private signing key is
outside Git and is not used by the new route. Do not restart API development.

## Research scope and preparation

Analyze already trained matched DoRA/LoRA checkpoints and mechanisms behind their
quality differences. No training requested. Audit found ten main candidate pairs
plus reserve Mistral/PeRL series; metadata/file access is not runtime validation.
Our symmetry argument establishes that the original magnitude/direction metric
is not invariant; it does not refute DoRA's quality advantage or establish a
replacement mechanism. Preserve those distinctions and negative-control pairs.

Branch: research/prepare-checkpoint-study. Cloud checkout:
/workspace/lora-dora-research. Use a new directory on the GPU server, next to
the user's other repository; do not touch that repository. SSH host:
185.185.59.19; user: kotelnikovni. Authentication is still unchecked.

Prepared: `checkpoint_inventory.json`, protocol, pinned pilot manifest
`configs/shadow_qwen3_4b_gsm8k.json` (about 8.25 GB), eight fixed GSM8K smoke
examples, NumPy algebra, read-only preflight, verified downloader, bounded pilot.
Ten CPU tests pass. GPU dependency compatibility and inference remain untested.
Reported hardware: seven RTX A4000 16 GiB; actual utilization is unknown.
Max three GPUs simultaneously, first pilot one idle card; follow scheduler rules.

## Next steps

1. Obtain the VM's actual baseline (RAM, ten-second CPU sample, Docker stats).
   The cloud cannot inspect it directly with the current transport. The user can
   run the read-only commands in `docs/VM_CLI.md` from their existing VM terminal.
2. If sufficient headroom remains, install official standalone Codex CLI under
   an ordinary VM user, sign in using device code, clone this branch. Give the
   VM-side CLI `AGENTS.md`, context, inventory, protocol and this handoff.
3. Establish ordinary VM-to-GPU SSH, preserving host-key verification. Bootstrap
   a new GPU checkout. Read scheduler/allocation rules; run server preflight and
   report real GPU utilization, RAM/disk and compatible CUDA/PyTorch.
4. Prepare GPU-local venv/cache, download the first pinned pair, verify hashes.
5. Pilot base/LoRA/DoRA serially on one idle card. Record separate download/load/
   adapter/inference timings, VRAM and host RAM. Only then consider 2–3 workers.
6. Report a measured resource/time estimate and fix runtime/merge fidelity issues
   before full evaluation. Eight smoke examples are not a quality comparison.

Communicate in Russian. Keep the access procedure simple. Do not claim actual
VM or GPU measurements from cloud-only tests.
