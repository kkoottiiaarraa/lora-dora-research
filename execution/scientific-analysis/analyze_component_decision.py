"""Frozen fidelity-budget gate, complete coverage and numerical acceptance."""
import argparse,csv,hashlib,json,math,random,statistics
from pathlib import Path

CONDITIONS=['native','remove_d','reset_m_fp32','remove_n_fp32','reset_m_rounded','remove_n_rounded']

def main(source,output):
    read=lambda n:json.loads((source/n).read_text())
    s=read('summary.json');f=read('frozen.json');rows=read('rows.json');cases=read('cases.json');controls=read('controls.json');audit=read('adapter-audit.json')
    n=8 if f['phase']=='development'else 64
    if s['status']!='complete'or len(rows)!=n*6 or len(cases)!=n or len(controls)!=17:raise ValueError('Coverage')
    if hashlib.sha256((source/'frozen.json').read_bytes()).hexdigest()!=s['frozen_sha256']:raise ValueError('Frozen changed')
    if hashlib.sha256((source/'cases.json').read_bytes()).hexdigest()!=f['cases_sha256']:raise ValueError('Cases changed')
    if not s['native_repeat_bitwise']or not s['restoration_bitwise']or not audit['exact_loaded_value_match']:raise ValueError('Controls failed')
    if audit['adapted_module_count']!=144:raise ValueError('Module coverage')
    by={}
    for r in rows:
        key=r['condition'],r['case']
        if key in by:raise ValueError('Duplicate')
        if any(not math.isfinite(v)for v in r.values()if isinstance(v,float)):raise ValueError('Nonfinite')
        if r['prompt_content_sha256']!=cases[r['case']]['prompt_content_sha256']:raise ValueError('Alignment')
        by[key]=r
    if set(by)!={(c,i)for c in CONDITIONS for i in range(n)}:raise ValueError('Cells')
    if len({c['prompt_content_sha256']for c in cases})!=n:raise ValueError('Duplicate question')
    rng=random.Random(20261014);indices=[[rng.randrange(n)for _ in range(n)]for _ in range(10000)]
    def interval(values,alpha=.05):
        samples=sorted(statistics.mean(values[i]for i in idx)for idx in indices)
        return [samples[int(10000*alpha/2)],samples[min(9999,int(10000*(1-alpha/2)))]]
    floor=max(c['rms']for c in controls);table=[]
    for c in CONDITIONS:
        kl=[by[c,i]['kl_reference_to_changed']for i in range(n)];delta=[by[c,i]['nll_difference']for i in range(n)];rms=[by[c,i]['rms']for i in range(n)]
        ci=interval(kl,alpha=.05/3);nllci=interval(delta)
        table.append(dict(condition=c,mean_kl=statistics.mean(kl),kl_simultaneous_lower=ci[0],kl_simultaneous_upper=ci[1],
          mean_nll_delta=statistics.mean(delta),nll_ci95_low=nllci[0],nll_ci95_high=nllci[1],
          mean_rms=statistics.mean(rms),min_rms=min(rms),floor_fraction=floor/min(rms)if min(rms)>0 else None,
          argmax_changes=sum(by[c,i]['argmax_disagreements']for i in range(n))))
    t={r['condition']:r for r in table};numeric_ok=all(r['floor_fraction']is not None and r['floor_fraction']<.01 for r in table if r['condition']!='native')
    threshold=f['threshold']
    if threshold!=.001:raise ValueError('Threshold changed')
    primary_dev=t['remove_d']['mean_kl']<threshold and all(t[c]['mean_kl']>threshold for c in ['reset_m_fp32','reset_m_rounded'])and numeric_ok
    secondary_dev=all(min(t['reset_m_'+ref]['mean_kl'],t['remove_n_'+ref]['mean_kl'])>threshold and min(t['reset_m_'+ref]['mean_kl'],t['remove_n_'+ref]['mean_kl'])>=10*t['remove_d']['mean_kl']for ref in ['fp32','rounded'])and numeric_ok
    confirmed=t['remove_d']['kl_simultaneous_upper']<threshold and all(t[c]['kl_simultaneous_lower']>threshold for c in ['reset_m_fp32','reset_m_rounded'])and numeric_ok if f['phase']=='validation'else False
    comp=read('radial-components.json')
    if len(comp)!=144:raise ValueError('Factor coverage')
    sums={k:sum(r[k]for r in comp)for k in ['log_l_energy','log_n_energy','log_d_energy','log_l_n_inner']}
    identity_error=abs(sums['log_d_energy']-(sums['log_l_energy']+sums['log_n_energy']+2*sums['log_l_n_inner']))
    result=dict(acceptance='PASS',phase=f['phase'],cases=n,rows=len(rows),primary_development_gate=primary_dev,secondary_development_gate=secondary_dev,
      advance_to_validation=(primary_dev or secondary_dev)if f['phase']=='development'else False,primary_confirmation=confirmed,
      numerical_controls_pass=numeric_ok,max_control_rms=floor,table=table,log_factor_energies=sums,
      log_factor_identity_absolute_error=identity_error,log_l_n_cosine=sums['log_l_n_inner']/math.sqrt(sums['log_l_energy']*sums['log_n_energy']),
      log_d_to_separate_energy_ratio=sums['log_d_energy']/(sums['log_l_energy']+sums['log_n_energy']),
      versions=s['versions'],source_sha256=f['source_sha256'],artifacts=f['artifacts'],cases_sha256=f['cases_sha256'],frozen_sha256=s['frozen_sha256'],
      wall_seconds=s['wall_seconds'],peak_rss_bytes=s['peak_rss_bytes'],gpu_hours=0,accuracy_measured=False,training_cause_identified=False,
      existing_paper_proxy_use_demonstrated=False)
    if f['phase']=='validation':
        if read('case-audit.json')['status']!='PASS':raise ValueError('Independent case audit missing')
        result['case_audit']=read('case-audit.json')
    output.mkdir(parents=True,exist_ok=True)
    (output/'validation.json').write_text(json.dumps(result,indent=2)+'\n')
    with (output/'conditions.csv').open('w',newline='')as out:
        w=csv.DictWriter(out,fieldnames=list(table[0]));w.writeheader();w.writerows(table)
    print(json.dumps(result,indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--source',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();main(a.source,a.output)
