"""Release only this study's completed idle keepers, preserving all active work."""
import os,sys,json,time,signal,datetime,fcntl,subprocess
from pathlib import Path
S=Path('/path/to/user-user/lora-dora-series');P=S.parent/'lora-dora-profiling';D=P/'distributed-important';sys.path.insert(0,str(S))
from lora_dora_study.server import gpu_snapshot,write_json
allowed=[b'admit_important_free_gpu.py',b'distributed_important.py',b'shared_localization_holder.py',b'distributed_localizations_v2.py',b'night_localization_admission.py',b'recover_gpu4_shared.py']
while True:
 for lane in ['gpu0','gpu1','gpu2','gpu4','gpu5','gpu6','night-k','night-o','night-qk']:
  f=D/(lane+'-state.json')
  if not f.exists():continue
  a=json.loads(f.read_text())
  # Release after all queued GPU outputs are complete. Pending result analysis
  # transfers to a CPU-only process; active inference is never terminated.
  if a.get('status') not in ['complete_gpu_retained','compute_complete_analysis_pending'] or a.get('worker_pid') is not None:continue
  pid=a['pid'];proc=Path('/proc',str(pid))
  try:
   if proc.stat().st_uid!=os.getuid():raise RuntimeError('Keeper UID mismatch')
   if not any(name in (proc/'cmdline').read_bytes() for name in allowed):raise RuntimeError('Unknown keeper command')
   if (proc/'task'/str(pid)/'children').read_text().strip():continue
   latest=json.loads(f.read_text())
   if latest.get('status') not in ['complete_gpu_retained','compute_complete_analysis_pending'] or latest.get('worker_pid') is not None:continue
   cpu=None
   if latest['status']=='compute_complete_analysis_pending':
    with (D/(lane+'-cpu-finish.log')).open('x') as log:cpu=subprocess.Popen([sys.executable,str(P/'finish_comparisons_cpu.py'),'--lane',lane],stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
    for _ in range(100):
     if (D/(lane+'-cpu-finish-prepared.json')).exists():break
     if cpu.poll() is not None:raise RuntimeError('CPU continuation failed to prepare')
     time.sleep(.1)
    else:raise RuntimeError('CPU continuation preparation timeout')
   os.kill(pid,signal.SIGTERM)
   for _ in range(50):
    p=proc/'stat'
    if not p.exists() or p.read_text().split()[2]=='Z':break
    time.sleep(.1)
   else:raise RuntimeError('Completed keeper did not terminate')
   released=datetime.datetime.now(datetime.timezone.utc).isoformat()
   if cpu is not None:
    a.update(status='compute_complete_gpu_released_analysis_pending',pid=cpu.pid,previous_gpu_keeper_pid=pid,released_utc=released,gpu_retained=False);write_json(f,a)
    write_json(D/(lane+'-cpu-finish-go.json'),dict(previous_state=latest,released_utc=released))
   else:
    a.update(status='complete_gpu_released',released_utc=released,gpu_retained=False);write_json(f,a)
   with open('/tmp/lora-dora-series-handoff-'+str(os.getuid())+'.lock','a') as lock:
    fcntl.flock(lock,fcntl.LOCK_EX)
    text='## Completed queue released GPU: '+lane+'\n\n'+json.dumps(a,ensure_ascii=False,indent=2)+'\n\nAll GPU workers finished; any pending comparisons continue in CPU-only process. Next: other users may use this GPU; night queues only admit truly idle cards after22Moscow.\n\n'
    for repo in ['lora-dora-series','lora-dora-research','lora-dora-dual']:
     path=P.parent/repo/'docs/HANDOFF.md';tmp=path.with_suffix('.tmp.release');tmp.write_text(text+path.read_text());tmp.replace(path)
  except FileNotFoundError:pass
  except Exception as error:write_json(D/(lane+'-release-error.json'),dict(error=str(error),pid=pid))
 time.sleep(10)
