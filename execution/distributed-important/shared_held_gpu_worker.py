"""Explicitly authorized shared GPU admission; frozen inference remains unchanged."""
import sys,os,json,time,runpy
from pathlib import Path
S=Path('/path/to/user-user/lora-dora-series');P=S.parent/'lora-dora-profiling';D=P/'distributed-important';sys.path.insert(0,str(S))
from lora_dora_study import server
uuid=os.environ['RESEARCH_GPU_LEASE_UUID'];keeper=int(os.environ['RESEARCH_GPU_KEEPER_PID']);policy=json.loads((D/'shared-admission-policy.json').read_text())['gpus'][uuid]
def identity(pid):return Path('/proc',str(pid),'stat').read_text().split()[21]
def allowed(g,processes):
 if g['uuid']!=uuid or g['used_mib']>1024 or g['utilization_percent']>10:return False
 for p in processes:
  if p['gpu_uuid']!=uuid or p['pid']==keeper:continue
  if str(p['pid']) not in policy['foreign_start_ticks']:return False
  try:
   if identity(p['pid'])!=policy['foreign_start_ticks'][str(p['pid'])]:return False
  except FileNotFoundError:return False
  if int(p['memory_mib'])>policy.get('max_foreign_process_mib',512):return False
 return True
# Permit preceding own-worker utilization counters to settle before the next child.
for _ in range(40):
 snap=server.gpu_snapshot();g=next(g for g in snap['gpus'] if g['uuid']==uuid)
 if allowed(g,snap['compute_processes']):break
 time.sleep(.25)
else:raise RuntimeError('Shared GPU admission changed; inspect instead of overriding')
original=server.idle_gpu
out=Path(sys.argv[sys.argv.index('--output-dir')+1])
def shared_idle(g,processes,*args,**kwargs):
 ok=allowed(g,processes)
 for _ in range(40):
  if ok:break
  time.sleep(.25);fresh=server.gpu_snapshot();g=next(x for x in fresh['gpus'] if x['uuid']==uuid);processes=fresh['compute_processes'];ok=allowed(g,processes)
 server.write_json(out/'shared-admission.json',dict(authorized_shared_gpu=True,policy=policy,actual_gpu=g,actual_processes=processes,accepted=ok,external_wrapper=str(Path(__file__)),generation_unchanged=True))
 return ok
server.idle_gpu=shared_idle
# Frozen wrapper verifies same-user direct parent and inherited leases, then runs
# frozen series_worker. Only its admission predicate is extended by user authorization.
runpy.run_path(str(S/'scripts/held_gpu_worker.py'),run_name='__main__')
