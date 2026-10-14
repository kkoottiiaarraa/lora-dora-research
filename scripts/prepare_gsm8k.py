#!/usr/bin/env python3
"""Download canonical test JSONL on GPU host only; preserve exact source + SHA."""
import argparse
import json
import sys
import time
import urllib.request
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lora_dora_study.evaluation import sha256_file
from lora_dora_study.server import write_json


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--config", default="configs/gsm8k_evaluation.json")
    p.add_argument("--output-dir", default="datasets/gsm8k-matched-v1")
    args = p.parse_args()
    config = json.loads(Path(args.config).read_text())
    destination = Path(args.output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    path = destination / "test.jsonl"
    url = ("https://raw.githubusercontent.com/openai/grade-school-math/" +
           config["dataset_revision"] + "/" + config["dataset_path"])
    started = time.perf_counter()
    cached = path.exists()
    if not cached:
        with urllib.request.urlopen(url, timeout=60) as response:
            data = response.read(10 * 1024**2)
        temporary = path.with_suffix(".tmp")
        temporary.write_bytes(data)
        temporary.replace(path)
    rows = [json.loads(line) for line in path.read_text().splitlines()]
    if len(rows) != config["expected_rows"]:
        raise ValueError("Unexpected test split size")
    for row in rows:
        if set(row) != {"question", "answer"} or "####" not in row["answer"]:
            raise ValueError("Unexpected GSM8K row")
    fixtures = [json.loads(line) for line in Path("fixtures/gsm8k_pilot_8.jsonl").read_text().splitlines()]
    for fixture in fixtures:
        source = rows[fixture["test_row_index"]]
        if source["question"] != fixture["question"] or source["answer"] != fixture["answer"]:
            raise ValueError("Canonical data disagrees with previously pinned HF fixture")
    manifest = dict(source=url, revision=config["dataset_revision"], rows=len(rows),
                    sha256=sha256_file(path), bytes=path.stat().st_size,
                    path=str(path.resolve()), cached=cached,
                    download_or_cache_seconds=time.perf_counter()-started,
                    hf_fixture_rows_verified=len(fixtures),
                    note="Canonical author test JSONL; full HF parquet equality not established")
    old = destination / "manifest.json"
    if old.exists() and json.loads(old.read_text())["sha256"] != manifest["sha256"]:
        raise ValueError("Existing dataset hash changed")
    write_json(old, manifest)
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
