import os,sys,argparse,json,fcntl,runpy
from pathlib import Path
S=Path('/path/to/user-user/lora-dora-series');P=S.parent/'lora-dora-profiling';D=P/'distributed-important';sys.path.insert(0,str(S))
from lora_dora_study.server import gpu_snapshot,write_json
p=argparse.ArgumentParser();p.add_argument('--lane',choices=['gpu0','gpu4'],required=True);lane=p.parse_args().lane;spec=json.loads((D/'plan.json').read_text());uuid=spec['lanes'][lane]['gpu_uuid'];slot={'gpu0':4,'gpu4':5}[lane];policy=json.loads((D/'shared-admission-policy.json').read_text())['gpus'][uuid]
root=Path('/tmp')/('lora-dora-gpu-locks-'+str(os.getuid()));locks=[]
for name in [uuid+'.lock','slot-'+str(slot)+'.lock']:
 f=(root/name).open('a');fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);locks.append(f)
snap=gpu_snapshot();g=next(g for g in snap['gpus'] if g['uuid']==uuid);assert g['used_mib']<=512 and g['utilization_percent']<=10
assert {str(p['pid']) for p in snap['compute_processes'] if p['gpu_uuid']==uuid}==set(policy['foreign_start_ticks'])
os.environ.update(CUDA_VISIBLE_DEVICES=uuid,OMP_NUM_THREADS='2',RESEARCH_GPU_LEASE_UUID=uuid,RESEARCH_GPU_LEASE_FDS=','.join(str(f.fileno()) for f in locks),RESEARCH_GPU_KEEPER_PID=str(os.getpid()))
write_json(D/(lane+'-admission.json'),dict(pid=os.getpid(),status='admitted_shared_by_user',gpu_uuid=uuid,policy=policy,slot=slot))
sys.argv=[str(P/'distributed_shared_localizations.py'),'--lane',lane];runpy.run_path(str(P/'distributed_shared_localizations.py'),run_name='__main__')
