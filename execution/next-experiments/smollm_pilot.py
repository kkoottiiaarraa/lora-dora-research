#!/usr/bin/env python3
"""Eight author-validation cases: pinned CPU loader and intervention acceptance."""
import argparse
import datetime
import gc
import importlib.metadata
import json
import os
from pathlib import Path
import resource
import signal
import sys
import time
os.environ.update(CUDA_VISIBLE_DEVICES='',OMP_NUM_THREADS='8',MKL_NUM_THREADS='8',OPENBLAS_NUM_THREADS='8',
    HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',TOKENIZERS_PARALLELISM='false')
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from lora_dora_study.server import write_json,available_memory_bytes
from lora_dora_study.evaluation import sha256_file
from lora_dora_study.intent_routing import chat_messages,gold_id,extract_id,case_digest


def main(root):
    start=time.monotonic();summary=dict(status='running',phase='setup',gpu_hours=0,cpu_threads=8,
        started_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),conditions=[],training=False)
    def save():
        summary.update(wall_seconds=time.monotonic()-start,peak_rss_bytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024)
        write_json(root/'summary.json',summary)
    def timeout(signum,frame):raise TimeoutError('CPU pilot protective deadline30min')
    signal.signal(signal.SIGALRM,timeout);signal.setitimer(signal.ITIMER_REAL,1800);save()
    try:
        manifest=json.loads((root/'manifest-private.json').read_text())
        for rel,h in manifest['source_sha256'].items():
            if sha256_file(ROOT/rel)!=h:raise ValueError('Frozen code changed: '+rel)
        readiness=Path(manifest['readiness_root']);ready=json.loads((readiness/'summary.json').read_text())
        if ready['status']!='complete' or sha256_file(readiness/'artifact-provenance.json')!=manifest['provenance_sha256']:
            raise ValueError('Pinned download not accepted')
        if sha256_file(root/'protocol-private.json')!=manifest['protocol_sha256']:raise ValueError('Protocol changed')
        protocol=json.loads((root/'protocol-private.json').read_text());raw=protocol['cases']
        if len(raw)!=8 or len({case_digest(c) for c in raw})!=8 or protocol['split']!='author_validation':
            raise ValueError('Smoke case coverage')
        if available_memory_bytes()<12*1024**3:raise BlockingIOError('Need12GiBfreehostRAM')
        import torch
        from transformers import AutoModelForCausalLM,AutoTokenizer
        from peft import PeftModel
        from lora_dora_study.adapters import verify_loaded_adapter
        from lora_dora_study.fidelity_audit import without_d,magnitude_gauge,metrics,convert_custom
        torch.set_num_threads(8);torch.set_num_interop_threads(1);torch.manual_seed(20261014)
        versions={k:importlib.metadata.version(k) for k in ['torch','transformers','peft','safetensors','accelerate','huggingface_hub']}
        paths={k:Path(v['snapshot_path']) for k,v in ready['artifacts'].items()}
        tokenizers={};compatibility={}
        for role,path in paths.items():
            config=json.loads((path/'tokenizer_config.json').read_text());extra=config.get('extra_special_tokens');kwargs={}
            if isinstance(extra,list):
                # New saved schema lists BOS/EOS again; older Transformers expects named mapping.
                # Do not erase arbitrary additional tokens or edit the pinned files.
                if set(extra)!={config['bos_token'],config['eos_token']}:
                    raise ValueError('Unrecognized tokenizer special-token schema')
                kwargs['extra_special_tokens']={}
                compatibility[role]='duplicate BOS/EOS list supplied through existing named token fields'
            tokenizers[role]=AutoTokenizer.from_pretrained(str(path),local_files_only=True,trust_remote_code=False,**kwargs)
        summary['tokenizer_compatibility']=compatibility
        tok=tokenizers['dora']
        for role in ['lora','base']:
            other=tokenizers[role]
            if other.get_vocab()!=tok.get_vocab() or other.chat_template!=tok.chat_template or other.all_special_ids!=tok.all_special_ids:
                raise ValueError('Tokenizer vocabulary/template/specialIDs mismatch: '+role)
        cases=[]
        for i,example in enumerate(raw):
            label=gold_id(example);messages=chat_messages(example,protocol['system_prompt'])
            prompt=tok.apply_chat_template(messages,tokenize=False,add_generation_prompt=True)
            ids=tok(prompt,return_tensors=None)['input_ids']
            full=tok.apply_chat_template(chat_messages(example,protocol['system_prompt'],with_answer=True),tokenize=False,add_generation_prompt=False)
            full_ids=tok(full,return_tensors=None)['input_ids'];label_ids=tok(label,add_special_tokens=False)['input_ids']
            if full_ids[:len(ids)]!=ids or len(label_ids)!=1 or full_ids[len(ids)]!=label_ids[0] or tok.decode(label_ids)!=label:
                raise ValueError('Gold boundary is not a single verified token')
            if len(ids)>tok.model_max_length:raise ValueError('Context overflow')
            cases.append(dict(case=i,case_sha256=case_digest(example),input_ids=ids,gold_id=label,target=label_ids[0],tools=len(example['available_tools'])))
        write_json(root/'cases-private.json',cases)
        write_json(root/'tokenization-audit.json',dict(status='PASS',case_count=8,tokenizers_match=True,
            source_data_sha256=protocol['source_data_sha256'],source_system_sha256=protocol['source_system_sha256'],
            case_rows=[{k:v for k,v in c.items() if k!='input_ids'}|dict(prompt_tokens=len(c['input_ids'])) for c in cases]))
        summary.update(phase='load',versions=versions,source_sha256=manifest['source_sha256'],
            provenance_sha256=manifest['provenance_sha256'],protocol_sha256=manifest['protocol_sha256'],
            cases_sha256=sha256_file(root/'cases-private.json'),case_count=8,dtype='torch.float32',attention='sdpa',
            tokenizer_match=True,task_accuracy_estimated=False)
        write_json(root/'frozen.json',dict(source_sha256=manifest['source_sha256'],protocol_sha256=manifest['protocol_sha256'],
            provenance_sha256=manifest['provenance_sha256'],cases_sha256=summary['cases_sha256'],before_outputs=True));save()
        cache=root/'logit-cache';cache.mkdir()
        def load(role):
            before=time.monotonic()
            model=AutoModelForCausalLM.from_pretrained(str(paths['base']),local_files_only=True,trust_remote_code=False,
                torch_dtype=torch.float32,device_map=None,low_cpu_mem_usage=True,attn_implementation='sdpa').eval()
            c=model.config
            expected={'hidden_size':960,'num_hidden_layers':32,'num_attention_heads':15,'num_key_value_heads':5,'vocab_size':49152,'attention_bias':False}
            if c.model_type!='llama' or any(getattr(c,k)!=v for k,v in expected.items()):raise ValueError('Base architecture changed')
            load_seconds=time.monotonic()-before;attach_start=time.monotonic();check=None
            if role!='base':
                model=PeftModel.from_pretrained(model,str(paths[role]),local_files_only=True,is_trainable=False,
                    torch_device='cpu',device_map={'':'cpu'}).eval()
                check=verify_loaded_adapter(model,paths[role],role=='dora')
                if check['adapted_module_count']!=128 or check['saved_tensor_count']!=(384 if role=='dora' else 256):
                    raise ValueError('Adapter coverage changed')
                if any(m['r']!=16 or m['alpha']!=32 or m['scaling']!=2 for m in check['modules']):raise ValueError('Scaling changed')
                write_json(root/(role+'-adapter-audit.json'),check)
            attach_seconds=time.monotonic()-attach_start;model.requires_grad_(False)
            for name,p in model.named_parameters():
                if p.device.type!='cpu' or p.dtype!=torch.float32 or p.is_meta or not bool(p.isfinite().all()):
                    raise ValueError('Invalid parameter: '+name)
            summary.setdefault('loads',[]).append(dict(role=role,base_load_seconds=load_seconds,
                adapter_attach_and_verify_seconds=attach_seconds,parameter_count=sum(p.numel() for p in model.parameters())))
            save();return model
        def logits(model,case):
            ids=torch.tensor([case['input_ids']],dtype=torch.long)
            with torch.inference_mode():y=model(input_ids=ids,attention_mask=torch.ones_like(ids),use_cache=False,logits_to_keep=1).logits[0].float().cpu()
            if y.shape!=(1,49152) or not bool(y.isfinite().all()):raise FloatingPointError('Invalid last logits')
            return y
        def run(model,condition,reference=None,count=8,generation=False):
            entry=dict(condition=condition,status='running',cases_completed=0);summary['conditions'].append(entry);summary['phase']=condition;save();rows=[]
            for case in cases[:count]:
                i=case['case'];begin=time.monotonic();y=logits(model,case);forward_seconds=time.monotonic()-begin
                ref=y if reference is None else torch.load(cache/f'{reference}-{i}.pt',map_location='cpu',weights_only=True)
                row=dict(condition=condition,case=i,case_sha256=case['case_sha256'],gold_id=case['gold_id'],target=case['target'],
                    prompt_tokens=len(case['input_ids']),forward_seconds=forward_seconds,**metrics(ref,y,[case['target']]))
                torch.save(y,cache/f'{condition}-{i}.pt')
                if generation:
                    ids=torch.tensor([case['input_ids']],dtype=torch.long);begin=time.monotonic()
                    with torch.inference_mode():out=model.generate(input_ids=ids,attention_mask=torch.ones_like(ids),max_new_tokens=8,do_sample=False,
                        temperature=None,top_p=None,pad_token_id=tok.eos_token_id,eos_token_id=tok.eos_token_id,use_cache=True,
                        return_dict_in_generate=True,output_scores=True)
                    elapsed=time.monotonic()-begin
                    if any(not bool(score.isfinite().all()) for score in out.scores):raise FloatingPointError('Invalid generation scores')
                    new=out.sequences[0,len(case['input_ids']):].tolist();text=tok.decode(new,skip_special_tokens=True);prediction=extract_id(text)
                    if not new or new[0]!=int(y.argmax(-1)[0]):raise ValueError('Greedy first token differs from full-forward argmax')
                    row.update(generation_seconds=elapsed,generated_tokens=new,raw_output=text,prediction=prediction,correct=prediction==case['gold_id'])
                with (root/'per-case.jsonl').open('a') as stream:stream.write(json.dumps(row,ensure_ascii=False)+'\n')
                rows.append(row);entry['cases_completed']=i+1;save()
            entry.update(status='complete',mean_rms=sum(r['rms'] for r in rows)/count,mean_nll=sum(r['changed_nll'] for r in rows)/count,
                forward_seconds=sum(r['forward_seconds'] for r in rows),generation_seconds=sum(r.get('generation_seconds',0) for r in rows),
                correct_smoke=sum(r.get('correct',False) for r in rows) if generation else None);save();return rows
        for role in ['base','lora','dora']:
            model=load(role);run(model,role,generation=True)
            if role=='dora':
                repeat=run(model,'repeat_dora','dora',2)
                if any(r['max_abs']!=0 for r in repeat):raise ValueError('Native repeat changed')
                with without_d(model):removed=run(model,'remove_d','dora',generation=True)
                effect=sum(r['rms'] for r in removed)/8
                for c in [.995,1.005]:
                    with magnitude_gauge(model,c):controls=run(model,'gauge_'+str(c),'dora',2)
                    if sum(r['rms'] for r in controls)/2>=.01*effect:raise ValueError('Gauge fidelity too large')
                for case in cases[:2]:
                    if not torch.equal(logits(model,case),torch.load(cache/f"dora-{case['case']}.pt",weights_only=True)):
                        raise ValueError('Source restoration changed')
                convert_custom(model);dense=run(model,'dense_control','dora',2)
                if sum(r['rms'] for r in dense)/2>=.01*effect:raise ValueError('Dense fidelity too large')
                summary.update(native_repeat_bitwise=True,restoration_bitwise=True,gauge_fidelity_pass=True,dense_fidelity_pass=True)
            del model;gc.collect()
        summary.update(status='complete',phase='complete',checkpoints_loaded=True,model_released=True,
            scientific_hypothesis_tested=False,conference_level_established=False);save()
    except Exception as exc:summary.update(status='failed',error=repr(exc));save();raise
    finally:signal.setitimer(signal.ITIMER_REAL,0)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);main(p.parse_args().root)
