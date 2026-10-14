#!/usr/bin/env python3
"""Read-only acceptance of saved scientific analysis; only write own two reports.

Run with the existing research Python on gpu-host, CPU <=2 threads. No bootstrap,
model imports, weights, SVD, inference, dependency installation, or input rewrites.
Default Q/C stage is explicitly incomplete; --final requires L/T and final report.
"""
import argparse
import csv
import gzip
import hashlib
import json
import math
import platform
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

ANALYSIS = Path('docs/analysis/2026-10-11')
BUNDLE = Path('docs/analysis-preparation/2026-10-11')
CODE = Path('execution/scientific-analysis')
BASE = 'gsm8k-quality-greedy/dora'
METRICS = ('author_em', 'final_em')
Q_SPEC = '3ddd31cf7ea359d495793276e9bf4098ddab88a4ad03ba11de73d488deb7574a'
C_SPEC = '9123f1a73138cbb544be223c3f1b3e0cfa6d6cf4b8c5da1b136d59e7e83d17c7'


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def holm(raw):
    result = [0.] * len(raw)
    running = 0.
    for rank, index in enumerate(sorted(range(len(raw)), key=raw.__getitem__)):
        running = max(running, (len(raw) - rank) * raw[index])
        result[index] = min(1., running)
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--repo', type=Path, default=Path.cwd())
    p.add_argument('--final', action='store_true')
    p.add_argument('--include-localizations', action='store_true')
    args = p.parse_args()
    repo = args.repo.resolve()
    out = repo / ANALYSIS / 'results'
    checks, records, historical = [], {}, []
    counts = {}

    def check(name, passed, **details):
        checks.append(dict(name=name, passed=bool(passed), **details))
        return bool(passed)

    def track(path, category, status='verified'):
        path = Path(path)
        path = path if path.is_absolute() else repo / path
        key = str(path.relative_to(repo)) if path.is_relative_to(repo) else str(path)
        if not path.is_file():
            check('exists ' + key, False)
            return path
        if key not in records:
            records[key] = dict(path=key, sha256=sha(path), bytes=path.stat().st_size,
                                category=category, status=status)
        return path

    def digest_check(path, expected, category='input'):
        path = track(path, category)
        if path.is_file():
            check('hash ' + str(path), sha(path) == expected, expected=expected)

    def load(path, category='input'):
        return json.loads(track(path, category).read_text())

    def table(path, count=None, required=(), category='artifact'):
        path = track(path, category)
        with path.open(newline='') as f:
            reader = csv.DictReader(f)
            fields = reader.fieldnames or []
            rows = list(reader)
        check('schema ' + path.name, set(required) <= set(fields) and len(set(fields)) == len(fields)
              and all(None not in r and None not in r.values() for r in rows), required=list(required))
        if count is not None:
            check('count ' + path.name, len(rows) == count, expected=count, actual=len(rows))
        counts[path.name] = len(rows)
        # Numeric fraction/probability/CI checks; blank cells are explicitly allowed.
        for col in ['mean', 'left_mean', 'right_mean', 'original_score', 'changed_mean', 'reference_mean',
                    'joint_mean', 'single1_mean', 'single2_mean', 'intervention_mean',
                    'raw_p', 'holm_p', 'existing_raw_p', 'existing_holm_p', 'global40_holm_p',
                    'difference', 'ci95_low', 'ci95_high', 'existing_ci95_low', 'existing_ci95_high']:
            if col not in fields:
                continue
            limit = 2 if path.name in ['joint-interactions.csv', 'compression-difference-in-differences.csv'] else 1
            lower = -limit if col == 'difference' or 'ci95' in col else 0
            upper = limit if lower < 0 else 1
            try:
                ok = all(math.isfinite(float(r[col])) and lower <= float(r[col]) <= upper
                         for r in rows if r[col] not in ('', 'null'))
            except ValueError:
                ok = False
            check('range ' + path.name + ':' + col, ok)
        for lo, hi in [('ci95_low', 'ci95_high'), ('existing_ci95_low', 'existing_ci95_high')]:
            if lo in fields:
                check('CI order ' + path.name, all(float(r[lo]) <= float(r[hi]) for r in rows if r[lo]))
        return rows

    def literal(rows, sources, key, name):
        source = {tuple(r[k] for k in key): r for r in sources}
        keys = [tuple(r[k] for k in key) for r in rows]
        check(name + ' unique keys', len(set(keys)) == len(keys))
        check(name + ' complete source keys', set(keys) == set(source))
        check(name + ' exact source fields/references', all(k in source and
              all(r.get(c) == v for c, v in source[k].items()) for r, k in zip(rows, keys)))

    def accepted(name, code):
        d = load(ANALYSIS / 'results' / name, 'saved_validation')
        check(name + ' prior accepted', d.get('passed') is True and
              all(c.get('passed') is True for c in d.get('checks', [])))
        inputs = d.get('inputs', d.get('input_hashes', {}))
        for path, value in inputs.items():
            digest_check(path, value['sha256'] if isinstance(value, dict) else value)
        for path, value in d['outputs'].items():
            digest_check(ANALYSIS / 'results' / path,
                         value['sha256'] if isinstance(value, dict) else value, 'artifact')
        if 'code_sha256' in d:
            digest_check(CODE / code, d['code_sha256'], 'code')
            digest_check(ANALYSIS / 'PLAN.md', d['plan_sha256'], 'plan')
        if name == 'quality-validation.json':
            current = sha(repo / ANALYSIS / 'EXECUTION_SPEC.md')
            note = (repo / ANALYSIS / 'CHECKPOINT.md').read_text()
            # Historical bytes are unavailable in saved Git history. This is an
            # explicit documented provenance exception, never a rewritten validation.
            known = d['spec_sha256'] == Q_SPEC and current == C_SPEC and 'эволюция ТЗ' in note
            check('Q spec historical evolution documented', current == d['spec_sha256'] or known)
            historical.append(dict(kind='execution_spec_evolution', saved_sha256=d['spec_sha256'],
                current_sha256=current, evidence='CHECKPOINT.md historical SPEC evolution note; C additions entropy/direct-original',
                historical_bytes_available=False, status='documented_historical_unavailable',
                scope='Q acceptance preserved; current Q tables compared literally to immutable input'))
        return d

    bundle = load(BUNDLE / 'manifests/bundle.json', 'manifest_input')
    check('immutable bundle43 manifest count', len(bundle['files']) == 43)
    for row in bundle['files']:
        digest_check(row['path'], row['sha256'], 'immutable_bundle')
    for name in ['PLAN.md', 'EXECUTION_SPEC.md', 'RESUME_SPEC.md', 'CHECKPOINT.md']:
        track(ANALYSIS / name, 'plan' if name == 'PLAN.md' else 'spec')
    for relative in [ANALYSIS / 'SYNTHESIS_DECISIONS.md', ANALYSIS / 'NOVELTY_AUDIT.md', Path('docs/literature/2026-10-11-lora-dora-mechanisms.md')]:
        if (repo / relative).is_file():
            track(relative, 'reasoning_input')
    for path in sorted((repo / CODE).glob('*.py')):
        track(path, 'code')
    q = accepted('quality-validation.json', 'build_quality.py')
    c = accepted('component-validation.json', 'build_components.py')
    for k, value in [('accepted_runs', 29), ('baseline_runs', 9), ('baseline_metric_contrasts', 15), ('dense_scorer_rows', 4)]:
        check('Q acceptance count ' + k, q.get(k) == value)
    inv = table(BUNDLE / '01-corpus-quality/tables/run_inventory.csv', 29, ('run_id',), 'input')
    check('29 unique accepted complete runs', len({r['run_id'] for r in inv}) == 29
          and all(r['complete'] == 'True' and r['full_evaluation'] == 'True' for r in inv))
    overview = table(ANALYSIS / 'results/quality-overview.csv', 219, ('row_type', 'run_id', 'metric', 'ci_scope'))
    baseline = table(BUNDLE / '01-corpus-quality/tables/baseline_metrics.csv', 15, category='input')
    contrasts = table(BUNDLE / '01-corpus-quality/tables/baseline_contrasts.csv', 15, category='input')
    literal([r for r in overview if r['row_type'] == 'baseline_mean'], baseline, ['run_id', 'metric'], 'baseline means')
    literal([r for r in overview if r['row_type'] == 'saved_baseline_contrast'], contrasts, ['job', 'contrast', 'metric'], 'baseline contrasts')
    dense = table(ANALYSIS / 'results/numerical-controls.csv', 4, ('actual_reference', 'reference_run', 'intervention_run'))
    metrics = table(BUNDLE / '02-interventions/tables/intervention_metrics.csv', 40, category='input')
    source = {(r['job_id'], r['metric']): r for r in metrics}
    literal(dense, [r for r in metrics if r['job_id'].startswith('gsm8k-dense-')], ['job_id', 'metric'], 'dense controls')
    allrows = table(ANALYSIS / 'results/all-intervention-evidence.csv', 40, ('actual_reference', 'left_run_id', 'right_run_id'))
    literal(allrows, metrics, ['job_id', 'metric'], 'all 40 contrasts')
    expected_jobs = {r['job_id'] for r in metrics}
    check('20 jobs both scorers', len(expected_jobs) == 20 and
          {(r['job_id'], r['metric']) for r in allrows} == {(j, m) for j in expected_jobs for m in METRICS})
    corrected = holm([float(r['existing_raw_p']) for r in allrows])
    check('global40 Holm independently reproduced', all(abs(float(r['global40_holm_p']) - p) < 1e-12 for r, p in zip(allrows, corrected)))
    for filename, n, jobs in [('component-necessity.csv', 4, {'gsm8k-base_magnitude-all', 'gsm8k-remove_d-all'}),
        ('compression-quality.csv', 8, {'gsm8k-r32','gsm8k-e95','gsm8k-e99','gsm8k-lora-matched-impact'})]:
        rows = table(ANALYSIS / 'results' / filename, n, ('job_id','metric','actual_reference'))
        literal(rows, [r for r in metrics if r['job_id'] in jobs], ['job_id','metric'], filename)
        check(filename + ' all requested pairs', {(r['job_id'],r['metric']) for r in rows} == {(j,m) for j in jobs for m in METRICS})
    entropy = table(ANALYSIS / 'results/spectral-entropy.csv', 576, ('source','input_spectrum_sha256','precision_scope','independence_scope'))
    check('entropy four jobs x 144 modules', len({r['job_id'] for r in entropy}) == 4 and
          len({(r['job_id'],r['module']) for r in entropy}) == 576)
    check('entropy finite nonnegative values',all(math.isfinite(float(r[k])) and float(r[k]) >= 0 for r in entropy for k in ['original_H_nats','ideal_H_nats'] if r[k]))
    check('entropy effective rank identities',all(abs(math.exp(float(r[h]))-float(r[e])) < 1e-9 for r in entropy for h,e in [('original_H_nats','original_effective_rank'),('ideal_H_nats','ideal_effective_rank')] if r[h] and r[e]))
    check('entropy ideal retained fraction range',all(0 <= float(r['ideal_energy_retained_fraction']) <= 1+1e-12 for r in entropy if r['ideal_energy_retained_fraction']))
    limits = load(ANALYSIS / 'results/matched-control-limitations.json', 'artifact')
    check('matched control one prompt 54 tokens 144 modules',limits.get('calibration_prompts') == 1 and limits.get('calibration_tokens') == 54 and limits.get('modules') == 144)
    # Source hashes in Q/C acceptance cover all original predictions and code;
    # scores are independently used here only for deterministic arithmetic.
    score_path = track(BUNDLE / '02-interventions/tables/per_example_scores.csv.gz', 'input')
    scores = defaultdict(dict)
    with gzip.open(score_path, 'rt', newline='') as f:
        for row in csv.DictReader(f):
            key, i = (row['run_id'],row['metric']), int(row['test_row_index'])
            if i in scores[key]:
                check('duplicate score ' + str((key,i)), False)
            scores[key][i] = row
    for key, rows in scores.items():
        check('score coverage/binary ' + str(key), set(rows) == set(range(1319)) and
              all(float(r['score']) in (0,1) for r in rows.values()))

    def vectors(runs, metric):
        rows = [[scores[(run,metric)][i] for i in range(1319)] for run in runs]
        fields = ['source_id','prompt_sha256','input_ids_sha256','metric','test_row_index']
        check('alignment ' + str((runs,metric)), all(all(a[k] == b[k] for k in fields)
              for candidate in rows[1:] for a,b in zip(rows[0],candidate)))
        return [[float(r['score']) for r in candidate] for candidate in rows]

    def transition_check(row, left, right):
        observed = Counter((a,b) for a,b in zip(left,right))
        names = {'correct_to_correct':(1,1),'correct_to_wrong':(1,0),'wrong_to_correct':(0,1),'wrong_to_wrong':(0,0)}
        check('transitions ' + str((row.get('job_id'),row['metric'],row.get('left_run_id'))),
              all(int(row[k]) == observed[v] for k,v in names.items()))

    for row in allrows:
        left,right = vectors([row['left_run_id'],row['right_run_id']],row['metric'])
        check('exact reference ' + row['job_id'] + row['metric'], row['left_run_id'] == row['actual_reference'])
        check('score means ' + row['job_id'] + row['metric'],
              abs(sum(left)/1319-float(row['left_mean'])) < 1e-12 and
              abs(sum(right)/1319-float(row['right_mean'])) < 1e-12 and
              abs(sum(b-a for a,b in zip(left,right))/1319-float(row['difference'])) < 1e-12)
        transition_check(row,left,right)
        for delta,label in [(.005,'0_5pp'),(.01,'1pp'),(.02,'2pp')]:
            check('pointwise criterion ' + row['job_id']+row['metric']+label,
                  row['pointwise_lower_gt_minus_'+label] == str(float(row['existing_ci95_low']) > -delta))

    def derived(filename, n, seeds, family):
        rows = table(ANALYSIS / 'results' / filename,n,('difference','z_distribution','seed','resamples','holm_p'))
        check(filename+' specified seeds', [int(r['seed']) for r in rows] == seeds)
        check(filename+' B/family', all(int(r['resamples']) == 50000 and
              int(r.get('holm_family_size',r.get('family_size'))) == family and int(r['n']) == 1319 for r in rows))
        adjusted = holm([float(r['raw_p']) for r in rows])
        check(filename+' Holm',all(abs(float(r['holm_p'])-p) < 1e-12 for r,p in zip(rows,adjusted)))
        for row in rows:
            runs = row['aligned_run_ids']
            runs = json.loads(runs) if runs.startswith('[') else runs.split(';')
            coefs = json.loads(row.get('coefficients','[1,-1,-1,1]'))
            vs = vectors(runs,row['metric'])
            z = [sum(c*v[i] for c,v in zip(coefs,vs)) for i in range(1319)]
            distribution = {str(int(k)):v for k,v in sorted(Counter(z).items())}
            check(filename+' deterministic estimand '+str((row.get('job_id'),row.get('method'),row.get('group'),row['metric'])),
                  abs(sum(z)/1319-float(row['difference'])) < 1e-12 and distribution == json.loads(row['z_distribution']))
        return rows

    derived('compression-difference-in-differences.csv',2,[2026101101,2026101102],2)
    original = derived('compression-original-reference.csv',6,list(range(2026101121,2026101127)),6)
    check('original compression references', all(r['actual_reference'] == BASE for r in original))
    staged = ['L','T','REPORT','claim-evidence']
    if args.final or args.include_localizations:
        staged.remove('L')
        accepted('localization-validation.json','build_localizations.py')
        local = table(ANALYSIS / 'results/localization-effects.csv',28,('method','target','actual_reference'))
        literal(local, [r for r in metrics if 'remove_d-' in r['job_id'] or 'base_magnitude-' in r['job_id']], ['job_id','metric'], 'localization exact historical fields')
        check('localization full 14 condition grid', {(r['method'],r['target'],r['metric']) for r in local} ==
              {(method,target,m) for method in ['remove_d','base_magnitude'] for target in ['all','q','k','v','o','qk','vo'] for m in METRICS})
        interactions = derived('joint-interactions.csv',8,list(range(2026101111,2026101119)),8)
        check('interaction exact reference', all(r['reference_run_id'] == BASE for r in interactions))
        trans = table(ANALYSIS / 'results/paired-outcome-transitions.csv',84,('left_run_id','right_run_id','metric'))
        check('transition references original/base/LoRA', {r['left_run_id'] for r in trans} ==
              {BASE,'gsm8k-quality-greedy/base','gsm8k-quality-greedy/lora'})
        check('84 unique transition pairs',len({(r['left_run_id'],r['right_run_id'],r['metric']) for r in trans}) == 84)
        for row in trans:
            a,b = vectors([row['left_run_id'],row['right_run_id']],row['metric']);transition_check(row,a,b)
    if args.final:
        for name in ['symmetry-scope.md','theory-audit.md','theory-review.md','REPORT.md','limitations.md']:
            path = track(ANALYSIS / 'results' / name,'final_artifact')
            if path.exists():
                check(name+' substantive text',len(path.read_text().strip()) > 200)
        claims = table(ANALYSIS / 'results/claim-evidence.csv',9, category='final_artifact')
        # Final column names are defined by the author; require nine unique L IDs
        # and nonempty evidence/status fields without guessing scientific verdicts.
        id_col = next((k for k in claims[0] if all(r[k] in ['L'+str(i) for i in range(1,10)] for r in claims)),None) if claims else None
        check('claim ledger L1-L9 coverage', id_col is not None and {r[id_col] for r in claims} == {'L'+str(i) for i in range(1,10)})
        for token in ['status','evidence','limitation']:
            columns = [k for k in claims[0] if token in k.lower() or (token == 'limitation' and k == 'what_is_not_identified')] if claims else []
            check('claim ledger nonempty '+token, bool(columns) and all(any(r[k].strip() for k in columns) for r in claims))
        if claims:
            expected_fields = ['claim_id','source_statement','source_url','operational_test','evidence_files','effect_and_uncertainty','status','what_is_not_identified','contribution_type']
            check('claim ledger exact schema',list(claims[0]) == expected_fields)
            check('claim ledger all required cells',all(all(r[k].strip() for k in expected_fields) for r in claims))
            check('claim ledger primary URLs',all(all(url.strip().startswith('https://') for url in r['source_url'].split(';')) for r in claims))
            for row in claims:
                paths = [Path(x.strip()) for x in row['evidence_files'].split(';')]
                check('claim evidence existing relative paths '+row['claim_id'],all(not p.is_absolute() and '..' not in p.parts and (out/p).is_file() for p in paths))
        staged = []
    # Include all current results, even staged ones, with explicit scope labels.
    excluded = {'analysis-manifest.json','integration-validation.json'}
    for path in sorted(out.iterdir()):
        if path.is_file() and path.name not in excluded:
            track(path,'artifact', 'verified' if args.final or (args.include_localizations and path.name.startswith(('localization-', 'joint-interactions', 'paired-outcome'))) or path.name in q['outputs'] or path.name in c['outputs'] else 'present_not_accepted_in_QC_stage')
    # Check preservation at the end, before writing exactly our two files.
    for key,record in list(records.items()):
        path = Path(key) if Path(key).is_absolute() else repo / key
        check('preserved '+key,sha(path) == record['sha256'])
    errors = [r for r in checks if not r['passed']]
    now = datetime.now(timezone.utc).isoformat()
    passed = not errors
    manifest = dict(schema_version=1,created_utc=now,stage='final' if args.final else ('QCL' if args.include_localizations else 'QC'),
        passed=passed,complete=passed and args.final,staged_pending=staged,
        exclusions=['analysis-manifest.json (self hash)','integration-validation.json (volatile report)'],
        files=sorted(records.values(),key=lambda r:r['path']))
    report = dict(schema_version=1,created_utc=now,passed=passed,complete=passed and args.final,
        stage=manifest['stage'],staged_pending=staged,counts=counts,checks=checks,errors=errors,
        historical_provenance=historical,scope='hashes, saved acceptance, schemas/counts/ranges, literal historical fields, deterministic paired-score means/transitions/estimands/Holm; no bootstrap rerun; prose presence/ledger structure only, scientific acceptance by primary investigator',
        immutable_sources_modified=any(not r['passed'] for r in checks if r['name'].startswith('preserved ')),
        environment=dict(python=platform.python_version(),compute='CPU gpu-host, <=2 threads; standard library only'),
        manifest_sha256=None)
    (out/'analysis-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    report['manifest_sha256'] = sha(out/'analysis-manifest.json')
    (out/'integration-validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(dict(passed=passed,complete=report['complete'],stage=report['stage'],checks=len(checks),errors=errors,files=len(records),staged_pending=staged),ensure_ascii=False))
    return 0 if passed else 1


if __name__ == '__main__':
    raise SystemExit(main())
