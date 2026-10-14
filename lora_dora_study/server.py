"""Read-only server probes. No process termination or GPU reservation here."""
import csv
import datetime
import io
import json
import os
import platform
import shutil
import subprocess
from pathlib import Path


def query(command):
    result = subprocess.run(command, capture_output=True, text=True, timeout=20)
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or "Command failed")
    return result.stdout


def parse_gpus(raw):
    rows = []
    for row in csv.reader(io.StringIO(raw), skipinitialspace=True):
        if not row:
            continue
        if len(row) != 6:
            raise ValueError("Unexpected nvidia-smi GPU row")
        index, uuid, name, total, used, utilization = row
        rows.append(dict(index=int(index), uuid=uuid.strip(), name=name.strip(),
                         total_mib=int(total), used_mib=int(used),
                         utilization_percent=int(utilization)))
    return rows


def gpu_snapshot():
    gpus = parse_gpus(query([
        "nvidia-smi", "--query-gpu=index,uuid,name,memory.total,memory.used,utilization.gpu",
        "--format=csv,noheader,nounits"]))
    processes = []
    for row in csv.reader(io.StringIO(query([
        "nvidia-smi", "--query-compute-apps=gpu_uuid,pid,used_memory",
        "--format=csv,noheader,nounits"])), skipinitialspace=True):
        if not row:
            continue
        if len(row) != 3:
            raise ValueError("Unexpected nvidia-smi process row")
        processes.append(dict(gpu_uuid=row[0].strip(), pid=int(row[1]),
                              memory_mib=row[2].strip()))
    return dict(gpus=gpus, compute_processes=processes)


def idle_gpu(gpu, processes, max_used_mib=1024, max_utilization=10):
    return (gpu["used_mib"] <= max_used_mib
            and gpu["utilization_percent"] <= max_utilization
            and not any(p["gpu_uuid"] == gpu["uuid"] for p in processes))


def available_memory_bytes():
    path = Path("/proc/meminfo")
    if not path.exists():
        return None
    for line in path.read_text().splitlines():
        if line.startswith("MemAvailable:"):
            return int(line.split()[1]) * 1024
    return None


def preflight(directory):
    report = dict(timestamp_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                  hostname=platform.node(), python=platform.python_version(),
                  cpus=os.cpu_count(), available_ram_bytes=available_memory_bytes(),
                  disk_free_bytes=shutil.disk_usage(directory).free)
    try:
        report.update(gpu_snapshot())
    except (OSError, ValueError, RuntimeError, subprocess.TimeoutExpired) as error:
        report.update(gpus=[], compute_processes=[], gpu_probe_error=str(error))
    return report


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n")
    temporary.replace(path)
