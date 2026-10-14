#!/usr/bin/env python3
"""Analyze fixed completed runs on CPU, without loading model weights.

Raw inputs stay outside Git. Only anonymous IDs, hashes and aggregate results
are exported. CIs are paired normal intervals, not training-seed uncertainty.
"""
import argparse
import collections
import csv
import hashlib
import json
import math
from pathlib import Path
import random
import statistics
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from lora_dora_study.benchmarks import score, normalize_span
from lora_dora_study.evaluation import clean_generated


def digest(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def exact_mcnemar(wins, losses):
    n = wins + losses
    if not n:
        return 1.0
    logs = [math.lgamma(n+1)-math.lgamma(i+1)-math.lgamma(n-i+1)-n*math.log(2)
            for i in range(min(wins, losses)+1)]
    peak = max(logs)
    return min(1.0, 2*math.exp(peak)*sum(math.exp(x-peak) for x in logs))


def interval(values, z=1.959963984540054):
    m = statistics.mean(values)
    se = statistics.stdev(values)/math.sqrt(len(values))
    return m, m-z*se, m+z*se, se


def holm(rows, field='p_exact'):
    ordered = sorted(rows, key=lambda r: r[field])
    running = 0
    for i, r in enumerate(ordered):
        running = max(running, (len(rows)-i)*r[field])
        r['holm_p'] = min(1, running)


def write_csv(path, rows):
    fields = list(dict.fromkeys(k for r in rows for k in r))
    with open(path, 'w') as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--inputs', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    a = ap.parse_args()
    a.out.mkdir(parents=True, exist_ok=True)
    gold = json.load(open(a.inputs/'gold.json'))
    summaries, runs, hashes, audit, means = {}, {}, {'gold.json':digest(a.inputs/'gold.json')}, [], []
    task_for = lambda label: 'squadv2' if label.startswith(('squad_', 'squadv2_')) else 'mmlu' if label.startswith('mmlu_') else 'gsm8k'
    for folder in sorted(a.inputs.iterdir()):
        if not folder.is_dir():
            continue
        label = folder.name
        s = json.load(open(folder/'summary.json'))
        summaries[label] = s
        for name in ['summary.json', 'predictions.jsonl', 'calibration.json']:
            if (folder/name).exists():
                hashes[f'{label}/{name}'] = digest(folder/name)
        assert s['status'] == 'complete' and s['full_evaluation']
        if label.startswith('text_'):
            continue
        task = task_for(label)
        data = []
        for i, line in enumerate(open(folder/'predictions.jsonl')):
            row = json.loads(line)
            assert row['test_row_index'] == i
            computed = score(task, row['text'], gold[task][i])
            assert all(math.isfinite(v) and abs(v-computed[k]) < 1e-10 for k,v in row['metrics'].items()), (label,i)
            row['answerable'] = any(normalize_span(x) for x in gold[task][i]['answers']['text']) if task == 'squadv2' else None
            text = row.pop('text')
            row['text_hash'] = hashlib.sha256(text.encode()).hexdigest()
            row['degenerate'] = bool(len(text)>30 and (text.count('!')/len(text)>.8 or len(set(text.strip()))<3))
            row['empty'] = not text.strip()
            if task == 'squadv2':
                cleaned = clean_generated(text)
                abstains = cleaned.lower() in {'unanswerable','no answer','n/a','none',''}
                row['outcome'] = 'correct' if computed['exact'] else 'false_abstention' if row['answerable'] and abstains else 'wrong_span' if row['answerable'] else 'false_answer'
            data.append(row)
        assert len(data) == len(gold[task]) == s['predictions_completed']
        if s.get('predictions_sha256'):
            assert s['predictions_sha256'] == hashes[f'{label}/predictions.jsonl']
        for metric in data[0]['metrics']:
            avg = statistics.mean(r['metrics'][metric] for r in data)
            assert abs(avg-s['metrics'][metric]) < 1e-10
            means.append(dict(run=label, task=task, metric=metric, n=len(data), mean=avg))
        audit.append(dict(run=label,n=len(data),rescored=True,degenerate=sum(r['degenerate'] for r in data),empty=sum(r['empty'] for r in data),token_limit=sum(r.get('hit_token_limit',r['generated_tokens']>=s['dataset']['max_new_tokens']) for r in data),truncated=sum(r['prompt_truncated'] for r in data)))
        runs[label] = data

    comparisons = []
    compatibility = []
    def compare(left, right, metric, family, subset='all'):
        x,y = runs[left],runs[right]
        assert len(x)==len(y)
        for u,v in zip(x,y):
            for key in ['test_row_index','source_id','prompt_sha256','input_ids_sha256','input_tokens','prompt_truncated']:
                assert u[key]==v[key], (left,right,key,u['test_row_index'])
        sx,sy = summaries[left],summaries[right]
        assert sx['versions']==sy['versions']
        for k in ['revision','jsonl_sha256','max_new_tokens','max_input_tokens']:
            assert sx['dataset'][k]==sy['dataset'][k], (left,right,k)
        for role in ['base','dora']:
            assert sx['artifacts'][role]['revision']==sy['artifacts'][role]['revision']
        common = set(sx['source_sha256']) & set(sy['source_sha256'])
        assert all(sx['source_sha256'][k]==sy['source_sha256'][k] for k in common)
        # max_new_tokens is passed explicitly at generation in the new runner.
        gx,gy = sx['generation_config'],sy['generation_config']
        assert all(gx[k]==gy[k] for k in gx if k in gy and k not in ['max_new_tokens'])
        compatibility.append(dict(left=left,right=right,prompt_and_token_hashes_equal=True,versions_equal=True,shared_source_hashes_equal=True,dataset_and_revisions_equal=True))
        ids=[i for i in range(len(x)) if subset=='all' or x[i]['answerable']==(subset=='answerable')]
        diffs=[x[i]['metrics'][metric]-y[i]['metrics'][metric] for i in ids]
        m,lo,hi,se=interval(diffs)
        binary=all(x[i]['metrics'][metric] in [0,1] and y[i]['metrics'][metric] in [0,1] for i in ids)
        r=dict(left=left,right=right,metric=metric,family=family,subset=subset,n=len(ids),left_mean=statistics.mean(x[i]['metrics'][metric] for i in ids),right_mean=statistics.mean(y[i]['metrics'][metric] for i in ids),difference=m,ci95_low=lo,ci95_high=hi,se=se,ci_method='paired normal; conditional on checkpoint')
        if binary:
            r.update(wins=sum(v>0 for v in diffs),losses=sum(v<0 for v in diffs))
            r['p_exact']=exact_mcnemar(r['wins'],r['losses'])
        if task_for(left)=='squadv2':
            groups=collections.defaultdict(list)
            for i,d in zip(ids,diffs):groups[gold['squadv2'][i]['context_sha256']].append(d)
            g=len(groups)
            cse=math.sqrt(g/(g-1)*sum((sum(v)-m*len(v))**2 for v in groups.values()))/len(ids)
            r.update(context_groups=g,context_ci95_low=m-1.95996398454*cse,context_ci95_high=m+1.95996398454*cse)
        comparisons.append(r)
        return r

    primary=[]
    for kind in ['permuted','directional']:
        r=compare('gsm8k-remove_d-all_dora',kind,'final_em','A_primary_Holm2')
        z=statistics.NormalDist().inv_cdf(.9875)
        r.update(simultaneous_ci95_low=r['difference']-z*r['se'],simultaneous_ci95_high=r['difference']+z*r['se'])
        primary.append(r)
        compare('gsm8k-remove_d-all_dora',kind,'author_em','A_scorer_sensitivity')
        compare(kind,'gsm8k_dora','final_em','A_secondary_vs_original')
    holm(primary)
    holm([r for r in comparisons if r['family']=='A_scorer_sensitivity'])
    compare('gsm8k-remove_d-all_dora','gsm8k_dora','final_em','historical_anchor')
    compare('mmlu_remove','mmlu_dora','accuracy','B_transfer')
    for subset in ['all','answerable','unanswerable']:
        for metric in ['exact','f1']:compare('squad_remove','squadv2_dora',metric,'B_transfer_exploratory',subset)
    # This two-endpoint family is an analysis-time sensitivity, not a claim
    # that an unspecified pre-run family was preregistered.
    b_binary=[r for r in comparisons if r['subset']=='all' and r['family'].startswith('B_') and r['metric'] in ['accuracy','exact']]
    holm(b_binary)
    for r in b_binary:r['holm_family_note']='exploratory joint MMLU accuracy / SQuAD exact sensitivity'

    churn=[]
    for kind in ['gsm8k-remove_d-all_dora','permuted','directional']:
        original=runs['gsm8k_dora']; changed=runs[kind]
        flips={i for i,(x,y) in enumerate(zip(original,changed)) if x['metrics']['final_em']!=y['metrics']['final_em']}
        rem={i for i,(x,y) in enumerate(zip(original,runs['gsm8k-remove_d-all_dora'])) if x['metrics']['final_em']!=y['metrics']['final_em']}
        churn.append(dict(run=kind,n=len(original),changed_texts=sum(x['text_hash']!=y['text_hash'] for x,y in zip(original,changed)),correctness_flips=len(flips),flips_shared_with_remove_d=len(flips&rem),flips_union_with_remove_d=len(flips|rem)))
    outcomes=collections.Counter((x['answerable'],x['outcome'],y['outcome']) for x,y in zip(runs['squadv2_dora'],runs['squad_remove']))
    outcome_rows=[dict(answerable=k[0],original_outcome=k[1],remove_d_outcome=k[2],n=v) for k,v in sorted(outcomes.items())]

    calibration=[]
    c1=json.load(open(a.inputs/'permuted/calibration.json'))
    c2=json.load(open(a.inputs/'directional/calibration.json'))
    assert c1==c2, 'Calibration changed between runs'
    assert c1['full_calibration'] and c1['train_count']==200 and c1['validation_count']==32
    assert c1['train_content_sha256']!=c1['validation_content_sha256']
    for split in ['refinement','validation']:
        for name,v in c1[split]['modules'].items():
            for kind in ['permuted','directional']:
                calibration.append(dict(split=split,module=name,kind=kind,native_remove_energy=v['native_remove'],realized_energy=v['realized'][kind],energy_ratio=v['realized'][kind]/v['native_remove'],ideal_vs_native_relative_rms=v['radial_vs_native_remove_relative_rms'],applied_scale=c1[split]['applied_scales'][kind][name]))

    nll=[];nll_diffs=[]
    for cond in ['base','lora','dora','remove_d']:
        s=summaries['text_'+cond];n=s['nll'];segments=n['per_segment']
        assert s['versions']==summaries['gsm8k_dora']['versions']
        for role in ['base','lora','dora']:
            assert s['artifacts'][role]['revision']==summaries['gsm8k_'+role]['artifacts'][role]['revision']
        assert len(segments)==1024 and all(r['index']==i and r['token_count']==255 and math.isfinite(r['mean_nll']) for i,r in enumerate(segments))
        assert abs(sum(r['summed_nll'] for r in segments)-n['summed_nll'])<1e-6
        assert abs(n['mean_nll']-n['summed_nll']/n['token_count'])<1e-12
        for key in ['corpus_file_sha256','actual_segments_sha256','corpus_metadata']:
            assert s[key]==summaries['text_base'][key]
        nll.append(dict(condition=cond,n_segments=1024,n_tokens=n['token_count'],mean_nll=n['mean_nll'],perplexity=math.exp(n['mean_nll'])))
    for left,right in [('remove_d','dora'),('dora','lora'),('dora','base')]:
        diffs=[x['mean_nll']-y['mean_nll'] for x,y in zip(summaries['text_'+left]['nll']['per_segment'],summaries['text_'+right]['nll']['per_segment'])]
        m,lo,hi,se=interval(diffs)
        r=dict(left=left,right=right,difference=m,ci95_low_iid_segments=lo,ci95_high_iid_segments=hi,perplexity_relative_change=math.expm1(m),segments_worse=sum(x>0 for x in diffs))
        # Adjacent segments share documents: report sensitivity with contiguous
        # nonoverlapping blocks, never pretend tokens/segments are independent.
        for size in [8,16,32]:
            blocks=[statistics.mean(diffs[i:i+size]) for i in range(0,len(diffs),size)]
            rng=random.Random(20261012+size)
            boot=sorted(statistics.mean(rng.choices(blocks,k=len(blocks))) for _ in range(10000))
            r[f'block{size}_ci95_low']=boot[250]
            r[f'block{size}_ci95_high']=boot[9749]
        nll_diffs.append(r)
    write_csv(a.out/'quality.csv',means)
    write_csv(a.out/'answer-churn.csv',churn)
    write_csv(a.out/'squad-error-transitions.csv',outcome_rows)
    write_csv(a.out/'paired-contrasts.csv',comparisons)
    write_csv(a.out/'calibration-modules.csv',calibration)
    write_csv(a.out/'text-nll.csv',nll)
    write_csv(a.out/'text-nll-contrasts.csv',nll_diffs)
    zero_hook={k:summaries[k]['zero_hook_fidelity'] for k in ['permuted','directional']}
    assert all(v['exact_equal'] and v['max_abs_error']==0 for v in zero_hook.values())
    for k in ['permuted','directional','mmlu_remove','squad_remove']:
        assert summaries[k]['adapter_validation']['exact_loaded_value_match']
    validation=dict(status='passed_recorded_artifact_checks',artifact_sha256=hashes,code_sha256=digest(Path(__file__)),scorer_sha256={p:digest(Path(__file__).resolve().parents[2]/p) for p in ['lora_dora_study/benchmarks.py','lora_dora_study/evaluation.py']},run_audit=audit,compatibility=compatibility,calibration_identical=True,zero_hook_fidelity=zero_hook,limitations=['No independent verification against finite device-memory corruption.', 'No training-seed uncertainty; one fixed permutation seed.', 'New controls subtract FP32 action and cast; native removeD uses different BF16 ordering.', 'NLL blocks are sensitivity units, not certified independent documents.', 'Task-specific noninferiority margins were not specified numerically before these runs.'])
    (a.out/'validation.json').write_text(json.dumps(validation,indent=2)+'\n')
    print(json.dumps(dict(primary=primary,transfer=[r for r in comparisons if r['family'].startswith('B_')],nll=nll_diffs,audit=audit),indent=2))


if __name__=='__main__':main()
