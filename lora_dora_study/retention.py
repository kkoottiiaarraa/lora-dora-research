"""Keep one acquired GPU occupied until its queue terminates."""
import os
from pathlib import Path
from lora_dora_study.leases import gpu_lease

LEASE=None

def lease_fds():
    return tuple(int(value) for value in os.environ.get('RESEARCH_GPU_LEASE_FDS','').split(',') if value)

def acquire_retained_lease(uuid):
    global LEASE
    directory=Path('/tmp')/('lora-dora-gpu-locks-'+str(os.getuid()))
    inherited=lease_fds()
    if inherited:
        if os.environ.get('RESEARCH_GPU_LEASE_UUID')!=uuid:raise RuntimeError('Inherited GPU mismatch')
        paths={Path(os.readlink('/proc/self/fd/'+str(fd))) for fd in inherited}
        if directory/(uuid+'.lock') not in paths or not any(p.name.startswith('slot-') for p in paths):
            raise RuntimeError('Missing inherited GPU/slot locks')
        return
    LEASE=gpu_lease(uuid)
    LEASE.__enter__()
    selected=[]
    for path in Path('/proc/self/fd').iterdir():
        try:target=Path(os.readlink(path))
        except FileNotFoundError:continue
        if target.parent==directory and (target.name==uuid+'.lock' or target.name.startswith('slot-')):
            selected.append(int(path.name))
    if len(selected)!=2:raise RuntimeError('GPU and slot lease descriptors required')
    os.environ.update(RESEARCH_GPU_LEASE_UUID=uuid,RESEARCH_GPU_LEASE_FDS=','.join(map(str,selected)))

def retain_gpu(uuid, acquire=True):
    if acquire:acquire_retained_lease(uuid)
    os.environ.update(CUDA_VISIBLE_DEVICES=uuid, OMP_NUM_THREADS='2')
    import torch
    torch.set_num_threads(2)
    allocation = torch.zeros(1, device='cuda:0')
    torch.cuda.synchronize()
    os.environ['RESEARCH_GPU_KEEPER_PID'] = str(os.getpid())
    return allocation
