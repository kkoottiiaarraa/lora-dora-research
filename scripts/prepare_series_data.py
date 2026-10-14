#!/usr/bin/env python3
"""Prepare pinned 4B pair/dataset manifests on GPU host only, workers <= 2."""
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lora_dora_study.evaluation import sha256_file
from lora_dora_study.server import write_json


def main():
    from huggingface_hub import hf_hub_download, snapshot_download
    import pyarrow.parquet as pq
    inventory = json.loads(Path("checkpoint_inventory.json").read_text())
    original = Path("/path/to/user-user/lora-dora-research")
    base = json.loads((original / "results/reverify-20261009.json").read_text())["artifacts"]["base"]
    cache = "/path/to/user-user/.cache/lora-dora-research/huggingface"
    datasets = dict(
        mmlu=dict(repo="cais/mmlu", revision="c30699e8356da336a370243923dbaf21066bb9fe",
                  file="all/test-00000-of-00001.parquet", rows=14042, max_new_tokens=10,
                  sha256="74a41822ce7d3def56e1682f958469c04642a5336a5ce912fa375fdb90fb25d7"),
        squadv2=dict(repo="rajpurkar/squad_v2", revision="3ffb306f725f7d2ce8394bc1873b24868140c412",
                  file="squad_v2/validation-00000-of-00001.parquet", rows=11873, max_new_tokens=32,
                  sha256="0560174ab095c5ac0a8c8dc8da05f1625453c45a77e4ce9cabc6947ddfdd24cb"))
    for task, config in datasets.items():
        raw = hf_hub_download(config["repo"], config["file"], repo_type="dataset",
                              revision=config["revision"], cache_dir=cache)
        if sha256_file(raw) != config["sha256"]:
            raise ValueError("Dataset source checksum mismatch")
        rows = pq.read_table(raw).to_pylist()
        if len(rows) != config["rows"]:
            raise ValueError("Split size mismatch")
        path = Path("datasets") / (task+"-test.jsonl")
        path.parent.mkdir(exist_ok=True)
        with path.open("x") as output:
            for index, row in enumerate(rows):
                output.write(json.dumps(dict(test_row_index=index, **row),ensure_ascii=False)+"\n")
        write_json(Path("results")/(task+"-dataset.json"), dict(config, path=str(path.resolve()),
                   jsonl_sha256=sha256_file(path), max_input_tokens=512))
    for pair in inventory["primary"]:
        if pair["pair_id"] not in {"shadow_4b_mmlu", "shadow_4b_squadv2", "shadow_4b_gsm8k"}:
            continue
        artifacts = dict(base=base)
        for role in ("lora", "dora"):
            spec = pair[role]
            directory = snapshot_download(spec["repo_id"], revision=spec["revision"],
                cache_dir=cache, allow_patterns=[f["rfilename"] for f in spec["files"]], max_workers=2)
            for file in spec["files"]:
                path = Path(directory)/file["rfilename"]
                if path.stat().st_size != file["size"]:
                    raise ValueError("Adapter size mismatch")
                if file.get("lfs") and sha256_file(path) != file["lfs"]["sha256"]:
                    raise ValueError("Adapter hash mismatch")
            artifacts[role] = dict(repo_id=spec["repo_id"], revision=spec["revision"], snapshot_path=directory)
        write_json(Path("results")/(pair["pair_id"]+"-downloads.json"), dict(pair=pair["pair_id"],artifacts=artifacts))


if __name__ == "__main__":
    main()
