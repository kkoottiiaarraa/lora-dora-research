"""Frozen evaluator, one sequential worker per retained GPU; deferred paired analysis."""
import argparse,datetime,fcntl,json,os,subprocess,sys,time,traceback
from pathlib import Path
S=Path('/path/to/user-user/lora-dora-series');P=S.parent/'lora-dora-profiling';D=P/'distributed-important';F=S/'results/first-series-greedy'
sys.path.insert(0,str(S))
from lora_dora_study.server import write_json
from lora_dora_study.evaluation import source_fingerprint,sha256_file
from lora_dora_study.series_results import load_run,compare_runs,holm

def utc():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def alive(pid):
 try:return Path('/proc',str(pid),'stat').read_text().split()[2]!='Z'
 except FileNotFoundError:return False

def main():
 args=argparse.ArgumentParser();args.add_argument('--lane',required=True);lane=args.parse_args().lane
 spec=json.loads((D/'plan.json').read_text());cfg=spec['lanes'][lane];uuid=cfg['gpu_uuid'];qout=D/(lane+'-state.json')
 os.environ.update(CUDA_VISIBLE_DEVICES=uuid,OMP_NUM_THREADS='2',OPENBLAS_NUM_THREADS='2',TOKENIZERS_PARALLELISM='false')
 import torch
 torch.set_num_threads(2);warm=torch.empty(1,device='cuda:0');torch.cuda.synchronize()
 state=dict(pid=os.getpid(),lane=lane,gpu_uuid=uuid,status='prepared_cuda_context',completed_jobs=list(cfg.get('prior_completed_jobs',[])),created_utc=utc())
 write_json(D/(lane+'-prepared.json'),state)
 reservation=None
 def save(**kw):state.update(kw,updated_utc=utc());write_json(qout,state)
 def reserve():
  nonlocal reservation
  torch.cuda.empty_cache();free,_=torch.cuda.mem_get_info();n=max(0,min(14*1024**3,free-256*1024**2));reservation=torch.empty(n,dtype=torch.uint8,device='cuda:0')
 def release():
  nonlocal reservation
  reservation=None;torch.cuda.empty_cache()
 def checked_summary(dest,full):
  a=json.loads((dest/'summary.json').read_text())
  if a['status']!='complete' or a['source_sha256']!=spec['frozen_source_sha256']:raise RuntimeError('Incomplete result or frozen-source mismatch: '+str(dest))
  if full:load_run(dest)
  return a
 def wait_reference(job_id,role):
  f=F/'jobs'/job_id/'status.json'
  if not f.exists():return None
  a=json.loads(f.read_text());p=a.get('outputs',{}).get('full/'+role)
  if not p:return None
  p=Path(p);p=p if p.is_absolute() else S/p
  f=p/'summary.json'
  return p if f.exists() and json.loads(f.read_text()).get('status')=='complete' else None
 def analyze_owned():
  pending=[]
  for id in cfg['jobs']:
   if id=='short-vo':continue
   j=spec['jobs'][id];dest=F/'jobs'/id;f=dest/'matched-comparison.json'
   if f.exists():continue
   reference=j.get('reference_job','gsm8k-quality-greedy');role=j.get('reference_role','dora')
   if j['intervention']=='dense_reference':reference='gsm8k-quality-greedy';role=j['roles'][0]
   left=wait_reference(reference,role);right=wait_reference(id,j['roles'][0])
   if left is None or right is None:pending.append(id);continue
   write_json(f,compare_runs(left,right))
   js=json.loads((dest/'status.json').read_text());js['status']='complete';js['analysis_completed_utc']=utc();write_json(dest/'status.json',js)
  return pending
 def family():
  with (D/'family.lock').open('a') as lock:
   fcntl.flock(lock,fcntl.LOCK_EX)
   paths={id:F/'jobs'/id/'matched-comparison.json' for id in spec['localization_family']}
   if not all(p.exists() for p in paths.values()):return
   results={id:json.loads(p.read_text()) for id,p in paths.items()}
   corrected=holm({id+':'+metric:v['paired_sign_permutation_p'] for id,r in results.items() for metric,v in r['metrics'].items()})
   write_json(D/'localization-family-holm.json',dict(contrasts=results,holm_pvalues=corrected,correction_family=list(paths),note='Nine scheduled localization contrasts, both scorers; separate family from the eight core interventions. CIs conditional on checkpoints and unadjusted. No joint17-contrast correction claimed.'))
 try:
  if cfg.get('adopt_full_job'):
   go=D/(lane+'-rebalance-go.json')
   while not go.exists():time.sleep(.1)
   adopted=json.loads(go.read_text());save(status='adopting_existing_worker',worker_pid=adopted['worker_pid'])
   while alive(adopted['worker_pid']):time.sleep(1)
  if cfg.get('carry_job'):
   go=D/(lane+'-go.json')
   while not go.exists():time.sleep(.1)
   old=json.loads(go.read_text());save(status='adopting_existing_worker',worker_pid=old['worker_pid'])
   while alive(old['worker_pid']):time.sleep(1)
  from lora_dora_study.retention import retain_gpu,lease_fds
  keeper=retain_gpu(uuid)
  if source_fingerprint(S)!=spec['frozen_source_sha256']:raise RuntimeError('Frozen source changed')
  os.chdir(S)
  if cfg.get('adopt_full_job'):
   dest=Path(adopted['output']);a=checked_summary(dest,True);id=cfg['adopt_full_job'];role=adopted['role']
   if a['role']!=role or a['job']['id']!=id:raise RuntimeError('Adopted job/role mismatch')
   jf=F/'jobs'/id/'status.json';js=json.loads(jf.read_text());key='full/'+role
   if key not in js['completed']:
    js['completed'].append(key);js.setdefault('outputs',{})[key]=str(dest);write_json(jf,js)
  if cfg.get('carry_job'):
   dest=Path(old['output']);a=checked_summary(dest,True)
   root=Path(cfg['carry_root']);jf=root/'jobs'/cfg['carry_job']['id']/'status.json';js=json.loads(jf.read_text());key='full/'+old['role']
   if a['role']!=old['role']:raise RuntimeError('Adopted role mismatch')
   if key not in js['completed']:
    js['completed'].append(key);js.setdefault('outputs',{})[key]=str(dest);js['measured_gpu_seconds']=js.get('measured_gpu_seconds',0)+a['inference_seconds'];write_json(jf,js)
   from scripts import run_series_queue as q
   q.PLAN_PATH=D/'carry-plan.json'
   state['retained_gpu_uuid']=uuid
   save(status='finishing_existing_pair',job=cfg['carry_job']['id'])
   q.run_job(cfg['carry_job'],root,state,qout)
   if json.loads(jf.read_text()).get('status')!='complete':raise RuntimeError('Existing pair failed')
   save(status='existing_pair_complete',existing_pair_completed_utc=utc())
  for id in cfg['jobs']:
   release()
   if id=='short-vo':
    save(status='short_symmetry_validation',job=id)
    with (D/'short-vo.log').open('x') as log:
     p=subprocess.Popen([sys.executable,str(P/'short_vo_validation.py')],cwd=S,stdout=log,stderr=subprocess.STDOUT,pass_fds=lease_fds());save(worker_pid=p.pid)
     if p.wait():raise RuntimeError('Short V/O validation failed')
    state['completed_jobs'].append(id);save();continue
   j=dict(spec['jobs'][id]);dest=F/'jobs'/id;dest.mkdir(exist_ok=True);jf=dest/'status.json'
   js=json.loads(jf.read_text()) if jf.exists() else dict(id=id,completed=[],outputs={})
   if j.get('impact_reference'):
    reserve();save(status='waiting_for_reference_artifact',job=id)
    while (ref:=wait_reference(j['impact_reference'],'dora')) is None:time.sleep(1)
    j['impact_manifest']=str(ref/'intervention.json');release()
   jobfile=dest/'job.json';write_json(jobfile,j)
   for phase,limit in [('smoke',2),('full',None)]:
    role=j['roles'][0];key=phase+'/'+role
    if key in js['completed']:continue
    n=1
    while (dest/(phase+'-'+role+'-distributed-'+str(n))).exists():n+=1
    out=dest/(phase+'-'+role+'-distributed-'+str(n))
    command=[sys.executable,'scripts/held_gpu_worker.py','scripts/series_worker.py','--job',str(jobfile),'--gpu-uuid',uuid,'--role',role,'--output-dir',str(out)]
    if limit:command+=['--limit',str(limit)]
    if source_fingerprint(S)!=spec['frozen_source_sha256']:raise RuntimeError('Source changed before worker')
    js.update(status='running',phase=phase,role=role,output_path=str(out));write_json(jf,js)
    with out.with_suffix('.log').open('x') as log:
     p=subprocess.Popen(command,cwd=S,stdout=log,stderr=subprocess.STDOUT,pass_fds=lease_fds());save(status='running',job=id,phase=phase,role=role,worker_pid=p.pid,command=command)
     if p.wait():raise RuntimeError('Worker failed: '+id+'/'+phase)
    a=checked_summary(out,phase=='full');js['completed'].append(key);js['outputs'][key]=str(out);write_json(jf,js)
   js.update(status='outputs_complete_analysis_pending',compute_completed_utc=utc());write_json(jf,js)
   state['completed_jobs'].append(id);save();analyze_owned();family()
  reserve();save(status='compute_complete_analysis_pending',compute_completed_utc=utc(),worker_pid=None)
  while (pending:=analyze_owned()):save(pending_comparisons=pending);time.sleep(5)
  family();save(status='complete_gpu_retained',analysis_completed_utc=utc(),pending_comparisons=[])
 except Exception as e:
  save(status='failed_gpu_retained',error=str(e),traceback=traceback.format_exc());reserve()
 while True:
  try:family()
  except Exception:pass
  time.sleep(10)
if __name__=='__main__':main()
