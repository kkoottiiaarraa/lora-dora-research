#!/usr/bin/env python3
"""Run a worker while ignoring only its authenticated parent's CUDA keeper.

The parent's small CUDA allocation keeps the card occupied between subprocesses.
Foreign processes remain visible to every admission guard. No source changes in
the original evaluator are necessary.
"""
import os
import contextlib
import fcntl
import runpy
import sys
from pathlib import Path

target = Path(sys.argv[1]).resolve()
keeper = int(os.environ['RESEARCH_GPU_KEEPER_PID'])
if keeper != os.getppid() or Path('/proc', str(keeper)).stat().st_uid != os.getuid():
    raise RuntimeError('GPU keeper must be the same-user direct parent')
sys.path.insert(0, str(target.parents[1]))
from lora_dora_study import server
original = server.gpu_snapshot
def snapshot():
    result = original()
    result['compute_processes'] = [p for p in result['compute_processes'] if p['pid'] != keeper]
    # With a continuous authenticated lease, utilization can still reflect the
    # preceding child. Foreign compute processes and actual VRAM remain guarded.
    held=os.environ['RESEARCH_GPU_LEASE_UUID']
    for gpu in result['gpus']:
        if gpu['uuid']==held and not any(p['gpu_uuid']==held for p in result['compute_processes']):
            gpu['utilization_percent']=0
    return result
server.gpu_snapshot = snapshot
from lora_dora_study import leases
uuid=os.environ['RESEARCH_GPU_LEASE_UUID']
fds=tuple(int(value) for value in os.environ['RESEARCH_GPU_LEASE_FDS'].split(','))
directory=Path('/tmp')/('lora-dora-gpu-locks-'+str(os.getuid()))
paths={Path(os.readlink('/proc/self/fd/'+str(fd))) for fd in fds}
if directory/(uuid+'.lock') not in paths or not any(p.parent==directory and p.name.startswith('slot-') for p in paths):
    raise RuntimeError('GPU and slot descriptors were not inherited')
for fd in fds:fcntl.flock(fd,fcntl.LOCK_EX|fcntl.LOCK_NB)
@contextlib.contextmanager
def borrowed_lease(requested, directory=None):
    if requested!=uuid or directory is not None:raise RuntimeError('Borrowed GPU lease mismatch')
    yield
leases.gpu_lease=borrowed_lease
sys.argv = [str(target)] + sys.argv[2:]
runpy.run_path(str(target), run_name='__main__')
