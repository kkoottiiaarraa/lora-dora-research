#!/usr/bin/env python3
"""Reject unmatched/partial runs; paired CI for both preregistered scorers."""
import argparse
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lora_dora_study.evaluation import paired_bootstrap, read_predictions, sha256_file
from lora_dora_study.server import write_json


def compare(directories):
    reports, predictions = {}, {}
    for role, directory in directories.items():
        report = json.loads((directory / "summary.json").read_text())
        if report["role"] != role or report["status"] != "complete" or not report["full_evaluation"]:
            raise ValueError("Complete full evaluation required: " + role)
        path = directory / "predictions.jsonl"
        if sha256_file(path) != report["predictions_sha256"]:
            raise ValueError("Prediction checksum mismatch")
        rows = read_predictions(path)
        if [r["test_row_index"] for r in rows] != list(range(report["protocol"]["expected_rows"])):
            raise ValueError("Missing or reordered test examples")
        reports[role], predictions[role] = report, rows
    reference = reports["base"]
    for role, report in reports.items():
        if any(report[key] != reference[key] for key in
               ["protocol_sha256", "generation_config", "versions", "artifacts", "code_revision", "source_sha256"]):
            raise ValueError("Unmatched generation/config/versions/checkpoints/code: " + role)
        for left, right in zip(predictions["base"], predictions[role]):
            if any(left[key] != right[key] for key in
                   ["question", "gold", "prompt_sha256", "input_ids_sha256", "input_tokens"]):
                raise ValueError("Unmatched input/gold: " + role)
    result = dict(protocol=reference["protocol"], accuracy={}, contrasts={},
                  limitations=["Test-example CI does not measure training-seed uncertainty",
                               "Current base revision at training is unknown",
                               "Three prespecified contrasts; CIs are unadjusted and not familywise claims",
                               "Author metric and secondary sensitivity metric both reported"])
    for scorer in ("author", "final"):
        values = {role: [r[scorer+"_correct"] for r in rows]
                  for role, rows in predictions.items()}
        result["accuracy"][scorer] = {role: sum(v)/len(v) for role, v in values.items()}
        result["contrasts"][scorer] = {right+"_minus_"+left: paired_bootstrap(values[left], values[right])
            for left, right in [("base", "lora"), ("base", "dora"), ("lora", "dora")]}
    result["censoring"] = {role: dict(truncated_prompts=report["truncated_prompts"],
        hit_token_limit=report["hit_token_limit"]) for role, report in reports.items()}
    return result


def main():
    p = argparse.ArgumentParser()
    for role in ("base", "lora", "dora"):
        p.add_argument("--"+role, type=Path, required=True)
    p.add_argument("--output", required=True)
    args = p.parse_args()
    result = compare({role:getattr(args, role) for role in ("base", "lora", "dora")})
    write_json(args.output, result)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
