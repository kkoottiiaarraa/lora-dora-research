"""Continue pending GPU0 result comparison without importing Torch or retaining CUDA."""
import json,sys,os,time,datetime
from pathlib import Path
S=Path('/path/to/user-user/lora-dora-series');P=S.parent/'lora-dora-profiling';D=P/'distributed-important';sys.path.insert(0,str(S))
from lora_dora_study.server import write_json
from lora_dora_study.series_results import compare_runs
statefile=D/'gpu0-state.json';go=D/'gpu0-cpu-comparison-go.json'
write_json(D/'gpu0-cpu-comparison-prepared.json',dict(pid=os.getpid(),cuda=False))
while not go.exists():time.sleep(1)
saved=json.loads(go.read_text());jobfile=S/'results/first-series-greedy/jobs/gsm8k-remove_d-vo/status.json'
a=dict(saved['previous_state'],pid=os.getpid(),previous_gpu_keeper_pid=saved['previous_state']['pid'],status='compute_complete_gpu_released_analysis_pending',worker_pid=None,released_utc=saved['released_utc'],gpu_retained=False);write_json(statefile,a)
try:
 while True:
  f=S/'results/first-series-greedy/jobs/gsm8k-quality-greedy/status.json';reference=json.loads(f.read_text()).get('outputs',{}).get('full/dora')
  if reference:
   p=Path(reference);p=p if p.is_absolute() else S/p
   if (p/'summary.json').exists() and json.loads((p/'summary.json').read_text()).get('status')=='complete':break
  time.sleep(5)
 st=json.loads(jobfile.read_text());out=Path(st['outputs']['full/dora']);out=out if out.is_absolute() else S/out
 write_json(jobfile.parent/'matched-comparison.json',compare_runs(p,out));st.update(status='complete',analysis_completed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat());write_json(jobfile,st)
 a.update(status='complete_gpu_released',analysis_completed_utc=st['analysis_completed_utc']);write_json(statefile,a)
except Exception as e:
 a.update(status='cpu_analysis_failed_gpu_released',error=str(e));write_json(statefile,a);raise
