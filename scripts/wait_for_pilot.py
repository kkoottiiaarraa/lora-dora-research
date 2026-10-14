#!/usr/bin/env python3
"""User-authorized 10s polling; two consecutive idle snapshots before one pilot."""
import argparse
import datetime
import fcntl
import json
import os
import subprocess
import sys
import time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lora_dora_study.server import gpu_snapshot, idle_gpu, write_json


def stable_idle(previous, snapshot):
    current = {g["uuid"] for g in snapshot["gpus"]
               if idle_gpu(g, snapshot["compute_processes"])}
    return current, current & previous


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--output-dir", required=True)
    p.add_argument("--downloads", default="results/reverify-20261009.json")
    args = p.parse_args()
    root = Path(args.output_dir)
    root.mkdir(parents=True, exist_ok=False)
    # One research waiter per user. Separate from worker GPU/three-slot locks.
    lock_path = Path("/tmp") / ("lora-dora-pilot-waiter-" + str(os.getuid()) + ".lock")
    with lock_path.open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        previous = set()
        count = 0
        while True:
            count += 1
            report = dict(status="waiting", checks=count, pid=os.getpid(),
                          timestamp_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                          interval_seconds=10, required_consecutive_checks=2)
            try:
                snapshot = gpu_snapshot()
                current, stable = stable_idle(previous, snapshot)
                report.update(snapshot=snapshot, idle_uuids=sorted(current),
                              stable_idle_uuids=sorted(stable))
                previous = current
            except Exception as error:
                previous, stable = set(), set()
                report["probe_error"] = str(error)
            write_json(root / "waiter.json", report)
            if stable:
                selected = sorted(stable)[0]
                attempt = root / ("pilot-attempt-" + str(count))
                command = [sys.executable, "scripts/run_pilot.py", "--workers", "1",
                           "--gpu-uuid", selected, "--downloads", args.downloads,
                           "--output-dir", str(attempt), "--cases", "2", "--merge-check"]
                report.update(status="running", gpu_uuid=selected, command=command)
                write_json(root / "waiter.json", report)
                with (root / ("attempt-" + str(count) + ".log")).open("w") as log:
                    outcome = subprocess.run(command, stdout=log, stderr=subprocess.STDOUT)
                report.update(exit_code=outcome.returncode, attempt_path=str(attempt))
                if outcome.returncode == 0:
                    report["status"] = "complete"
                    write_json(root / "waiter.json", report)
                    return
                # A failed loaded worker needs runtime investigation, no blind retries.
                # A race before destination creation can safely return to waiting.
                if attempt.exists():
                    report["status"] = "failed_needs_inspection"
                    write_json(root / "waiter.json", report)
                    raise RuntimeError("Pilot failed; inspect recorded worker logs")
                report["status"] = "waiting_after_guard_refusal"
                write_json(root / "waiter.json", report)
                previous = set()
            time.sleep(10)


if __name__ == "__main__":
    main()
