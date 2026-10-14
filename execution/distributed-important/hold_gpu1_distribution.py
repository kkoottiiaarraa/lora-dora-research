import os,sys,json,time,fcntl,runpy
from pathlib import Path
S=Path('/path/to/user-user/lora-dora-series');P=S.parent/'lora-dora-profiling';D=P/'distributed-important';D.mkdir(exist_ok=True)
sys.path.insert(0,str(S))
from lora_dora_study.server import gpu_snapshot,idle_gpu,write_json
UUID='GPU_UUID'
def idle():
 d=gpu_snapshot();g=next(x for x in d['gpus'] if x['uuid']==UUID)
 return idle_gpu(g,d['compute_processes'])
consecutive=0
while consecutive<2:
 consecutive=consecutive+1 if idle() else 0
 write_json(D/'gpu1-reserved.json',dict(pid=os.getpid(),gpu_uuid=UUID,status='waiting_for_gpu1',consecutive_idle_checks=consecutive))
 if consecutive<2:time.sleep(10)
root=Path('/tmp')/('lora-dora-gpu-locks-'+str(os.getuid()));root.mkdir(exist_ok=True)
locks=[]
for name in [UUID+'.lock','slot-3.lock']:
 f=(root/name).open('a');fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);locks.append(f)
if not idle():raise RuntimeError('GPU1 admission race')
os.environ.update(CUDA_VISIBLE_DEVICES=UUID,OMP_NUM_THREADS='2',RESEARCH_GPU_LEASE_UUID=UUID,RESEARCH_GPU_LEASE_FDS=','.join(str(f.fileno()) for f in locks),RESEARCH_GPU_KEEPER_PID=str(os.getpid()))
import torch
torch.set_num_threads(2);warm=torch.empty(1,device='cuda:0');reservation=torch.empty(14*1024**3,dtype=torch.uint8,device='cuda:0');torch.cuda.synchronize()
write_json(D/'gpu1-reserved.json',dict(pid=os.getpid(),gpu_uuid=UUID,status='retained_for_important_interventions',reserved_gib=14,lease_slot=3))
while not (D/'launch-gpu1.json').exists():time.sleep(.5)
reservation=None;torch.cuda.empty_cache()
sys.argv=[str(P/'distributed_important.py'),'--lane','gpu1']
runpy.run_path(str(P/'distributed_important.py'),run_name='__main__')
