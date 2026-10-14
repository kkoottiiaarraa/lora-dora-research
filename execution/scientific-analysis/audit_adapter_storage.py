#!/usr/bin/env python3
"""Read actual safetensors headers and lengths without loading model weights."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import struct


def inspect(path):
    sizes={'F32':4,'F16':2,'BF16':2,'I8':1}
    with path.open('rb') as stream:
        raw=stream.read(8)
        if len(raw)!=8:raise ValueError('Truncated header')
        length=struct.unpack('<Q',raw)[0]
        if length>16*1024**2:raise ValueError('Unexpected header size')
        header=json.loads(stream.read(length))
    payload=[];dtypes={};total=0;records={}
    for name,record in header.items():
        if name=='__metadata__':continue
        dtype=record['dtype'];shape=record['shape'];begin,end=record['data_offsets']
        expected=math.prod(shape)*sizes[dtype]
        if begin<0 or end-begin!=expected:raise ValueError('Tensor length mismatch')
        total+=expected;payload.append((begin,end));dtypes[dtype]=dtypes.get(dtype,0)+1
        records[name]=dict(dtype=dtype,shape=shape)
    previous=0
    for begin,end in sorted(payload):
        if begin!=previous:raise ValueError('Gap/overlap in tensor payload')
        previous=end
    if previous!=total or path.stat().st_size!=8+length+total:raise ValueError('Archive length mismatch')
    h=hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda:stream.read(1024**2),b''):h.update(chunk)
    return dict(payload_bytes=total,file_bytes=path.stat().st_size,tensor_count=len(records),dtypes=dtypes,
                sha256=h.hexdigest()),records


def main(root):
    manifest=json.loads((root/'manifest-private.json').read_text())
    if 'screen_root' in manifest:screen=Path(manifest['screen_root'])
    else:screen=root
    sm=json.loads((screen/'manifest-private.json').read_text())
    storage=json.loads((screen/'storage.json').read_text());results={}
    for label,rank,mode in [('structural_fp16_r15',15,'F16'),('structural_int8_r30',30,'I8')]:
        meta,records=inspect(screen/(label+'.safetensors'))
        saved=storage[label]
        if meta['sha256']!=saved['sha256'] or meta['payload_bytes']!=saved['payload_bytes']:
            raise ValueError('Archive mismatch')
        grouped={}
        for name,info in records.items():
            module,field=name.rsplit('.',1);grouped.setdefault(module,{})[field]=info
        if len(grouped)!=144:raise ValueError('Module coverage')
        for module,rec in grouped.items():
            left,right,d=rec['left'],rec['right'],rec['row_scale']
            if left['dtype']!=mode or right['dtype']!=mode or d['dtype']!='F32':
                raise ValueError('Wrong dtypes')
            if left['shape'][1]!=rank or right['shape'][0]!=rank or d['shape']!=[left['shape'][0]]:
                raise ValueError('Wrong ranks/row count')
            expected={'left','right','row_scale'}
            if mode=='I8':
                expected|={'left_scale','right_scale'}
                if rec['left_scale']!=dict(dtype='F32',shape=[1,rank]) or rec['right_scale']!=dict(dtype='F32',shape=[rank,1]):
                    raise ValueError('Scale shapes')
            if set(rec)!=expected:raise ValueError('Unaccounted tensors')
        total=meta['file_bytes']+(screen/(label+'.json')).stat().st_size
        if total!=saved['total_file_bytes'] or total>23592960:raise ValueError('File budget')
        results[label]=dict(meta,total_file_bytes=total,modules=144,rank=rank)
    full=Path(sm['full_root']);fm=json.loads((full/'manifest-private.json').read_text())
    old=json.loads((Path(fm['parent_root'])/'manifest-private.json').read_text())
    source,_=inspect(Path(old['artifacts']['dora']['snapshot_path'])/'adapter_model.safetensors')
    if source['tensor_count']!=432:raise ValueError('Source tensor coverage')
    result=dict(status='PASS',archives=results,source_adapter=source,base_in_budget=False,
        model_loaded=False,gpu_hours=0,runtime_storage_saving_claimed=False)
    (root/'storage-audit.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);main(p.parse_args().root)
