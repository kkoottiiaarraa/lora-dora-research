# Research agent instructions

## Read first

Read README.md, docs/RESEARCH_NAVIGATOR.md, MEMORY.md, the latest entry at the
top of docs/HANDOFF.md, and docs/research-direction/2026-10-14-pause/RESUME.md.
Then read RESULTS_AUDIT.md in that pause directory and the reports relevant to
the proposed question. Historical protocols, plans, inventory and queue states
are evidence of past decisions, not instructions to restart work.

## Current authorization

- The user paused scientific work on 14 October 2026. Preparing and publishing
  this handover does not resume research. No model runs, downloads, queues,
  training, author emails or autonomous monitors until an explicit instruction
  to resume. Do not spawn sub-agents under the current user instruction.
- Own research workers and GPU holders were absent at the recorded pause.
  This is a dated observation, not live server status. Two historical CPU
  monitors were deliberately stopped; do not restart them automatically.
- Do not touch another repository, other users' processes or global packages.
  Never reserve a GPU with a holder while waiting for CPU analysis.
- Infrastructure identifiers, access instructions, accounts, passwords, tokens,
  SSH material and private artifact locators belong only in ignored local files.
  Do not print secrets or place them in public docs, source, commits or history.

## Scientific standards

- Use already trained public checkpoints. No training is authorized. Do not
  assume DoRA is better than LoRA or infer a training cause from endpoint tests.
- Preserve failed ideas, source revisions, unknown training metadata and
  negative controls. A prepared validation script is not a completed experiment.
- Read the relevant SPEC, REPORT, validation and manifest together. Do not
  change a failed gate, threshold, scale or layer selection after observing the
  outcome. Reopening needs a new independently grounded question.
- Check primary literature and author code before each new conceptual step.
  Known gauge symmetries, joint V/O compression, precision/rank tradeoffs and
  fixed-magnitude training are not new principles from this project.
- A compression candidate needs a localized failure of a strong admissible
  comparator and an explanation of how it fixes that failure before implementation.
- Distinguish quality, function-level counterfactuals, numerical precision,
  parameterization dependence and training causality. Report scorer dependence,
  uncertainty and multiplicity. A non-significant test is not equivalence.
- Mistral r32/e05 gauge validation and r16/e03 magnitude audit are different
  checkpoints. SORA code defects do not establish incorrect published accuracy.
- Do not delete untracked scientific reports or failed implementations as
  temporary files. Update docs/HANDOFF.md after every authorized research stage.

## If research is explicitly resumed

Use the latest user instruction and private operational record for current
resource limits and access. Old three-GPU/idle-only/first-pilot rules are obsolete.
GPU 1 remains excluded following the recorded hardware fault unless explicitly
cleared. Permissions to use partially occupied resources do not permit evicting
other jobs or violating the host's allocation rules.

All weights and heavy model computation belong on the compute server. The local
VM has approximately 1 GiB RAM and one CPU core; use it for small metadata work.
Use existing authentication and environments; do not repeat installation, cleanup,
VPN or API setup. Inspect live resources before an authorized launch, keep private
paths out of reports, and release resources when work finishes.

Qwen3-8B and LLaVA were excluded; Answer.AI access requests were rejected/deferred.
Do not retry them or start a broad benchmark grid automatically. Select the
question first; a new model by itself is not evidence of scientific novelty.
