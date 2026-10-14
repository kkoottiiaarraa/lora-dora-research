#!/usr/bin/env python3
"""CPU/std-library export of recorded diagnostics; never imports model libraries."""
import argparse,csv,datetime,hashlib,json,math,pathlib,statistics
P=pathlib.Path
inputs={};tables={};checks=[]
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def read(p):
 inputs[str(p)]={'sha256':sha(p),'bytes':p.stat().st_size};return json.loads(p.read_text())
def flat(x,prefix=''):
 d={}
 for k,v in x.items():
  key=prefix+k
  if isinstance(v,dict):d.update(flat(v,key+'.'))
  elif not isinstance(v,list):d[key]=v
 return d
def add(t,**r):tables.setdefault(t,[]).append(r)
def check(name,ok,**details):checks.append(dict(name=name,passed=bool(ok),**details))
def main():
 a=argparse.ArgumentParser();a.add_argument('--source-root',default='/path/to/user-user/lora-dora-series');a.add_argument('--diagnostic-root',default='/path/to/user-user/lora-dora-profiling/distributed-important');a.add_argument('--output',required=True);a.add_argument('--check',action='store_true');a.add_argument('--verify-local',action='store_true');args=a.parse_args();S=P(args.source_root);D=P(args.diagnostic_root);out=P(args.output)
 if args.verify_local:
  manifest=json.loads((out/'manifests/hashes.json').read_text());bad=[n for n,v in manifest['outputs'].items() if not (out/n).is_file() or sha(out/n)!=v['sha256']];ok=not bad and sha(P(__file__))==manifest['extractor_sha256'] and json.loads((out/'validation/checks.json').read_text())['passed'];print(json.dumps({'passed':ok,'failed_output_hashes':bad,'extractor_hash_matches':sha(P(__file__))==manifest['extractor_sha256']}));raise SystemExit(0 if ok else 1)
 plans={}
 for n in ['plan.json','night-plan.json']:plans.update(read(D/n)['jobs'])
 accepted={};modules={};resource_fields=['tokenizer_load_seconds','base_load_seconds','adapter_load_seconds','intervention_seconds','inference_seconds']
 for root in [S/'results/first-series-greedy/jobs',S/'results/extra-series-greedy/jobs']:
  for sp in sorted(root.glob('*/status.json')):
   st=read(sp);job=sp.parent.name
   for phase,path in st.get('outputs',{}).items():
    if phase.startswith('full/'):
     p=P(path);p=p if p.is_absolute() else S/p;accepted[str(p)]=(job,phase.split('/')[1],sp)
   if st.get('status')!='complete':add('attempts',job=job,source=str(sp),status=st.get('status'),reason=st.get('reason'),phase=st.get('phase'),accepted_full=False)
   for ap in sorted(sp.parent.glob('*/*summary.json')):
    if str(ap.parent) in accepted:continue
    x=read(ap);r=flat({k:v for k,v in x.items() if k in resource_fields+['memory','load_memory','status','error','reason','full_evaluation','predictions_completed']});add('attempts',job=job,source=str(ap),phase=ap.parent.name,accepted_full=False,**r)
   # Failed attempts can have only an error artifact.
   for ap in sorted(sp.parent.glob('*/error.json')):
    x=read(ap);add('attempts',job=job,source=str(ap),phase=ap.parent.name,accepted_full=False,status='error',recorded_error_json=json.dumps(x,sort_keys=True))
 for path,(job,role,sp) in sorted(accepted.items()):
  p=P(path);s=read(p/'summary.json');j=s.get('job',{});meta=dict(job=job,role=role,source=str(p/'summary.json'),status_source=str(sp));r={k:s.get(k) for k in resource_fields};r.update(flat({'memory':s.get('memory',{}),'load_memory':s.get('load_memory',{})}));tokens=0;token_known=True;idx=[];pred=p/'predictions.jsonl';inputs[str(pred)]={'sha256':sha(pred),'bytes':pred.stat().st_size}
  with pred.open() as f:
   for line in f:
    row=json.loads(line);idx.append(row.get('test_row_index'));v=row.get('generated_tokens',row.get('new_tokens',row.get('output_tokens')));token_known &= isinstance(v,(int,float));tokens+=v if isinstance(v,(int,float)) else 0
  check(job+'/'+role+'/integrity',s.get('status')=='complete' and s.get('full_evaluation') is True and len(idx)==s.get('expected_rows')==s.get('predictions_completed') and len(set(idx))==len(idx) and idx==sorted(idx) and inputs[str(pred)]['sha256']==s.get('predictions_sha256'),rows=len(idx),expected_rows=s.get('expected_rows'),prediction_sha256_matches=inputs[str(pred)]['sha256']==s.get('predictions_sha256'))
  r.update(inference_gpu_hours=s.get('inference_seconds',0)/3600 if s.get('inference_seconds') is not None else None,generated_tokens=tokens if token_known else None,tokens_per_inference_second=tokens/s['inference_seconds'] if token_known and s.get('inference_seconds') else None,wall_seconds=None,wall_missing_reason='No explicit run start/end pair',cost_scope='accepted full inference only; not campaign cost');add('resources',**meta,**r)
  ip=p/'intervention.json';i=read(ip) if ip.exists() else s.get('intervention',{});i=i if isinstance(i,dict) else {};src=str(ip) if ip.exists() else str(p/'summary.json')+'#/intervention';modules[job]=[]
  for m in i.get('modules',[]):
   if isinstance(m,str):m={'module':m}
   rr=flat({k:v for k,v in m.items() if k!='spectrum'});rr.update(shape=json.dumps(m.get('shape')) if m.get('shape') else None,calibration_source=i.get('calibration_source'),calibration_sha256=j.get('calibration_sha256'),calibration_tokens=i.get('calibration_tokens'),intervention=i.get('method',j.get('intervention')),targets=json.dumps(j.get('targets')),source=src,job=job,role=role)
   spec=m.get('spectrum');
   if spec:
    energy=[v*v for v in spec];total=math.fsum(energy);cum=0;ranks={}
    for k,v in enumerate(energy,1):
     cum+=v
     for threshold in [.95,.99]:
      if threshold not in ranks and cum>=total*threshold:ranks[threshold]=k
    rr.update(derived_energy_at_rank=math.fsum(energy[:m['rank']])/total if total and isinstance(m.get('rank'),int) else None,derived_rank95=ranks.get(.95),derived_rank99=ranks.get(.99),energy_denominator='sum(square(saved spectrum)); per module',spectrum_count=len(spec),spectrum_energy_sum=total)
    check(job+'/'+m['module']+'/spectrum',all(math.isfinite(v) and v>=0 for v in spec) and all(spec[k]>=spec[k+1] for k in range(len(spec)-1)) and len(spec)==min(m['shape']),spectrum_count=len(spec))
    if m.get('retained_energy') is not None and rr['derived_energy_at_rank'] is not None:check(job+'/'+m['module']+'/energy_reproduction',abs(rr['derived_energy_at_rank']-m['retained_energy'])<1e-5,absolute_difference=abs(rr['derived_energy_at_rank']-m['retained_energy']))
   modules[job].append(rr);add('rank_modules',**rr)
  for key in sorted({k for m in modules[job] for k,v in m.items() if isinstance(v,(float,int)) and not isinstance(v,bool)}):
   vals=[m[key] for m in modules[job] if isinstance(m.get(key),(int,float))];add('rank_job_summary',job=job,role=role,field=key,module_count=len(modules[job]),observed_modules=len(vals),minimum=min(vals),median=statistics.median(vals),maximum=max(vals),aggregation='unweighted module summary; not global energy',source=src)
  if i.get('dense_fidelity'):add('numerical_fidelity',job=job,role=role,reference='original '+role+' adapter before dense conversion',dtype=None,dtype_missing_reason='not explicitly recorded in summary',source=src,**flat(i['dense_fidelity']))
  fields={'module_rank':any('rank'in m for m in modules[job]),'shape':any(m.get('shape') for m in modules[job]),'spectrum':any('spectrum_count'in m for m in modules[job]),'frobenius_error':any(any('froben' in k.lower() for k in m) for m in modules[job]),'activation_error':any('activation.relative_squared_error'in m for m in modules[job]),'dense_fidelity':bool(i.get('dense_fidelity')),'run_wall_start_end':False}
  for k,v in fields.items():add('availability',job=job,role=role,field=k,available=v,source=src,missing_reason=None if v else 'not recorded in accepted diagnostic/summary fields')
 check('accepted_full_count',len(accepted)==29,expected=29,actual=len(accepted));check('planned_interventions',len(plans)==20,expected=20,actual=len(plans))
 target={m['module']:m for m in modules.get('gsm8k-r32',[])}
 matched=modules.get('gsm8k-lora-matched-impact',[])
 check('matched_impact_module_alignment',len(matched)==144 and set(target)=={m['module'] for m in matched},target_modules=len(target),achieved_modules=len(matched))
 for job,rows in modules.items():
  check(job+'/unique_modules',len({m['module'] for m in rows})==len(rows),modules=len(rows))
  for m in rows:
   numerator=m.get('activation.squared_output_error');denominator=m.get('activation.original_update_output_energy');relative=m.get('activation.relative_squared_error')
   if numerator is not None and denominator and relative is not None:check(job+'/'+m['module']+'/activation_reproduction',abs(numerator/denominator-relative)<1e-8)
 for m in matched:
  ref=target.get(m['module'],{});check('matched_calibration/'+m['module'],m.get('calibration_sha256')==ref.get('calibration_sha256') and m.get('activation.calibration_tokens')==ref.get('activation.calibration_tokens') and m.get('calibration_source')==ref.get('calibration_source'))
 for m in modules.get('gsm8k-lora-matched-impact',[]):
  t=target.get(m['module'],{}).get('activation.relative_squared_error');v=m.get('activation.relative_squared_error');add('matched_impact_checks',job=m['job'],module=m['module'],target_job='gsm8k-r32',target=t,achieved=v,absolute_mismatch=abs(v-t) if t is not None and v is not None else None,relative_mismatch=abs(v-t)/abs(t) if t else None,units='dimensionless relative squared activation output error',method='squared_output_error / original_update_output_energy on saved calibration',source=m['source'],target_source=target.get(m['module'],{}).get('source'),missing_reason=None if t is not None and v is not None else 'measurement absent')
 short=read(D/'short-vo-validation.json');src=str(D/'short-vo-validation.json')
 symp=D.parent/'interventions-direct/gsm8k-vo-symmetry/intervention.json';sym=read(symp)
 diagnostic_code=D.parent/'short_vo_validation.py';inputs[str(diagnostic_code)]={'sha256':sha(diagnostic_code),'bytes':diagnostic_code.stat().st_size}
 check('short_vo_diagnostic_code_hash',inputs[str(diagnostic_code)]['sha256']==short.get('diagnostic_sha256'),source=str(diagnostic_code))
 for m in sym.get('modules',[]):add('symmetry_statistics',record_type='module_transform',source=str(symp),fixed_base_admissibility='unknown',**flat(m))
 for transform,rows in sym.get('layer_statistics',{}).items():
  for index,row in enumerate(rows):add('symmetry_statistics',record_type='layer_statistic',transform=transform,layer_index=index,source=str(symp),statistic_definition=sym.get('statistic_definition'),**row)
 for k in ['correlation_before','correlation_joint_base_after','correlation_fixed_base_after']:check('symmetry/'+k,short.get(k)==sym.get(k))
 for c in short['cases']:add('numerical_fidelity',job='short-vo',reference='dense reference',dtype=None,dtype_missing_reason='not recorded in validation artifact',source=src,**c)
 add('numerical_fidelity',job='short-vo-dense-conversion',reference='original DoRA adapter',source=src,**short['dense_fidelity'])
 for transform,key,rank in [('before','correlation_before',None),('joint_base','correlation_joint_base_after',short.get('joint_base_rank_preserved')),('fixed_base','correlation_fixed_base_after',None)]:add('symmetry_statistics',transform=transform,magnitude_direction_correlation=short.get(key),correlation_source_field=key,rank_admissibility='recorded_preserved' if rank else 'unknown',fixed_base_admissibility='unknown',parameters=None,parameters_missing_reason='module_transform records in this table supply saved scale parameters',fixed_base_same_rank_not_guaranteed=short.get('fixed_base_same_rank_not_guaranteed'),source=src)
 for field in ['fixed_base_rank_admissibility','dtype','allclose_tolerances']:add('availability',job='short-vo',field=field,available=False,source=src,missing_reason='not explicitly recorded in validation artifact')
 add('attempts',job='short-vo',source=src,phase='numerical_only',accepted_full=False,status=short.get('status'),wall_seconds=short.get('wall_seconds'),peak_allocated_bytes=short.get('peak_allocated_bytes'),max_process_rss_bytes=short.get('max_process_rss_bytes'),generation_calls=short.get('generation_calls'))
 for folder in ['tables','manifests','validation']:(out/folder).mkdir(parents=True,exist_ok=True)
 schemas={}
 for name,rows in tables.items():
  columns=sorted({k for r in rows for k in r});schemas[name]=columns
  with (out/'tables'/f'{name}.csv').open('w',newline='') as f:
   w=csv.DictWriter(f,fieldnames=columns);w.writeheader();w.writerows(rows)
 validation={'passed':all(c['passed'] for c in checks),'checks':checks,'table_rows':{k:len(v) for k,v in tables.items()}}
 (out/'validation/checks.json').write_text(json.dumps(validation,indent=2)+'\n')
 (out/'manifests/schemas.json').write_text(json.dumps(schemas,indent=2)+'\n')
 (out/'README.md').write_text('''# Existing diagnostic export (package C)

CPU-only, Python standard library. Accepted full runs are resolved exclusively from status.json outputs. Spectra and predictions stay on the GPU server; only compact aggregates are copied to the VM. Empty CSV fields mean unavailable, never zero. availability.csv supplies missing reasons for diagnostic categories. No quality interpretation or new uncertainty tests are produced.

Run on server (OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2):

```sh
python3 /path/to/user-user/lora-dora-profiling/analysis-preparation/2026-10-11/build_diagnostics.py --output /path/to/user-user/lora-dora-profiling/analysis-preparation/2026-10-11/03-diagnostics --check
```

resources contains accepted full runs; attempts contains other discovered summaries, error artifacts, cancellations, and the short numerical check. Coverage is the two specified job roots, not every historical campaign or controller log. Inference seconds /3600 are inference GPU-hours only. Bytes are bytes (GiB=2^30 bytes), times seconds, token rate generated tokens/inference seconds. Process maximum RSS and available_host_ram are separate measurements; neither is a campaign cost. Memory peaks are per run, never added. Wall time is missing without explicit start/end. Field names retain recorded memory/load_memory provenance.

rank_modules contains recorded module diagnostics and CPU-derived energy/ranks from saved singular values. Derived denominator is sum of squared saved spectrum per module; it is not model-global energy. rank_job_summary is unweighted min/median/max over available module values, with observed module counts. Activation error is squared output error divided by original update output energy on recorded calibration; it is not quality. matched_impact_checks joins the same module name with gsm8k-r32 and reports absolute difference and relative difference over target (undefined at zero).

numerical_fidelity preserves saved logit errors, argmax agreement and allclose flags. Short V/O cases use dense reference; dense-conversion errors use original adapter. Algebraic symmetry does not imply bitwise equivalence. symmetry_statistics exports only recorded correlations and rank flags; module_transform records retain saved scale parameters, layer_statistic records retain saved layer values; unmeasured fixed-base admissibility remains unknown. Recorded flags are not independent admissibility measurements.

Local verification without server sources: `python3 execution/analysis-preparation/build_diagnostics.py --output docs/analysis-preparation/2026-10-11/03-diagnostics --check --verify-local`.

All CSV column schemas are in manifests/schemas.json. Input hashes cover every read JSON and streamed predictions; output hashes cover tables, schemas, validation and this README. The manifest excludes its own hash. Validation checks complete/full flags, row counts, unique ordered test indices, prediction hash, accepted/planned counts, saved spectrum shape/order/nonnegativity, and energy reproduction. --check fails on any failed check.
''')
 manifest={'export_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source_roots':[str(S),str(D)],'extractor_sha256':sha(P(__file__)),'command':'python3 build_diagnostics.py --output '+str(out)+' --check','inputs':inputs,'outputs':{str(p.relative_to(out)):{'sha256':sha(p),'bytes':p.stat().st_size} for p in sorted(out.rglob('*')) if p.is_file() and p.name!='hashes.json'}}
 (out/'manifests/hashes.json').write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps({'passed':validation['passed'],'rows':validation['table_rows'],'failed':[c for c in checks if not c['passed']]}))
 if args.check and not validation['passed']:raise SystemExit(1)
if __name__=='__main__':main()
