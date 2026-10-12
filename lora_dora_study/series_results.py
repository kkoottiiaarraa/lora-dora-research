"""Paired metrics on fixed inputs; no assumption about the winning method."""
import json
from pathlib import Path
from lora_dora_study.evaluation import sha256_file


def paired_difference(left,right,replicates=10000):
    import numpy as np
    if len(left)!=len(right) or not left:raise ValueError('Paired nonempty data required')
    differences=np.asarray(right,dtype=float)-np.asarray(left,dtype=float)
    values,counts=np.unique(differences,return_counts=True)
    rng=np.random.default_rng(42)
    boot=[]
    # Sampling the empirical difference histogram is exactly the paired bootstrap.
    for start in range(0,replicates,128):
        samples=rng.multinomial(len(left),counts/len(left),size=min(128,replicates-start))
        boot.extend((samples@values/len(left)).tolist())
    absolute,counts=np.unique(np.abs(differences),return_counts=True)
    permutations=[]
    for start in range(0,replicates,128):
        signs=2*rng.binomial(counts,.5,size=(min(128,replicates-start),len(counts)))-counts
        permutations.extend((signs@absolute/len(left)).tolist())
    observed=float(differences.mean())
    return dict(difference=observed,ci95=np.quantile(boot,[.025,.975]).tolist(),
        paired_sign_permutation_p=(1+sum(abs(v)>=abs(observed)-1e-12 for v in permutations))/(replicates+1),
        n=len(left),resamples=replicates,seed=42,ci_adjustment='none',
        scope='paired evaluation examples, not independent training repetitions')


def load_run(directory):
    directory=Path(directory)
    summary=json.loads((directory/'summary.json').read_text())
    path=directory/'predictions.jsonl'
    if summary['status']!='complete' or not summary['full_evaluation']:
        raise ValueError('Full completed runs required')
    if sha256_file(path)!=summary['predictions_sha256']:
        raise ValueError('Predictions changed')
    rows=[json.loads(line) for line in path.read_text().split("\n") if line]
    if [r['test_row_index'] for r in rows]!=list(range(summary['dataset']['rows'])):
        raise ValueError('Incomplete/reordered/duplicate examples')
    return summary,rows


def compare_runs(left_directory,right_directory):
    left,a=load_run(left_directory);right,b=load_run(right_directory)
    for key in ['dataset','generation_config','versions','source_sha256']:
        if left[key]!=right[key]:raise ValueError('Unmatched '+key)
    if len(a)!=len(b) or any(x['input_ids_sha256']!=y['input_ids_sha256'] or
        x['prompt_sha256']!=y['prompt_sha256'] for x,y in zip(a,b)):
        raise ValueError('Unmatched prompts')
    result=dict(left=str(left_directory),right=str(right_directory),
        metrics={key:paired_difference([r['metrics'][key] for r in a],[r['metrics'][key] for r in b])
                 for key in a[0]['metrics']},
        caveat='CI is conditional on these checkpoints. Final interventions do not identify training cause.')
    subjects=sorted({r.get('subject') for r in a if r.get('subject')})
    if subjects:
        result['per_subject']={subject:{key:dict(
            left=sum(r['metrics'][key] for r in a if r['subject']==subject)/sum(r['subject']==subject for r in a),
            right=sum(r['metrics'][key] for r in b if r['subject']==subject)/sum(r['subject']==subject for r in b))
            for key in a[0]['metrics']} for subject in subjects}
        result['subject_macro']={key:{side:sum(result['per_subject'][s][key][side] for s in subjects)/len(subjects)
            for side in ['left','right']} for key in a[0]['metrics']}
    return result


def holm(pvalues):
    ordered=sorted(pvalues,key=pvalues.get)
    adjusted={};previous=0.
    for index,key in enumerate(ordered):
        previous=max(previous,min(1.,pvalues[key]*(len(ordered)-index)))
        adjusted[key]=previous
    return adjusted
