#!/usr/bin/env python3
"""Pinned public weights/tokenizers only; no inference/training/GPU."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import signal
import sys
import time
os.environ.update(CUDA_VISIBLE_DEVICES='',HF_HUB_DISABLE_TELEMETRY='1',TOKENIZERS_PARALLELISM='false')
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from lora_dora_study.server import write_json
from lora_dora_study.evaluation import sha256_file


def main(root):
    start=time.monotonic();summary=dict(status='running',phase='setup',gpu_hours=0,model_loaded=False,artifacts={})
    def save():summary.update(wall_seconds=time.monotonic()-start);write_json(root/'summary.json',summary)
    def timeout(signum,frame):raise TimeoutError('Readiness download deadline')
    signal.signal(signal.SIGALRM,timeout);signal.setitimer(signal.ITIMER_REAL,1800);save()
    try:
        manifest=json.loads((root/'manifest-private.json').read_text())
        for rel,digest in manifest['source_sha256'].items():
            if sha256_file(ROOT/rel)!=digest:raise ValueError('Frozen source changed: '+rel)
        from huggingface_hub import HfApi,snapshot_download
        api=HfApi(token=False);cache=Path(manifest['cache_dir'])
        for role in ['base','lora','dora']:
            item=manifest['artifacts'][role];summary.update(phase='download_'+role);save()
            info=api.model_info(item['repo_id'],revision=item['revision'],files_metadata=True,token=False)
            if info.sha!=item['revision'] or info.gated or info.private:raise ValueError('Pinned public revision not accepted')
            folder=item.get('subfolder','')
            allowed=[];weights=[]
            for sibling in info.siblings:
                path=sibling.rfilename
                if folder:
                    if not path.startswith(folder+'/'):continue
                    leaf=path[len(folder)+1:]
                else:
                    if '/' in path:continue
                    leaf=path
                if leaf.endswith('.safetensors') or leaf in ['config.json','generation_config.json','adapter_config.json','tokenizer.json','tokenizer_config.json','special_tokens_map.json','chat_template.jinja','merges.txt','vocab.json']:
                    allowed.append(path)
                    if leaf.endswith('.safetensors'):
                        lfs=sibling.lfs
                        digest=lfs.get('sha256') if isinstance(lfs,dict) else getattr(lfs,'sha256',None)
                        if not digest or len(digest)!=64:raise ValueError('Weights have no published SHA256')
                        weights.append(dict(path=path,sha256=digest,size=sibling.size))
            if not weights:raise ValueError('No pinned safetensors weights')
            began=time.monotonic()
            snapshot=Path(snapshot_download(item['repo_id'],revision=item['revision'],allow_patterns=allowed,
                cache_dir=cache,token=False,max_workers=2))
            download_seconds=time.monotonic()-began
            checks=[];verify_start=time.monotonic()
            for entry in weights:
                file=snapshot/entry['path']
                if file.stat().st_size!=entry['size'] or sha256_file(file)!=entry['sha256']:
                    raise ValueError('Downloaded weights mismatch')
                checks.append(entry)
            result=dict(repo_id=item['repo_id'],revision=item['revision'],subfolder=folder,
                snapshot_path=str(snapshot/folder) if folder else str(snapshot),
                download_seconds=download_seconds,verification_seconds=time.monotonic()-verify_start,
                weights=checks,files_sha256={p:sha256_file(snapshot/p) for p in allowed})
            summary['artifacts'][role]=result;save()
        configs={role:json.loads((Path(item['snapshot_path'])/'adapter_config.json').read_text()) for role,item in summary['artifacts'].items() if role!='base'}
        for role,c in configs.items():
            if c['base_model_name_or_path']!='HuggingFaceTB/SmolLM2-360M-Instruct' or c['r']!=16 or c['lora_alpha']!=32 or c['bias']!='none' or c['use_dora']!=(role=='dora') or set(c['target_modules'])!={'q_proj','k_proj','v_proj','o_proj'}:
                raise ValueError('Adapter configuration mismatch')
        scientific={role:{k:v for k,v in item.items() if k!='snapshot_path'} for role,item in summary['artifacts'].items()}
        write_json(root/'artifact-provenance.json',scientific)
        summary.update(status='complete',phase='complete',source_sha256=manifest['source_sha256'],checkpoints_loaded=False);save()
    except Exception as exc:summary.update(status='failed',error=repr(exc));save();raise
    finally:signal.setitimer(signal.ITIMER_REAL,0)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);main(p.parse_args().root)
