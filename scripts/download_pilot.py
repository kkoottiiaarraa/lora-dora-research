#!/usr/bin/env python3
"""Download only pinned pilot files to a dedicated server cache, verify weights."""
import argparse
import hashlib
import json
import shutil
import sys
import time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lora_dora_study.server import write_json


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", default="configs/shadow_qwen3_4b_gsm8k.json")
    parser.add_argument("--cache", default="cache/huggingface")
    parser.add_argument("--output", default="results/download.json")
    parser.add_argument("--plan-only", action="store_true")
    args = parser.parse_args()
    manifest = json.loads(Path(args.manifest).read_text())
    total = sum(f["size"] or 0 for artifact in manifest["artifacts"].values()
                for f in artifact["files"])
    if args.plan_only:
        print(json.dumps(dict(download_bytes=total, roles=list(manifest["artifacts"])), indent=2))
        return
    from huggingface_hub import snapshot_download
    cache = Path(args.cache).resolve()
    cache.mkdir(parents=True, exist_ok=True)
    # An empty-cache download must leave room for reports and temporary files.
    # Existing blobs are shared across snapshots and are not downloaded again.
    if shutil.disk_usage(cache).free < total + 2 * 1024 ** 3:
        raise RuntimeError("Insufficient free disk for conservative pilot budget")
    report = dict(pair=manifest["pair"], artifacts={})
    write_json(args.output, report)
    for role, artifact in manifest["artifacts"].items():
        started = time.perf_counter()
        directory = Path(snapshot_download(repo_id=artifact["repo_id"],
            revision=artifact["revision"], cache_dir=str(cache),
            allow_patterns=[f["path"] for f in artifact["files"]], max_workers=2))
        elapsed = time.perf_counter() - started
        started = time.perf_counter()
        verified = []
        for file in artifact["files"]:
            path = directory / file["path"]
            if not path.is_file():
                raise RuntimeError("Missing pinned file: " + file["path"])
            if file["size"] is not None and path.stat().st_size != file["size"]:
                raise RuntimeError("Size mismatch: " + file["path"])
            if file["sha256"]:
                digest = hashlib.sha256()
                with path.open("rb") as stream:
                    for block in iter(lambda: stream.read(8 * 1024 ** 2), b""):
                        digest.update(block)
                if digest.hexdigest() != file["sha256"]:
                    raise RuntimeError("Hash mismatch: " + file["path"])
                verified.append(file["path"])
        report["artifacts"][role] = dict(repo_id=artifact["repo_id"],
            revision=artifact["revision"], snapshot_path=str(directory),
            download_or_cache_lookup_seconds=elapsed,
            verification_seconds=time.perf_counter() - started,
            sha256_verified_files=verified)
        write_json(args.output, report)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
