#!/usr/bin/env python3
"""Adopt an unchanged running evaluator; retain its GPU through the first series."""
import argparse
import datetime
import fcntl
import json
import os
import subprocess
import sys
import time
from pathlib import Path
NEW=Path(__file__).resolve().parents[1]
OLD=Path('/path/to/user-user/lora-dora-research')
sys.path.insert(0,str(NEW))
from lora_dora_study.retention import retain_gpu, acquire_retained_lease, lease_fds
from lora_dora_study.server import write_json

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--adopt-worker',type=int,required=True)
    p.add_argument('--gpu-uuid',required=True)
    args=p.parse_args()
    worker=Path('/proc')/str(args.adopt_worker)
    if worker.stat().st_uid!=os.getuid():raise RuntimeError('Not our worker')
    keeper=retain_gpu(args.gpu_uuid,acquire=False)
    ready=NEW/'results/primary-retention-ready.json'
    write_json(ready,dict(pid=os.getpid(),adopted_pid=args.adopt_worker,gpu_uuid=args.gpu_uuid))
    # Original scheduler is stopped/replaced externally only after this ready file.
    root=OLD/'results/pipeline-20261009T1535Z'
    while worker.exists():
        stat=(worker/'stat').read_text().split(') ')[1].split()[0]
        if stat=='Z':break
        time.sleep(10)
    with (Path('/tmp')/('lora-dora-continuation-'+str(os.getuid())+'.lock')).open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        acquire_retained_lease(args.gpu_uuid)
        state=json.loads((root/'state.json').read_text())
        state.update(pid=os.getpid(),retained_gpu_uuid=args.gpu_uuid,
                     gpu_policy='Acquired once, retained through first-series interventions')
        try:
            for role in ['base','lora','dora']:
                destination=root/'evaluation-full'/role
                summary=destination/'summary.json'
                if summary.exists():
                    result=json.loads(summary.read_text())
                    if result['status']!='complete':raise RuntimeError('Adopted evaluator incomplete')
                    handoff('Полная оценка '+role,dict(path=str(destination),result=result))
                    continue
                command=[sys.executable,str(NEW/'scripts/held_gpu_worker.py'),
                    str(OLD/'scripts/evaluate_gsm8k.py'),'--role',role,'--gpu-uuid',args.gpu_uuid,
                    '--pilot-dir','results/deferred-pilot-20261009T1530Z/pilot-attempt-351',
                    '--downloads','results/reverify-20261009.json','--output-dir',str(destination)]
                state.update(status='running',phase='evaluation-full',role=role,command=command)
                write_json(root/'state.json',state)
                with (root/('evaluation-full-'+role+'-retained.log')).open('x') as log:
                    subprocess.run(command,cwd=OLD,stdout=log,stderr=subprocess.STDOUT,check=True,pass_fds=lease_fds())
                result=json.loads(summary.read_text())
                if result['status']!='complete':raise RuntimeError('Incomplete quality evaluator')
                handoff('Полная оценка '+role,dict(path=str(destination),result=result))
            sys.path.insert(0,str(OLD))
            from scripts.compare_gsm8k import compare
            comparison=compare({r:root/'evaluation-full'/r for r in ['base','lora','dora']})
            write_json(root/'matched-comparison.json',comparison)
            state.update(status='quality_complete_interventions_pending',comparison_path=str(root/'matched-comparison.json'))
            write_json(root/'state.json',state)
            handoff('Первая серия: quality complete',comparison)
        except Exception as error:
            state.update(status='failed_needs_inspection',error=str(error));write_json(root/'state.json',state)
            handoff('Ошибка первой серии',state);raise
    # exec replaces this keeper (no competing fourth queue), preserving the GPU
    # assignment. The new queue initializes its keeper immediately on the same GPU.
    os.chdir(NEW)
    for fd in lease_fds():os.set_inheritable(fd,True)
    os.execv(sys.executable,[sys.executable,'scripts/run_series_queue.py','--series','3',
        '--plan','configs/first_series_interventions.json','--output-root','results/first-series-interventions',
        '--retained-gpu',args.gpu_uuid])

def handoff(stage,data):
    path=OLD/'docs/HANDOFF.md'
    text='## '+stage+'\n\nUTC: '+datetime.datetime.now(datetime.timezone.utc).isoformat()
    text+='\n\n```json\n'+json.dumps(data,ensure_ascii=False,indent=2)+'\n```\n\n'
    temporary=path.with_suffix('.retention.tmp');temporary.write_text(text+path.read_text());temporary.replace(path)

if __name__=='__main__':main()
