#!/usr/bin/env python3
"""Launch base/LoRA/DoRA on 1-3 idle GPUs. Default serial execution on one."""
import argparse
import concurrent.futures
import json
import subprocess
import sys
import time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lora_dora_study.server import (available_memory_bytes, gpu_snapshot, idle_gpu,
                                     write_json)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, choices=[1, 2, 3], default=1)
    parser.add_argument("--downloads", default="results/download.json")
    parser.add_argument("--output-dir", default="results/pilot-serial")
    parser.add_argument("--cases", type=int, choices=range(1, 9), default=2)
    parser.add_argument("--merge-check", action="store_true")
    args = parser.parse_args()
    snapshot = gpu_snapshot()
    idle = [g for g in snapshot["gpus"] if idle_gpu(g, snapshot["compute_processes"])]
    if len(idle) < args.workers:
        raise RuntimeError("Not enough idle GPUs for requested worker count")
    memory = available_memory_bytes()
    if memory is None or memory < (10 * args.workers + 2) * 1024 ** 3:
        raise RuntimeError("Insufficient or unknown available host RAM for conservative pilot budget")
    destination = Path(args.output_dir)
    # Each run must have its own directory so measurements are not overwritten.
    destination.mkdir(parents=True, exist_ok=False)
    write_json(destination / "preflight.json", snapshot)
    roles = ["base", "lora", "dora"]
    # Fixed queues: each worker owns one GPU and runs its assigned roles serially.
    queues = [roles[index::args.workers] for index in range(args.workers)]
    started = time.perf_counter()

    def worker(index):
        results = []
        for role in queues[index]:
            command = [sys.executable, "scripts/pilot_worker.py", "--role", role,
                "--gpu-uuid", idle[index]["uuid"], "--downloads", args.downloads,
                "--output", str(destination / (role + ".json")), "--cases", str(args.cases)]
            if args.merge_check:
                command.append("--merge-check")
            with (destination / (role + ".log")).open("w") as log:
                try:
                    result = subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, timeout=600)
                    results.append(dict(role=role, exit_code=result.returncode))
                except subprocess.TimeoutExpired:
                    # subprocess.run kills its own timed-out child, never another job.
                    results.append(dict(role=role, timed_out=True))
            if results[-1].get("exit_code", 1) != 0:
                break
        return results

    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as executor:
        outcomes = list(executor.map(worker, range(args.workers)))
    report = dict(workers=args.workers, gpu_uuids=[g["uuid"] for g in idle[:args.workers]],
                  wall_seconds=time.perf_counter() - started, outcomes=outcomes)
    write_json(destination / "summary.json", report)
    print(json.dumps(report, indent=2))
    if sum(len(queue) for queue in outcomes) != 3 or any(
            result.get("exit_code", 1) != 0 for queue in outcomes for result in queue):
        raise RuntimeError("Pilot incomplete; inspect per-role logs and JSON")


if __name__ == "__main__":
    main()
