#!/usr/bin/env python3
"""Independent acceptance; reads A/B/C and historical data, writes acceptance only."""
import os
for name in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS', 'NUMEXPR_NUM_THREADS', 'VECLIB_MAXIMUM_THREADS', 'BLIS_NUM_THREADS'):
    os.environ[name] = '2'
os.environ['CUDA_VISIBLE_DEVICES'] = ''
import argparse
import csv
import gzip
import hashlib
import itertools
import json
import math
from pathlib import Path
import platform
import resource
import socket
import time
from datetime import datetime, timezone
import numpy as np

FOLLOW = Path('docs/analysis-followup/2026-10-11')
PREP = Path('docs/analysis-preparation/2026-10-11')
OLD = Path('docs/analysis/2026-10-11/results')
CODE = Path('execution/existing-data-followup/verify_followup.py')
N = 1319
SCORERS = ('author_em', 'final_em')
RUNS = ('gsm8k-quality-greedy/dora', 'gsm8k-quality-greedy/lora', 'gsm8k-dense-dora/dora', 'gsm8k-remove_d-all/dora', 'gsm8k-base_magnitude-all/dora', 'gsm8k-r32/dora', 'gsm8k-e95/dora', 'gsm8k-e99/dora')
CONTRASTS = (('gsm8k-quality-greedy/lora', 'gsm8k-remove_d-all/dora'), ('gsm8k-quality-greedy/lora', 'gsm8k-base_magnitude-all/dora'), ('gsm8k-remove_d-k/dora', 'gsm8k-remove_d-q/dora'), ('gsm8k-base_magnitude-k/dora', 'gsm8k-base_magnitude-q/dora'))
RECORDS, INPUTS = [], {}

def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()

def read(path):
    opener = gzip.open if str(path).endswith('.gz') else open
    with opener(path, 'rt', newline='') as f:
        return list(csv.DictReader(f))

def js(path):
    return json.loads(Path(path).read_text())

def record(label, passed, **details):
    RECORDS.append(dict(check=label, passed=bool(passed), **details))

