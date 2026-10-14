#!/usr/bin/env python3
"""Identical full GSM8K evaluation per role, guarded by a completed technical pilot."""
import argparse
import datetime
import importlib.metadata
import json
import os
import re
import resource
import subprocess
import sys
import time
import traceback
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lora_dora_study.adapters import verify_loaded_adapter
from lora_dora_study.evaluation import (author_answer, final_answer, gold_answer,
                                       prompt_text, sha256_file, source_fingerprint)
from lora_dora_study.leases import gpu_lease
from lora_dora_study.server import available_memory_bytes, gpu_snapshot, idle_gpu, write_json


def validate_pilot(path, downloads):
    summary = json.loads((path / "summary.json").read_text())
    outcomes = [item for queue in summary["outcomes"] for item in queue]
    if len(outcomes) != 3 or any(r.get("exit_code") != 0 for r in outcomes):
        raise ValueError("Pilot incomplete")
    for role in ("base", "lora", "dora"):
        report = json.loads((path / (role + ".json")).read_text())
        if report["status"] != "complete" or not report["generation_cases"]:
            raise ValueError("Pilot role incomplete: " + role)
        for artifact in downloads["artifacts"]:
            if report["artifacts"][artifact]["revision"] != downloads["artifacts"][artifact]["revision"]:
                raise ValueError("Pilot used different checkpoints")
        if role != "base":
            if report.get("adapter_validation", {}).get("status") != "verified":
                raise ValueError("Pilot did not validate loaded adapters")
            if "merge_fidelity" not in report:
                raise ValueError("Missing pilot merge measurement")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--role", required=True, choices=["base", "lora", "dora"])
    p.add_argument("--gpu-uuid", required=True)
    p.add_argument("--pilot-dir", type=Path, required=True)
    p.add_argument("--downloads", default="results/reverify-20261009.json")
    p.add_argument("--config", default="configs/gsm8k_evaluation.json")
    p.add_argument("--dataset-dir", type=Path, default=Path("datasets/gsm8k-matched-v1"))
    p.add_argument("--output-dir", type=Path, required=True)
    p.add_argument("--limit", type=int, help="Runtime validation only; omitted means all 1319")
    args = p.parse_args()
    if not re.fullmatch(r"GPU-[a-zA-Z0-9-]+", args.gpu_uuid):
        p.error("GPU UUID required")
    downloads = json.loads(Path(args.downloads).read_text())
    validate_pilot(args.pilot_dir, downloads)
    config = json.loads(Path(args.config).read_text())
    dataset_manifest = json.loads((args.dataset_dir / "manifest.json").read_text())
    dataset_path = args.dataset_dir / "test.jsonl"
    if (sha256_file(dataset_path) != dataset_manifest["sha256"] or
            dataset_manifest["sha256"] != config["dataset_sha256"]):
        raise ValueError("Dataset hash mismatch")
    rows = [json.loads(line) for line in dataset_path.read_text().splitlines()]
    if len(rows) != config["expected_rows"]:
        raise ValueError("Wrong test split size")
    if args.limit is not None and not 1 <= args.limit <= len(rows):
        p.error("Invalid --limit")
    count = args.limit or len(rows)
    report = dict(role=args.role, status="starting", protocol=config,
                  protocol_sha256=sha256_file(args.config), dataset=dataset_manifest,
                  artifacts=downloads["artifacts"], expected_rows=count,
                  full_evaluation=count == len(rows), gpu_uuid=args.gpu_uuid,
                  timestamp_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                  code_revision=subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
                  code_dirty=bool(subprocess.check_output(["git", "status", "--porcelain"], text=True)),
                  source_sha256=source_fingerprint(Path(__file__).resolve().parents[1]),
                  predictions_completed=0)
    args.output_dir.mkdir(parents=True, exist_ok=False)
    report_path = args.output_dir / "summary.json"
    write_json(report_path, report)
    try:
        with gpu_lease(args.gpu_uuid):
            snapshot = gpu_snapshot()
            gpu = next(g for g in snapshot["gpus"] if g["uuid"] == args.gpu_uuid)
            ram = available_memory_bytes()
            if not idle_gpu(gpu, snapshot["compute_processes"]) or ram is None or ram < 12*1024**3:
                raise RuntimeError("GPU occupied or host RAM insufficient/unknown")
            os.environ.update(CUDA_VISIBLE_DEVICES=args.gpu_uuid, OMP_NUM_THREADS="2",
                              TOKENIZERS_PARALLELISM="false", HF_HUB_OFFLINE="1",
                              TRANSFORMERS_OFFLINE="1")
            import torch
            from transformers import AutoModelForCausalLM, AutoTokenizer, GenerationConfig
            from peft import PeftModel
            torch.set_num_threads(2)
            torch.set_num_interop_threads(1)
            torch.manual_seed(config["seed"])
            if not torch.cuda.is_bf16_supported():
                raise RuntimeError("BF16 CUDA device required")
            paths = {r: a["snapshot_path"] for r, a in downloads["artifacts"].items()}
            report["versions"] = {name: importlib.metadata.version(name) for name in
                                  ["torch", "transformers", "peft", "safetensors", "accelerate"]}
            report["torch_cuda"] = torch.version.cuda
            report["preflight"] = snapshot
            torch.cuda.reset_peak_memory_stats()

            def timed(operation):
                torch.cuda.synchronize()
                started = time.perf_counter()
                value = operation()
                torch.cuda.synchronize()
                return value, time.perf_counter()-started

            def memory():
                return dict(peak_allocated_bytes=torch.cuda.max_memory_allocated(),
                            peak_reserved_bytes=torch.cuda.max_memory_reserved(),
                            max_process_rss_bytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024,
                            available_host_ram_bytes=available_memory_bytes())

            tokenizer, report["tokenizer_load_seconds"] = timed(lambda: AutoTokenizer.from_pretrained(
                paths["base"], local_files_only=True, trust_remote_code=False))
            model, report["base_load_seconds"] = timed(lambda: AutoModelForCausalLM.from_pretrained(
                paths["base"], local_files_only=True, trust_remote_code=False,
                torch_dtype=torch.bfloat16, device_map={"": "cuda:0"},
                low_cpu_mem_usage=True, attn_implementation="sdpa"))
            if args.role != "base":
                model, report["adapter_load_seconds"] = timed(lambda: PeftModel.from_pretrained(
                    model, paths[args.role], local_files_only=True, is_trainable=False))
                report["adapter_validation"] = verify_loaded_adapter(model, paths[args.role], args.role=="dora")
            model.eval()
            def generate(inputs):
                # Match the author's BF16 autocast, including FP32 PEFT adapters.
                with torch.autocast(device_type="cuda", dtype=torch.bfloat16):
                    return model.generate(**inputs, generation_config=generation)

            # Explicit fresh generation config prevents checkpoint defaults changing behavior.
            generation = GenerationConfig(do_sample=False, num_beams=1,
                max_new_tokens=config["max_new_tokens"], use_cache=config["use_cache"],
                pad_token_id=tokenizer.pad_token_id if tokenizer.pad_token_id is not None else tokenizer.eos_token_id,
                eos_token_id=tokenizer.eos_token_id, bos_token_id=tokenizer.bos_token_id)
            report.update(status="running", generation_config=generation.to_dict(), load_memory=memory())
            write_json(report_path, report)
            correct_author = correct_final = truncated = limited = 0
            evaluation_started = time.perf_counter()
            with (args.output_dir / "predictions.jsonl").open("x") as output, torch.inference_mode():
                for index, row in enumerate(rows[:count]):
                    prompt = prompt_text(tokenizer, row["question"])
                    ids = tokenizer(prompt, add_special_tokens=False)["input_ids"]
                    selected = ids[:config["max_input_tokens"]]
                    inputs = dict(input_ids=torch.tensor([selected], device="cuda:0"),
                                  attention_mask=torch.ones((1, len(selected)), device="cuda:0", dtype=torch.long))
                    generated, elapsed = timed(lambda: generate(inputs))
                    new_tokens = generated[0, len(selected):]
                    text = tokenizer.decode(new_tokens, skip_special_tokens=True)
                    gold = gold_answer(row["answer"])
                    author, final = author_answer(text), final_answer(text)
                    at_limit = len(new_tokens) == config["max_new_tokens"]
                    prediction = dict(test_row_index=index, question=row["question"], gold=gold,
                        text=text, author_answer=author, final_answer=final,
                        author_correct=bool(gold and author==gold), final_correct=bool(gold and final==gold),
                        prompt_sha256=__import__("hashlib").sha256(prompt.encode()).hexdigest(),
                        input_ids_sha256=__import__("hashlib").sha256(json.dumps(selected).encode()).hexdigest(),
                        original_prompt_tokens=len(ids), input_tokens=len(selected),
                        prompt_truncated=len(ids)>len(selected), generated_tokens=len(new_tokens),
                        hit_token_limit=at_limit, seconds=elapsed)
                    output.write(json.dumps(prediction, ensure_ascii=False)+"\n")
                    output.flush()
                    correct_author += prediction["author_correct"]
                    correct_final += prediction["final_correct"]
                    truncated += prediction["prompt_truncated"]
                    limited += at_limit
                    report.update(predictions_completed=index+1,
                        author_accuracy=correct_author/(index+1), final_accuracy=correct_final/(index+1),
                        truncated_prompts=truncated, hit_token_limit=limited,
                        inference_seconds=time.perf_counter()-evaluation_started, memory=memory())
                    write_json(report_path, report)
            report["status"] = "complete"
            report["predictions_sha256"] = sha256_file(args.output_dir / "predictions.jsonl")
            write_json(report_path, report)
    except Exception as error:
        report.update(status="failed", error=str(error))
        write_json(report_path, report)
        raise


if __name__ == "__main__":
    main()
