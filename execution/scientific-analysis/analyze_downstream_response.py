"""Validate and summarize the frozen exploratory downstream response screen."""
import argparse,csv,hashlib,json,math,random,statistics
from pathlib import Path


def main(source,output):
    read=lambda n:json.loads((source/n).read_text())
    summary=read('summary.json');rows=read('rows.json');controls=read('controls.json')
    dense=read('native-dense-controls.json');frozen=read('frozen-calibration.json');cases=read('cases.json')
    if summary['status']!='complete' or len(rows)!=96 or len(controls)!=18 or len(dense)!=4:raise ValueError('Coverage')
    if hashlib.sha256((source/'frozen-calibration.json').read_bytes()).hexdigest()!=summary['frozen_calibration_sha256']:raise ValueError('Calibration changed')
    if hashlib.sha256((source/'cases.json').read_bytes()).hexdigest()!=summary['cases_sha256']:raise ValueError('Cases changed')
    if hashlib.sha256(json.dumps(cases[8:],sort_keys=True).encode()).hexdigest()!=frozen['evaluation_cases_sha256']:raise ValueError('Evaluation changed')
    if frozen['fit_count']!=8 or frozen['evaluation_count']!=16 or frozen['fit_targets_used']:raise ValueError('Fitting scope')
    if frozen['source_sha256']!=summary['source_sha256']:raise ValueError('Sources changed')
    by={}
    for r in rows:
        key=(r['layer'],r['mode'],r['case'])
        if key in by:raise ValueError('Duplicate')
        if any(not math.isfinite(v)for v in r.values()if isinstance(v,float)):raise ValueError('Nonfinite')
        if r['prompt_content_sha256']!=cases[r['case']+8]['prompt_content_sha256']:raise ValueError('Alignment')
        if r['frozen_kl']<=0 or r['actual_kl']<0:raise ValueError('Invalid KL')
        if abs(r['attenuation']-(1-math.sqrt(r['actual_kl']/r['frozen_kl'])))>1e-12:raise ValueError('Attenuation formula')
        by[key]=r
    if set(by)!={(l,m,i)for l in [0,17,35]for m in ['remove','gain']for i in range(16)}:raise ValueError('Cells')
    if not all(r['bitwise']for r in controls if r['kind']in ['repeat','restoration']):raise ValueError('Restoration')
    floor=max(r['rms']for r in dense+controls)
    rng=random.Random(20261014)
    bootindices=[[rng.randrange(16)for _ in range(16)]for _ in range(10000)]
    def ci(values):
        b=sorted(statistics.mean(values[i]for i in idx)for idx in bootindices)
        return [b[250],b[9749]]
    table=[]
    for l in [0,17,35]:
        a=[by[l,'remove',i]for i in range(16)];b=[by[l,'gain',i]for i in range(16)]
        diff=[x['attenuation']-y['attenuation']for x,y in zip(a,b)]
        interval=ci(diff);mean=statistics.mean(diff)
        ratios=[r['dose_energy_ratio']for r in a]
        floor_fraction=max(floor/r[k]for r in a+b for k in ['actual_rms','frozen_rms'])
        numeric_ok=floor_fraction<.01;dose_ok=min(ratios)>=.5 and max(ratios)<=2
        row=dict(layer=l,remove_mean_attenuation=statistics.mean(r['attenuation']for r in a),
          gain_mean_attenuation=statistics.mean(r['attenuation']for r in b),difference=mean,
          ci95_low=interval[0],ci95_high=interval[1],remove_mean_actual_kl=statistics.mean(r['actual_kl']for r in a),
          remove_mean_frozen_kl=statistics.mean(r['frozen_kl']for r in a),gain_mean_actual_kl=statistics.mean(r['actual_kl']for r in b),
          gain_mean_frozen_kl=statistics.mean(r['frozen_kl']for r in b),
          remove_mean_source_denominator_kl=statistics.mean(r['frozen_source_denominator_kl']for r in a),
          remove_mean_counteraction=statistics.mean(r['residual_counteraction']for r in a),
          dose_ratio_min=min(ratios),dose_ratio_max=max(ratios),numeric_floor_fraction=floor_fraction,
          dose_ok=dose_ok,numeric_ok=numeric_ok,
          passed_gate=mean>=.25 and interval[0]>0 and numeric_ok and dose_ok)
        table.append(row)
    result=dict(acceptance='PASS',exploratory=True,passed_gate=sum(r['passed_gate']for r in table)>=2,
      matched_layers=sum(r['passed_gate']for r in table),cases=16,rows=96,layers=table,
      control_floor_rms=floor,max_branch_partition_relative=max(r['branch_partition_relative']for r in rows),
      max_branch_partition_abs=max(r['branch_partition_max_abs']for r in rows),
      wall_seconds=summary['wall_seconds'],peak_rss_bytes=summary['peak_rss_bytes'],gpu_hours=0,
      versions=summary['versions'],source_sha256=summary['source_sha256'],
      cases_sha256=summary['cases_sha256'],frozen_calibration_sha256=summary['frozen_calibration_sha256'],
      independent_confirmation=False,accuracy_measured=False,training_mechanism_identified=False)
    output.mkdir(parents=True,exist_ok=True)
    (output/'validation.json').write_text(json.dumps(result,indent=2)+'\n')
    with (output/'layers.csv').open('w',newline='')as f:
        w=csv.DictWriter(f,fieldnames=list(table[0]));w.writeheader();w.writerows(table)
    (output/'manifest.json').write_text(json.dumps({'artifacts':{p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in output.iterdir()if p.is_file()and p.name!='manifest.json'}},indent=2)+'\n')
    print(json.dumps(result,indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--source',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();main(a.source,a.output)
