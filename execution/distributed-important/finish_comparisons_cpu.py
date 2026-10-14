"""Complete only saved-result analysis after releasing a finished queue's GPU."""
import argparse,json,sys,os,time,datetime,fcntl
from pathlib import Path
S=Path('/path/to/user-user/lora-dora-series');P=S.parent/'lora-dora-profiling';D=P/'distributed-important';sys.path.insert(0,str(S))
from lora_dora_study.server import write_json
from lora_dora_study.series_results import compare_runs,holm
p=argparse.ArgumentParser();p.add_argument('--lane',required=True);args=p.parse_args();lane=args.lane
spec=json.loads((D/('night-plan.json' if lane.startswith('night-') else 'plan.json')).read_text());cfg=spec['lanes'][lane];ids=[id for id in cfg['jobs'] if id!='short-vo'];prepared=D/(lane+'-cpu-finish-prepared.json');go=D/(lane+'-cpu-finish-go.json');statefile=D/(lane+'-state.json');write_json(prepared,dict(pid=os.getpid(),cuda=False))
while not go.exists():time.sleep(.1)
saved=json.loads(go.read_text());a=dict(saved['previous_state'],pid=os.getpid(),previous_gpu_keeper_pid=saved['previous_state']['pid'],status='compute_complete_gpu_released_analysis_pending',worker_pid=None,gpu_retained=False,released_utc=saved['released_utc']);write_json(statefile,a)
def full(id,role):
 f=S/'results/first-series-greedy/jobs'/id/'status.json'
 if not f.exists():return None
 value=json.loads(f.read_text()).get('outputs',{}).get('full/'+role)
 if not value:return None
 out=Path(value);out=out if out.is_absolute() else S/out
 return out if (out/'summary.json').exists() and json.loads((out/'summary.json').read_text()).get('status')=='complete' else None
try:
 while True:
  pending=[]
  for id in ids:
   job=spec['jobs'][id];dest=S/'results/first-series-greedy/jobs'/id;f=dest/'matched-comparison.json'
   if f.exists():
    result=json.loads(f.read_text());assert 'metrics' in result
    jf=dest/'status.json';st=json.loads(jf.read_text())
    if st.get('status')!='complete':st.update(status='complete',analysis_completed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat());write_json(jf,st)
    continue
   ref=job.get('reference_job','gsm8k-quality-greedy');role=job.get('reference_role','dora')
   if job['intervention']=='dense_reference':ref='gsm8k-quality-greedy';role=job['roles'][0]
   left=full(ref,role);right=full(id,job['roles'][0])
   if left is None or right is None:pending.append(id);continue
   write_json(f,compare_runs(left,right));st=json.loads((dest/'status.json').read_text());st.update(status='complete',analysis_completed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat());write_json(dest/'status.json',st)
  if not pending:break
  a.update(pending_comparisons=pending);write_json(statefile,a);time.sleep(5)
 with (D/'family.lock').open('a') as lock:
  fcntl.flock(lock,fcntl.LOCK_EX)
  groups=[(spec.get('core_jobs',[]),'intervention-family-holm.json'),(spec.get('localization_family',[]),'night-localization-family-holm.json' if lane.startswith('night-') else 'localization-family-holm.json')]
  for group,name in groups:
   paths={id:S/'results/first-series-greedy/jobs'/id/'matched-comparison.json' for id in group}
   if not paths or not all(f.exists() for f in paths.values()):continue
   results={id:json.loads(f.read_text()) for id,f in paths.items()};adjusted=holm({id+':'+metric:v['paired_sign_permutation_p'] for id,r in results.items() for metric,v in r['metrics'].items()});write_json(D/name,dict(contrasts=results,holm_pvalues=adjusted,correction_family=list(paths),note='Separate prespecified family; CPU-only analysis; conditional unadjusted CIs.'))
 a.update(status='complete_gpu_released',pending_comparisons=[],analysis_completed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat());write_json(statefile,a)
except Exception as error:
 a.update(status='cpu_analysis_failed_gpu_released',error=str(error));write_json(statefile,a);raise
