"""Accept the prespecified published-trajectory screen without outcome fitting."""
import argparse,csv,hashlib,json,math,random,statistics
from pathlib import Path


def main(source,output):
    read=lambda n:json.loads((source/n).read_text())
    s=read('summary.json');rows=read('rows.json');controls=read('controls.json');f=read('frozen.json');cases=read('cases.json')
    if s['status']!='complete' or len(rows)!=144 or len(controls)!=6 or len(cases)!=16:raise ValueError('Coverage')
    if not s['repeat_bitwise']or not s['restoration_bitwise']or not s['adapter_exact']:raise ValueError('Control failure')
    for k in ['source_sha256','cases_sha256','provenance_sha256']:
        if f[k]!=s[k]:raise ValueError('Frozen changed')
    if hashlib.sha256((source/'cases.json').read_bytes()).hexdigest()!=s['cases_sha256']:raise ValueError('Cases changed')
    if len({c['prompt_content_sha256']for c in cases})!=16:raise ValueError('Duplicate prompts')
    by={}
    for r in rows:
        key=r['step'],r['condition'],r['case']
        if key in by:raise ValueError('Duplicate row')
        if r['prompt_content_sha256']!=cases[r['case']]['prompt_content_sha256']:raise ValueError('Alignment')
        if any(not math.isfinite(x)for x in r.values()if isinstance(x,float)):raise ValueError('Nonfinite')
        by[key]=r
    if set(by)!={(t,c,i)for t in [64,512,1024]for c in ['native','remove_d','base_magnitude']for i in range(16)}:raise ValueError('Cell coverage')
    for step in [64,512,1024]:
        a=read(f'adapter-audit-{step}.json')
        if not a['exact_loaded_value_match']or a['saved_tensor_count']!=588 or a['adapted_module_count']!=196:raise ValueError('Loaded state')
        for cond in ['remove_d','base_magnitude']:
            for i in range(16):
                if by[step,cond,i]['native_to_base_kl']!=by[step,'native',i]['native_to_base_kl']:raise ValueError('Reference changed')
    mean=lambda t,c,k:statistics.mean(by[t,c,i][k]for i in range(16))
    table=[];floor=max(r['rms']for r in controls)
    for step in [64,512,1024]:
        base=mean(step,'native','native_to_base_kl')
        for condition in ['remove_d','base_magnitude']:
            kl=mean(step,condition,'kl_reference_to_changed');effect=min(by[step,condition,i]['rms']for i in range(16))
            table.append(dict(step=step,condition=condition,mean_kl=kl,native_to_base_kl=base,normalized_role=kl/base if base>0 else None,
              mean_nll_delta=mean(step,condition,'nll_difference'),floor_fraction=floor/effect if effect>0 else None))
    rng=random.Random(20261014);logs=[]
    def role(t,idx):
        num=statistics.mean(by[t,'remove_d',i]['kl_reference_to_changed']for i in idx)
        den=statistics.mean(by[t,'native',i]['native_to_base_kl']for i in idx)
        if num<=0 or den<=0:raise ValueError('Degenerate normalization')
        return num/den
    for _ in range(10000):
        idx=[rng.randrange(16)for _ in range(16)];logs.append(math.log(role(64,idx)/role(1024,idx)))
    logs.sort();interval=[logs[250],logs[9749]];fold=role(64,list(range(16)))/role(1024,list(range(16)))
    floor_ok=all(r['floor_fraction']is not None and r['floor_fraction']<.01 for r in table)
    floor_ok=floor_ok and all(floor/by[t,'native',i]['native_to_base_rms']<.01 for t in [64,512,1024]for i in range(16))
    primary=fold>=2 and interval[0]>0 and mean(64,'remove_d','kl_reference_to_changed')>=1e-3 and floor_ok
    opposite=fold<=.5 and interval[1]<0 and mean(1024,'remove_d','kl_reference_to_changed')>=1e-3 and floor_ok
    result=dict(acceptance='PASS',exploratory=True,primary_transient_gate=primary,opposite_growth_gate=opposite,
      early_to_late_normalized_role_fold=fold,log_fold_ci95=interval,numeric_floor_ok=floor_ok,control_floor_rms=floor,
      cases=16,rows=144,table=table,wall_seconds=s['wall_seconds'],peak_rss_bytes=s['peak_rss_bytes'],gpu_hours=0,
      versions=s['versions'],cases_sha256=s['cases_sha256'],source_sha256=s['source_sha256'],provenance_sha256=s['provenance_sha256'],
      independent_seed_replication=False,training_causality_identified=False,benchmark_accuracy_measured=False)
    output.mkdir(parents=True,exist_ok=True)
    (output/'validation.json').write_text(json.dumps(result,indent=2)+'\n')
    with (output/'trajectory.csv').open('w',newline='')as out:
        w=csv.DictWriter(out,fieldnames=list(table[0]));w.writeheader();w.writerows(table)
    print(json.dumps(result,indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--source',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();main(a.source,a.output)
