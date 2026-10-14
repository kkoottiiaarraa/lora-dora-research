#!/usr/bin/env python3
"""Read-only pinned public split audit; no model weights or GPU."""
import argparse
import concurrent.futures
import hashlib
import json
from pathlib import Path
import sys
import urllib.request
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from lora_dora_study.server import write_json
from lora_dora_study.intent_routing import gold_id,case_digest


def semantic_digest(example):
    copy=dict(example);copy['available_tools']=sorted(example['available_tools'],key=lambda t:str(t['name']).lower())
    copy['answer']=str(example['answer']).strip().lower()
    return case_digest(copy)


def main(root):
    manifest=json.loads((root/'manifest-private.json').read_text());revision=manifest['revision']
    if len(revision)!=40 or not revision.isalnum():raise ValueError('Need pinned revision')
    data=root/'data';data.mkdir(exist_ok=True)
    def fetch(item):
        path=item['path']
        if not path.startswith('dataset_full/sample_') or '/' in path[len('dataset_full/'):]:raise ValueError('Invalid source path')
        request=urllib.request.Request(f'https://raw.githubusercontent.com/kon172verma/intent-classifier/{revision}/{path}',headers={'User-Agent':'checkpoint-provenance-audit'})
        with urllib.request.urlopen(request,timeout=90) as response:raw=response.read(2*1024**2)
        if hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()!=item['sha']:
            raise ValueError('Git blob mismatch: '+path)
        rows=json.loads(raw)
        if not isinstance(rows,list) or len(rows)!=100:raise ValueError('Expected100rows/file')
        for row in rows:gold_id(row)
        (data/Path(path).name).write_bytes(raw)
        return dict(path=path,sha256=hashlib.sha256(raw).hexdigest(),git_blob=item['sha'],bytes=len(raw),rows=len(rows))
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:files=list(pool.map(fetch,manifest['files']))
    splits={
        'train':[r for i in range(2,10) for r in json.loads((data/f'sample_{i:04}.json').read_text())],
        'validation':json.loads((data/'sample_0010.json').read_text()),
        'test':json.loads((data/'sample_0001.json').read_text())}
    sets={};stats={}
    for name,rows in splits.items():
        full=[case_digest(r) for r in rows];semantic=[semantic_digest(r) for r in rows]
        request=[' '.join(str(r['user_request']).lower().split()) for r in rows]
        sets[name]=dict(full=set(full),semantic=set(semantic),request=set(request))
        labels=[gold_id(r) for r in rows]
        stats[name]=dict(rows=len(rows),unique_full=len(set(full)),unique_semantic=len(set(semantic)),unique_request=len(set(request)),
            no_tool=sum(label=='-' for label in labels),tool_count_min=min(len(r['available_tools']) for r in rows),
            tool_count_max=max(len(r['available_tools']) for r in rows),label_counts={v:labels.count(v) for v in sorted(set(labels))})
    overlap=[]
    for a,b in [('train','validation'),('train','test'),('validation','test')]:
        overlap.append(dict(left=a,right=b,**{key:len(sets[a][key]&sets[b][key]) for key in ['full','semantic','request']}))
    write_json(root/'audit.json',dict(status='complete',revision=revision,files=files,splits=stats,overlap=overlap,
        random_independent_sampling_established=False,synthetic_source=True,near_duplicates_excluded=False))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);main(p.parse_args().root)
