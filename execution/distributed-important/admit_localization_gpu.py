"""Queue one localization lane on its requested idle GPU, with external permit4/5."""
import argparse,os,sys,json,time,fcntl,runpy,contextlib
from pathlib import Path
S=Path('/path/to/user-user/lora-dora-series');P=S.parent/'lora-dora-profiling';D=P/'distributed-important';sys.path.insert(0,str(S))
from lora_dora_study.server import gpu_snapshot,idle_gpu,write_json
p=argparse.ArgumentParser();p.add_argument('--lane',required=True,choices=['gpu0','gpu4']);args=p.parse_args();lane=args.lane;spec=json.loads((D/'plan.json').read_text());cfg=spec['lanes'][lane];uuid=cfg['gpu_uuid'];slot={'gpu0':4,'gpu4':5}[lane];root=Path('/tmp')/('lora-dora-gpu-locks-'+str(os.getuid()));root.mkdir(exist_ok=True);previous=False
while True:
 try:
  snapshot=gpu_snapshot();g=next(g for g in snapshot['gpus'] if g['uuid']==uuid);current=idle_gpu(g,snapshot['compute_processes'])
  write_json(D/(lane+'-admission.json'),dict(pid=os.getpid(),gpu_uuid=uuid,gpu_index=g['index'],status='waiting_for_idle_gpu',consecutive_idle_checks=2 if current and previous else int(current),slot=slot))
  if current and previous:
   stack=contextlib.ExitStack()
   try:
    locks=[]
    for name in [uuid+'.lock','slot-'+str(slot)+'.lock']:
     f=stack.enter_context((root/name).open('a'));fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);locks.append(f)
    fresh=gpu_snapshot();g=next(g for g in fresh['gpus'] if g['uuid']==uuid)
    if idle_gpu(g,fresh['compute_processes']):break
   except BlockingIOError:pass
   stack.close();current=False
  previous=current
 except Exception as error:
  previous=False;write_json(D/(lane+'-admission.json'),dict(pid=os.getpid(),status='probe_error_waiting',error=str(error),gpu_uuid=uuid))
 time.sleep(10)
os.environ.update(CUDA_VISIBLE_DEVICES=uuid,OMP_NUM_THREADS='2',RESEARCH_GPU_LEASE_UUID=uuid,RESEARCH_GPU_LEASE_FDS=','.join(str(f.fileno()) for f in locks),RESEARCH_GPU_KEEPER_PID=str(os.getpid()))
write_json(D/(lane+'-admission.json'),dict(pid=os.getpid(),gpu_uuid=uuid,status='admitted',slot=slot))
sys.argv=[str(P/'distributed_localizations_v2.py'),'--lane',lane];runpy.run_path(str(P/'distributed_localizations_v2.py'),run_name='__main__')
