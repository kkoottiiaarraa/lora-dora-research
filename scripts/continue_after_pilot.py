#!/usr/bin/env python3
"""Continue the authorized pipeline after deferred pilot; stop on any runtime error.

Records each completed stage in HANDOFF. No training, no interventions before a
valid complete quality baseline. All workers are sequential on one idle GPU.
"""
import argparse
import datetime
import fcntl
import json
import os
import subprocess
import sys
import time
import traceback
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lora_dora_study.server import gpu_snapshot, write_json
from scripts.wait_for_pilot import stable_idle
from scripts.evaluate_gsm8k import validate_pilot
from scripts.compare_gsm8k import compare


def handoff(stage, data):
    path = Path("docs/HANDOFF.md")
    text = ("## Автоматическая запись этапа: " + stage + "\n\nUTC: " +
            datetime.datetime.now(datetime.timezone.utc).isoformat() +
            "\n\n```json\n" + json.dumps(data, ensure_ascii=False, indent=2) + "\n```\n\n")
    temporary = path.with_suffix(".tmp")
    temporary.write_text(text + path.read_text())
    temporary.replace(path)


def await_idle(state, output):
    previous = set()
    while True:
        try:
            snapshot = gpu_snapshot()
            previous, stable = stable_idle(previous, snapshot)
            state.update(idle_uuids=sorted(previous), stable_idle_uuids=sorted(stable))
        except Exception as error:
            previous, stable = set(), set()
            state["probe_error"] = str(error)
        state["timestamp_utc"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        write_json(output, state)
        if stable:
            return sorted(stable)[0]
        time.sleep(10)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--waiter-dir", type=Path, required=True)
    p.add_argument("--output-dir", type=Path, required=True)
    p.add_argument("--downloads", default="results/reverify-20261009.json")
    args = p.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=False)
    state_path = args.output_dir / "state.json"
    state = dict(status="waiting_for_pilot", pid=os.getpid(), waiter_dir=str(args.waiter_dir),
                 next_stage="pilot runtime validation then GSM8K smoke/full, serial one GPU")
    lock_path = Path("/tmp") / ("lora-dora-continuation-" + str(os.getuid()) + ".lock")
    with lock_path.open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        try:
            write_json(state_path, state)
            while True:
                waiter = json.loads((args.waiter_dir / "waiter.json").read_text())
                state.update(pilot_status=waiter["status"], pilot_checks=waiter["checks"])
                write_json(state_path, state)
                if waiter["status"] == "complete":
                    break
                if waiter["status"] == "failed_needs_inspection":
                    raise RuntimeError("Deferred pilot failed; inspect logs before continuing")
                # Detect a dead waiter, without examining or altering anyone else's process.
                try:
                    os.kill(waiter["pid"], 0)
                except ProcessLookupError:
                    raise RuntimeError("Recorded pilot waiter exited before completion")
                time.sleep(10)
            pilot_dir = Path(waiter["attempt_path"])
            downloads = json.loads(Path(args.downloads).read_text())
            validate_pilot(pilot_dir, downloads)
            pilot = {role: json.loads((pilot_dir / (role + ".json")).read_text())
                     for role in ("base", "lora", "dora")}
            measurements = {role: {k: report[k] for k in
                ["base_load_seconds", "adapter_load_seconds", "first_forward_seconds",
                 "warm_forward_seconds", "merge_fidelity", "inference_memory", "versions"]
                if k in report} for role, report in pilot.items()}
            handoff("пилот выполнен", dict(path=str(pilot_dir.resolve()),
                    measurements=measurements,
                    next_step="Одинаковая оценка качества; smoke не является accuracy"))
            directories = {}
            for phase, limit in [("evaluation-smoke", 2), ("evaluation-full", None)]:
                for role in ("base", "lora", "dora"):
                    state.update(status="waiting_for_evaluation_gpu", phase=phase, role=role)
                    selected = await_idle(state, state_path)
                    destination = args.output_dir / phase / role
                    command = [sys.executable, "scripts/evaluate_gsm8k.py", "--role", role,
                        "--gpu-uuid", selected, "--pilot-dir", str(pilot_dir),
                        "--downloads", args.downloads, "--output-dir", str(destination)]
                    if limit:
                        command.extend(["--limit", str(limit)])
                    state.update(status="running", command=command, gpu_uuid=selected)
                    write_json(state_path, state)
                    with (args.output_dir / (phase + "-" + role + ".log")).open("x") as log:
                        subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, check=True)
                    result = json.loads((destination / "summary.json").read_text())
                    if result["status"] != "complete":
                        raise RuntimeError("Evaluator incomplete")
                    handoff(phase + "/" + role, {k: result[k] for k in
                        ["role", "predictions_completed", "full_evaluation", "author_accuracy",
                         "final_accuracy", "truncated_prompts", "hit_token_limit", "memory",
                         "inference_seconds", "versions"]} | dict(path=str(destination.resolve()),
                         next_step="Завершить matched три роли; вмешательства ещё не запускались"))
                    if limit is None:
                        directories[role] = destination
            comparison = compare(directories)
            write_json(args.output_dir / "matched-comparison.json", comparison)
            handoff("matched GSM8K завершён", dict(path=str(args.output_dir.resolve()),
                    results=comparison,
                    next_step="Проверить результаты; реализовать вмешательства и дополнительные пары, включая без выигрыша DoRA"))
            state.update(status="quality_complete_interventions_pending",
                         comparison_path=str(args.output_dir / "matched-comparison.json"))
            write_json(state_path, state)
        except Exception as error:
            state.update(status="failed_needs_inspection", error=str(error))
            write_json(state_path, state)
            handoff("цепочка остановлена с ошибкой", state)
            raise


if __name__ == "__main__":
    main()
