"""One-time user-authorized shared launch on GPUs0/4 with unchanged tiny contexts."""
import os,sys,json,time,fcntl,subprocess,signal,datetime
from pathlib import Path
S=Path('/path/to/user-user/lora-dora-series');P=S.parent/'lora-dora-profiling';D=P/'distributed-important';sys.path.insert(0,str(S))
from lora_dora_study.server import gpu_snapshot,write_json
snap=gpu_snapshot();spec=json.loads((D/'plan.json').read_text());pol=dict(authorization='User explicitly requests launch over existing processes if GPU0/4 load unchanged',timestamp_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),gpus={})
for lane in ['gpu0','gpu4']:
 uuid=spec['lanes'][lane]['gpu_uuid'];g=next(g for g in snap['gpus'] if g['uuid']==uuid);assert g['utilization_percent']<=10 and g['used_mib']<=512
 foreign=[p for p in snap['compute_processes'] if p['gpu_uuid']==uuid];assert all(int(p['memory_mib'])<=512 for p in foreign)
 pol['gpus'][uuid]=dict(initial_gpu=g,foreign_start_ticks={str(p['pid']):Path('/proc',str(p['pid']),'stat').read_text().split()[21] for p in foreign},initial_processes=foreign)
# Recheck the same condition10s later, then cancel waiting-only launchers.
time.sleep(10)
fresh=gpu_snapshot()
for lane in ['gpu0','gpu4']:
 uuid=spec['lanes'][lane]['gpu_uuid'];g=next(g for g in fresh['gpus'] if g['uuid']==uuid);assert g['utilization_percent']<=10 and g['used_mib']<=512
 assert {str(p['pid']) for p in fresh['compute_processes'] if p['gpu_uuid']==uuid}==set(pol['gpus'][uuid]['foreign_start_ticks'])
write_json(D/'shared-admission-policy.json',pol)
for lane in ['gpu0','gpu4']:
 a=json.loads((D/(lane+'-admission.json')).read_text());pid=a['pid'];assert a['status']=='waiting_for_idle_gpu';assert Path('/proc',str(pid)).stat().st_uid==os.getuid();assert b'admit_localization_gpu.py' in Path('/proc',str(pid),'cmdline').read_bytes();os.kill(pid,signal.SIGSTOP)
 assert json.loads((D/(lane+'-admission.json')).read_text())['status']=='waiting_for_idle_gpu'
 os.kill(pid,signal.SIGTERM);os.kill(pid,signal.SIGCONT)
 for _ in range(100):
  f=Path('/proc',str(pid),'stat')
  if not f.exists() or f.read_text().split()[2]=='Z':break
  time.sleep(.1)
 else:raise RuntimeError('Admission waiter failed to terminate')
 with (D/(lane+'-shared-launch.log')).open('x') as log:
  proc=subprocess.Popen(['/path/to/user-user/.venvs/lora-dora-research/bin/python',str(P/'shared_localization_holder.py'),'--lane',lane],stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
 print(lane,'new shared holder',proc.pid,flush=True)