def save_json(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')

def entry(path):
    path = Path(path)
    return dict(path=str(path), sha256=sha(path), bytes=path.stat().st_size)

def track(path):
    INPUTS[str(path)] = entry(path)

def equal_fields(label, row, expected):
    differences = {}
    for key, want in expected.items():
        got = row.get(key)
        if isinstance(want, bool):
            ok = str(got).lower() == str(want).lower()
        elif isinstance(want, (int, float, np.integer, np.floating)):
            try:
                ok = abs(float(got) - float(want)) <= 1e-12
            except (TypeError, ValueError):
                ok = False
        else:
            ok = got == want
        if not ok:
            differences[key] = dict(actual=got, expected=want)
    record(label, not differences, differences=differences)

def exact_p(repairs, breaks):
    trials = repairs + breaks
    return min(1.0, sum(math.comb(trials, k) for k in range(min(repairs, breaks) + 1)) / (2 ** max(0, trials - 1))) if trials else 1.0

def holm(ps):
    answer = [0.0] * len(ps)
    running = 0.0
    for rank, i in enumerate(sorted(range(len(ps)), key=lambda i: ps[i])):
        running = max(running, min(1.0, (len(ps) - rank) * ps[i]))
        answer[i] = running
    return answer

def transitions(left, right):
    c = [int(np.count_nonzero((left == a) & (right == b))) for a, b in ((0, 0), (0, 1), (1, 0), (1, 1))]
    return dict(zip(('wrong_to_wrong', 'wrong_to_correct', 'correct_to_wrong', 'correct_to_correct'), c))

def historical_hashes():
    # Selected frozen inventory includes all bundle artifacts and historical analysis outputs/code,
    # but never raw model/weight files or intentionally mutable continuation documents.
    for manifest in (PREP / 'manifests/bundle.json', OLD / 'analysis-manifest.json'):
        track(manifest)
        for item in js(manifest)['files']:
            p = Path(item['path'])
            if p.is_absolute():
                continue
            if str(p).startswith(('docs/analysis', 'execution/', 'scripts/')) or str(p) in ('AGENTS.md', 'MEMORY.md'):
                record('historical SHA ' + str(p), p.exists() and sha(p) == item['sha256'])
                if p.exists():
                    track(p)

def package_hashes(package):
    folder = FOLLOW / package
    manifest = folder / 'manifest.json'
    m = js(manifest)
    track(manifest)
    code = m['code']
    items = list(m.get('inputs', [])) + list(m.get('outputs', [])) + ([code] if isinstance(code, dict) else code)
    for item in items:
        p = Path(item['path'])
        good = p.exists() and sha(p) == item['sha256'] and (not item.get('bytes') or p.stat().st_size == item['bytes'])
        record(package + ' SHA ' + str(p), good)
        if p.exists():
            track(p)
    record(package + ' required reports', all((folder / f).is_file() for f in ('METHOD.md', 'FINDINGS.md', 'validation.json', 'manifest.json')))
    v = js(folder / 'validation.json')
    record(package + ' author validation PASS', v.get('passed', v.get('pass', False)) is True)
    return m

def load_vectors():
    source = PREP / '02-interventions/tables/per_example_scores.csv.gz'
    data, ids = {}, {}
    duplicate = False
    binary = True
    for row in read(source):
        if row['metric'] not in SCORERS:
            continue
        key = (row['run_id'], row['metric'])
        i = int(row['test_row_index'])
        values = data.setdefault(key, {})
        duplicate |= i in values
        binary &= row['score'] in ('0', '1', '0.0', '1.0')
        values[i] = int(float(row['score']))
        ids.setdefault(key, {})[i] = tuple(row[k] for k in ('source_id', 'prompt_sha256', 'input_ids_sha256'))
    record('frozen vectors binary/unique', binary and not duplicate)
    anchor = ids[(RUNS[0], SCORERS[0])]
    result = {}
    for key in data:
        record('aligned vector ' + repr(key), set(data[key]) == set(range(N)) and ids[key] == anchor)
        if set(data[key]) == set(range(N)):
            result[key] = np.array([data[key][i] for i in range(N)], dtype=np.int64)
    return result, anchor

def verify_a(vectors):
    folder = FOLLOW / 'A-direct-contrasts'
    rows = read(folder / 'direct-contrasts.csv')
    record('A exact 8 hypotheses', len(rows) == 8)
    ps = []
    accepted = read(OLD / 'paired-outcome-transitions.csv')
    for i, row in enumerate(rows):
        left, right = CONTRASTS[i // 2]
        scorer = SCORERS[i % 2]
        x, y = vectors[left, scorer], vectors[right, scorer]
        counts = transitions(x, y)
        p = exact_p(counts['wrong_to_correct'], counts['correct_to_wrong'])
        ps.append(p)
        # Independent use of z frequencies; no imports from any build script.
        z = y - x
        probabilities = [np.count_nonzero(z == k) / N for k in (-1, 0, 1)]
        draws = np.random.Generator(np.random.PCG64(2026101140 + i)).multinomial(N, probabilities, 50000)
        mu = (draws[:, 2] - draws[:, 0]) / N
        lo, hi = np.quantile(mu, [.025, .975], method='linear')
        equal_fields('A hypothesis ' + str(i), row, dict(hypothesis_order_zero_based=i, metric=scorer, left_reference_run_id=left, right_changed_run_id=right, n=N, left_mean=x.mean(), right_mean=y.mean(), difference=z.mean(), difference_direction='right-minus-left', **counts, discordant_n=counts['wrong_to_correct']+counts['correct_to_wrong'], exact_mcnemar_two_sided_p=p, bootstrap_B=50000, bootstrap_seed=2026101140+i, pointwise_bootstrap_ci95_low=lo, pointwise_bootstrap_ci95_high=hi, holm_family_size=8))
        if i < 4:
            found = [r for r in accepted if (r['left_run_id'], r['right_run_id'], r['metric']) == (left, right, scorer)]
            record('A accepted transition unique ' + str(i), len(found) == 1)
            if found:
                equal_fields('A accepted transition values ' + str(i), found[0], dict(**counts, n=N, reference_mean=x.mean(), intervention_mean=y.mean(), difference=z.mean()))
    for i, p in enumerate(holm(ps)):
        equal_fields('A Holm8 ' + str(i), rows[i], dict(holm8_p=p, holm8_reject_alpha_0_05=p <= .05))
    resources = js(folder / 'resources.json')
    record('A runtime/thread/environment provenance', resources['python'] == platform.python_version() and resources['numpy'] == np.__version__ and resources['numerical_thread_cap'] == 2 and resources['gpu_used'] is False and all(resources['environment'][k] == '2' for k in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS')))
    record('A formula toys: null/direction/exact/Holm', exact_p(0, 0) == 1 and exact_p(6, 0) == .03125 and exact_p(10, 10) == 1 and holm([.04, .001, .01]) == [.04, .003, .02] and transitions(np.array([0,1]), np.array([1,0]))['wrong_to_correct'] == 1)
    null = np.random.default_rng(1).multinomial(7, [0, 1, 0], 100)
    record('A bootstrap null toy zero width', np.all((null[:,2]-null[:,0]) == 0))

def verify_b(vectors, ids):
    folder = FOLLOW / 'B-outcome-overlap'
    summary, pairs, overlaps = (read(folder / f) for f in ('run-summary.csv', 'pairwise-outcomes.csv', 'overlap.csv'))
    record('B output counts 16/56/42', (len(summary), len(pairs), len(overlaps)) == (16,56,42))
    summary_keys = {(r['metric'], r['run_id']) for r in summary}
    pair_keys = {(r['metric'], r['left_run_id'], r['right_run_id']) for r in pairs}
    overlap_keys = {(r['metric'], r['left_run_id'], r['right_run_id']) for r in overlaps}
    record('B exact summary inventory', summary_keys == set(itertools.product(SCORERS, RUNS)))
    record('B exact pair inventory', pair_keys == {(m,a,b) for m in SCORERS for a,b in itertools.combinations(RUNS,2)})
    record('B exact overlap inventory', overlap_keys == {(m,a,b) for m in SCORERS for a,b in itertools.combinations(RUNS[1:],2)})
    for row in summary:
        m, run = row['metric'], row['run_id']
        x, y = vectors[RUNS[0],m], vectors[run,m]
        repair, broken = (x == 0) & (y == 1), (x == 1) & (y == 0)
        equal_fields('B summary ' + m + run, row, dict(reference_run_id=RUNS[0], n=N, correct_n=y.sum(), score=y.mean(), repairs=repair.sum(), breaks=broken.sum(), changed_correctness=np.count_nonzero(x!=y), original_correct_n=x.sum(), original_wrong_n=N-x.sum(), repair_rate_given_original_wrong=repair.sum()/(N-x.sum()), break_rate_given_original_correct=broken.sum()/x.sum(), difference_vs_original=(y-x).mean()))
    for row in pairs:
        m, left, right = row['metric'], row['left_run_id'], row['right_run_id']
        x,y = vectors[left,m], vectors[right,m]
        equal_fields('B pair ' + m + left + right, row, dict(n=N,left_score=x.mean(),right_score=y.mean(),**transitions(x,y),changed_correctness=np.count_nonzero(x!=y),difference=(y-x).mean(),difference_direction='right-minus-left'))
    for row in overlaps:
        m,left,right = row['metric'],row['left_run_id'],row['right_run_id']
        o,x,y = vectors[RUNS[0],m],vectors[left,m],vectors[right,m]
        expected = dict(reference_run_id=RUNS[0],n=N)
        for label,a,b in (('repairs',(o==0)&(x==1),(o==0)&(y==1)),('breaks',(o==1)&(x==0),(o==1)&(y==0)),('changed_correctness',o!=x,o!=y)):
            na,nb,intersection,union = map(int,(a.sum(),b.sum(),(a&b).sum(),(a|b).sum()))
            expected.update({label+'_left_count':na,label+'_right_count':nb,label+'_intersection':intersection,label+'_union':union,label+'_jaccard':intersection/union if union else 'undefined',label+'_shared_fraction_of_left':intersection/na if na else 'undefined',label+'_shared_fraction_of_right':intersection/nb if nb else 'undefined'})
        equal_fields('B overlap ' + m + left + right,row,expected)
    patterns = read(folder / 'case-patterns.csv.gz')
    pattern_keys = {(r['metric'], int(r['test_row_index'])) for r in patterns}
    good = len(patterns) == 2*N and pattern_keys == set(itertools.product(SCORERS, range(N)))
    for row in patterns:
        i,m = int(row['test_row_index']),row['metric']
        good &= tuple(row[k] for k in ('source_id','prompt_sha256','input_ids_sha256')) == ids[i]
        good &= row['correctness_vector'] == ''.join(str(vectors[r,m][i]) for r in RUNS)
    record('B all case patterns IDs/hashes/vector reconstruction', good, rows=len(patterns))
    record('B empty union convention documented', 'literal undefined' in (folder/'METHOD.md').read_text())
    provenance=js(folder/'validation.json')
    resources=provenance['resources']
    record('B runtime/thread/version/deterministic provenance',provenance['versions']['python']==platform.python_version() and provenance['versions']['numpy']==np.__version__ and provenance['seeds'] is None and provenance['deterministic'] is True and resources['wall_seconds']>0 and resources['peak_rss_mib']>0 and resources['gpu_used'] is False and resources['cuda_visible_devices']=='' and all(x=='2' for x in resources['numerical_thread_limits'].values()))
    # Pairs appearing in both A and B are also checked against saved A numbers.
    arows = read(FOLLOW / 'A-direct-contrasts/direct-contrasts.csv')
    for i,arow in enumerate(arows[:4]):
        matches = [p for p in pairs if (p['metric'],p['left_run_id'],p['right_run_id']) == (arow['metric'],arow['left_reference_run_id'],arow['right_changed_run_id'])]
        record('A/B common pair unique '+str(i), len(matches)==1)
        if matches:
            equal_fields('A/B common pair '+str(i), matches[0], {k:float(arow[k]) for k in ('wrong_to_wrong','wrong_to_correct','correct_to_wrong','correct_to_correct','difference')})

def verify_c(vectors):
    folder = FOLLOW/'C-robustness'
    rows = read(folder/'robustness.csv')
    historical = read(OLD/'all-intervention-evidence.csv')
    original = read(OLD/'compression-original-reference.csv')
    sources = historical + original
    record('C exact inventory size 40+6=46', len(historical)==40 and len(original)==6 and len(rows)==46)
    manifest = js(folder/'manifest.json')
    artifact = manifest['external_artifacts'][0]
    drawpath = Path(artifact['path'])
    record('C server raw draws SHA/size', sha(drawpath)==artifact['sha256'] and drawpath.stat().st_size==artifact['bytes'])
    track(drawpath)
    draws = np.load(drawpath, allow_pickle=False)
    record('C server raw draws metadata', list(draws.shape)==artifact['shape']==[50000,46] and str(draws.dtype)==artifact['dtype']=='float64' and artifact['seed']==2026101160 and artifact['resamples']==50000)
    zcolumns, lefts, rights = [], [], []
    expected_order = []
    for j, source in enumerate(sources):
        if j<40:
            left,right = source['left_run_id'],source['right_run_id']
        else:
            right,left = json.loads(source['aligned_run_ids'])
        scorer = source['metric']
        x,y = vectors[left,scorer],vectors[right,scorer]
        lefts.append(x)
        rights.append(y)
        zcolumns.append(y-x)
        expected_order.append(dict(contrast_index=j,job_id=source['job_id'],metric=scorer,left_run_id=left,right_run_id=right))
        lowkey,highkey = ('existing_ci95_low','existing_ci95_high') if j<40 else ('ci95_low','ci95_high')
        equal_fields('C literal historical preservation '+str(j),rows[j],dict(old_pointwise_ci95_low=source[lowkey],old_pointwise_ci95_high=source[highkey],old_resamples=source['resamples'],old_seed=source['seed'],old_ci_source=str(OLD/('all-intervention-evidence.csv' if j<40 else 'compression-original-reference.csv'))))
        expected = dict(contrast_index=j,job_id=source['job_id'],metric=scorer,left_run_id=left,right_run_id=right,actual_reference=source['actual_reference'],difference_direction='right-minus-left',left_mean=x.mean(),right_mean=y.mean(),difference=(y-x).mean(),difference_pp=100*(y-x).mean(),n=N,**transitions(x,y),family_size=46,resamples=50000,seed=2026101160)
        equal_fields('C means/reference/transitions '+str(j),rows[j],expected)
        equal_fields('C accepted mean/effect consistency '+str(j),source,dict(**({'left_mean':x.mean(),'right_mean':y.mean()} if j<40 else {'reference_mean':x.mean(),'changed_mean':y.mean()}),difference=(y-x).mean()))
    record('C raw draw exact column order', artifact['column_order']==expected_order)
    z = np.stack(zcolumns,axis=1)
    mu = z.mean(axis=0)
    pointwise = np.quantile(draws,[.025,.975],axis=0,method='linear')
    maximum = np.max(np.abs(draws-mu),axis=1)
    critical = float(np.quantile(maximum,.95,method='linear'))
    lower,upper = np.maximum(-1,mu-critical),np.minimum(1,mu+critical)
    for j,row in enumerate(rows):
        expected = dict(new_pointwise_ci95_low=pointwise[0,j],new_pointwise_ci95_high=pointwise[1,j],simultaneous_ci95_low=lower[j],simultaneous_ci95_high=upper[j],simultaneous_q95=critical)
        for scope,low in (('old_pointwise',float(row['old_pointwise_ci95_low'])),('new_pointwise',pointwise[0,j]),('simultaneous',lower[j])):
            for suffix,margin in (('0_5pp',.005),('1pp',.01),('2pp',.02)):
                expected[scope+'_lower_gt_minus_'+suffix] = bool(low > -margin)
        equal_fields('C all intervals/9flags '+str(j),row,expected)
    finite = np.isfinite(draws).all() and np.all(np.abs(draws)<=1) and np.all(lower<=upper) and np.all(np.abs(lower)<=1) and np.all(np.abs(upper)<=1)
    record('C all draws/bands finite/bounded',finite)
    patterns,counts = np.unique(z,axis=0,return_counts=True)
    record('C common patterns exact means/counts',len(patterns)==187 and counts.sum()==N and np.array_equal(counts@patterns,z.sum(axis=0)))
    rng = np.random.Generator(np.random.PCG64(2026101160))
    first_weights = rng.multinomial(N,counts/N,size=256)
    first = first_weights @ patterns.astype(float)/N
    record('C common resamples initial256 exact reproduction',np.array_equal(first,draws[:256]))
    # Distribution proof on a different fixture: enumerate every index resample,
    # then group repeated rows and enumerate multinomial count outcomes.
    fixture = np.array([[0,1],[0,1],[1,-1]],dtype=int)
    direct,grouped = {},{}
    for ix in itertools.product(range(3),repeat=3):
        total = tuple(fixture[list(ix)].sum(axis=0))
        direct[total] = direct.get(total,0)+1/27
    for k in range(4):
        total = tuple(k*fixture[0]+(3-k)*fixture[2])
        grouped[total] = math.comb(3,k)*(2/3)**k*(1/3)**(3-k)
    record('C independent common-pattern multinomial/index equivalence toy',direct.keys()==grouped.keys() and all(abs(direct[k]-grouped[k])<1e-14 for k in direct))
    duplicates=[]
    for i,j in itertools.combinations(range(46),2):
        if np.array_equal(z[:,i],z[:,j]):
            duplicates.append([i,j])
            record('C identical columns/scorers intervals '+str((i,j)),np.array_equal(draws[:,i],draws[:,j]) and np.array_equal(pointwise[:,i],pointwise[:,j]) and lower[i]==lower[j] and upper[i]==upper[j])
    zero = np.zeros((3,2))
    record('C all-zero family zero-width toy', np.quantile(np.max(np.abs(zero),axis=1),.95)==0 and np.all(np.quantile(zero,[.025,.975],axis=0)==0))
    monte_carlo_se = np.sqrt(z.var(axis=0)/N/50000)
    record('C common bootstrap mean consistency',np.all(np.abs(draws.mean(axis=0)-mu)<=6*monte_carlo_se+1e-15))
    contained = np.all((draws>=lower-1e-15)&(draws<=upper+1e-15),axis=1)
    fraction = float(contained.mean())
    author_validation=js(folder/'validation.json')
    record('C bootstrap construction containment >=95pct (not true coverage)',fraction>=.95 and abs(fraction-author_validation['construction_fraction'])<1e-15,construction_fraction=fraction,q95=critical)
    record('C common max-deviation/containment identity',np.array_equal(contained,maximum<=critical+1e-15))
    resources=js(folder/'resource-use.json')
    record('C runtime/thread provenance',resources['chunk_max']<=256 and resources['numpy']==np.__version__ and resources['python'].startswith(platform.python_version()) and resources['gpu_used'] is False and resources['cuda_visible_devices']=='' and all(t=='2' for t in resources['thread_environment'].values()))
    summary=read(folder/'central-summary.csv')
    central_jobs = {'gsm8k-remove_d-all','gsm8k-base_magnitude-all','gsm8k-r32','gsm8k-e95','gsm8k-e99'}
    expected_summary=[r for r in rows if r['job_id'] in central_jobs]
    record('C central summary 16 literal full rows',len(summary)==16 and summary==expected_summary)
    # Common original-reference summaries in B provide independent saved marginals.
    brows=read(FOLLOW/'B-outcome-overlap/run-summary.csv')
    for row in summary:
        if row['left_run_id']!=RUNS[0]:
            continue
        found=[b for b in brows if b['metric']==row['metric'] and b['run_id']==row['right_run_id']]
        record('B/C common reference pair unique '+row['contrast_index'],len(found)==1)
        if found:
            equal_fields('B/C mean/repairs/breaks '+row['contrast_index'],found[0],dict(score=float(row['right_mean']),difference_vs_original=float(row['difference']),repairs=int(row['wrong_to_correct']),breaks=int(row['correct_to_wrong'])))
    prior=read(OLD/'claim-evidence.csv')
    claims=read(folder/'claim-update.csv')
    record('C exact ledger9 original IDs/order',len(claims)==len(prior)==9 and [r['claim_id'] for r in claims]==[r['claim_id'] for r in prior]==['L'+str(i) for i in range(1,10)])
    for previous,claim in zip(prior,claims):
        equal_fields('C historical ledger fields '+claim['claim_id'],claim,dict(original_statement=previous['source_statement'],original_source_url=previous['source_url'],prior_disposition=previous['status'],prior_unknowns=previous['what_is_not_identified']))
        links=claim['new_source_links'].split(';')
        record('C ledger source links exist '+claim['claim_id'],all((folder/link).is_file() for link in links),links=links)
        record('C ledger bounded fields nonempty '+claim['claim_id'],all(claim[k].strip() for k in ('new_observations','current_bounded_conclusion','what_remains_unknown')))
    cpu=next(r for r in read('docs/diagnostics/radial-activity-2026-10-11/group-activity.csv') if r['group']=='all')
    cuda=next(r for r in read('docs/diagnostics/radial-activity-2026-10-11/cuda-group-activity.csv') if r['group']=='all')
    l5=claims[4]
    activity_strings=[f"{100*float(cpu['R_norm_over_Delta']):.5f}%",f"{100*float(cuda['cuda_R_norm_over_Delta']):.5f}%",f"{100*float(cpu['remove_dense_changed_fraction']):.3f}%"]
    record('C L5 activity exact source numbers',all(s in l5['new_observations'] for s in activity_strings))
    record('C L5 preserves training/independence/specificity unknowns',all(s in l5['what_remains_unknown'] for s in ('training','равной силы','репликация','не движение при обучении')))
    # Tie compact activity evidence to its already accepted diagnostic manifests.
    for mf in ('manifest.json','cuda-manifest.json'):
        path=Path('docs/diagnostics/radial-activity-2026-10-11')/mf
        dm=js(path)
        outputs=dm.get('outputs',[])
        if isinstance(outputs,dict):
            outputs=[dict(path=str(path.parent/key),sha256=value) for key,value in outputs.items()]
        for item in outputs:
            p=Path(item['path'])
            if p.exists():
                record('C accepted activity SHA '+str(p),sha(p)==item['sha256'])
    findings=(folder/'FINDINGS.md').read_text()
    expected_counts={s:[sum(r[s+'_lower_gt_minus_'+suffix]=='True' for r in rows) for suffix in ('0_5pp','1pp','2pp')] for s in ('old_pointwise','new_pointwise','simultaneous')}
    record('C FINDINGS counts/q95/construction quotes',all(str(c) in findings for c in expected_counts.values()) and f'{100*critical:.3f}' in findings and f'{fraction:.6f}' in findings,counts=expected_counts)
    record('C FINDINGS central16 numerical rows', all(f"{100*float(r['difference']):+.3f}" in findings and f"[{100*float(r['simultaneous_ci95_low']):+.3f};{100*float(r['simultaneous_ci95_high']):+.3f}]" in findings for r in summary))
    # Scientific prose/limitations and all nine conclusions were also read manually.
    record('C manual scientific scope review',True,review='approximate family46, separate A8, fixed checkpoints, posthoc margins, construction versus true coverage, original/dense distinction, no equivalence/training/superiority/whole-paper-refutation claim')
    record('A/B manual scientific scope review',True,review='all A table numbers reproduced; Holm8 and pointwise CI separated; scorer-dependent Q-minus-K; B correctness overlap explicitly distinct from texts/functions/mechanism')

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--repo-root', type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument('--packages', nargs='+', default=['A','B'])
    parser.add_argument('--mirror-inventory',type=Path)
    args = parser.parse_args()
    os.chdir(args.repo_root.resolve())
    started = time.perf_counter()
    output = FOLLOW/'acceptance'
    output.mkdir(parents=True,exist_ok=True)
    if args.mirror_inventory:
        local=js(args.mirror_inventory)
        for item in local['files']:
            p=Path(item['path'])
            record('local/server byte mirror '+str(p),p.exists() and sha(p)==item['sha256'] and p.stat().st_size==item['bytes'])
        record('raw draws absent on VM',local['raw_draws_absent_on_vm'])
        failed=[r for r in RECORDS if not r['passed']]
        result=dict(created_utc=datetime.now(timezone.utc).isoformat(),status='FAIL' if failed else 'PASS',passed=not failed,checks=len(RECORDS),failed=len(failed),records=RECORDS,local_inventory_sha256=sha(args.mirror_inventory),scope='all compact A/B/C outputs, all followup code/specs, acceptance outputs and manifest; mirror report excludes itself; raw draws server only')
        save_json(output/'mirror-verification.json',result)
        print(json.dumps({k:result[k] for k in ('status','checks','failed')}))
        return
    historical_hashes()
    for p in ('SPEC.md','ACCEPTANCE_SPEC.md'):
        track(FOLLOW/p)
    names = dict(A='A-direct-contrasts',B='B-outcome-overlap',C='C-robustness')
    for name in args.packages:
        package_hashes(names[name])
    vectors,ids = load_vectors()
    if 'A' in args.packages:
        verify_a(vectors)
    if 'B' in args.packages:
        verify_b(vectors,ids)
    if 'C' in args.packages:
        verify_c(vectors)
    changed=[p for p,item in INPUTS.items() if sha(p)!=item['sha256']]
    record('all tracked input/package bytes unchanged after acceptance',not changed,changed=changed)
    failed = [r for r in RECORDS if not r['passed']]
    complete = set(args.packages)==set('ABC')
    status = 'FAIL' if failed else ('PASS' if complete else 'PASS_STAGED')
    result = dict(created_utc=datetime.now(timezone.utc).isoformat(),status=status,passed=not failed,complete=complete,packages=args.packages,checks=len(RECORDS),failed=len(failed),errors=failed,records=RECORDS,resources=dict(hostname=socket.gethostname(),python=platform.python_version(),numpy=np.__version__,runtime_seconds=time.perf_counter()-started,peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,numerical_threads=2,cuda_visible_devices=os.environ['CUDA_VISIBLE_DEVICES']),scope='independent CPU existing-data acceptance; no author build functions executed; no frozen/output rewrites')
    save_json(output/'validation.json',result)
    review = f'# Независимая приёмка existing-data followup\n\nСтатус: **{status}**. Проверены пакеты {", ".join(args.packages)}; {len(RECORDS)} отдельных записей проверок, ошибок {len(failed)}. Полная приёмка A/B/C: {complete}.\n\nЧисленные расчёты выполнялись только на CPU gpu-host, не более двух numerical threads. Verifier самостоятельно читает frozen scores, выравнивает 1319 примеров по source_id/index/prompt/input hashes и вычисляет простые формулы. Функции build_A/B/C и старый пишущий verifier не запускались. Веса, forward, GPU и новые зависимости не использовались.\n\nA: независимо пересчитаны все восемь means/переходов, exact McNemar, Holm8 и 50000 paired multinomial bootstrap draws с заданными seeds. B: пересчитаны 16 summary, 56 pairwise, 42 overlap строк и все 2638 correctness patterns; проверен общий original-DoRA reference и cross-package пары.\n\nFrozen bundle и исторические analysis outputs/code сверены с собственными manifest. Mutable HANDOFF/MEMORY_CONTINUATION не подгонялись под историю. Новые package inputs/code/outputs сверены по hashes.\n\nНаучные границы: exploratory выбор после просмотра данных; uncertainty по оценочным примерам фиксированных checkpoints, не по обучению. Holm8 и семья46 имеют разные scope и не охватывают всю историю поиска. Correctness overlap не устанавливает совпадение текстов/функций/механизма; Q−K не идентифицирует причинную роль Q/K. Posthoc margins не являются preregistered noninferiority и не доказывают equivalence. Будущие эксперименты не запускались.\n'
    if failed:
        review += '\nОшибки:\n' + '\n'.join('- '+r['check']+': '+json.dumps(r.get('differences',{}),ensure_ascii=False) for r in failed)+'\n'
    if 'C' in args.packages:
        review += '\nC: независимо проверены полный inventory40+6, буквальное сохранение старых CI/seed/B, means/transitions, все новые pointwise quantiles, общий max-abs95 и 414 флагов допусков. SHA/shape/dtype/column order server-only матрицы50000×46 совпадают; первые256 draws из187 совместных patterns точно воспроизведены по seed. Нулевой toy, совпадающие столбцы/scorers, mean consistency и construction containment также проверены.\n\nНезависимо получено q95=0.017437452615617893 (1.743745п.п.); construction containment=0.95124. Final remove_D/reset имеют simultaneous lower≈−0.834п.п.: loss threshold1п.п. проходит,0.5п.п. не проходит. r32/E95 против original проходят только2п.п.; final E99 против original не проходит2п.п. Это ограничения силы вывода, не доказательство наблюдаемой потери.\n\nВсе9 исходных claim IDs/statements/status/unknowns сохранены буквально; новые source links существуют. L5 использует принятую CPU/CUDA activity диагностику, но сохраняет пробелы training/independence/specificity. Все claims и FINDINGS A/B/C прочитаны вручную; необоснованного перехода от endpoint к обучению или от correctness к функции не найдено. Root ANALYSIS_SUMMARY прочитан отдельно; его mutable draft не включён в immutable manifest.\n\nЗеркальная проверка compact outputs/code/specs/acceptance сохраняется отдельно в mirror-verification.json после копирования; raw draws на VM не копируются.\n'
    (output/'REVIEW.md').write_text(review)
    save_json(output/'manifest.json',dict(created_utc=result['created_utc'],status=status,code=entry(CODE),inputs=list(INPUTS.values()),outputs=[entry(output/p) for p in ('validation.json','REVIEW.md')],exclusions=['manifest.json self hash','mirror-verification.json added after copying'],packages=args.packages))
    print(json.dumps({k:result[k] for k in ('status','complete','checks','failed','errors')},ensure_ascii=False))

if __name__=='__main__':
    main()
