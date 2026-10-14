"""Admit the important 15h lane on GPU3 preferentially, otherwise another idle GPU."""
import os,sys,json,time,fcntl,runpy,contextlib
from pathlib import Path
S=Path('/path/to/user-user/lora-dora-series');P=S.parent/'lora-dora-profiling';D=P/'distributed-important';sys.path.insert(0,str(S))
from lora_dora_study.server import gpu_snapshot,idle_gpu,write_json
previous=set();root=Path('/tmp')/('lora-dora-gpu-locks-'+str(os.getuid()));root.mkdir(exist_ok=True)
while True:
 d=gpu_snapshot();available={g['uuid'] for g in d['gpus'] if idle_gpu(g,d['compute_processes'])};stable=previous&available;previous=available
 write_json(D/'gpu1-reserved.json',dict(pid=os.getpid(),status='waiting_for_any_free_gpu_prefer3',idle_uuids=sorted(available),stable_idle_uuids=sorted(stable)))
 selected=None
 for g in sorted(d['gpus'],key=lambda g:(g['index']!=3,g['index'])):
  if g['uuid'] not in stable:continue
  stack=contextlib.ExitStack()
  try:
   locks=[]
   for name in [g['uuid']+'.lock','slot-3.lock']:
    f=stack.enter_context((root/name).open('a'));fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);locks.append(f)
   fresh=gpu_snapshot();target=next(x for x in fresh['gpus'] if x['uuid']==g['uuid'])
   if not idle_gpu(target,fresh['compute_processes']):stack.close();continue
   selected=g;break
  except BlockingIOError:stack.close()
 if selected:break
 time.sleep(10)
uuid=selected['uuid'];spec=json.loads((D/'plan.json').read_text());spec['lanes']['gpu1'].update(gpu_uuid=uuid,gpu_index=selected['index'],logical_lane_name='gpu1 retained for historical identity; physical GPU reassigned by user')
write_json(D/'plan.json',spec)
os.environ.update(CUDA_VISIBLE_DEVICES=uuid,OMP_NUM_THREADS='2',RESEARCH_GPU_LEASE_UUID=uuid,RESEARCH_GPU_LEASE_FDS=','.join(str(f.fileno()) for f in locks),RESEARCH_GPU_KEEPER_PID=str(os.getpid()))
import torch
torch.set_num_threads(2);warm=torch.empty(1,device='cuda:0');torch.cuda.synchronize()
write_json(D/'gpu1-reserved.json',dict(pid=os.getpid(),status='admitted_important_lane',gpu_uuid=uuid,gpu_index=selected['index'],lease_slot=3))
sys.argv=[str(P/'distributed_important.py'),'--lane','gpu1'];runpy.run_path(str(P/'distributed_important.py'),run_name='__main__')
