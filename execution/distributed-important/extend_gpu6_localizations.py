"""One-time safe transfer of Energy99 worker into expanded GPU6 queue."""
import os,sys,json,signal,time,subprocess
from pathlib import Path
S=Path('/path/to/user-user/lora-dora-series');P=S.parent/'lora-dora-profiling';D=P/'distributed-important';sys.path.insert(0,str(S))
from lora_dora_study.server import write_json,gpu_snapshot
from lora_dora_study.evaluation import source_fingerprint
old=4163392;path=D/'gpu6-state.json';prior=json.loads(path.read_text());assert prior['pid']==old and prior['status']=='running' and prior['job']=='gsm8k-e99' and prior['phase']=='full'
assert Path('/proc',str(old)).stat().st_uid==os.getuid();assert b'distributed_important.py' in Path('/proc',str(old),'cmdline').read_bytes()
os.kill(old,signal.SIGSTOP);new=None;transferred=False;original=(D/'plan.json').read_text()
try:
 prior=json.loads(path.read_text());assert prior['job']=='gsm8k-e99' and prior['phase']=='full';worker=prior['worker_pid'];assert Path('/proc',str(worker)).stat().st_uid==os.getuid();assert b'held_gpu_worker.py' in Path('/proc',str(worker),'cmdline').read_bytes()
 command=prior['command'];output=command[command.index('--output-dir')+1];spec=json.loads((D/'plan-with-localizations.json').read_text());assert source_fingerprint(S)==spec['frozen_source_sha256']
 write_json(D/'gpu6-state-before-localizations.json',prior);write_json(D/'plan-before-localizations.json',json.loads(original));write_json(D/'plan.json',spec)
 with (D/'gpu6-localizations.log').open('x') as log:new=subprocess.Popen(['/path/to/user-user/.venvs/lora-dora-research/bin/python',str(P/'distributed_localizations.py'),'--lane','gpu6'],stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
 for _ in range(120):
  if new.poll() is not None:raise RuntimeError('New controller exited')
  f=D/'gpu6-prepared.json'
  if f.exists() and json.loads(f.read_text())['pid']==new.pid:break
  time.sleep(.5)
 else:raise RuntimeError('CUDA preparation timed out')
 assert any(p['pid']==new.pid and p['gpu_uuid']==prior['gpu_uuid'] for p in gpu_snapshot()['compute_processes'])
 os.kill(old,signal.SIGTERM);os.kill(old,signal.SIGCONT)
 for _ in range(100):
  f=Path('/proc',str(old),'stat')
  if not f.exists() or f.read_text().split()[2]=='Z':break
  time.sleep(.1)
 else:raise RuntimeError('Old controller still alive')
 write_json(D/'gpu6-localizations-go.json',dict(old_coordinator_pid=old,worker_pid=worker,role='dora',output=output));transferred=True
 print(json.dumps(dict(new_controller_pid=new.pid,preserved_worker_pid=worker,additional_jobs=spec['localization_family'],hours=spec['localization_schedule']),indent=2))
finally:
 if not transferred:
  if new is not None:new.terminate()
  write_json(D/'plan.json',json.loads(original))
  if Path('/proc',str(old)).exists():os.kill(old,signal.SIGCONT)
