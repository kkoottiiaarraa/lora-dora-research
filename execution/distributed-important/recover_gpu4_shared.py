"""Resume failed GPU4 keeper without rerunning completed full jobs."""
import json,os,sys,time,signal,fcntl,runpy
from pathlib import Path
S=Path('/path/to/user-user/lora-dora-series');P=S.parent/'lora-dora-profiling';D=P/'distributed-important';sys.path.insert(0,str(S))
from lora_dora_study.server import gpu_snapshot,write_json
uuid='GPU_UUID';a=json.loads((D/'gpu4-state.json').read_text());old=a['pid'];assert a['status']=='failed_gpu_retained';proc=Path('/proc',str(old));assert proc.stat().st_uid==os.getuid();assert b'shared_localization_holder.py' in (proc/'cmdline').read_bytes();assert not (proc/'task'/str(old)/'children').read_text().strip()
policy=json.loads((D/'shared-admission-policy.json').read_text())['gpus'][uuid]
def foreign_ok():
 snap=gpu_snapshot()
 for p in snap['compute_processes']:
  if p['gpu_uuid']!=uuid or p['pid'] in [old,os.getpid()]:continue
  assert str(p['pid']) in policy['foreign_start_ticks'];assert Path('/proc',str(p['pid']),'stat').read_text().split()[21]==policy['foreign_start_ticks'][str(p['pid'])];assert int(p['memory_mib'])<=512
foreign_ok();os.environ.update(CUDA_VISIBLE_DEVICES=uuid,OMP_NUM_THREADS='2')
import torch
torch.set_num_threads(2);warm=torch.empty(1,device='cuda:0');torch.cuda.synchronize();foreign_ok();write_json(D/'gpu4-failure-before-recovery.json',a)
os.kill(old,signal.SIGTERM)
for _ in range(100):
 f=proc/'stat'
 if not f.exists() or f.read_text().split()[2]=='Z':break
 time.sleep(.1)
else:raise RuntimeError('Failed keeper did not exit')
root=Path('/tmp')/('lora-dora-gpu-locks-'+str(os.getuid()));locks=[]
for name in [uuid+'.lock','slot-5.lock']:
 f=(root/name).open('a');fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);locks.append(f)
os.environ.update(RESEARCH_GPU_LEASE_UUID=uuid,RESEARCH_GPU_LEASE_FDS=','.join(str(f.fileno()) for f in locks),RESEARCH_GPU_KEEPER_PID=str(os.getpid()))
sys.argv=[str(P/'distributed_shared_localizations.py'),'--lane','gpu4'];runpy.run_path(str(P/'distributed_shared_localizations.py'),run_name='__main__')
