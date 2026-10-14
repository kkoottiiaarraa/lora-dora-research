"""Reuse existing eligibility/locks; release all GPUs during CPU preparation."""
import argparse
import fcntl
import importlib.util
import itertools
import json
import os
from pathlib import Path
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from lora_dora_study.server import gpu_snapshot,write_json


def acquire(root,manifest,phase):
    os.environ.update(RESEARCH_MAX_USED_MIB='7168',RESEARCH_EXCLUDED_GPU_INDICES='1',
                      RESEARCH_EXCLUDED_GPU_UUIDS=','.join(manifest['excluded_gpu_uuids']))
    spec=importlib.util.spec_from_file_location('previous_admission',ROOT/'execution/next-experiments/admit_queues.py')
    admission=importlib.util.module_from_spec(spec);spec.loader.exec_module(admission)
    admission.LOCKS.mkdir(exist_ok=True)
    previous=set();started=time.monotonic()
    while time.monotonic()-started<120:
        snapshot=gpu_snapshot()['gpus']
        eligible={g['uuid'] for g in snapshot if admission.eligible(g)}
        stable=eligible&previous;previous=eligible
        candidates=[g for g in snapshot if g['uuid'] in stable]
        candidates.sort(key=lambda g:g['used_mib'])
        for pair in itertools.combinations(candidates,2):
            capacities=[(g['total_mib']-g['used_mib']-2048)*1024**2 for g in pair]
            if min(capacities)<4*1024**3 or sum(capacities)<17*1024**3:continue
            handles=[]
            try:
                for g in pair:
                    h=(admission.LOCKS/(g['uuid']+'.lock')).open('a');handles.append(h)
                    fcntl.flock(h,fcntl.LOCK_EX|fcntl.LOCK_NB)
                fresh={g['uuid']:g for g in gpu_snapshot()['gpus']}
                selected=[fresh[g['uuid']] for g in pair]
                if not all(admission.eligible(g) for g in selected):raise BlockingIOError('Admission changed')
                caps=[(g['total_mib']-g['used_mib']-2048)*1024**2 for g in selected]
                if min(caps)<4*1024**3 or sum(caps)<17*1024**3:raise BlockingIOError('Memory changed')
                allocation=dict(mode='cuda',gpus=[dict(g,max_memory_bytes=n) for g,n in zip(selected,caps)])
                write_json(root/(phase+'-allocation-private.json'),allocation)
                write_json(root/'admission-private.json',dict(phase=phase,status='admitted',gpus=selected))
                return allocation,handles
            except BlockingIOError:
                for h in handles:h.close()
        write_json(root/'admission-private.json',dict(phase=phase,status='waiting_for_two_gpus',last_poll_unix=time.time(),gpus=snapshot))
        time.sleep(10)
    # Bounded wait; CPU fallback preserves FP32 and consumes no GPU.
    allocation=dict(mode='cpu',gpus=[])
    write_json(root/(phase+'-allocation-private.json'),allocation)
    return allocation,[]


def main(root):
    manifest=json.loads((root/'manifest-private.json').read_text())
    state=dict(status='running',phases=[])
    write_json(root/'state.json',state)
    for phase in ['capture','prepare','evaluate']:
        handles=[]
        try:
            allocation,handles=acquire(root,manifest,phase) if phase!='prepare' else (dict(mode='cpu',gpus=[]),[])
            budget=1800 if phase in ['capture','prepare'] else (3600 if allocation['mode']=='cuda' else 10800)
            env=dict(os.environ,CUDA_VISIBLE_DEVICES=','.join(g['uuid'] for g in allocation['gpus']),
                     OMP_NUM_THREADS='4',MKL_NUM_THREADS='4',OPENBLAS_NUM_THREADS='4')
            state.update(current_phase=phase,device=allocation['mode'],gpus_released=not bool(handles));write_json(root/'state.json',state)
            start=time.monotonic()
            with (root/(phase+'.log')).open('x') as log:
                result=subprocess.run([sys.executable,str(ROOT/'execution/next-experiments/compression_followup.py'),
                    '--root',str(root),'--phase',phase,'--budget-seconds',str(budget)],cwd=ROOT,env=env,
                    stdout=log,stderr=subprocess.STDOUT,pass_fds=tuple(h.fileno() for h in handles),timeout=budget+120)
            row=dict(phase=phase,exit_code=result.returncode,wall_seconds=time.monotonic()-start,
                     gpu_count=len(allocation['gpus']))
            state['phases'].append(row)
            if result.returncode:raise RuntimeError('Phase failed: '+phase)
        except Exception as exc:
            state.update(status='failed',error=repr(exc));write_json(root/'state.json',state);raise
        finally:
            for h in handles:h.close()
            state.update(gpus_released=True);write_json(root/'state.json',state)
        state.update(gpus_released=True);write_json(root/'state.json',state)
    state.update(status='complete',current_phase=None);write_json(root/'state.json',state)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True)
    main(p.parse_args().root)
