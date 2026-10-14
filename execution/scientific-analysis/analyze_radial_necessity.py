#!/usr/bin/env python3
"""Accept the fixed development gate without fitting or significance fishing."""
import argparse
import collections
import csv
import hashlib
import json
import math
from pathlib import Path
import statistics


def main(source,output):
    summary=json.loads((source/'summary.json').read_text());frozen=json.loads((source/'frozen.json').read_text())
    if summary['status']!='complete' or summary['rows']!=448 or not summary['numerical_controls_pass']:
        raise ValueError('Incomplete/invalid development gate')
    for key in ['source_sha256','cases_sha256','source_data_sha256','provenance_sha256','protocol_sha256','data_audit_sha256']:
        if frozen[key]!=summary[key]:raise ValueError('Frozen protocol changed')
    rows=[json.loads(s) for s in (source/'per-case.jsonl').read_text().splitlines()]
    by=collections.defaultdict(dict)
    for row in rows:
        if row['case'] in by[row['condition']]:raise ValueError('Duplicate case')
        if any(not math.isfinite(row[k]) for k in ['changed_nll','reference_nll','nll_difference','rms','kl_reference_to_changed']):raise ValueError('Invalid metric')
        if row['correct']!=(row['prediction']==row['gold_id']):raise ValueError('Correctness mismatch')
        by[row['condition']][row['case']]=row
    conditions=['dora','remove_d','base_magnitude','learned_only','scalar_d','centered_d','lora']
    if set(by)!=set(conditions) or len(rows)!=448:raise ValueError('Condition coverage')
    native=by['dora'];quality=[];contrasts=[]
    if len({r['request_sha256'] for r in native.values()})!=64:raise ValueError('Requests not unique')
    for condition in conditions:
        values=by[condition]
        if set(values)!=set(range(64)):raise ValueError('Case coverage')
        for i,r in values.items():
            if any(r[k]!=native[i][k] for k in ['case_sha256','request_sha256','gold_id','source_row']):raise ValueError('Inputs not aligned')
            if abs(r['reference_nll']-native[i]['changed_nll'])>1e-12:raise ValueError('Wrong reference')
        quality.append(dict(condition=condition,cases=64,correct=sum(r['correct'] for r in values.values()),
            accuracy_percent=100*statistics.mean(r['correct'] for r in values.values()),invalid=sum(not r['valid_prediction'] for r in values.values()),
            mean_nll=statistics.mean(r['changed_nll'] for r in values.values()),mean_nll_delta=statistics.mean(r['nll_difference'] for r in values.values()),
            mean_kl=statistics.mean(r['kl_reference_to_changed'] for r in values.values()),mean_rms=statistics.mean(r['rms'] for r in values.values())))
        gains=sum(not native[i]['correct'] and values[i]['correct'] for i in range(64))
        losses=sum(native[i]['correct'] and not values[i]['correct'] for i in range(64))
        contrasts.append(dict(condition=condition,gains=gains,losses=losses,net_correct_loss=losses-gains,correctness_discordant=gains+losses,
            prediction_changes=sum(native[i]['prediction']!=values[i]['prediction'] for i in range(64)),
            primary_gate_eligible=condition in ['remove_d','base_magnitude'],
            passed_gate=condition in ['remove_d','base_magnitude'] and (losses-gains>=4 or gains+losses>=8)))
        old=next(c for c in summary['conditions'] if c['condition']==condition)
        if old['correct']!=quality[-1]['correct'] or abs(old['mean_nll']-quality[-1]['mean_nll'])>1e-12:raise ValueError('Summary differs from rows')
    gates=[r for r in contrasts if r['primary_gate_eligible']]
    for old,new in zip(summary['gates'],gates):
        if any(old[k]!=new[k] for k in ['condition','net_correct_loss','correctness_discordant']) or old['passed']!=new['passed_gate']:
            raise ValueError('Worker gate disagrees')
    controls=json.loads((source/'controls.json').read_text())
    if len(controls)!=8:raise ValueError('Control coverage')
    effect=next(q['mean_rms'] for q in quality if q['condition']=='remove_d');floor=max(r['rms'] for r in controls)
    if floor>=.01*effect:raise ValueError('Numeric floor too high')
    if len(json.loads((source/'radial-components.json').read_text()))!=128:raise ValueError('Radial module coverage')
    for role,tensors in [('lora',256),('dora',384)]:
        a=json.loads((source/(role+'-adapter-audit.json')).read_text())
        if not a['exact_loaded_value_match'] or a['saved_tensor_count']!=tensors or a['adapted_module_count']!=128:
            raise ValueError('Adapter not accepted')
    output.mkdir(parents=True,exist_ok=True)
    for name,records in [('quality.csv',quality),('contrasts.csv',contrasts)]:
        with (output/name).open('w',newline='') as f:
            w=csv.DictWriter(f,fieldnames=list(records[0]));w.writeheader();w.writerows(records)
    result=dict(acceptance='PASS',cases=64,unique_requests=64,rows=448,gates=gates,passed_gate=any(r['passed_gate'] for r in gates),
        max_control_rms=floor,remove_d_mean_rms=effect,numeric_floor_fraction=floor/effect,
        native_repeat_bitwise=summary['native_repeat_bitwise'],restoration_bitwise=summary['restoration_bitwise'],
        versions=summary['versions'],source_sha256=summary['source_sha256'],cases_sha256=summary['cases_sha256'],
        source_data_sha256=summary['source_data_sha256'],provenance_sha256=summary['provenance_sha256'],
        wall_seconds=summary['wall_seconds'],peak_rss_bytes=summary['peak_rss_bytes'],cpu_threads=8,gpu_hours=0,
        exploratory=True,predictor_tested=False,independent_test_evaluated=False,equivalence_proven=False,training_mechanism_identified=False,
        quality=quality,contrasts=contrasts)
    (output/'validation.json').write_text(json.dumps(result,indent=2)+'\n')
    (output/'manifest.json').write_text(json.dumps(dict(artifacts={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in output.iterdir() if p.is_file() and p.name!='manifest.json'}),indent=2)+'\n')
    print(json.dumps(dict(acceptance='PASS',gates=gates,quality=quality,wall_seconds=summary['wall_seconds'])))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--source',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();main(a.source,a.output)
