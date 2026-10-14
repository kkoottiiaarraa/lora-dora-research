#!/usr/bin/env python3
"""Descriptive overlap screen; no model runs or claims of numerical causation."""
import argparse
import collections
import csv
import gzip
import hashlib
import json
import math
from pathlib import Path
from fractions import Fraction

p=argparse.ArgumentParser()
p.add_argument('--repo',type=Path,default=Path(__file__).resolve().parents[2])
p.add_argument('--out',type=Path,required=True)
a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True)
source=a.repo/'docs/analysis-preparation/2026-10-11/02-interventions/tables/per_example_scores.csv.gz'
runs=collections.defaultdict(dict)
with gzip.open(source,'rt') as f:
    for r in csv.DictReader(f):
        if r['metric']=='final_em':
            i=int(r['test_row_index']);assert i not in runs[r['run_id']]
            runs[r['run_id']][i]=int(float(r['score']))
orig=runs['gsm8k-quality-greedy/dora']
dense=runs['gsm8k-dense-dora/dora']
assert set(orig)==set(dense)==set(range(1319))
df={i for i in orig if orig[i]!=dense[i]}
rows=[]
for name in ['gsm8k-remove_d-all/dora','gsm8k-r32/dora','gsm8k-e95/dora','gsm8k-e99/dora']:
    x=runs[name];assert set(x)==set(orig)
    flips={i for i in orig if orig[i]!=x[i]}
    expected=0
    for correct in [0,1]:
        ids={i for i in orig if orig[i]==correct}
        expected+=len(flips&ids)*len(df&ids)/len(ids)
    rows.append(dict(run=name,n=1319,correct=sum(x.values()),flips_vs_original=len(flips),dense_flips=len(df),shared_flips=len(flips&df),jaccard=len(flips&df)/len(flips|df),expected_overlap_under_stratified_exchangeability=expected,flips_vs_dense=sum(x[i]!=dense[i] for i in orig),delta_pp_vs_original=100*(sum(x.values())-sum(orig.values()))/1319,delta_pp_vs_dense=100*(sum(x.values())-sum(dense.values()))/1319))
with open(a.out/'conversion-overlap.csv','w') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
activity=a.repo/'docs/diagnostics/radial-activity-2026-10-11/module-activity.csv'
mods=list(csv.DictReader(open(activity)))
s=lambda k:sum(float(r[k]) for r in mods)
summary=dict(n=1319,original_correct=sum(orig.values()),dense_correct=sum(dense.values()),dense_correctness_flips=len(df),global_radial_directional_weight_cosine=s('R_dot_L')/math.sqrt(s('R_ss')*s('L_ss')),limitations=['Overlap is descriptive and selected after observing outcomes.', 'Exchangeability baseline is not a mechanistic null or causal test.', 'Custom dense reconstruction is not verified official PEFT merge.', 'Global weight cosine is not functional orthogonality or independence.'],input_sha256={str(f.relative_to(a.repo)):hashlib.sha256(f.read_bytes()).hexdigest() for f in [source,activity]},code_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())

# Scalar V/O symmetry: change only m_V -> c m_V, m_O -> m_O/c.
# Reconstruct norms analytically from recorded inner-product identities.
gauges=[]
for c in [.5,.99,.995,1.,1.005,1.01,2.]:
    total_r=total_delta=0
    for r in mods:
        scale=c if r['projection']=='V' else 1/c if r['projection']=='O' else 1.
        wd,u,w0,radial,delta=[float(r[k]) for k in ['WD_ss','U_ss','W0_ss','R_ss','Delta_ss']]
        total_r+=scale*scale*wd+u-scale*(wd+u-radial)
        total_delta+=scale*scale*wd+w0-scale*(wd+w0-delta)
    gauges.append(dict(c=c,radial_norm=math.sqrt(total_r),update_norm=math.sqrt(total_delta),radial_over_update=math.sqrt(total_r/total_delta),measurement='algebraic FP32-weight-summary reconstruction; not a new model-output measurement'))
with open(a.out/'gauge-norm-screen.csv','w') as f:
    w=csv.DictWriter(f,fieldnames=list(gauges[0]));w.writeheader();w.writerows(gauges)

# Exact rational witness, bases I_8 and rank-one directions held fixed.
v=[Fraction(2)]+[Fraction(1)]*7
o=[Fraction(1),Fraction(3,2)]+[Fraction(1)]*6
reference=[x*y for x,y in zip(v,o)]
def spectral_entropy(diagonal):
    energy=[float(x*x) for x in diagonal if x]
    return -sum((e/sum(energy))*math.log(e/sum(energy)) for e in energy)
toy=[]
for c in [Fraction(1,2),Fraction(1),Fraction(2)]:
    vs=[c*x for x in v];os=[x/c for x in o]
    assert [x*y for x,y in zip(vs,os)]==reference
    # removeD restores the same U_V,U_O because only magnitudes changed.
    mv=[c*x for x in v];mo=[x/c for x in o]
    remove_v=[w/(m/u) for w,m,u in zip(vs,mv,v)]
    remove_o=[w/(m/u) for w,m,u in zip(os,mo,o)]
    assert remove_v==v and remove_o==o
    assert [x*y for x,y in zip(remove_v,remove_o)]==reference
    dv=[x-1 for x in vs];do=[x-1 for x in os]
    toy.append(dict(c=str(c),base_fixed=True,directional_rank_v=1,directional_rank_o=1,delta_rank_v=sum(x!=0 for x in dv),delta_rank_o=sum(x!=0 for x in do),delta_entropy_v=spectral_entropy(dv),delta_entropy_o=spectral_entropy(do),original_function_exactly_equal=True,remove_d_function_exactly_equal=True))
(a.out/'exact-counterexample.json').write_text(json.dumps(dict(dimension=8,method='rational diagonal witness; identity bases; bias-free V/O composition',rows=toy,limitations='Real-arithmetic counterexample; not a claim about deployed BF16 equality, training dynamics, or all DoRA capacity.'),indent=2)+'\n')
(a.out/'screen.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps(dict(summary=summary,overlap=rows),indent=2))
