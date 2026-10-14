"""Three independent delayed queues. No CUDA allocation before idle admission."""
import os,sys,time,json,datetime,argparse,fcntl,contextlib,runpy
from pathlib import Path
S=Path('/path/to/user-user/lora-dora-series');P=S.parent/'lora-dora-profiling';D=P/'distributed-important';sys.path.insert(0,str(S))
from lora_dora_study.server import gpu_snapshot,idle_gpu,write_json
p=argparse.ArgumentParser();p.add_argument('--lane',required=True,choices=['night-k','night-o','night-qk']);lane=p.parse_args().lane;spec=json.loads((D/'night-plan.json').read_text());deadline=datetime.datetime.fromisoformat(spec['lanes'][lane].get('not_before_utc',spec['not_before_utc']));state=dict(pid=os.getpid(),lane=lane,status='scheduled_not_before22_moscow',not_before=deadline.astimezone(datetime.timezone(datetime.timedelta(hours=3))).isoformat(),jobs=spec['lanes'][lane]['jobs']);out=D/(lane+'-admission.json');write_json(out,state)
while datetime.datetime.now(datetime.timezone.utc)<deadline:time.sleep(min(10,max(.1,(deadline-datetime.datetime.now(datetime.timezone.utc)).total_seconds())))
# Explicit GPU5 exception for night-qk only; preserve all other lanes.
if lane=='night-qk' and spec['lanes'][lane].get('authorized_shared_gpu'):
 policy=json.loads((D/'shared-admission-policy.json').read_text())['gpus'][spec['lanes'][lane]['authorized_shared_gpu']]
 def idle_gpu(g,processes):
  if g['uuid']!=policy['initial_gpu']['uuid'] or g['used_mib']>1024 or g['utilization_percent']>10:return False
  for proc in processes:
   if proc['gpu_uuid']!=g['uuid']:continue
   if str(proc['pid']) not in policy['foreign_start_ticks']:return False
   try:
    if Path('/proc',str(proc['pid']),'stat').read_text().split()[21]!=policy['foreign_start_ticks'][str(proc['pid'])]:return False
   except FileNotFoundError:return False
   if int(proc['memory_mib'])>policy.get('max_foreign_process_mib',512):return False
  return True

root=Path('/tmp')/('lora-dora-gpu-locks-'+str(os.getuid()));previous=set()
while True:
 try:
  snap=gpu_snapshot();available={g['uuid'] for g in snap['gpus'] if idle_gpu(g,snap['compute_processes'])};stable=previous&available;previous=available;state.update(status='waiting_for_idle_gpu',idle_uuids=sorted(available),stable_idle_uuids=sorted(stable));write_json(out,state)
  selected=None
  for g in snap['gpus']:
   if g['uuid'] not in stable:continue
   if spec['lanes'][lane].get('requested_gpu_index') is not None and g['index']!=spec['lanes'][lane]['requested_gpu_index']:continue
   stack=contextlib.ExitStack();locks=[]
   try:
    f=stack.enter_context((root/(g['uuid']+'.lock')).open('a'));fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);locks.append(f)
    for slot in range(6):
     f=(root/('slot-'+str(slot)+'.lock')).open('a')
     try:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB)
     except BlockingIOError:f.close();continue
     stack.enter_context(f);locks.append(f);break
    else:stack.close();continue
    fresh=gpu_snapshot();actual=next(x for x in fresh['gpus'] if x['uuid']==g['uuid'])
    if not idle_gpu(actual,fresh['compute_processes']):stack.close();continue
    selected=g;break
   except BlockingIOError:stack.close()
  if selected:break
 except Exception as error:previous=set();state.update(status='probe_error_waiting',error=str(error));write_json(out,state)
 time.sleep(10)
uuid=selected['uuid']
# Serialize only this tiny shared plan update; no GPU reserved until actual idle admission.
with (D/'night-plan.lock').open('a') as lock:
 fcntl.flock(lock,fcntl.LOCK_EX);spec=json.loads((D/'night-plan.json').read_text());spec['lanes'][lane].update(gpu_uuid=uuid,gpu_index=selected['index']);write_json(D/'night-plan.json',spec)
os.environ.update(CUDA_VISIBLE_DEVICES=uuid,OMP_NUM_THREADS='2',RESEARCH_GPU_LEASE_UUID=uuid,RESEARCH_GPU_LEASE_FDS=','.join(str(f.fileno()) for f in locks),RESEARCH_GPU_KEEPER_PID=str(os.getpid()))
state.update(status='admitted',gpu_uuid=uuid,gpu_index=selected['index']);write_json(out,state)
worker=P/('night_localization_worker_shared.py' if spec['lanes'][lane].get('authorized_shared_gpu') else 'night_localization_worker.py');sys.argv=[str(worker),'--lane',lane];runpy.run_path(str(worker),run_name='__main__')
