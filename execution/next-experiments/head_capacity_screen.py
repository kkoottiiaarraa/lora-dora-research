#!/usr/bin/env python3
"""No-model CPU diagnostic of nine fixed head output tables."""
import argparse
import datetime
import importlib.metadata
import json
import os
from pathlib import Path
import resource
import signal
import sys
import time
os.environ.update(CUDA_VISIBLE_DEVICES='',OMP_NUM_THREADS='4',MKL_NUM_THREADS='4',OPENBLAS_NUM_THREADS='4')
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from lora_dora_study.evaluation import sha256_file
from lora_dora_study.server import write_json,available_memory_bytes


def main(root):
    started=time.monotonic();summary=dict(status='running',phase='setup',heads_completed=0,gpu_hours=0,model_loaded=False)
    def save():
        summary.update(wall_seconds=time.monotonic()-started,rss_bytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024)
        write_json(root/'summary.json',summary)
    def timeout(signum,frame):raise TimeoutError('Head capacity screen deadline')
    signal.signal(signal.SIGALRM,timeout);signal.setitimer(signal.ITIMER_REAL,900);save()
    try:
        manifest=json.loads((root/'manifest-private.json').read_text())
        for rel,digest in manifest['source_sha256'].items():
            if sha256_file(ROOT/rel)!=digest:raise ValueError('Frozen source changed: '+rel)
        full=Path(manifest['full_root']);capture=json.loads((full/'capture/summary.json').read_text())
        old=json.loads((Path(json.loads((full/'manifest-private.json').read_text())['parent_root'])/'manifest-private.json').read_text())
        if capture['status']!='complete' or capture['saved_modules']!=144:raise ValueError('Capture incomplete')
        cfg=json.loads((Path(old['artifacts']['base']['snapshot_path'])/'config.json').read_text())
        if any(cfg[k]!=v for k,v in {'hidden_size':2560,'num_attention_heads':32,'head_dim':128,'num_hidden_layers':36}.items()):
            raise ValueError('Model/head shape changed')
        calpath=Path(old['calibration_cases'])
        if sha256_file(calpath)!=old['calibration_cases_sha256'] or len(json.loads(calpath.read_text()))!=64:
            raise ValueError('Activation calibration provenance changed')
        selected={layer:next(item for item in capture['modules'] if item['name'].endswith(f'layers.{layer}.self_attn.o_proj')) for layer in [0,17,35]}
        for item in selected.values():
            if sha256_file(full/'capture'/item['file'])!=item['sha256']:raise ValueError('Capture tensor file changed')
        write_json(root/'frozen.json',dict(source_sha256=manifest['source_sha256'],layers=[0,17,35],heads=[0,15,31],rank=32,
            calibration_cases_sha256=old['calibration_cases_sha256'],source_module_sha256={str(layer):item['sha256'] for layer,item in selected.items()},
            before_outputs=True,exploration_only=True))
        import torch
        from safetensors import safe_open
        from lora_dora_study.head_capacity import analyze,action_error
        torch.set_num_threads(4);torch.set_num_interop_threads(1)
        if available_memory_bytes()<8*1024**3:raise BlockingIOError('Need8GiBfreeRAM')
        summary.update(phase='analyze',versions={k:importlib.metadata.version(k) for k in capture['versions']},
            source_sha256=manifest['source_sha256'],frozen_sha256=sha256_file(root/'frozen.json'),
            calibration_cases_sha256=old['calibration_cases_sha256'],source_capture_casehash_is_not_activation_casehash=True,
            artifacts={k:{j:v[j] for j in ['repo_id','revision']} for k,v in old['artifacts'].items()},cpu_threads=4)
        adapter_file=Path(old['artifacts']['dora']['snapshot_path'])/'adapter_model.safetensors'
        summary['adapter_weights_sha256']=sha256_file(adapter_file)
        rows=[]
        for layer,item in selected.items():
            data=torch.load(full/'capture'/item['file'],map_location='cpu',weights_only=True)
            if data['base'].shape!=(2560,4096) or data['inputs'].shape!=(2048,4096) or data['b'].shape[1]!=32:
                raise ValueError('Source tensor shape changed')
            direction=data['base'].double()+(data['b'].double()@data['a'].double())*data['scaling']
            with safe_open(str(adapter_file),framework='pt',device='cpu') as handle:
                keys=[key for key in handle.keys() if f'layers.{layer}.self_attn.o_proj.' in key and 'lora_magnitude_vector' in key]
                if len(keys)!=1:raise ValueError('Pinned source magnitude not unique')
                magnitude=handle.get_tensor(keys[0]).double()
            if magnitude.shape!=(2560,):raise ValueError('Source magnitude shape changed')
            source=(magnitude/direction.norm(dim=1))[:,None]*direction
            for head in [0,15,31]:
                cols=slice(head*128,(head+1)*128)
                base=data['base'][:,cols].double();value=source[:,cols];inputs=data['inputs'][:,cols].double()
                result=analyze(base,value,inputs,32)
                control=analyze(base,direction[:,cols],inputs,32)
                floor=action_error(value,data['value'][:,cols],inputs)
                gauges=[]
                for c in [.995,1.005]:
                    changed=analyze(base,value/c,inputs*c,32)
                    gauges.append(dict(c=c,relative_tail_change=abs(changed['tail_energy']-result['tail_energy'])/max(result['tail_energy'],1e-30),
                        relative_source_energy_change=abs(changed['source_energy']-result['source_energy'])/max(result['source_energy'],1e-30)))
                if control['tail_fraction_source']>1e-20 or max(g['relative_tail_change'] for g in gauges)>1e-10:
                    raise ValueError('Algebraic control failed')
                practical=(result['tail_fraction_source']>=1e-6 and result['tail_fraction_outside']>=.05 and result['tail_energy']>=1000*floor)
                row=dict(layer=layer,head=head,rank=32,calibration_rows=2048,**result,
                    no_d_tail_fraction_source=control['tail_fraction_source'],fp32_merge_action_floor=floor,
                    fp32_merge_floor_fraction_source=floor/max(result['source_energy'],1e-30),
                    practical_gate=practical,gauges=gauges)
                rows.append(row);write_json(root/'heads.json',rows)
                summary.update(heads_completed=len(rows));save()
            del data,direction,source
        summary.update(status='complete',phase='complete',practical_heads=sum(r['practical_gate'] for r in rows),
            passed_practical_gate=sum(r['practical_gate'] for r in rows)>=3,
            full_network_expressivity_bound=False,task_quality=False,training_mechanism_identified=False,conference_level_established=False);save()
    except Exception as exc:
        summary.update(status='failed',error=repr(exc));save();raise
    finally:signal.setitimer(signal.ITIMER_REAL,0)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);main(p.parse_args().root)
