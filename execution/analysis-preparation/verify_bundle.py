#!/usr/bin/env python3
"""Sequential offline stdlib bundle acceptance; no source/server access."""
import argparse,csv,datetime,gzip,hashlib,json,os,pathlib,subprocess,sys
P=pathlib.Path
PACKAGES={
 '01-corpus-quality':('build_corpus_quality.py',['--out','{out}','--verify-only'],'validation/integrity.json','manifests/export.json',['attempts.csv','run_inventory.csv','coverage.csv','comparability.csv','baseline_metrics.csv','baseline_contrasts.csv','mmlu_subject_metrics.csv','gsm8k_scorer_agreement.csv','gsm8k_token_limits.csv','baseline_pair_transitions.csv','squadv2_answerability.csv']),
 '02-interventions':('build_interventions.py',['--output','{out}','--check'],'validation/checks.json','manifests/export.json',['intervention_metrics.csv','paired_transitions.csv','localization_grid.csv','localization_interactions.csv','numerical_control_contrasts.csv','per_example_scores.csv.gz']),
 '03-diagnostics':('build_diagnostics.py',['--output','{out}','--check','--verify-local'],'validation/checks.json','manifests/hashes.json',['rank_modules.csv','rank_job_summary.csv','matched_impact_checks.csv','numerical_fidelity.csv','symmetry_statistics.csv','resources.csv','attempts.csv','availability.csv'])}
def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(262144),b''):h.update(b)
 return h.hexdigest()
def load(p):
 with open(p) as f:return json.load(f)
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--root',type=P,default=P(__file__).resolve().parents[2]);parser.add_argument('--bundle',default='docs/analysis-preparation/2026-10-11');parser.add_argument('--build-manifest',action='store_true',help='Snapshot only after package finalization; always runs acceptance first');a=parser.parse_args();root=a.root.resolve();R=root/a.bundle;report={'checked_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'passed':False,'offline':True,'packages':{},'errors':[]}
 def need(ok,message):
  if not ok:raise ValueError(message)
 try:
  for file in ('README.md','SPEC.md'):need((R/file).is_file(),'missing '+file)
  need((root/'MEMORY.md').is_file(),'missing MEMORY.md');need((root/'AGENTS.md').is_file(),'missing AGENTS.md')
  for package,(builder,flags,validation,manifest,mandatory) in PACKAGES.items():
   out=R/package;need((out/'README.md').is_file(),'missing package README '+package)
   for name in mandatory:need((out/'tables'/name).is_file(),'missing table '+package+'/'+name)
   v=load(out/validation);need(v.get('passed') is True or v.get('status')=='passed','package validation failed '+package)
   for check in v.get('checks',[]):need(check.get('passed') is True,'failed declared check '+package+'/'+str(check.get('name')))
   for check in v.get('alignments',[]):need(check.get('status')=='passed','failed alignment '+package)
   m=load(out/manifest);expected_hash=m.get('extractor_sha256',m.get('extractor',{}).get('sha256'));need(expected_hash==sha(root/'execution/analysis-preparation'/builder),'extractor hash mismatch '+builder)
   outputs=m['outputs'];items=outputs.items() if isinstance(outputs,dict) else ((i['path'],i) for i in outputs)
   for path,item in items:need(sha(out/path)==item['sha256'],'package output hash mismatch '+package+'/'+path)
   for p in sorted(out.rglob('*.json')):load(p)
   counts={}
   for name,n in v['table_rows'].items():
    name=name if '.csv' in name else name+'.csv';p=out/'tables'/name;opener=gzip.open if name.endswith('.gz') else open
    with opener(p,'rt',newline='') as f:
     reader=csv.DictReader(f);need(bool(reader.fieldnames),'empty schema '+str(p));counts[name]=sum(1 for _ in reader)
    need(counts[name]==n,'row count mismatch '+package+'/'+name)
   if package=='01-corpus-quality':
    need(counts['run_inventory.csv']==29 and counts['comparability.csv']==29,'A expected corpus/contrast counts')
    need(any(c['name']=='expected_counts' and c['passed'] for c in v['checks']),'missing A expected counts check')
   elif package=='02-interventions':
    need(v['accepted_gsm8k_runs']==23 and v['intervention_contrasts']==20,'B expected counts')
    need(sorted(x['contrasts'] for x in v['family_sizes'].values())==[3,8,9],'B family sizes')
    need(v['interaction_four_run_alignments']==4,'B four-run alignments')
    for name,n in {'intervention_metrics.csv':40,'paired_transitions.csv':40,'localization_grid.csv':28,'localization_interactions.csv':8,'numerical_control_contrasts.csv':12,'per_example_scores.csv.gz':60674}.items():need(counts[name]==n,'B mandatory count '+name)
   else:need(counts['resources.csv']==29,'C expected resource count');need((out/'manifests/schemas.json').is_file(),'C schema missing')
   command=[sys.executable,str(root/'execution/analysis-preparation'/builder)]+[x.format(out=str(out)) for x in flags]
   env=os.environ.copy();env.update({k:'1' for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS')})
   result=subprocess.run(command,capture_output=True,text=True,env=env)
   need(result.returncode==0,'offline package verifier failed '+package+': '+result.stdout+result.stderr)
   report['packages'][package]={'passed':True,'command':command,'stdout':result.stdout.strip(),'table_rows':counts}
  excluded={R/'manifests/bundle.json',R/'validation/bundle.json'}
  paths=sorted({p for p in R.rglob('*') if p.is_file() and p not in excluded}|{root/'MEMORY.md',root/'AGENTS.md'}|set((root/'execution/analysis-preparation').glob('*.py')))
  files=[{'path':str(p.relative_to(root)),'sha256':sha(p),'bytes':p.stat().st_size} for p in paths]
  manifest_path=R/'manifests/bundle.json'
  if a.build_manifest:
   manifest_path.parent.mkdir(parents=True,exist_ok=True);manifest_path.write_text(json.dumps({'created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'path_base':'repository root','scope':'all files in bundle directory, MEMORY.md, AGENTS.md and analysis-preparation Python extractors/verifier','excluded':['docs/analysis-preparation/2026-10-11/manifests/bundle.json','docs/analysis-preparation/2026-10-11/validation/bundle.json'],'files':files},indent=2)+'\n')
  saved=load(manifest_path);need(saved['files']==files,'bundle files/hash/size mismatch; rebuild only after authorized finalization')
  report['attempts_scopes']={'01-corpus-quality':{'rows':report['packages']['01-corpus-quality']['table_rows']['attempts.csv'],'scope':'32 nonselected full/smoke directories in the two job roots'},'03-diagnostics':{'rows':report['packages']['03-diagnostics']['table_rows']['attempts.csv'],'scope':'35 discovered summaries/error artifacts/cancellations/short numerical check in specified diagnostic coverage'},'interpretation':'Expected distinct scopes, not a deduplicated or complete campaign total'}
  need(report['attempts_scopes']['01-corpus-quality']['rows']==32 and report['attempts_scopes']['03-diagnostics']['rows']==35,'expected distinct attempts counts')
  report.update(passed=True,verified_files=len(files),total_bytes=sum(r['bytes'] for r in files),bundle_manifest_sha256=sha(manifest_path))
 except (OSError,ValueError,KeyError,AssertionError) as error:report['errors'].append(str(error))
 (R/'validation').mkdir(parents=True,exist_ok=True);(R/'validation/bundle.json').write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps({'passed':report['passed'],'verified_files':report.get('verified_files'),'errors':report['errors']}));return 0 if report['passed'] else 1
if __name__=='__main__':sys.exit(main())
