#!/usr/bin/env python3
"""CPU-only deterministic export from accepted artifacts; no model imports."""
import argparse,csv,datetime,gzip,hashlib,io,json,os,pathlib
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'): os.environ[k]='2'
P=pathlib.Path
METRICS=('author_em','final_em')
def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def main():
 a=argparse.ArgumentParser();a.add_argument('--source-root',default='/path/to/user-user/lora-dora-series');a.add_argument('--distributed-root',default='/path/to/user-user/lora-dora-profiling/distributed-important');a.add_argument('--output',required=True);a.add_argument('--check',action='store_true');args=a.parse_args();S=P(args.source_root);D=P(args.distributed_root);O=P(args.output)
 if args.check:
  m=json.load(open(O/'manifests/export.json'))
  for r in m['outputs']:assert sha(O/r['path'])==r['sha256'],r
  print('Output hash verification passed');return
 for d in ('tables','manifests','validation'):(O/d).mkdir(parents=True,exist_ok=True)
 inputs={};checks={'runs':[],'alignments':[],'family_sizes':{},'interactions':[]};tables={}
 def read(p):
  inputs[str(p)]=sha(p);return json.load(open(p))
 def write(name,rows):
  tables[name]=len(rows);fields=list(dict.fromkeys(k for r in rows for k in r));path=O/'tables'/name
  stream=io.TextIOWrapper(gzip.GzipFile(filename='',mode='wb',fileobj=open(path,'wb'),mtime=0),newline='') if name.endswith('.gz') else open(path,'wt',newline='')
  with stream as f:
   w=csv.DictWriter(f,fields);w.writeheader();w.writerows(rows)
 def resolve(p):return P(p) if P(p).is_absolute() else S/p
 jobs={}
 for f in ('plan.json','night-plan.json'):jobs.update(read(D/f)['jobs'])
 assert len(jobs)==20
 families={};contrasts={}
 for f,size in [('intervention-family-holm.json',8),('localization-family-holm.json',9),('night-localization-family-holm.json',3)]:
  x=read(D/f);assert len(x['contrasts'])==size;assert set(x['contrasts'])==set(x['correction_family']);assert len(x['holm_pvalues'])==size*2;checks['family_sizes'][f]={'contrasts':size,'metric_hypotheses':size*2}
  for j,c in x['contrasts'].items():assert j not in contrasts;contrasts[j]=c;families[j]=(f,x)
 assert set(jobs)==set(contrasts)
 runs={};byjob={}
 for j,job in list(jobs.items())+[('gsm8k-quality-greedy',{'roles':['base','lora','dora']})]:
  p=S/'results/first-series-greedy/jobs'/j;st=read(p/'status.json')
  assert st['status']=='complete',j
  for role in job['roles']:
   out=resolve(st['outputs']['full/'+role]);s=read(out/'summary.json');pred=out/'predictions.jsonl';inputs[str(pred)]=sha(pred)
   assert s['status']=='complete' and s['full_evaluation'] is True
   assert inputs[str(pred)]==s['predictions_sha256']
   rows=[]
   with open(pred) as f:
    for line in f:
     r=json.loads(line);assert set(METRICS)<=set(r['metrics']);assert all(r['metrics'][m] in (0,1) for m in METRICS)
     r['generated_text_sha256']=hashlib.sha256(r.pop('text').encode()).hexdigest();rows.append(r)
   n=len(rows);assert n==s['expected_rows']==s['predictions_completed']==s['dataset']['rows']==1319
   assert [r['test_row_index'] for r in rows]==list(range(n))
   for m in METRICS:assert abs(sum(r['metrics'][m] for r in rows)/n-s['metrics'][m])<1e-12
   runs[str(out)]={'s':s,'rows':rows,'id':j+'/'+role};byjob[(j,role)]=str(out)
   checks['runs'].append({'run_id':j+'/'+role,'path':str(out),'n':n,'hash_rows_complete_means':'passed'})
 def align(paths,label):
  rr=[runs[p] for p in paths];ref=rr[0]
  for r in rr[1:]:
   for field in ('dataset','generation_config','versions','source_sha256'):assert r['s'][field]==ref['s'][field],(label,field)
   assert len(r['rows'])==len(ref['rows'])
   for x,y in zip(ref['rows'],r['rows']):
    for field in ('test_row_index','source_id','prompt_sha256','input_ids_sha256'):assert x[field]==y[field],(label,field)
  checks['alignments'].append({'label':label,'paths':paths,'matched_rows':1319,'status':'passed','summary_fields':['dataset','generation_config','versions','source_sha256'],'row_fields':['test_row_index','source_id','prompt_sha256','input_ids_sha256']});return [r['rows'] for r in rr]
 metrics=[];trans=[]
 for j,c in contrasts.items():
  saved=read(S/'results/first-series-greedy/jobs'/j/'matched-comparison.json');assert saved==c,(j,'family exact comparison')
  left,right=map(lambda k:str(resolve(c[k])),('left','right'));assert right==byjob[(j,jobs[j]['roles'][0])]
  L,R=align([left,right],j);f,x=families[j]
  for m,stat in c['metrics'].items():
   lm=sum(r['metrics'][m] for r in L)/len(L);rm=sum(r['metrics'][m] for r in R)/len(R);diff=rm-lm;assert abs(diff-stat['difference'])<1e-12;assert stat['n']==len(L)
   row=dict(job_id=j,metric=m,actual_reference=runs[left]['id'],left_path=left,right_path=right,targets=';'.join(jobs[j]['targets']),left_mean=lm,right_mean=rm,difference=diff,difference_direction='right-minus-left',existing_ci95_low=stat['ci95'][0],existing_ci95_high=stat['ci95'][1],existing_raw_p=stat['paired_sign_permutation_p'],existing_holm_p=x['holm_pvalues'][j+':'+m],family=f,family_size=len(x['contrasts']),family_metric_hypotheses=len(x['holm_pvalues']),n=len(L),resamples=stat['resamples'],seed=stat['seed'],ci_adjustment=stat['ci_adjustment'],scope=stat['scope']);metrics.append(row)
   counts={name:0 for name in ('correct_to_correct','correct_to_wrong','wrong_to_correct','wrong_to_wrong')}
   for l,r in zip(L,R):counts[('correct' if l['metrics'][m] else 'wrong')+'_to_'+('correct' if r['metrics'][m] else 'wrong')]+=1
   assert sum(counts.values())==len(L);assert abs((counts['wrong_to_correct']-counts['correct_to_wrong'])/len(L)-diff)<1e-12
   trans.append(dict(job_id=j,metric=m,n=len(L),**counts,generated_text_changes=sum(l['generated_text_sha256']!=r['generated_text_sha256'] for l,r in zip(L,R)),difference=diff,left_path=left,right_path=right))
 write('intervention_metrics.csv',metrics);write('paired_transitions.csv',trans)
 grid=[]
 for method in ('remove_d','base_magnitude'):
  for target in ('all','q','k','v','o','qk','vo'):
   j='gsm8k-'+method+'-'+target
   for m in METRICS:
    found=next((r for r in metrics if r['job_id']==j and r['metric']==m),None)
    grid.append(dict(method=method,target=target,metric=m,status='available' if found else 'missing',missing_reason='' if found else 'no accepted contrast',job_id=j,reference=found['actual_reference'] if found else None,difference=found['difference'] if found else None,difference_direction='intervention-minus-unmodified-DoRA'))
 write('localization_grid.csv',grid)
 interactions=[];zero=byjob[('gsm8k-quality-greedy','dora')]
 for method in ('remove_d','base_magnitude'):
  for joint,singles in [('qk',('q','k')),('vo',('v','o'))]:
   ids=['gsm8k-'+method+'-'+t for t in (joint,*singles)];paths=[byjob[(j,'dora')] for j in ids]+[zero];rr=align(paths,method+'/'+joint)
   for m in METRICS:
    value=sum(a['metrics'][m]-b['metrics'][m]-c['metrics'][m]+d['metrics'][m] for a,b,c,d in zip(*rr))/1319
    interactions.append(dict(method=method,interaction='I_'+joint.upper(),metric=m,value=value,n=1319,status='exploratory_descriptive',formula='mean(Y_joint-Y_single1-Y_single2+Y_unmodified_DoRA)',joint=ids[0],single1=ids[1],single2=ids[2],reference=runs[zero]['id'],run_paths=';'.join(paths),source_families=';'.join(families[j][0] for j in ids),existing_ci95_low=None,existing_ci95_high=None,existing_raw_p=None,existing_holm_p=None,missing_reason='No inferential statistics computed for derived interaction'))
 checks['interactions']=[{'method':r['method'],'interaction':r['interaction'],'metric':r['metric'],'n':r['n'],'four_run_alignment':'passed','reference':r['reference']} for r in interactions]
 write('localization_interactions.csv',interactions)
 control=[]
 for j,refrole in [('gsm8k-r32','dora'),('gsm8k-e95','dora'),('gsm8k-e99','dora'),('gsm8k-lora-matched-impact','lora'),('gsm8k-dense-dora','dora'),('gsm8k-dense-lora','lora')]:
  refjob='gsm8k-quality-greedy' if j.startswith('gsm8k-dense-') else 'gsm8k-dense-'+refrole
  left=byjob[(refjob,refrole)];right=byjob[(j,refrole)];L,R=align([left,right],'numerical/'+j)
  exact=contrasts[j]['left']==left and contrasts[j]['right']==right
  for m in METRICS:
   existing=next(r for r in metrics if r['job_id']==j and r['metric']==m)
   control.append(dict(job_id=j,metric=m,reference=runs[left]['id'],left_path=left,right_path=right,n=1319,left_mean=sum(r['metrics'][m] for r in L)/1319,right_mean=sum(r['metrics'][m] for r in R)/1319,difference=sum(r['metrics'][m]-l['metrics'][m] for l,r in zip(L,R))/1319,difference_direction='right-minus-left',status='existing_exact_pair' if exact else 'newly_derived_descriptive',**{k:existing[k] if exact else None for k in ('existing_ci95_low','existing_ci95_high','existing_raw_p','existing_holm_p','family','family_size')},missing_reason='' if exact else 'No existing statistics for exactly this pair'))
 write('numerical_control_contrasts.csv',control)
 scores=[]
 for path,run in runs.items():
  for r in run['rows']:
   for m in METRICS:scores.append(dict(run_id=run['id'],test_row_index=r['test_row_index'],source_id=r['source_id'],metric=m,score=r['metrics'][m],**{k:r.get(k) for k in ('hit_token_limit','prompt_truncated','input_tokens','generated_tokens','seconds','prompt_sha256','input_ids_sha256')}))
 write('per_example_scores.csv.gz',scores)
 checks.update(status='passed',accepted_gsm8k_runs=len(runs),intervention_contrasts=len(contrasts),metrics_rows=len(metrics),transition_checks=40,interaction_four_run_alignments=4,missing_fields=[],table_rows=tables)
 (O/'validation/checks.json').write_text(json.dumps(checks,indent=2)+'\n')
 readme='''# Intervention preparation\n\nDeterministic CPU export of saved GSM8K scores. All differences are right-minus-left fractions; scores lie in [0,1]. All 1319 examples and both author_em/final_em are retained per run. No inference, weights, new p-values or confidence intervals. Existing CI/p/Holm are copied only from the exact saved pair, with independent families of 8/9/3 contrasts (16/18/6 scorer hypotheses). CI scope is test examples conditional on fixed checkpoints. Interactions are exploratory descriptive arithmetic on four aligned runs, without inference or inherited adjustment.\n\nEmpty CSV fields represent null; missing_reason explains unavailable statistics. Generated text changes compare SHA256 of exact decoded text, separately from correctness; texts and their hashes are not exported. The compact score table contains no question, gold, generated text or tokens. seconds is per-example inference time; token columns are counts.\n\nTables: intervention_metrics contains references, paths, targets, means, existing exact-pair statistics and family provenance; paired_transitions contains binary transition counts and separate generated-text change counts; localization_grid enumerates all 2×7×2 cells including availability; localization_interactions contains I_QK/I_VO and four-run provenance; numerical_control_contrasts contains dense-relative rank/matched-impact comparisons and dense-original differences; per_example_scores.csv.gz is a complete long run/example/scorer table. CSV headers define individual fields. validation/checks.json records run hash/completeness/means, pair and four-run fingerprint alignments, counts and family membership checks. manifests/export.json records all source and output SHA256, extractor hash and export UTC.\n\nReproduce on GPU host CPU (stdlib only, at most two threads):\n```bash\nOMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 python3 /path/to/user-user/lora-dora-profiling/analysis-preparation/2026-10-11/build_interventions.py --output /path/to/user-user/lora-dora-profiling/analysis-preparation/2026-10-11/02-interventions\npython3 /path/to/user-user/lora-dora-profiling/analysis-preparation/2026-10-11/build_interventions.py --output /path/to/user-user/lora-dora-profiling/analysis-preparation/2026-10-11/02-interventions --check\nscp -r gpu-host:/path/to/user-user/lora-dora-profiling/analysis-preparation/2026-10-11/02-interventions docs/analysis-preparation/2026-10-11/\n```\n\nThe source-root/distributed-root arguments support relocated source trees. Source artifacts remain unchanged. Integrity errors stop export explicitly. Local VM receives code and compact outputs only; all source scanning, row alignment, hashing and aggregation runs on host CPU.\n'''
 readme+='\nColumn schemas (empty fields are null):\n\n'
 for name in tables:
  opener=gzip.open if name.endswith('.gz') else open
  with opener(O/'tables'/name,'rt') as f:columns=next(csv.reader(f))
  readme+='- `'+name+'`: '+', '.join('`'+c+'`' for c in columns)+'.\n'
 readme+='\nUnits: `score`, means, differences, interaction value and CI endpoints are fractions (no percentage conversion); p-values lie in [0,1]; `n`, family sizes, transition/text-change counts and tokens are integer counts; `seconds` is elapsed seconds. Hash fields are SHA256 hex strings. `test_row_index` is zero-based source order. `source_id` is the retained source identifier. `run_id` is job/role. Flags are Boolean. Paths identify accepted server artifacts.\n'
 (O/'README.md').write_text(readme)
 manifest={'export_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source_root':str(S),'distributed_root':str(D),'server_output':str(O),'extractor':{'path':str(P(__file__).resolve()),'sha256':sha(__file__)},'command':['python3',str(P(__file__).resolve()),'--source-root',str(S),'--distributed-root',str(D),'--output',str(O)],'inputs':[{'path':p,'sha256':h} for p,h in sorted(inputs.items())],'outputs':[{'path':str(p.relative_to(O)),'sha256':sha(p),'bytes':p.stat().st_size} for p in sorted(O.rglob('*')) if p.is_file() and p.name!='export.json']}
 (O/'manifests/export.json').write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps({'tables':tables,'checks':'passed'}))
if __name__=='__main__':main()
