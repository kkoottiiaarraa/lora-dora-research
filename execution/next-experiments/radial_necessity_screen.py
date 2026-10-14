#!/usr/bin/env python3
"""Fixed 64-request development gate; no fitted predictor or heldout evaluation."""
import argparse
from contextlib import nullcontext
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
from lora_dora_study.evaluation import sha256_file
from lora_dora_study.server import write_json,available_memory_bytes
from lora_dora_study.intent_routing import chat_messages,gold_id,extract_id,case_digest


def main(root):
    start=time.monotonic();summary=dict(status='running',phase='setup',conditions=[],gpu_hours=0,cpu_threads=8)
    def save():summary.update(wall_seconds=time.monotonic()-start,peak_rss_bytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024);write_json(root/'summary.json',summary)
    def timeout(signum,frame):raise TimeoutError('Development gate20min protective deadline')
    signal.signal(signal.SIGALRM,timeout);signal.setitimer(signal.ITIMER_REAL,1200);save()
    try:
        manifest=json.loads((root/'manifest-private.json').read_text())
        for rel,h in manifest['source_sha256'].items():
            if sha256_file(ROOT/rel)!=h:raise ValueError('Frozen code changed:'+rel)
        ready_root=Path(manifest['readiness_root']);ready=json.loads((ready_root/'summary.json').read_text())
        if ready['status']!='complete' or sha256_file(ready_root/'artifact-provenance.json')!=manifest['provenance_sha256']:
            raise ValueError('Pinned artifact provenance changed')
        protocol=json.loads((root/'protocol-private.json').read_text())
        if sha256_file(root/'protocol-private.json')!=manifest['protocol_sha256']:raise ValueError('Protocol changed')
        audit_root=Path(manifest['data_audit_root']);audit=json.loads((audit_root/'audit.json').read_text())
        if sha256_file(audit_root/'audit.json')!=manifest['data_audit_sha256'] or audit['status']!='complete':raise ValueError('Split audit changed')
        rawpath=audit_root/'data/sample_0010.json';expected=next(f['sha256'] for f in audit['files'] if f['path'].endswith('sample_0010.json'))
        if sha256_file(rawpath)!=expected:raise ValueError('Validation source changed')
        raw=json.loads(rawpath.read_text());normalize=lambda x:' '.join(x.lower().split());used={normalize(r['user_request']) for r in raw[:8]};selected=[]
        for i,example in enumerate(raw[8:],8):
            request=normalize(example['user_request'])
            if request in used:continue
            used.add(request);selected.append((i,example))
            if len(selected)==64:break
        if len(selected)!=64:raise ValueError('Insufficient unique development requests')
        if available_memory_bytes()<12*1024**3:raise BlockingIOError('Need12GiBhostRAM')
        import torch
        from transformers import AutoTokenizer
        from lora_dora_study.precision_ablation import load_explicit_cpu
        from lora_dora_study.adapters import verify_loaded_adapter
        from lora_dora_study.fidelity_audit import without_d,magnitude_gauge,metrics,convert_custom
        from lora_dora_study.radial_partition import intervention,components
        torch.set_num_threads(8);torch.set_num_interop_threads(1);torch.manual_seed(20261014)
        paths={k:Path(v['snapshot_path']) for k,v in ready['artifacts'].items()};cfg=json.loads((paths['dora']/'tokenizer_config.json').read_text())
        if cfg['extra_special_tokens']!=[cfg['bos_token'],cfg['eos_token']]:raise ValueError('Tokenizer compatibility schema changed')
        tok=AutoTokenizer.from_pretrained(str(paths['dora']),local_files_only=True,trust_remote_code=False,extra_special_tokens={})
        cases=[]
        for idx,example in selected:
            label=gold_id(example);text=tok.apply_chat_template(chat_messages(example,protocol['system_prompt']),tokenize=False,add_generation_prompt=True)
            ids=tok(text)['input_ids'];full=tok.apply_chat_template(chat_messages(example,protocol['system_prompt'],with_answer=True),tokenize=False,add_generation_prompt=False)
            full_ids=tok(full)['input_ids'];label_ids=tok(label,add_special_tokens=False)['input_ids']
            if len(label_ids)!=1 or full_ids[:len(ids)]!=ids or full_ids[len(ids)]!=label_ids[0]:raise ValueError('Gold boundary changed')
            cases.append(dict(case=len(cases),source_row=idx,input_ids=ids,target=label_ids[0],gold_id=label,case_sha256=case_digest(example),
                request_sha256=__import__('hashlib').sha256(normalize(example['user_request']).encode()).hexdigest(),valid_labels=list('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'[:len(example['available_tools'])])+['-']))
        write_json(root/'cases-private.json',cases)
        summary.update(versions={k:importlib.metadata.version(k) for k in ['torch','transformers','peft','safetensors','accelerate','huggingface_hub']},
            source_sha256=manifest['source_sha256'],case_count=64,cases_sha256=sha256_file(root/'cases-private.json'),
            source_data_sha256=expected,provenance_sha256=manifest['provenance_sha256'],protocol_sha256=manifest['protocol_sha256'],data_audit_sha256=manifest['data_audit_sha256'],exploratory=True)
        write_json(root/'frozen.json',{k:v for k,v in summary.items() if k in ['source_sha256','cases_sha256','source_data_sha256','provenance_sha256','protocol_sha256','data_audit_sha256']}|dict(before_outputs=True));save()
        cache=root/'logit-cache';cache.mkdir();allrows=[];controls=[]
        def load(role):
            began=time.monotonic();model=load_explicit_cpu(str(paths['base']),str(paths[role]),torch.float32)
            check=verify_loaded_adapter(model,paths[role],role=='dora')
            if check['adapted_module_count']!=128 or check['saved_tensor_count']!=(384 if role=='dora' else 256):raise ValueError('Adapter coverage')
            if any(m['r']!=16 or m['scaling']!=2 for m in check['modules']):raise ValueError('Adapter rank/scaling')
            if any(p.is_meta or p.dtype!=torch.float32 or p.device.type!='cpu' or not bool(p.isfinite().all()) for p in model.parameters()):raise ValueError('Invalid parameter')
            if max(len(c['input_ids']) for c in cases)+8>model.config.max_position_embeddings:raise ValueError('Context overflow')
            write_json(root/(role+'-adapter-audit.json'),check);summary.setdefault('loads',[]).append(dict(role=role,seconds=time.monotonic()-began));save();return model
        def full_forward(model,case):
            ids=torch.tensor([case['input_ids']],dtype=torch.long)
            with torch.inference_mode():y=model(input_ids=ids,attention_mask=torch.ones_like(ids),use_cache=False,logits_to_keep=1).logits[0].float().cpu()
            if not bool(y.isfinite().all()):raise FloatingPointError('Nonfinite control')
            return y
        def run(model,condition):
            entry=dict(condition=condition,status='running',cases_completed=0);summary['conditions'].append(entry);summary['phase']=condition;save();rows=[]
            for case in cases:
                ids=torch.tensor([case['input_ids']],dtype=torch.long);began=time.monotonic()
                with torch.inference_mode():out=model.generate(input_ids=ids,attention_mask=torch.ones_like(ids),max_new_tokens=8,do_sample=False,
                    temperature=None,top_p=None,pad_token_id=tok.eos_token_id,eos_token_id=tok.eos_token_id,use_cache=True,return_dict_in_generate=True,output_scores=True)
                if not out.scores or any(not bool(y.isfinite().all()) for y in out.scores):raise FloatingPointError('Invalid generation scores')
                y=out.scores[0].detach().float().cpu()
                if y.shape!=(1,49152):raise ValueError('Vocabulary changed')
                ref=y if condition=='dora' else torch.load(cache/f"dora-{case['case']}.pt",weights_only=True,map_location='cpu')
                new=out.sequences[0,len(case['input_ids']):].tolist();text=tok.decode(new,skip_special_tokens=True);pred=extract_id(text)
                if new[0]!=int(y.argmax(-1)[0]):raise ValueError('Unexpected greedy processing')
                row=dict(condition=condition,case=case['case'],source_row=case['source_row'],case_sha256=case['case_sha256'],request_sha256=case['request_sha256'],
                    gold_id=case['gold_id'],prediction=pred,correct=pred==case['gold_id'],valid_prediction=pred in case['valid_labels'],
                    raw_output=text,generated_tokens=new,generation_seconds=time.monotonic()-began,prompt_tokens=len(case['input_ids']),**metrics(ref,y,[case['target']]))
                if condition=='dora':torch.save(y,cache/f"dora-{case['case']}.pt")
                allrows.append(row);rows.append(row)
                with (root/'per-case.jsonl').open('a') as f:f.write(json.dumps(row,ensure_ascii=False)+'\n')
                entry['cases_completed']+=1;save()
            entry.update(status='complete',correct=sum(r['correct'] for r in rows),invalid=sum(not r['valid_prediction'] for r in rows),
                mean_nll=sum(r['changed_nll'] for r in rows)/64,mean_rms=sum(r['rms'] for r in rows)/64,seconds=sum(r['generation_seconds'] for r in rows));save();return rows
        model=load('dora');parts=[]
        for name,m in model.named_modules():
            if hasattr(m,'use_dora') and m.use_dora.get('default',False):
                p=components(m);parts.append(dict(module=name,gain=float(p['gain']),learned_log_rms=float(p['learned'].log().square().mean().sqrt()),
                    normalization_log_rms=float(p['normalization'].log().square().mean().sqrt()),shape_log_rms=float(p['shape'].log().square().mean().sqrt())))
        write_json(root/'radial-components.json',parts);native=run(model,'dora')
        refs=[full_forward(model,c) for c in cases[:2]]
        for c,y in zip(cases[:2],refs):
            if not torch.equal(y,full_forward(model,c)):raise ValueError('Native full-forward repeat changed')
            controls.append(dict(condition='generation_vs_full',case=c['case'],**metrics(torch.load(cache/f"dora-{c['case']}.pt",weights_only=True),y,[c['target']])))
        removed=None
        for condition in ['remove_d','base_magnitude','learned_only','scalar_d','centered_d']:
            context=without_d(model) if condition=='remove_d' else intervention(model,condition)
            with context:result=run(model,condition)
            if condition=='remove_d':removed=result
        verify_loaded_adapter(model,paths['dora'],True)
        for c,y in zip(cases[:2],refs):
            if not torch.equal(y,full_forward(model,c)):raise ValueError('Source restoration changed')
        for scale in [.995,1.005]:
            with magnitude_gauge(model,scale):
                for c,y in zip(cases[:2],refs):controls.append(dict(condition='gauge_'+str(scale),case=c['case'],**metrics(y,full_forward(model,c),[c['target']])))
        convert_custom(model)
        for c,y in zip(cases[:2],refs):controls.append(dict(condition='dense_control',case=c['case'],**metrics(y,full_forward(model,c),[c['target']])))
        write_json(root/'controls.json',controls)
        effect=sum(r['rms'] for r in removed)/64
        if max(r['rms'] for r in controls)>=.01*effect:raise ValueError('Numeric control floor too large')
        del model;gc.collect();model=load('lora');run(model,'lora');del model;gc.collect()
        gates=[]
        for condition in ['remove_d','base_magnitude']:
            changed=[r for r in allrows if r['condition']==condition];loss=sum(a['correct'] for a in native)-sum(b['correct'] for b in changed)
            discordant=sum(a['correct']!=b['correct'] for a,b in zip(native,changed))
            gates.append(dict(condition=condition,net_correct_loss=loss,correctness_discordant=discordant,passed=loss>=4 or discordant>=8))
        summary.update(status='complete',phase='complete',rows=len(allrows),gates=gates,passed_gate=any(g['passed'] for g in gates),
            native_repeat_bitwise=True,restoration_bitwise=True,numerical_controls_pass=True,model_released=True,
            predictor_trained=False,independent_test_evaluated=False,training_mechanism_identified=False,conference_level_established=False);save()
    except Exception as exc:summary.update(status='failed',error=repr(exc));save();raise
    finally:signal.setitimer(signal.ITIMER_REAL,0)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);main(p.parse_args().root)
