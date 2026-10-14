# Distributed important interventions

Live files: `/path/to/user-user/lora-dora-profiling/distributed-important`.
This archive preserves external orchestration without changing the frozen evaluator.

- Physical GPU3 (historical logical lane `gpu1`): dense DoRA, rank32, energy95, baseMagnitudeAll (14.78h after admission).
- GPU2: finish existing SQuADv2 triple, dense LoRA, removeDAll, matched LoRA (7.45h more).
- GPU6: finish existing MMLU triple, short V/O diagnostic, energy99 (2.22h + short check).
- GPU5: finish existing GSM8K baseline triple; retain GPU after completion.

Eight full intervention jobs exactly once. Twelve localization ablations deferred.
Matched LoRA waits for actual rank32 full intervention artifact; statistical comparisons
wait for completed reference outputs. No repeated baseline generation, training,
Qwen8B or LLaVA. Full V/O benchmark and full no-op remain cancelled.

`adopt_distributed.py` is a one-time migration with recorded historical PID guards;
do not rerun against other processes. Existing workers were preserved without signals.
`distributed_important.py` retains the GPU, completes the adopted pair, then runs
its lane sequentially using frozen `held_gpu_worker.py` / `series_worker.py`.
Failures retain CUDA context and are recorded, not silently skipped.
`hold_gpu1_distribution.py` admits GPU1 only after two idle checks 10s apart and
borrows external slot3 under the user's updated five-GPU limit. Other lanes use
original slots0–2. GPU retention is cooperative, not scheduler exclusivity.
`short_vo_validation.py` performs forward-only dense-reference symmetry and weight
statistic checks; no generation benchmark. Initial BF16 dense conversion discrepancy
is recorded separately. No claim about training trajectories follows from this check.
`watch_distributed_handoff.py` records actual transitions in all study HANDOFF files.
`report_distributed.py` snapshots progress/load and conditional timing estimates.

Versions: Python3.12.3, Torch2.5.1+cu121, Transformers4.57.1, PEFT0.17.1,
Accelerate1.11.0. Detailed hashes and the frozen source SHA256 map are in plan/report.
Forecasts use four stratified generation probes/job and live progress; these are not
confidence intervals. Absolute overall ETA is unknown while GPU1 is occupied.

User reassignment: stopped waiting-only GPU1 controller; `admit_important_free_gpu.py`
admitted physical GPU3 after two idle checks, with fallback to another idle GPU.
DenseDoRA two-case smoke passed and full worker started. Estimated lane finish
10 October 2026 ~15:12 UTC+03:00. Use live plan/state, not the historical admission
holder, for current physical assignment.

GPU6 extension: `distributed_localizations.py` safely adopts the running Energy99
full worker, then executes removeD q/k/v/o and baseMagnitude V, ~33.935 additional
GPUh. `extend_gpu6_localizations.py` is the historical one-time transfer, not a
reusable launcher. Seven other localizations remain unscheduled, ~49.573GPUh.
New5localizations have a separate prespecified Holm family over both scorers;
core8family remains unchanged. Latest load/progress/ETA is in external
`distributed-important/localization-schedule-report.json` (VM copy in outputs).
Energy99 and prior MMLU/V/O are not repeated. Expected GPU6 compute completion
11October2026 ~12:40 UTC+03:00, extrapolation rather than guaranteed ETA.

Latest redistribution (10October morning): physicalGPU0 removeD-vo4.80h;
physicalGPU4 removeD-k/v/o/qk25.44h; physicalGPU6 adopts unchanged removeD-q,
then baseMagnitude-v/q/vo23.50future hours, ETA11October~08:00Moscow.
GPU0/4 currently have foreign CUDA contexts and are waiting for2idle checks10s
apart. User authorizes these two additional cards, temporary maximum6.
`admit_localization_gpu.py` admits exact requested cards with external permits4/5;
`distributed_localizations_v2.py` owns the revised9-localization family. No localized
full result was complete when the family expanded; core8 family unchanged.
`rebalance_gpu6.py` is the one-time historical safe transfer, not a reusable launcher.
Three localizations remain unscheduled (baseMagnitude-k/o/qk),23.6245GPUh.
Latest report: external `distributed-important/six-gpu-localization-schedule.json`.
Use current plan/live states rather than earlier historical estimates in this README.

Explicit sharing authorization: user instructed launch on GPU0/4 over unchanged
near-zero-utilization tiny CUDA contexts. `launch_shared_localizations.py` recorded
two real snapshots10s apart and foreign PIDstartticks, then replaced waiting-only
admission processes with `shared_localization_holder.py` / shared controllers.
`shared_held_gpu_worker.py` extends admission for only those authorized contexts;
original frozen generation/scoring/weights/seed and lease-parent checks unchanged.
Each worker saves `shared-admission.json` with actual measurements and decision.
Guard rejects new unknown contexts, >512MiB per known foreign context,
>1024MiB total pre-load VRAM or >10%utilization. Other foreign processes untouched.
External wrapper hashes, actual load and ETAs: `shared-launch-report.json`.

Night schedule: `night-plan.json` assigns remaining baseMagnitude-k/o/qk to three
independent delayed queues, not before10October22:00Moscow (19:00UTC).
`night_localization_admission.py` uses no CUDA or leases before22, then requires
2trulyidle checks10s apart and a free permit among6. No daytime card reservation
or shared-context exception is used for these night queues.
`release_finished_queue_gpus.py` releases only completed own keepers (terminal
complete_gpu_retained, worker_pidNone, no children); current inference and
comparisons are not interrupted. User reversed a brief comparison-stop request;
comparisons stay enabled. Earliest night completion~06:00Oct11 if admitted22;
09–10completion needs admission by~01–02. Runtime timing/admission not guaranteed.
All remaining23.6245GPUh now scheduled; unscheduled0. Historical daytime plan's
three deferred entries are assigned by the authoritative separate night plan.

Release fix: earlier monitor waited for CPUcomparisons, which incorrectly retained
GPU0 while the reference was pending. Superseded: release also triggers at
compute_complete_analysis_pending, provided worker_pidNone and no children.
Remaining comparison work transfers to `finish_comparisons_cpu.py` with no Torch
or CUDA. GPU0 actual transfer via `cpu_compare_released_gpu0.py` verified no GPU
context; other5active inference workers preserved. Global day/night release check
runs every10s; future generic transfer runtime validation pending next completion.
Artifact: `release-after-compute-fix.json`. Comparisons remain enabled.

Latest night override: K and O merged sequentially into historical lane night-k,
started immediately on idle physicalGPU3 after2checks. Per-lane not_before overrides
global22deadline only for K/O; QK remains independently scheduled22Moscow.
Old delayedK/Olaunchers cancelled, no duplicate. Merged15.7435h, ETA11October~07:30.
Plan retains3independent quality contrasts and night Holm family. Automatic release
at end of compute remains enabled. Report: `merged-night-ko-report.json`.
