#!/usr/bin/env python3
"""CPU/stdlib extraction of saved accepted evaluation artifacts; no model imports."""
import argparse,collections,csv,datetime,hashlib,json,pathlib,subprocess,sys,os
os.environ.update({k:'2' for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS')})
def digest(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def fp(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--source',default='/path/to/user-user/lora-dora-series');ap.add_argument('--distributed',default='/path/to/user-user/lora-dora-profiling/distributed-important');ap.add_argument('--out',required=True);ap.add_argument('--check',action='store_true');ap.add_argument('--verify-only',action='store_true');a=ap.parse_args()
 if a.verify_only:
  out=pathlib.Path(a.out);manifest=json.load(open(out/'manifests/export.json'));errors=[]
  for item in manifest['outputs']:
   p=out/item['path']
   if not p.exists() or digest(p)!=item['sha256']:errors.append(item['path'])
  if digest(__file__)!=manifest['extractor_sha256']:errors.append('extractor_sha256')
  integrity=json.load(open(out/'validation/integrity.json'))
  if not integrity['passed']:errors.append('integrity.passed')
  for name,n in integrity['table_rows'].items():
   with open(out/'tables'/name,newline='') as f:actual=sum(1 for _ in csv.DictReader(f))
   if actual!=n:errors.append(name+':row_count')
  print(json.dumps(dict(passed=not errors,verified_outputs=len(manifest['outputs']),errors=errors)));sys.exit(bool(errors))
 S=pathlib.Path(a.source);D=pathlib.Path(a.distributed);O=pathlib.Path(a.out)
 for x in ('tables','manifests','validation'):(O/x).mkdir(parents=True,exist_ok=True)
 inputs={};tables={};checks=[];missing=[]
 def read(p):
  p=pathlib.Path(p);inputs[str(p)]=digest(p);return json.load(open(p))
 def resolve(p):
  p=pathlib.Path(p);return p if p.is_absolute() else S/p
 def check(name,ok,**kw):checks.append(dict(name=name,passed=bool(ok),**kw))
 def emit(name,rows):
  tables[name]=rows;fields=list(dict.fromkeys(k for r in rows for k in r))
  with open(O/'tables'/name,'w',newline='') as f:
   w=csv.DictWriter(f,fields);w.writeheader()
   for r in rows:w.writerow({k:('null' if v is None else json.dumps(v,sort_keys=True) if isinstance(v,(dict,list)) else v) for k,v in r.items()})
 worker=S/'scripts/series_worker.py';inputs[str(worker)]=digest(worker)
 worker_text=worker.read_text()
 plans={}
 for name in ('plan.json','night-plan.json'):plans.update(read(D/name)['jobs'])
 runs={};inventory=[];coverage=[];baselines=['gsm8k-quality-greedy','shadow_4b_mmlu','shadow_4b_squadv2']
 for stp in sorted(S.glob('results/*-series-greedy/jobs/*/status.json')):
  st=read(stp);job=stp.parent.name;accepted=[]
  for key,raw in sorted(st.get('outputs',{}).items()):
   if not key.startswith('full/'):continue
   role=key.split('/')[1];p=resolve(raw);sm=read(p/'summary.json');pp=p/'predictions.jsonl';inputs[str(pp)]=digest(pp)
   rows=[]
   with open(pp) as f:
    for line in f:
     r=json.loads(line);rows.append({k:v for k,v in r.items() if k!='text'})
   n=len(rows);idx=[r['test_row_index'] for r in rows];rid=job+'/'+role
   check('run_integrity',sm.get('status')=='complete' and sm.get('full_evaluation') is True and n==sm.get('expected_rows')==sm.get('predictions_completed')==sm['dataset']['rows'] and idx==list(range(n)) and inputs[str(pp)]==sm.get('predictions_sha256'),run_id=rid,n=n,expected=sm.get('expected_rows'),unique_indices=len(set(idx)),sha256_match=inputs[str(pp)]==sm.get('predictions_sha256'))
   for metric,v in sm['metrics'].items():check('mean_reproduction',abs(sum(r['metrics'][metric] for r in rows)/n-v)<1e-12,run_id=rid,metric=metric)
   runs[str(p)]=(sm,rows,rid);accepted.append(rid)
   art=sm['artifacts'];unknown=[k for k in ('quantization',) if k not in sm]
   if unknown:missing.append(dict(run_id=rid,fields=unknown,missing_reason='not recorded as explicit summary fields'))
   inventory.append(dict(run_id=rid,job=job,task=sm['job']['task'],role=role,intervention=sm['job']['intervention'],targets=sm['job']['targets'],summary_path=str(p/'summary.json'),predictions_path=str(pp),status_path=str(stp),rows=n,expected_rows=sm['expected_rows'],predictions_completed=sm['predictions_completed'],predictions_sha256=inputs[str(pp)],summary_sha256=inputs[str(p/'summary.json')],status_sha256=inputs[str(stp)],dataset_revision=sm['dataset'].get('revision'),base_revision=art['base'].get('revision'),adapter_revision=art.get(role,{}).get('revision') if role!='base' else None,dtype='bfloat16' if inputs[str(worker)]==sm['source_sha256'].get('scripts/series_worker.py') and 'torch_dtype=torch.bfloat16' in worker_text else sm.get('dtype'),dtype_provenance=str(worker),quantization=sm.get('quantization'),tokenizer={'repo_id':art['base']['repo_id'],'revision':art['base']['revision'],'source':'base snapshot; recorded verified tokenizer.json'},missing_reason='; '.join(unknown)+' not recorded; base adapter not applicable' if unknown else None,generation_fingerprint=fp(sm['generation_config']),source_fingerprint=fp(sm['source_sha256']),versions_fingerprint=fp(sm['versions']),complete=sm['status']=='complete',full_evaluation=sm['full_evaluation']))
  coverage.append(dict(job=job,planned=True,status='completed' if accepted else st.get('status'),accepted_full_runs=len(accepted),source_decision=str(stp),reason=st.get('reason'),smoke_as_replication=False))
 attempts=[]
 accepted_paths=set(runs)
 for root in sorted(S.glob('results/*-series-greedy/jobs/*')):
  for p in sorted(root.iterdir()):
   if not p.is_dir() or not p.name.startswith(('full-','smoke-')) or str(p) in accepted_paths:continue
   sp=p/'summary.json';sm=read(sp) if sp.exists() else {}
   attempts.append(dict(job=root.name,attempt_path=str(p),phase='smoke' if p.name.startswith('smoke-') else 'full',accepted=False,status=sm.get('status','missing_summary'),reason=sm.get('reason',sm.get('error','not selected by authoritative status full output; no failure inferred')),summary_path=str(sp) if sp.exists() else None,missing_reason=None if sp.exists() else 'no saved summary'))
 for label,status in [('Answer.AI','deferred'),('Qwen3-8B','excluded'),('LLaVA','excluded')]:coverage.append(dict(job=label,planned=False,status=status,accepted_full_runs=0,source_decision='SPEC.md: Sources and reproducibility',reason='scope decision; no inference implied',smoke_as_replication=False))
 comp=[];bc=[];bm=[];subjects=[];agreement=[];limits=[];transitions=[];answerability=[]
 for root in sorted(S.glob('results/*-series-greedy/jobs/*')):
  cp=root/'matched-comparison.json'
  if not cp.exists():continue
  c=read(cp);cs=c.get('contrasts',{'intervention_minus_reference':c} if 'left' in c else {})
  for cname,co in cs.items():
   lp,rp=map(lambda x:str(resolve(x)),(co['left'],co['right']));l,lr,lid=runs[lp];r,rr,rid=runs[rp]
   matched=[];mismatch=[]
   for field in ('dataset','generation_config','versions','source_sha256'):(matched if l[field]==r[field] else mismatch).append(field)
   for field in ('test_row_index','source_id','prompt_sha256','input_ids_sha256'):
    good=len(lr)==len(rr) and all(x.get(field) is not None and x.get(field)==y.get(field) for x,y in zip(lr,rr));(matched if good else mismatch).append(field)
   good=not mismatch;check('comparability',good,job=root.name,contrast=cname,mismatched_fields=mismatch)
   comp.append(dict(job=root.name,contrast=cname,left_run=lid,right_run=rid,matched_fields=matched,mismatched_fields=mismatch,matched_rows=sum(x['test_row_index']==y['test_row_index'] and x['prompt_sha256']==y['prompt_sha256'] and x['input_ids_sha256']==y['input_ids_sha256'] for x,y in zip(lr,rr)),status='compatible' if good else 'rejected',refusal_reason=None if good else 'mismatched required provenance'))
   if not good:continue
   for metric,stats in co['metrics'].items():
    delta=sum(y['metrics'][metric]-x['metrics'][metric] for x,y in zip(lr,rr))/len(lr);check('saved_difference',abs(delta-stats['difference'])<1e-12,job=root.name,contrast=cname,metric=metric)
    if root.name in baselines:
     binary=all(x['metrics'][metric] in (0,1) and y['metrics'][metric] in (0,1) for x,y in zip(lr,rr))
     counts=collections.Counter((int(x['metrics'][metric]),int(y['metrics'][metric])) for x,y in zip(lr,rr)) if binary else collections.Counter('increase' if y['metrics'][metric]>x['metrics'][metric] else 'decrease' if y['metrics'][metric]<x['metrics'][metric] else 'equal' for x,y in zip(lr,rr))
     tr=dict(job=root.name,contrast=cname,metric=metric,left_run=lid,right_run=rid,n=len(lr),score_type='binary' if binary else 'continuous',correct_correct=counts[1,1] if binary else None,correct_wrong=counts[1,0] if binary else None,wrong_correct=counts[0,1] if binary else None,wrong_wrong=counts[0,0] if binary else None,increase=counts['increase'] if not binary else None,equal=counts['equal'] if not binary else None,decrease=counts['decrease'] if not binary else None,missing_reason=None)
     transitions.append(tr);check('baseline_transition_sum',sum(counts.values())==len(lr),job=root.name,contrast=cname,metric=metric)
     ci=stats.get('ci95',[None,None]);bc.append(dict(job=root.name,contrast=cname,metric=metric,left_run=lid,right_run=rid,difference_direction='right-minus-left',difference=stats['difference'],ci95_low=ci[0],ci95_high=ci[1],raw_p=stats.get('paired_sign_permutation_p'),holm_p=c.get('holm_pvalues',{}).get(cname+':'+metric),family=str(cp),family_size=len(c.get('holm_pvalues',{})),adjustment='Holm within saved comparison file',ci_adjustment=stats.get('ci_adjustment'),n=stats['n'],resamples=stats.get('resamples'),seed=stats.get('seed'),scope=stats.get('scope'),source_path=str(cp),missing_reason=None))
   if root.name=='shadow_4b_mmlu':
    for side,sm,rows in [('left',l,lr),('right',r,rr)]:
     for sub,met in co.get('per_subject',{}).items():
      subset=[x for x in rows if x['subject']==sub]
      for metric,values in met.items():check('saved_per_subject',abs(sum(x['metrics'][metric] for x in subset)/len(subset)-values[side])<1e-12,contrast=cname,side=side,subject=sub)
     for metric,values in co.get('subject_macro',{}).items():
      subs=collections.defaultdict(list)
      for x in rows:subs[x['subject']].append(x['metrics'][metric])
      check('saved_subject_macro',abs(sum(sum(v)/len(v) for v in subs.values())/len(subs)-values[side])<1e-12,contrast=cname,side=side)
 for p,(sm,rows,rid) in sorted(runs.items()):
  if sm['job']['id'] not in baselines:continue
  for metric,score in sm['metrics'].items():bm.append(dict(run_id=rid,task=sm['job']['task'],role=sm['role'],metric=metric,n=len(rows),original_score=score,source_path=p+'/summary.json'))
  if sm['job']['task']=='squadv2':
   dp=resolve(sm['dataset']['path']);inputs[str(dp)]=digest(dp);labels={}
   with open(dp) as f:
    for line in f:
     datum=json.loads(line);labels[datum['test_row_index']]=(bool(datum['answers']['text']),datum['id'])
   check('answerability_dataset_hash',inputs[str(dp)]==sm['dataset']['jsonl_sha256'],run_id=rid)
   check('answerability_alignment',all(labels[x['test_row_index']][1]==x['source_id'] for x in rows),run_id=rid)
   for label in (False,True):
    subset=[x for x in rows if labels[x['test_row_index']][0]==label]
    for metric in sm['metrics']:answerability.append(dict(run_id=rid,role=sm['role'],metric=metric,answerability='answerable' if label else 'unanswerable',n=len(subset),mean=sum(x['metrics'][metric] for x in subset)/len(subset),source_path=str(dp),label_rule='nonempty explicit answers.text',missing_reason=None))
   check('answerability_counts',sum(x['n'] for x in answerability if x['run_id']==rid and x['metric']=='exact')==len(rows),run_id=rid)
  if sm['job']['task']=='mmlu':
   subs=collections.defaultdict(list)
   for r in rows:subs[r['subject']].append(r['metrics']['accuracy'])
   for sub,v in sorted(subs.items()):subjects.append(dict(run_id=rid,role=sm['role'],aggregation='subject',subject=sub,n=len(v),subject_count=1,metric='accuracy',mean=sum(v)/len(v)))
   subjects.extend([dict(run_id=rid,role=sm['role'],aggregation='micro',subject=None,n=len(rows),subject_count=len(subs),metric='accuracy',mean=sm['metrics']['accuracy']),dict(run_id=rid,role=sm['role'],aggregation='macro_unweighted_subjects',subject=None,n=len(rows),subject_count=len(subs),metric='accuracy',mean=sum(sum(v)/len(v) for v in subs.values())/len(subs))])
  if sm['job']['task']=='gsm8k':
   counts=collections.Counter((r['metrics']['author_em'],r['metrics']['final_em']) for r in rows)
   for x in (0,1):
    for y in (0,1):agreement.append(dict(run_id=rid,role=sm['role'],author_em=x,final_em=y,n=counts[x,y]))
   h=sum(r['hit_token_limit'] for r in rows);t=sum(r['prompt_truncated'] for r in rows);check('gsm8k_limits',h==sm['hit_token_limit'] and t==sm['truncated_prompts'],run_id=rid)
   limits.append(dict(run_id=rid,n=len(rows),max_new_tokens=sm['generation_config']['max_new_tokens'],max_input_tokens=sm['dataset']['max_input_tokens'],hit_token_limit=h,prompt_truncated=t))
 for name,rows in [('attempts.csv',attempts),('baseline_pair_transitions.csv',transitions),('squadv2_answerability.csv',answerability),('run_inventory.csv',inventory),('coverage.csv',coverage),('comparability.csv',comp),('baseline_metrics.csv',bm),('baseline_contrasts.csv',bc),('mmlu_subject_metrics.csv',subjects),('gsm8k_scorer_agreement.csv',agreement),('gsm8k_token_limits.csv',limits)]:emit(name,rows)
 check('contrast_count',len(comp)==29,expected_baseline=9,expected_intervention=20,actual=len(comp))
 check('expected_counts',len(inventory)==29 and len(plans)==20 and len([r for r in inventory if r['job'] in baselines])==9,expected_full=29,actual_full=len(inventory),expected_interventions=20,actual_plan_jobs=len(plans),expected_baseline_triples=3,actual_baseline_triples=len({r['job'] for r in inventory if r['job'] in baselines}))
 check('planned_interventions_accepted',set(plans)=={r['job'] for r in inventory if r['job'] not in baselines},expected=sorted(plans),actual=sorted(r['job'] for r in inventory if r['job'] not in baselines))
 def js(path,data):path.write_text(json.dumps(data,indent=2,sort_keys=True)+'\n')
 integrity=dict(passed=all(c['passed'] for c in checks),checks=checks,missing_fields=missing,table_rows={k:len(v) for k,v in tables.items()});js(O/'validation/integrity.json',integrity)
 readme=['# Corpus and baseline quality export','', 'CPU/stdlib extraction of all status-selected accepted full runs. No new CI, p values or inference. Scores are fractions in [0,1]; differences are right-minus-left. Existing CI/p/Holm are copied with each original comparison family. CI is conditional on fixed checkpoints and evaluation examples, not training seeds. CSV null is the literal `null`; unknown metadata has missing_reason.','', 'Reproduce on GPU host (upload this extractor to the temporary directory first):','', '```bash','OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 python3 /path/to/user-user/lora-dora-profiling/analysis-preparation/2026-10-11/build_corpus_quality.py --out /path/to/user-user/lora-dora-profiling/analysis-preparation/2026-10-11/01-corpus-quality --check','```','', 'Local verification (no SSH/raw data): `python3 execution/analysis-preparation/build_corpus_quality.py --out docs/analysis-preparation/2026-10-11/01-corpus-quality --verify-only`.', '', 'Then copy only 01-corpus-quality back to docs/analysis-preparation/2026-10-11/. Raw predictions stay on the GPU host. --check writes validation and exits nonzero on any failed check. Source paths resolve relative to --source (default /path/to/user-user/lora-dora-series); plans come from --distributed.','', 'Fields: IDs and paths preserve source provenance; *_sha256 are byte hashes, *_fingerprint is SHA256 of canonical sorted JSON. rows/n are example counts; expected/predictions_completed are saved counts. complete/full_evaluation are saved acceptance flags. status is recorded coverage or explicit comparability result. matched/mismatched_fields list required equality checks. original_score is copied from summary; means are deterministic saved-score aggregates. subject micro weights examples, macro weights subjects equally. author_em/final_em rows cover all four binary combinations; token limit counts are separate. resamples/seed/scope/adjustment describe existing statistics only. Family is exactly the original matched-comparison path. No training metadata inferred.','', 'Transition columns correct_correct/correct_wrong/wrong_correct/wrong_wrong are counts of left-to-right binary correctness. Continuous metrics use increase/equal/decrease and have null binary columns. Answerability labels use explicit source answers.text; n is examples in each stratum. attempts.csv contains nonselected full and smoke directories separately; missing summary does not assert failure. dtype comes from the byte-matched saved evaluator source, tokenizer from pinned base snapshot; quantization remains null because not explicitly recorded.', '', 'Schemas:']
 for name,rows in tables.items():readme.extend(['',f'- `{name}` ({len(rows)} rows): '+', '.join(rows[0])])
 (O/'README.md').write_text('\n'.join(readme)+'\n')
 js(O/'manifests/export.json',dict(exported_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),source_root=str(S),distributed_root=str(D),server_output=str(O),extractor_sha256=digest(__file__),command='OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 python3 '+str(pathlib.Path(__file__).resolve())+' --out '+str(O)+' --check',inputs=[dict(path=k,sha256=v) for k,v in sorted(inputs.items())],outputs=[dict(path=str(p.relative_to(O)),sha256=digest(p),bytes=p.stat().st_size) for p in sorted(O.rglob('*')) if p.is_file() and p.name!='export.json']))
 print(json.dumps({'passed':integrity['passed'],'table_rows':integrity['table_rows'],'checks':len(checks)}))
 if a.check and not integrity['passed']:sys.exit(1)
if __name__=='__main__':main()
