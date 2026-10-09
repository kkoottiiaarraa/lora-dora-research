#!/usr/bin/env python3
"""One GPU, one model, short inference only. Torch imports after GPU isolation."""
import argparse
import importlib.metadata
import json
import os
import re
import resource
import sys
import time
import traceback
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lora_dora_study.server import gpu_snapshot, idle_gpu, write_json
from lora_dora_study.leases import gpu_lease


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--role", choices=["base", "lora", "dora"], required=True)
    parser.add_argument("--gpu-uuid", required=True)
    parser.add_argument("--downloads", default="results/download.json")
    parser.add_argument("--fixture", default="fixtures/gsm8k_pilot_8.jsonl")
    parser.add_argument("--output", required=True)
    parser.add_argument("--cases", type=int, default=2)
    parser.add_argument("--merge-check", action="store_true")
    args = parser.parse_args()
    if not re.fullmatch(r"GPU-[a-zA-Z0-9-]+", args.gpu_uuid):
        parser.error("An nvidia-smi GPU UUID is required")
    if not 1 <= args.cases <= 8:
        parser.error("Pilot supports one to eight fixture examples")
    report = dict(role=args.role, gpu_uuid=args.gpu_uuid, status="starting",
                  purpose="timing smoke check, not accuracy evaluation")
    write_json(args.output, report)
    with gpu_lease(args.gpu_uuid):
        snapshot = gpu_snapshot()
        gpu = next(g for g in snapshot["gpus"] if g["uuid"] == args.gpu_uuid)
        if not idle_gpu(gpu, snapshot["compute_processes"]):
            raise RuntimeError("GPU is occupied; pilot will not start")
        # Isolation precedes Torch and Transformers imports.
        os.environ["CUDA_VISIBLE_DEVICES"] = args.gpu_uuid
        os.environ["OMP_NUM_THREADS"] = "2"
        os.environ["TOKENIZERS_PARALLELISM"] = "false"
        os.environ["HF_HUB_OFFLINE"] = "1"
        os.environ["TRANSFORMERS_OFFLINE"] = "1"
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer
        from peft import PeftModel
        torch.set_num_threads(2)
        torch.set_num_interop_threads(1)
        torch.manual_seed(42)
        if not torch.cuda.is_available() or not torch.cuda.is_bf16_supported():
            raise RuntimeError("Pilot requires a BF16-capable CUDA device")
        downloads = json.loads(Path(args.downloads).read_text())
        paths = {role: value["snapshot_path"] for role, value in downloads["artifacts"].items()}
        report.update(gpu=gpu, artifacts=downloads["artifacts"],
            versions={name: importlib.metadata.version(name)
                      for name in ["torch", "transformers", "peft", "safetensors", "accelerate"]},
            torch_cuda=torch.version.cuda, input_token_limit=256, new_token_limit=64,
            dtype="bfloat16", attention="sdpa", batch_size=1, generation_cases=[])
        torch.cuda.reset_peak_memory_stats()

        def timed(operation):
            torch.cuda.synchronize()
            started = time.perf_counter()
            value = operation()
            torch.cuda.synchronize()
            return value, time.perf_counter() - started

        def memory():
            return dict(allocated_bytes=torch.cuda.memory_allocated(),
                reserved_bytes=torch.cuda.memory_reserved(),
                peak_allocated_bytes=torch.cuda.max_memory_allocated(),
                peak_reserved_bytes=torch.cuda.max_memory_reserved(),
                max_process_rss_bytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024)

        tokenizer, report["tokenizer_load_seconds"] = timed(lambda: AutoTokenizer.from_pretrained(
            paths["base"], local_files_only=True, trust_remote_code=False))
        model, report["base_load_seconds"] = timed(lambda: AutoModelForCausalLM.from_pretrained(
            paths["base"], local_files_only=True, trust_remote_code=False,
            torch_dtype=torch.bfloat16, device_map={"": "cuda:0"},
            low_cpu_mem_usage=True, attn_implementation="sdpa"))
        report["base_loaded_memory"] = memory()
        if args.role != "base":
            config = json.loads((Path(paths[args.role]) / "adapter_config.json").read_text())
            if (config.get("use_dora", False) != (args.role == "dora")
                    or config.get("r") != 32 or config.get("lora_alpha") != 32):
                raise RuntimeError("Adapter configuration does not match the pinned pilot")
            report["adapter_config"] = config
            model, report["adapter_load_seconds"] = timed(lambda: PeftModel.from_pretrained(
                model, paths[args.role], is_trainable=False, local_files_only=True))
        model.eval()
        report["model_loaded_memory"] = memory()
        examples = [json.loads(line) for line in Path(args.fixture).read_text().splitlines()]

        def encode(example):
            prompt = tokenizer.apply_chat_template([dict(role="user",
                content="Question: " + example["question"] + "\nAnswer:")],
                tokenize=False, add_generation_prompt=True, enable_thinking=False)
            original_tokens = len(tokenizer(prompt, add_special_tokens=False)["input_ids"])
            encoded = tokenizer(prompt, add_special_tokens=False, return_tensors="pt",
                                truncation=True, max_length=256).to("cuda:0")
            return encoded, original_tokens

        with torch.inference_mode():
            first, _ = encode(examples[0])
            # Use only final-position logits to avoid a large vocabulary x context tensor.
            reference, report["first_forward_seconds"] = timed(
                lambda: model(**first, use_cache=False, logits_to_keep=1).logits[:, -1].float())
            _, report["warm_forward_seconds"] = timed(
                lambda: model(**first, use_cache=False, logits_to_keep=1).logits[:, -1].float())
            for example in examples[:args.cases]:
                inputs, original_tokens = encode(example)
                generated, elapsed = timed(lambda: model.generate(**inputs, do_sample=False,
                    max_new_tokens=64, pad_token_id=tokenizer.pad_token_id or tokenizer.eos_token_id))
                new_tokens = generated[0, inputs["input_ids"].shape[1]:]
                report["generation_cases"].append(dict(test_row_index=example["test_row_index"],
                    original_prompt_tokens=original_tokens,
                    input_tokens=int(inputs["input_ids"].shape[1]),
                    prompt_truncated=original_tokens > 256,
                    generated_tokens=int(new_tokens.numel()), seconds=elapsed,
                    hit_token_limit=new_tokens.numel() == 64,
                    text=tokenizer.decode(new_tokens, skip_special_tokens=True)))
                report["inference_memory"] = memory()
                write_json(args.output, report)
            if args.merge_check and args.role != "base":
                # Recompute immediately before merging, using the same input.
                reference = model(**first, use_cache=False, logits_to_keep=1).logits[:, -1].float()
                model, report["merge_seconds"] = timed(lambda: model.merge_and_unload(safe_merge=True))
                merged = model(**first, use_cache=False, logits_to_keep=1).logits[:, -1].float()
                difference = (merged - reference).abs()
                logp, logq = reference.log_softmax(-1), merged.log_softmax(-1)
                report["merge_fidelity"] = dict(max_absolute_logit_error=difference.max().item(),
                    mean_absolute_logit_error=difference.mean().item(),
                    kl_reference_to_merged=(logp.exp() * (logp - logq)).sum().item(),
                    top1_equal=bool(torch.equal(reference.argmax(-1), merged.argmax(-1))),
                    bitwise_equal=bool(torch.equal(reference, merged)),
                    scope="One example, final token; roundoff measured, not guaranteed universal")
                report["merge_memory"] = memory()
        report.update(status="complete", final_memory=memory())
        write_json(args.output, report)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        traceback.print_exc()
        sys.exit(1)
