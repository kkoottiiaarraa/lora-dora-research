#!/usr/bin/env python3
"""CPU-only package C; read frozen data, independently audit paired scores.

Run on compute-host using the existing research venv and at most two BLAS threads.
No model imports, weight reads, new decompositions, inference, or dependencies.
New bootstrap estimands/method/seeds are fixed in EXECUTION_SPEC.md.
"""
import argparse
import csv
import gzip
import hashlib
import json
import platform
from collections import defaultdict
from pathlib import Path

import numpy as np


def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def holm(raw):
    order = np.argsort(raw, kind='stable')
    adjusted = np.empty(len(raw))
    running = 0.0
    for rank, index in enumerate(order):
        running = max(running, (len(raw) - rank) * raw[index])
        adjusted[index] = min(1.0, running)
    return adjusted.tolist()


def write_csv(path, rows):
    fields = list(dict.fromkeys(key for row in rows for key in row))
    with path.open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fields)
        writer.writeheader()
        writer.writerows(rows)


def bootstrap(z, seed):
    values, counts = np.unique(z, return_counts=True)
    observed = float(np.mean(z))
    samples = np.random.default_rng(seed).multinomial(len(z), counts / len(z), size=50000)
    means = samples @ values / len(z)
    low, high = np.percentile(means, [2.5, 97.5])
    p = min(1.0, (1 + int(np.sum(np.abs(means - observed) >= abs(observed) - 1e-12))) / 50001)
    if np.all(z == 0):
        low, high, p = 0.0, 0.0, 1.0
    return dict(difference=observed, ci95_low=float(low), ci95_high=float(high),
                raw_p=p, n=len(z), resamples=50000, seed=seed,
                bootstrap_method='paired empirical iid multinomial bootstrap of z; percentile CI95; centered two-sided p',
                z_distribution=json.dumps({str(int(v)): int(c) for v, c in zip(values, counts)}, sort_keys=True),
                uncertainty_scope='paired test examples conditional on fixed checkpoints; not training uncertainty',
                ci_adjustment='none; pointwise')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, default=Path.cwd())
    args = parser.parse_args()
    repo = args.repo.resolve()
    bundle = repo / 'docs/analysis-preparation/2026-10-11'
    output = repo / 'docs/analysis/2026-10-11/results'
    output.mkdir(parents=True, exist_ok=True)
    records = {r['path']: r for r in json.loads((bundle / 'manifests/bundle.json').read_text())['files']}
    inputs = {}
    checks = []

    def check(name, passed, **details):
        checks.append(dict(name=name, passed=bool(passed), **details))
        if not passed:
            raise ValueError(name + ': ' + str(details))

    def frozen(relative):
        path = bundle / relative
        key = str(path.relative_to(repo))
        actual = digest(path)
        check('bundle hash ' + relative, actual == records[key]['sha256'])
        inputs[key] = actual
        return path

    def table(relative):
        with frozen(relative).open(newline='') as stream:
            return list(csv.DictReader(stream))

    metrics = table('02-interventions/tables/intervention_metrics.csv')
    transitions = {(r['job_id'], r['metric']): r for r in table('02-interventions/tables/paired_transitions.csv')}
    modules = table('03-diagnostics/tables/rank_modules.csv')
    summaries = table('03-diagnostics/tables/rank_job_summary.csv')
    impact = table('03-diagnostics/tables/matched_impact_checks.csv')
    fidelity = table('03-diagnostics/tables/numerical_fidelity.csv')
    for relative in ['02-interventions/validation/checks.json', '03-diagnostics/validation/checks.json']:
        prior = json.loads(frozen(relative).read_text())
        check('prior validation ' + relative, prior.get('passed', prior.get('status') == 'passed'))
    # Check immutable original artifact hashes, including predictions, on server CPU.
    source_manifest = json.loads(frozen('02-interventions/manifests/export.json').read_text())
    for row in source_manifest['inputs']:
        check('original hash ' + row['path'], digest(row['path']) == row['sha256'])
    diagnostic_manifest = json.loads(frozen('03-diagnostics/manifests/hashes.json').read_text())

    score_path = frozen('02-interventions/tables/per_example_scores.csv.gz')
    scores = defaultdict(dict)
    with gzip.open(score_path, 'rt', newline='') as stream:
        for row in csv.DictReader(stream):
            key = (row['run_id'], row['metric'])
            index = int(row['test_row_index'])
            check_key = key + (index,)
            if index in scores[key]:
                raise ValueError('Duplicate score ' + str(check_key))
            scores[key][index] = row
    for key, values in scores.items():
        check('score completeness ' + str(key), set(values) == set(range(1319)))
        check('binary scores ' + str(key), all(float(r['score']) in (0, 1) for r in values.values()))
    check('all 40 unique contrasts', len(metrics) == 40 and len({(r['job_id'], r['metric']) for r in metrics}) == 40)

    def vectors(run_ids, metric):
        rows = [[scores[(run, metric)][i] for i in range(1319)] for run in run_ids]
        alignment = ['test_row_index', 'source_id', 'prompt_sha256', 'input_ids_sha256', 'metric']
        for field in alignment:
            check('alignment ' + metric + ' ' + '|'.join(run_ids) + ' ' + field,
                  all([r[field] for r in candidate] == [r[field] for r in rows[0]] for candidate in rows[1:]))
        check('nonempty source/prompt hashes ' + metric + ' ' + '|'.join(run_ids),
              all(r['source_id'] != '' and len(r['prompt_sha256']) == 64 and len(r['input_ids_sha256']) == 64 for r in rows[0]))
        return [np.array([float(r['score']) for r in candidate]) for candidate in rows]

    global_p = holm([float(r['existing_raw_p']) for r in metrics])
    evidence = []
    for index, row in enumerate(metrics):
        job, metric = row['job_id'], row['metric']
        role = 'lora' if job in {'gsm8k-dense-lora', 'gsm8k-lora-matched-impact'} else 'dora'
        left_run, right_run = row['actual_reference'], job + '/' + role
        left, right = vectors([left_run, right_run], metric)
        check('means ' + job + ' ' + metric,
              abs(left.mean() - float(row['left_mean'])) < 1e-12 and
              abs(right.mean() - float(row['right_mean'])) < 1e-12 and
              abs((right - left).mean() - float(row['difference'])) < 1e-12)
        counts = dict(correct_to_correct=int(np.sum((left == 1) & (right == 1))),
                      correct_to_wrong=int(np.sum((left == 1) & (right == 0))),
                      wrong_to_correct=int(np.sum((left == 0) & (right == 1))),
                      wrong_to_wrong=int(np.sum((left == 0) & (right == 0))))
        prepared = transitions[(job, metric)]
        check('transitions ' + job + ' ' + metric, all(value == int(prepared[key]) for key, value in counts.items()))
        check('transition references ' + job + ' ' + metric,
              row['left_path'] == prepared['left_path'] and row['right_path'] == prepared['right_path'])
        new = dict(row)
        new.update(left_run_id=left_run, right_run_id=right_run,
                   global40_holm_p=global_p[index], global40_family='all 40 saved intervention scorer contrasts',
                   global40_family_size=40, historical_family_scope='family_metric_hypotheses; family_size counts jobs',
                   historical_ci_scope='pointwise paired test-example CI; not simultaneous or training uncertainty',
                   practical_criterion='existing_ci95_low > -delta; pointwise loss exclusion, not functional equivalence',
                   **counts, generated_text_changes=prepared['generated_text_changes'],
                   source_metrics='docs/analysis-preparation/2026-10-11/02-interventions/tables/intervention_metrics.csv',
                   source_transitions='docs/analysis-preparation/2026-10-11/02-interventions/tables/paired_transitions.csv')
        for delta, label in [(.005, '0_5pp'), (.01, '1pp'), (.02, '2pp')]:
            new['pointwise_lower_gt_minus_' + label] = float(row['existing_ci95_low']) > -delta
        evidence.append(new)
    write_csv(output / 'all-intervention-evidence.csv', evidence)

    radial = []
    formulas = {'gsm8k-base_magnitude-all': 'diag(norm_rows(W0)/norm_rows(W0+sBA)) (W0+sBA)',
                'gsm8k-remove_d-all': 'W0+sBA; trained DoRA A/B retained, DoRA dispatcher disabled'}
    for row in evidence:
        if row['job_id'] in formulas:
            check('radial original reference ' + row['job_id'], row['actual_reference'] == 'gsm8k-quality-greedy/dora')
            radial_summary = json.loads((Path(row['right_path']) / 'summary.json').read_text())['intervention']
            check('144 radial modules ' + row['job_id'], len(radial_summary['modules']) == 144 and len(set(radial_summary['modules'])) == 144)
            radial.append(dict(row, intervention_formula=formulas[row['job_id']],
                               estimand='global final-checkpoint intervention minus original PEFT DoRA accuracy',
                               changed_module_count=len(radial_summary['modules']),
                               implementation_source='lora_dora_study/interventions.py',
                               magnitude_activity_status='unavailable: accepted summaries do not record D-I or learned m minus base row norms; BF16 activity not measured'))
    check('four radial rows', len(radial) == 4)
    write_csv(output / 'component-necessity.csv', radial)

    compression_jobs = ['gsm8k-r32', 'gsm8k-e95', 'gsm8k-e99', 'gsm8k-lora-matched-impact']
    summary_by_key = {(r['job'], r['field']): r for r in summaries}
    compression = []
    for row in evidence:
        job = row['job_id']
        if job not in compression_jobs:
            continue
        expected = 'gsm8k-dense-lora/lora' if job == 'gsm8k-lora-matched-impact' else 'gsm8k-dense-dora/dora'
        check('compression dense reference ' + job, row['actual_reference'] == expected)
        new = dict(row, estimand='intervention accuracy minus corresponding dense reference accuracy',
                   module_summary_scope='unweighted min/median/max across 144 modules; not model-global energy or independent replicas',
                   saved_spectrum_stage='input full effective delta, before truncation or attenuation; not post-intervention spectrum',
                   post_intervention_spectrum_available=False,
                   dense_fidelity_scope='original adapter vs dense conversion before rank/attenuation; not post-intervention fidelity',
                   spectrum_entropy_status='saved input and ideal pre-BF16 approximation only; actual post-materialization spectrum unmeasured',
                   rank_precision_scope='recorded kept rank is FP32 SVD approximant before addition to W0 and BF16 linear.weight.copy_; actual finite-precision delta rank unmeasured')
        for field in ['rank', 'retained_energy', 'derived_rank95', 'derived_rank99',
                      'activation.relative_squared_error', 'activation.squared_output_error',
                      'activation.original_update_output_energy', 'attenuation']:
            summary = summary_by_key.get((job, field))
            for stat in ['minimum', 'median', 'maximum']:
                new[field.replace('.', '_') + '_' + stat] = summary[stat] if summary else ''
        if job == 'gsm8k-lora-matched-impact':
            new['retained_energy_field_scope'] = 'saved retained_energy describes preliminary SVD(delta,32), discarded before scalar attenuation; not actual attenuated energy'
            attenuated = [(1 - float(m['attenuation'])) ** 2 for m in modules if m['job'] == job]
            for stat, value in zip(['minimum', 'median', 'maximum'], [min(attenuated), np.median(attenuated), max(attenuated)]):
                new['nominal_attenuated_energy_fraction_' + stat] = float(value)
            new['nominal_attenuated_energy_scope'] = '(1-attenuation)^2 of original LoRA update energy before BF16 materialization; not post-materialization measurement'
        else:
            new['retained_energy_field_scope'] = 'squared input singular values retained by FP32 truncation / total input squared spectrum; before BF16 materialization'
        compression.append(new)
    check('eight compression rows', len(compression) == 8)
    write_csv(output / 'compression-quality.csv', compression)

    # Verify selected raw diagnostic files against immutable export hashes and audit spectra.
    spectrum_audit = {}
    spectral_sources = []
    entropy_rows = []

    def entropy(spectrum):
        energy = np.square(spectrum)
        if energy.sum() == 0:
            return '', ''
        positive = energy[energy > 0] / energy.sum()
        value = float(-np.sum(positive * np.log(positive)))
        return value, float(np.exp(value))

    for job in compression_jobs:
        source = next(m['source'] for m in modules if m['job'] == job)
        check('raw diagnostic hash ' + job, digest(source) == diagnostic_manifest['inputs'][source]['sha256'])
        inputs[source] = digest(source)
        raw = json.loads(Path(source).read_text())
        spectral_sources.append(source)
        check('calibration tokens ' + job, raw['calibration_tokens'] == 54 and all(m['activation']['calibration_tokens'] == 54 for m in raw['modules']))
        check('144 diagnostic modules ' + job, len(raw['modules']) == 144)
        checksums = {}
        for module in raw['modules']:
            spectrum = np.array(module['spectrum'], dtype=float)
            check('valid input spectrum ' + job + ' ' + module['module'],
                  len(spectrum) == min(module['shape']) and np.all(spectrum >= 0) and np.all(spectrum[:-1] >= spectrum[1:]))
            checksums[module['module']] = hashlib.sha256(spectrum.tobytes()).hexdigest()
            original_h, original_rank = entropy(spectrum)
            if job == 'gsm8k-lora-matched-impact':
                ideal_spectrum = spectrum * (1 - module['attenuation'])
                operation = 'uniform attenuation (1-a)*delta; not recorded preliminary rank32 SVD'
                retained_rank = ''
            else:
                ideal_spectrum = spectrum[:module['rank']]
                operation = 'truncate full input spectrum to recorded kept_rank; renormalize squared values'
                retained_rank = module['rank']
            ideal_h, ideal_rank = entropy(ideal_spectrum)
            if job == 'gsm8k-lora-matched-impact':
                check('scalar attenuation entropy invariant ' + module['module'], abs(original_h - ideal_h) < 1e-12)
            entropy_rows.append(dict(job_id=job, role='lora' if job == 'gsm8k-lora-matched-impact' else 'dora',
                module=module['module'], source=source, kept_rank=retained_rank,
                input_spectrum_count=len(spectrum), original_H_nats=original_h,
                original_effective_rank=original_rank, ideal_H_nats=ideal_h, ideal_effective_rank=ideal_rank,
                ideal_energy_retained_fraction=float(np.square(ideal_spectrum).sum() / np.square(spectrum).sum()),
                ideal_operation=operation, entropy_definition='p=sigma^2/sum sigma^2; H=-sum p*ln(p); effective_rank=exp(H)',
                precision_scope='ideal FP32/pre-BF16 operation; post-materialization spectrum unmeasured',
                missing_reason='' if original_h != '' and ideal_h != '' else 'zero spectrum energy',
                independence_scope='same DoRA input repeated in r32/e95/e99; 144 modules are not training replicates',
                input_spectrum_sha256=checksums[module['module']]))
        spectrum_audit[job] = dict(source=source, spectrum_stage='input delta before compression/attenuation',
                                   module_spectrum_sha256=checksums,
                                   delta_definition='effective FP32 adapted weight minus FP32 base',
                                   post_materialization_spectrum_saved=False)
    first = spectrum_audit['gsm8k-r32']['module_spectrum_sha256']
    check('DoRA input spectra repeated across r32/e95/e99', all(spectrum_audit[j]['module_spectrum_sha256'] == first for j in ['gsm8k-e95', 'gsm8k-e99']))
    check('576 entropy rows', len(entropy_rows) == 576)
    write_csv(output / 'spectral-entropy.csv', entropy_rows)
    # Code audit establishes one prompt and ordering; these files are frozen and hashed.
    for relative in ['scripts/series_worker.py', 'lora_dora_study/rank_symmetry.py', 'lora_dora_study/interventions.py']:
        inputs[relative] = digest(repo / relative)
    worker = (repo / 'scripts/series_worker.py').read_text()
    rank_code = (repo / 'lora_dora_study/rank_symmetry.py').read_text()
    check('one prompt implementation', 'calibration.read_text().splitlines()[0]' in worker)
    check('saved spectrum is input before approximation', 'spectrum=s.cpu().tolist()' in rank_code and 'compressed_update(delta' in rank_code)
    check('matched field is before attenuation', rank_code.index('item.update(details)') < rank_code.index("if method=='rank_lora_control':") < rank_code.index('approximation=delta*(1-attenuation)'))
    check('144 matched impact rows', len(impact) == 144 and len({r['module'] for r in impact}) == 144)
    mismatches = [float(r['absolute_mismatch']) for r in impact]
    relative_mismatches = [float(r['relative_mismatch']) for r in impact]
    for row in impact:
        achieved, target = float(row['achieved']), float(row['target'])
        check('matched recomputation ' + row['module'], abs(abs(achieved - target) - float(row['absolute_mismatch'])) < 1e-15)
    limitations = dict(
        status='limited per-module relative activation error matching, not rank matching or equal functional disruption',
        modules=144, calibration_prompts=1, calibration_tokens=54,
        calibration_source='first line of saved training calibration JSONL; first 128 token cap, actual 54 tokens',
        calibration_activations='captured from original adapter forward before dense replacement and interventions; each checkpoint has its own activations',
        matching_target='per-module squared output error divided by own original update output energy',
        control_formula='LoRA delta_control=(1-sqrt(target relative squared error))*delta_LoRA',
        control_rank='nominal <=32 before BF16 materialization; no new measured post-materialization rank',
        absolute_matching_error_min_median_max=[min(mismatches), float(np.median(mismatches)), max(mismatches)],
        relative_matching_error_min_median_max=[min(relative_mismatches), float(np.median(relative_mismatches)), max(relative_mismatches)],
        different_quantities_not_matched=['absolute output perturbation', 'input distributions across checkpoints', 'direction of perturbation',
                                         'test-set activation error', 'combined propagation across 144 modules', 'generation functions', 'training trajectories'],
        matched_retained_energy_warning='saved rank and retained_energy come from preliminary rank32 SVD, then approximation is replaced by scalar attenuation; use nominal_attenuated_energy_fraction fields for analytic pre-BF16 control',
        dense_fidelity_warning='saved dense_fidelity precedes rank/attenuation intervention; does not measure its final fidelity',
        spectra=spectrum_audit,
        entropy='spectral-entropy.csv reports input and ideal pre-BF16 operations only; matched uniform attenuation preserves normalized entropy; repeated DoRA inputs are not independent',
        magnitude_activity='unavailable: no accepted module diagnostic records D-I or learned m minus base norms, or their BF16 effect; do not infer substantial component activity',
        finite_precision_rank='linear weights use original base dtype BF16; copy_(W0+FP32 approximant) casts back; actual BF16 delta rank is unmeasured and need not remain <=32',
        difference_in_differences_scope='difference of observed sensitivity under limited calibration matching; not pure causal rank effect',
        sources=spectral_sources + ['scripts/series_worker.py:103', 'lora_dora_study/rank_symmetry.py'])
    (output / 'matched-control-limitations.json').write_text(json.dumps(limitations, indent=2) + '\n')

    did = []
    run_ids = ['gsm8k-r32/dora', 'gsm8k-dense-dora/dora', 'gsm8k-lora-matched-impact/lora', 'gsm8k-dense-lora/lora']
    for metric, seed in [('author_em', 2026101101), ('final_em', 2026101102)]:
        a, b, c, d = vectors(run_ids, metric)
        result = bootstrap(a - b - c + d, seed)
        result.update(metric=metric, estimand='(r32-denseD)-(matchedL-denseL)',
                      aligned_run_ids=json.dumps(run_ids), coefficients='[1,-1,-1,1]',
                      component_DoRA_difference=float((a - b).mean()), component_LoRA_difference=float((c - d).mean()),
                      interpretation='difference in sensitivity under limited matching; not pure effect of rank',
                      family='two new scorer difference-in-differences', family_size=2)
        did.append(result)
    for row, p in zip(did, holm([r['raw_p'] for r in did])):
        row['holm_p'] = p
    write_csv(output / 'compression-difference-in-differences.csv', did)

    original_comparisons = []
    seed = 2026101121
    for job in ['gsm8k-r32', 'gsm8k-e95', 'gsm8k-e99']:
        for metric in ['author_em', 'final_em']:
            original_run_ids = [job + '/dora', 'gsm8k-quality-greedy/dora']
            changed, original = vectors(original_run_ids, metric)
            result = bootstrap(changed - original, seed)
            result.update(job_id=job, metric=metric, aligned_run_ids=json.dumps(original_run_ids),
                          coefficients='[1,-1]', actual_reference='gsm8k-quality-greedy/dora',
                          estimand='compressed accuracy minus original PEFT DoRA accuracy',
                          family='six exploratory original-reference numerical-sensitivity comparisons', family_size=6,
                          changed_mean=float(changed.mean()), reference_mean=float(original.mean()),
                          precision_scope='ideal FP32 SVD approximant then BF16 weight cast; actual delta rank unmeasured',
                          selection_scope='added after observing dense shift; spec method and seeds fixed before computation')
            for delta, label in [(.005, '0_5pp'), (.01, '1pp'), (.02, '2pp')]:
                result['pointwise_lower_gt_minus_' + label] = result['ci95_low'] > -delta
            original_comparisons.append(result)
            seed += 1
    for row, p in zip(original_comparisons, holm([r['raw_p'] for r in original_comparisons])):
        row['holm_p'] = p
    check('six original-reference rows', len(original_comparisons) == 6)
    write_csv(output / 'compression-original-reference.csv', original_comparisons)

    # Vector plot written as SVG without plotting dependencies.
    from html import escape
    svg = ['<svg xmlns="http://www.w3.org/2000/svg" width="1120" height="480" viewBox="0 0 1120 480">',
           '<rect width="1120" height="480" fill="white"/>',
           '<g font-family="sans-serif" font-size="15" fill="#18212b">',
           '<text x="28" y="30" font-size="20">GSM8K compression: accuracy change from corresponding dense reference</text>',
           '<text x="28" y="55">Historical pointwise 95% paired-example CI; fixed checkpoints, n=1319. Units: percentage points.</text>']
    x = lambda value: 600 + value * 100 * 90
    for tick in [-1, 0, 1, 2, 3]:
        pos = x(tick / 100)
        svg.append(f'<line x1="{pos}" x2="{pos}" y1="76" y2="388" stroke="#ccd2d8"/><text x="{pos-8}" y="410">{tick}</text>')
    for index, row in enumerate(sorted(compression, key=lambda r: (compression_jobs.index(r['job_id']), r['metric']))):
        y = 98 + index * 39
        color = '#1565a7' if row['metric'] == 'author_em' else '#a34a13'
        low, mean, high = [float(row[k]) for k in ['existing_ci95_low', 'difference', 'existing_ci95_high']]
        label = row['job_id'].replace('gsm8k-', '') + ' / ' + row['metric']
        svg.append(f'<text x="28" y="{y+5}">{escape(label)}</text>')
        svg.append(f'<line x1="{x(low)}" x2="{x(high)}" y1="{y}" y2="{y}" stroke="{color}" stroke-width="3"/><circle cx="{x(mean)}" cy="{y}" r="5" fill="{color}"/>')
        svg.append(f'<text x="890" y="{y+5}">{mean*100:+.3f} [{low*100:+.3f}, {high*100:+.3f}]</text>')
    svg += ['<text x="28" y="449">r32/E95/E99 reference: dense DoRA. Matched attenuation reference: dense LoRA.</text>',
            '<text x="28" y="471">Dense conversion already changes generated answers; pre-intervention fidelity does not certify compressed weights.</text>', '</g></svg>']
    (output / 'compression-quality.svg').write_text('\n'.join(svg) + '\n')

    def formatted(row):
        return f"{100*float(row['difference']):+.3f} pp [{100*float(row['existing_ci95_low']):+.3f}, {100*float(row['existing_ci95_high']):+.3f}]"

    lines = ['# Global components and compression', '',
             'Exploratory analysis after data collection. All effects condition on these fixed GSM8K checkpoints and 1319 test examples; no independent training replicates.', '',
             '## Global radial components', '',
             '| Intervention | Scorer | Change vs original PEFT DoRA [pointwise CI95] | Excludes loss >0.5 pp |',
             '|---|---|---|---|']
    for row in radial:
        lines.append(f"| {row['job_id']} | {row['metric']} | {formatted(row)} | {row['pointwise_lower_gt_minus_0_5pp']} |")
    lines += ['',
              'In this final checkpoint, removing the learned diagonal factor or replacing learned magnitude by base row norms does not show a material GSM8K accuracy loss at the stated pointwise 0.5 pp criterion. This is neither equivalence of generated functions nor a simultaneous guarantee. It does not show that magnitude was irrelevant during training, that a newly trained LoRA would reach the same solution, or that the retained BA alone explains why DoRA learned it. Learned A/B and their training history remain present.', '',
              '## Compression relative to dense controls', '',
              '| Intervention | Scorer | Change vs corresponding dense [pointwise CI95] |',
              '|---|---|---|']
    for row in compression:
        lines.append(f"| {row['job_id']} | {row['metric']} | {formatted(row)} |")
    lines += ['',
              'Rank32 and E95 exclude an accuracy loss exceeding 0.5 pp pointwise under both scorers; E99 excludes a loss exceeding 1 pp but does not meet 0.5 pp. These statements concern dense references. All compression historical Holm p values exceed 0.05. Preserved accuracy does not mean preserved answers, and lack of significant harm alone is not equivalence.', '',
              'Rank32 retains the leading 32 singular components of each full effective DoRA delta in its ideal FP32 approximation. Adding W0 and copying into BF16 weights may increase the algebraic rank of the actual materialized delta; that rank is unmeasured. This is not a tested same-rank trained LoRA. E95 has unweighted module rank median 21 (range 1–114); E99 median 303.5 (99–655). These ranks and energies are module summaries, not global model energies or independent experimental units. No correlation is fit across the three compression conditions.', '',
              'All saved spectra in r32/E95/E99 describe the same input DoRA delta before truncation; their per-module hashes agree. spectral-entropy.csv reports 576 module/job rows with input and ideal pre-BF16 normalized squared-spectrum entropy H (natural logarithm) and exp(H). Ideal truncation uses the recorded kept rank; actual post-materialization spectra remain unmeasured. Matched uniform attenuation retains input normalized entropy and scales energy by (1-a)^2. These are descriptive geometric calculations, not a causal entropy experiment or 576 independent checkpoints.', '',
              'The matched-control retained_energy field describes an intermediate rank32 SVD that is discarded before scalar attenuation. It must not be interpreted as the attenuated control retaining 100% of LoRA update energy. Analytic (1-attenuation)^2 fractions are exported separately and labelled before BF16 materialization.', '',
              'No accepted saved diagnostic records learned D-I or learned magnitude minus base row norms, nor their activity in BF16. The numerical size of the removed factor is unavailable. These results therefore cannot establish that a substantially active factor was dispensable, or diagnose whether BF16 rounding attenuated its effect.', '',
              '## Exploratory direct comparison against original PEFT DoRA', '',
              'After observing the dense-conversion shift, six direct paired contrasts were added to the execution spec before computation. They use their own 50,000-resample bootstrap and Holm family of six; original pointwise criteria are not inferred by adding historical CI endpoints.', '',
              '| Intervention | Scorer | Direct change, pp | CI95, pp | Holm (6) | Excludes loss >0.5 pp |',
              '|---|---|---|---|---|---|']
    for row in original_comparisons:
        lines.append(f"| {row['job_id']} | {row['metric']} | {100*row['difference']:+.3f} | [{100*row['ci95_low']:+.3f}, {100*row['ci95_high']:+.3f}] | {row['holm_p']:.6g} | {row['pointwise_lower_gt_minus_0_5pp']} |")
    lines += ['',
              'Against original PEFT DoRA, r32 and E95 exclude a loss exceeding 1 pp pointwise, but cannot exclude 0.5 pp. E99 only meets the 2 pp criterion. Thus the stronger dense-relative 0.5 pp statement does not directly transfer to the original adapter.', '',
              '## Limited calibration matching and sensitivity contrast', '',
              'Per-module relative squared activation perturbation matches closely on one training prompt (54 tokens), using each original checkpoint’s own activations. Absolute perturbations, perturbation directions, combined network effects and test-distribution errors are not matched. Saved dense_fidelity measures adapter-to-dense conversion before compression or attenuation; no final compressed fidelity is certified.', '',
              '| Scorer | (r32−denseD)−(matchedL−denseL), pp | CI95, pp | raw p | Holm (2) |',
              '|---|---|---|---|---|']
    for row in did:
        lines.append(f"| {row['metric']} | {100*row['difference']:+.3f} | [{100*row['ci95_low']:+.3f}, {100*row['ci95_high']:+.3f}] | {row['raw_p']:.6g} | {row['holm_p']:.6g} |")
    lines += ['',
              'The new four-run contrast uses aligned source IDs, prompt/input hashes and scorer, common-index empirical bootstrap (50,000; fixed spec seeds), percentile CI and centered two-sided bootstrap p. It compares sensitivity under this restricted matching, not a pure causal rank effect. Neither scorer establishes a difference in sensitivity.', '',
              '## Descriptive saved-spectrum summaries', '',
              'The following are unweighted medians across 144 modules. The same DoRA input is repeated for three operations; no module-level hypothesis test or cross-condition correlation is used.', '',
              '| Operation | Input H (nats) | Ideal H (nats) | Input exp(H) | Ideal exp(H) | Ideal retained energy fraction |',
              '|---|---|---|---|---|---|']
    for job in compression_jobs:
        rows = [r for r in entropy_rows if r['job_id'] == job]
        values = [float(np.median([r[field] for r in rows])) for field in ['original_H_nats', 'ideal_H_nats', 'original_effective_rank', 'ideal_effective_rank', 'ideal_energy_retained_fraction']]
        lines.append('| ' + job + ' | ' + ' | '.join(f'{value:.6f}' for value in values) + ' |')
    lines += ['',
              'Lower ideal entropy and near-preserved accuracy here constrain the necessity of the removed ideal spectral tail in this construction. They do not isolate entropy from energy, singular-vector changes, BF16 materialization, or movement toward the base weights, and do not establish an entropy cause of training success.', '',
              '## Multiplicity and practical criteria', '',
              f"All 40 saved contrasts and their literal historical estimates/CI/p are retained. Global Holm across all 40 raw p leaves {sum(p < .05 for p in global_p)} contrasts below 0.05; this sensitivity analysis does not replace historical families or account for the full adaptive research process.", '',
              'The 0.5/1/2 pp columns test lower_CI > −δ using existing pointwise intervals. They are thresholds for excluding specified accuracy losses, not formal simultaneous noninferiority, two-sided mathematical equivalence, function equivalence, or training uncertainty.', '',
              'Reproduce on server: `OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 ./artifacts execution/scientific-analysis/build_components.py --repo ./artifacts`.', '',
              'Inputs and independent checks are recorded in component-validation.json; source metadata and scope details are in matched-control-limitations.json. New output manifest is coordinated by the main analysis agent.']
    (output / 'component-findings.md').write_text('\n'.join(lines) + '\n')
    for relative in ['docs/analysis/2026-10-11/PLAN.md', 'docs/analysis/2026-10-11/EXECUTION_SPEC.md', 'execution/scientific-analysis/build_components.py']:
        inputs[relative] = digest(repo / relative)
    output_paths = ['component-necessity.csv', 'compression-quality.csv', 'all-intervention-evidence.csv',
                    'compression-difference-in-differences.csv', 'matched-control-limitations.json',
                    'compression-original-reference.csv', 'spectral-entropy.csv',
                    'compression-quality.svg', 'component-findings.md']
    validation = dict(passed=all(r['passed'] for r in checks), checks=checks,
                      counts=dict(all_contrasts=len(evidence), radial_rows=len(radial), compression_rows=len(compression), did_rows=len(did), original_reference_rows=len(original_comparisons), entropy_rows=len(entropy_rows)),
                      environment=dict(python=platform.python_version(), numpy=np.__version__, host_scope='CPU compute-host; no model computation'),
                      inputs=inputs, outputs={name: digest(output / name) for name in output_paths},
                      bootstrap=dict(B=50000, seeds={'author_em': 2026101101, 'final_em': 2026101102}, original_reference_seeds=list(range(2026101121, 2026101127)),
                                     method='NumPy default_rng multinomial common-index empirical distribution; percentile CI; centered two-sided p'),
                      source_hashes_verified=len(source_manifest['inputs']),
                      practical_criteria='pointwise lower confidence bound exceeds -0.005/-0.01/-0.02; no simultaneous guarantee',
                      global40_holm_significant=sum(p < .05 for p in global_p))
    (output / 'component-validation.json').write_text(json.dumps(validation, indent=2) + '\n')
    print(json.dumps(dict(passed=validation['passed'], counts=validation['counts'], did=did, original_reference=original_comparisons,
                          global40_holm_significant=validation['global40_holm_significant'],
                          matching_abs_max=max(mismatches), matching_relative_max=max(relative_mismatches)), indent=2))


if __name__ == '__main__':
    main()
