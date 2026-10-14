"""Append actual distributed-stage transitions to HANDOFF; no GPU work."""
import os,time,json,fcntl,datetime
from pathlib import Path
P=Path('/path/to/user-user/lora-dora-profiling');D=P/'distributed-important';seen={};statefile=D/'handoff-monitor.json'
if statefile.exists():seen=json.loads(statefile.read_text()).get('seen',{})
while True:
 for lane in ['gpu0','gpu1','gpu2','gpu4','gpu5','gpu6']:
  p=D/(lane+'-state.json')
  if not p.exists():p=D/(lane+'-admission.json')
  if not p.exists():continue
  a=json.loads(p.read_text());signature=json.dumps({k:a.get(k) for k in ['status','completed_jobs','job','phase','role','error']},sort_keys=True)
  if seen.get(lane)==signature:continue
  with open('/tmp/lora-dora-series-handoff-'+str(os.getuid())+'.lock','a') as lock:
   fcntl.flock(lock,fcntl.LOCK_EX)
   text='## Distributed intervention stage: '+lane+' / '+a['status']+'\n\nUTC '+datetime.datetime.now(datetime.timezone.utc).isoformat()+'\n\nState: '+str(p)+'. External controller: '+str(P/('distributed_shared_localizations.py' if lane in ['gpu0','gpu4'] and (D/'shared-admission-policy.json').exists() else 'distributed_localizations_v2.py' if lane in ['gpu0','gpu4'] or (lane=='gpu6' and (D/'gpu6-rebalance-go.json').exists()) else 'distributed_localizations.py' if lane=='gpu6' and (D/'gpu6-localizations-go.json').exists() else 'distributed_important.py'))+'. Frozen evaluator unchanged; versions Torch2.5.1+cu121 / Transformers4.57.1 / PEFT0.17.1 / Accelerate1.11.0.\n\n```json\n'+json.dumps(a,ensure_ascii=False,indent=2)+'\n```\n\nNext: inspect failures immediately; otherwise follow lane plan.json sequentially, compare only completed matched outputs, retain assigned GPU after compute.\n\n'
   for repo in ['lora-dora-series','lora-dora-research','lora-dora-dual']:
    dest=P.parent/repo/'docs/HANDOFF.md';tmp=dest.with_suffix('.tmp.monitor');tmp.write_text(text+dest.read_text());tmp.replace(dest)
  seen[lane]=signature
 statefile.write_text(json.dumps(dict(pid=os.getpid(),seen=seen)))
 time.sleep(10)
