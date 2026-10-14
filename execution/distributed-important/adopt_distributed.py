"""Transfer only this study's coordinators, preserving current workers."""
import os,sys,json,signal,time,subprocess
from pathlib import Path
S=Path('/path/to/user-user/lora-dora-series');P=S.parent/'lora-dora-profiling';D=P/'distributed-important';sys.path.insert(0,str(S))
from lora_dora_study.server import write_json,gpu_snapshot
spec=json.loads((D/'plan.json').read_text())
configs=[('gpu6',3786742,S/'results/extra-series-greedy/series-1.json'),('gpu2',3785635,S/'results/extra-series-greedy/series-2.json'),('gpu5',3914873,S/'results/first-series-greedy/series-3.json')]
def alive(pid):
 try:return Path('/proc',str(pid),'stat').read_text().split()[2]!='Z'
 except FileNotFoundError:return False
for lane,old,path in configs:
 if (D/(lane+'-go.json')).exists():print(lane,'already transferred',flush=True);continue
 assert Path('/proc',str(old)).stat().st_uid==os.getuid()
 cmd=Path('/proc',str(old),'cmdline').read_bytes()
 assert ({'gpu6':b'run_series_queue.py','gpu2':b'takeover_squad_queue.py','gpu5':b'continue_filtered_first.py'}[lane] in cmd)
 os.kill(old,signal.SIGSTOP);new=None;transferred=False
 try:
  state=json.loads(path.read_text());worker=state['worker_pid']
  if alive(worker):
   assert Path('/proc',str(worker)).stat().st_uid==os.getuid()
   assert (b'resume_series_worker.py' if lane=='gpu5' else b'held_gpu_worker.py') in Path('/proc',str(worker),'cmdline').read_bytes()
  if lane=='gpu5':
   adopted=json.loads((P/'filtered-first/handover-go.json').read_text());role=adopted['role'];output=adopted['output']
  else:
   role=state['role'];cmd=state['command'];output=cmd[cmd.index('--output-dir')+1]
  output=Path(output);output=output if output.is_absolute() else S/output
  manifest=dict(old_coordinator_pid=old,worker_pid=worker,role=role,output=str(output))
  with (D/(lane+'.log')).open('x') as log:
   new=subprocess.Popen(['/path/to/user-user/.venvs/lora-dora-research/bin/python',str(P/'distributed_important.py'),'--lane',lane],stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
  for _ in range(120):
   if new.poll() is not None:raise RuntimeError('New coordinator exited')
   f=D/(lane+'-prepared.json')
   if f.exists() and json.loads(f.read_text())['pid']==new.pid:break
   time.sleep(.5)
  else:raise RuntimeError('No prepared CUDA context')
  assert any(p['pid']==new.pid and p['gpu_uuid']==spec['lanes'][lane]['gpu_uuid'] for p in gpu_snapshot()['compute_processes'])
  os.kill(old,signal.SIGTERM);os.kill(old,signal.SIGCONT)
  for _ in range(100):
   if not alive(old):break
   time.sleep(.1)
  else:raise RuntimeError('Old coordinator did not exit')
  write_json(D/(lane+'-go.json'),manifest);transferred=True
  state.update(pid=new.pid,status='transferred_to_distributed_continuation',distributed_state=str(D/(lane+'-state.json')),old_coordinator_pid=old);write_json(path,state)
  if lane=='gpu5':
   pp=S.parent/'lora-dora-research/results/pipeline-20261009T1535Z/state.json';ps=json.loads(pp.read_text());ps.update(pid=new.pid,status='running',distributed_state=str(D/(lane+'-state.json')));write_json(pp,ps)
   fs=P/'filtered-first/state.json';a=json.loads(fs.read_text());a.update(status='superseded_by_distributed_continuation',new_coordinator_pid=new.pid);write_json(fs,a)
  print(lane,dict(new=new.pid,preserved_worker=worker,role=role),flush=True)
 finally:
  if not transferred:
   if new is not None:new.terminate()
   if alive(old):os.kill(old,signal.SIGCONT)
