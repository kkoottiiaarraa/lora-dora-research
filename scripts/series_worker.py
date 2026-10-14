#!/usr/bin/env python3
"""One guarded worker; old pipeline/venv remain untouched."""
import argparse
import datetime
import hashlib
import importlib.metadata
import json
import os
import re
import resource
import sys
import time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lora_dora_study.adapters import verify_loaded_adapter
from lora_dora_study.benchmarks import user_content, score
from lora_dora_study.evaluation import sha256_file, source_fingerprint
from lora_dora_study.interventions import apply_intervention
from lora_dora_study.leases import gpu_lease
from lora_dora_study.server import available_memory_bytes, gpu_snapshot, idle_gpu, write_json


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--job", type=Path, required=True)
    p.add_argument("--gpu-uuid", required=True)
    p.add_argument("--role", choices=["base", "lora", "dora"], required=True)
    p.add_argument("--output-dir", type=Path, required=True)
    p.add_argument("--limit", type=int)
    args = p.parse_args()
    if not re.fullmatch(r"GPU-[a-zA-Z0-9-]+", args.gpu_uuid):
        p.error("GPU UUID required")
    job = json.loads(args.job.read_text())
    dataset = json.loads(Path(job["dataset_manifest"]).read_text())
    if sha256_file(dataset["path"]) != dataset["jsonl_sha256"]:
        raise ValueError("Dataset changed")
    rows = [json.loads(line) for line in Path(dataset["path"]).read_text().split("\n") if line]
    if len(rows) != dataset["rows"] or args.limit is not None and not 1<=args.limit<=len(rows):
        raise ValueError("Dataset/limit mismatch")
    count = args.limit or len(rows)
    downloads = json.loads(Path(job["downloads"]).read_text())
    args.output_dir.mkdir(parents=True, exist_ok=False)
    summary = args.output_dir / "summary.json"
    report = dict(status="starting", job=job, role=args.role, gpu_uuid=args.gpu_uuid,
        dataset=dataset, artifacts=downloads["artifacts"], expected_rows=count,
        full_evaluation=count==len(rows), predictions_completed=0,
        source_sha256=source_fingerprint(Path(__file__).resolve().parents[1]),
        timestamp_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
    write_json(summary, report)
    loaded = False
    try:
        with gpu_lease(args.gpu_uuid):
            snapshot = gpu_snapshot()
            selected = next(g for g in snapshot["gpus"] if g["uuid"] == args.gpu_uuid)
            ram = available_memory_bytes()
            if not idle_gpu(selected, snapshot["compute_processes"]) or ram is None or ram<12*1024**3:
                raise BlockingIOError("GPU/RAM guard refused before model load")
            os.environ.update(CUDA_VISIBLE_DEVICES=args.gpu_uuid, OMP_NUM_THREADS="2",
                TOKENIZERS_PARALLELISM="false", HF_HUB_OFFLINE="1", TRANSFORMERS_OFFLINE="1")
            import torch
            from transformers import AutoModelForCausalLM, AutoTokenizer, GenerationConfig
            from peft import PeftModel
            torch.set_num_threads(2)
            torch.set_num_interop_threads(1)
            torch.manual_seed(42)
            if not torch.cuda.is_bf16_supported():
                raise RuntimeError("BF16 required")
            paths = {r:a["snapshot_path"] for r,a in downloads["artifacts"].items()}
            report["versions"]={name:importlib.metadata.version(name) for name in
                ["torch","transformers","peft","safetensors","accelerate"]}
            torch.cuda.reset_peak_memory_stats()

            def timed(operation):
                torch.cuda.synchronize()
                started=time.perf_counter()
                value=operation()
                torch.cuda.synchronize()
                return value,time.perf_counter()-started

            def memory():
                return dict(peak_allocated_bytes=torch.cuda.max_memory_allocated(),
                    peak_reserved_bytes=torch.cuda.max_memory_reserved(),
                    max_process_rss_bytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024,
                    available_host_ram_bytes=available_memory_bytes())

            loaded=True
            tokenizer,report["tokenizer_load_seconds"]=timed(lambda:AutoTokenizer.from_pretrained(
                paths["base"],local_files_only=True,trust_remote_code=False))
            model,report["base_load_seconds"]=timed(lambda:AutoModelForCausalLM.from_pretrained(
                paths["base"],local_files_only=True,trust_remote_code=False,torch_dtype=torch.bfloat16,
                device_map={"":"cuda:0"},low_cpu_mem_usage=True,attn_implementation="sdpa"))
            if args.role!="base":
                model,report["adapter_load_seconds"]=timed(lambda:PeftModel.from_pretrained(
                    model,paths[args.role],local_files_only=True,is_trainable=False))
                report["adapter_validation"]=verify_loaded_adapter(model,paths[args.role],args.role=="dora")
            model.eval()
            advanced=job.get("intervention") in {"dense_reference","rank_fixed","rank_energy","rank_lora_control","vo_symmetry"}
            if advanced:
                from lora_dora_study.rank_symmetry import prepare
                calibration=Path(job["calibration"])
                if sha256_file(calibration)!=job["calibration_sha256"]:
                    raise ValueError("Calibration changed")
                row=json.loads(calibration.read_text().splitlines()[0])
                prompt=tokenizer.apply_chat_template([dict(role="user",content=user_content("gsm8k",row))],
                    tokenize=False,add_generation_prompt=True,enable_thinking=False)
                ids=tokenizer(prompt,add_special_tokens=False)["input_ids"][:128]
                inputs=dict(input_ids=torch.tensor([ids],device="cuda:0"),
                    attention_mask=torch.ones((1,len(ids)),device="cuda:0",dtype=torch.long))
                with torch.inference_mode():
                    report["intervention"],report["intervention_seconds"]=timed(lambda:prepare(model,job,inputs))
                write_json(args.output_dir/"intervention.json",report["intervention"])
            else:
                report["intervention"]=apply_intervention(model,job.get("intervention","none"),
                    set(job.get("targets",["q_proj","k_proj","v_proj","o_proj"])))
            generation=GenerationConfig(do_sample=False,num_beams=1,max_new_tokens=dataset["max_new_tokens"],
                use_cache=False,pad_token_id=tokenizer.pad_token_id if tokenizer.pad_token_id is not None else tokenizer.eos_token_id,
                eos_token_id=tokenizer.eos_token_id,bos_token_id=tokenizer.bos_token_id)
            report.update(status="running",generation_config=generation.to_dict(),load_memory=memory())
            write_json(summary,report)
            totals={}
            started=time.perf_counter()
            truncated=limited=0
            with (args.output_dir/"predictions.jsonl").open("x") as output,torch.inference_mode():
                for index,row in enumerate(rows[:count]):
                    prompt=tokenizer.apply_chat_template([dict(role="user",content=user_content(job["task"],row))],
                        tokenize=False,add_generation_prompt=True,enable_thinking=False)
                    original=tokenizer(prompt,add_special_tokens=False)["input_ids"]
                    ids=original[:dataset["max_input_tokens"]]
                    inputs=dict(input_ids=torch.tensor([ids],device="cuda:0"),
                        attention_mask=torch.ones((1,len(ids)),device="cuda:0",dtype=torch.long))
                    def generate():
                        with torch.autocast(device_type="cuda",dtype=torch.bfloat16):
                            return model.generate(**inputs,generation_config=generation,use_model_defaults=False,do_sample=False)
                    generated,elapsed=timed(generate)
                    tokens=generated[0,len(ids):]
                    text=tokenizer.decode(tokens,skip_special_tokens=True)
                    metrics=score(job["task"],text,row)
                    for name,value in metrics.items(): totals[name]=totals.get(name,0)+value
                    prediction=dict(test_row_index=index,source_id=row.get("id",index),subject=row.get("subject"),
                        input_ids_sha256=hashlib.sha256(json.dumps(ids).encode()).hexdigest(),
                        prompt_sha256=hashlib.sha256(prompt.encode()).hexdigest(),
                        text=text,metrics=metrics,seconds=elapsed,input_tokens=len(ids),generated_tokens=len(tokens),
                        prompt_truncated=len(original)>len(ids),hit_token_limit=len(tokens)==dataset["max_new_tokens"])
                    output.write(json.dumps(prediction,ensure_ascii=False)+"\n");output.flush()
                    truncated+=prediction["prompt_truncated"];limited+=prediction["hit_token_limit"]
                    report.update(predictions_completed=index+1,metrics={k:v/(index+1) for k,v in totals.items()},
                        inference_seconds=time.perf_counter()-started,memory=memory(),
                        truncated_prompts=truncated,hit_token_limit=limited)
                    write_json(summary,report)
            report.update(status="complete",predictions_sha256=sha256_file(args.output_dir/"predictions.jsonl"))
            write_json(summary,report)
    except Exception as error:
        transient=not loaded and (isinstance(error,BlockingIOError) or
                                  "Three research GPU workers" in str(error))
        report.update(status="guard_refused" if transient else "failed_needs_inspection",error=str(error))
        write_json(summary,report)
        if transient: return 75
        raise
    return 0


if __name__=="__main__":
    sys.exit(main())
