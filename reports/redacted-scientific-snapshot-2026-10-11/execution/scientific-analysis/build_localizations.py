# Redacted reading copy. Canonical execution requires private provenance inputs.
#!artifact://local/usr/bin/env python3
"""Package L: CPU-only read-only analysis of frozen final-checkpoint scores.

No models, weights, new forward passes, SVD, or dependency installation.
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


N, B = 1319, 50000
METHODS = ['remove_d', 'base_magnitude']
TARGETS = ['all', 'q', 'k', 'v', 'o', 'qk', 'vo']
METRICS = ['author_em', 'final_em']
BASELINE = 'gsm8k-quality-greedy/dora'


def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def write_csv(path, rows):
    fields = list(dict.fromkeys(k for row in rows for k in row))
    with path.open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fields)
        writer.writeheader()
        writer.writerows(rows)


def holm(raw):
    order = np.argsort(raw, kind='stable')
    adjusted = np.empty(len(raw))
    running = 0.0
    for rank, index in enumerate(order):
        running = max(running, (len(raw) - rank) * raw[index])
        adjusted[index] = min(1.0, running)
    return adjusted.tolist()


def bootstrap(z, seed):
    values, counts = np.unique(z, return_counts=True)
    mean = float(z.mean())
    samples = np.random.default_rng(seed).multinomial(N, counts / N, size=B)
    boot = samples @ values / N
    lo, hi = np.percentile(boot, [2.5, 97.5])
    p = min(1.0, (1 + int(np.sum(np.abs(boot - mean) >= abs(mean) - 1e-12))) / (B + 1))
    if np.all(z == 0):
        lo, hi, p = 0.0, 0.0, 1.0
    return dict(difference=mean, ci95_low=float(lo), ci95_high=float(hi), raw_p=p,
                n=N, resamples=B, seed=seed, rng='NumPy default_rng',
                bootstrap_method='paired empirical iid multinomial bootstrap of z; percentile CI95; centered two-sided p',
                z_distribution=json.dumps({str(int(v)): int(c) for v, c in zip(values, counts)}, sort_keys=True),
                ci_adjustment='none; pointwise',
                uncertainty_scope='test examples conditional on fixed checkpoints; not independent training uncertainty')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, default=Path.cwd())
    args = parser.parse_args()
    repo = args.repo.resolve()
    bundle = repo / 'docs/analysis-preparation/2026-10-11'
    out = repo / 'docs/analysis/2026-10-11/results'
    out.mkdir(parents=True, exist_ok=True)
    manifest = {r['path']: r for r in json.loads((bundle / 'manifests/bundle.json').read_text())['files']}
    inputs, checks = {}, []

    def check(name, passed, **details):
        checks.append(dict(name=name, passed=bool(passed), **details))
        if not passed:
            raise ValueError(name + ': ' + str(details))

    def frozen(relative):
        path = bundle / relative
        key = str(path.relative_to(repo))
        sha = digest(path)
        check('bundle hash ' + relative, sha == manifest[key]['sha256'])
        inputs[key] = sha
        return path

    def table(relative):
        with frozen(relative).open(newline='') as stream:
            return list(csv.DictReader(stream))

    grid = table('02-interventions/tables/localization_grid.csv')
    descriptive = table('02-interventions/tables/localization_interactions.csv')
    saved_transitions = {(r['job_id'], r['metric']): r for r in table('02-interventions/tables/paired_transitions.csv')}
    metrics = {(r['job_id'], r['metric']): r for r in table('02-interventions/tables/intervention_metrics.csv')}
    source = json.loads(frozen('02-interventions/manifests/export.json').read_text())
    for row in source['inputs']:
        check('original source hash ' + row['path'], digest(row['path']) == row['sha256'])
    prior = json.loads(frozen('02-interventions/validation/checks.json').read_text())
    check('prior immutable bundle validation', prior.get('passed', prior.get('status') == 'passed'))
    c_path = out / 'all-intervention-evidence.csv'
    inputs[str(c_path.relative_to(repo))] = digest(c_path)
    with c_path.open(newline='') as stream:
        evidence = {(r['job_id'], r['metric']): r for r in csv.DictReader(stream)}
    check('all 40 unique C ledger rows', len(evidence) == 40)

    scores = defaultdict(dict)
    with gzip.open(frozen('02-interventions/tables/per_example_scores.csv.gz'), 'rt', newline='') as stream:
        for row in csv.DictReader(stream):
            key = row['run_id'], row['metric']
            index = int(row['test_row_index'])
            if index in scores[key]:
                raise ValueError('duplicate score ' + str((key, index)))
            scores[key][index] = row
    for key, data in scores.items():
        check('complete gap-free score indices ' + str(key), set(data) == set(range(N)))
        check('binary score values ' + str(key), all(float(r['score']) in (0, 1) for r in data.values()))

    def vectors(run_ids, metric):
        rows = [[scores[(run, metric)][i] for i in range(N)] for run in run_ids]
        for field in ['test_row_index', 'source_id', 'prompt_sha256', 'input_ids_sha256', 'metric']:
            check('aligned ' + metric + ' ' + '|'.join(run_ids) + ' ' + field,
                  all([r[field] for r in candidate] == [r[field] for r in rows[0]] for candidate in rows[1:]))
        check('nonempty source and complete hashes ' + metric + ' ' + '|'.join(run_ids),
              all(r['source_id'] and len(r['prompt_sha256']) == 64 and len(r['input_ids_sha256']) == 64 for r in rows[0]))
        return [np.array([float(r['score']) for r in candidate]) for candidate in rows]

    expected = {(m, t, s) for m in METHODS for t in TARGETS for s in METRICS}
    check('complete 28 localization cells', len(grid) == 28 and {(r['method'], r['target'], r['metric']) for r in grid} == expected)
    effects, transitions = [], []
    for cell in grid:
        job, scorer = cell['job_id'], cell['metric']
        row = evidence[(job, scorer)]
        check('C exact pair equals immutable metrics ' + job + ' ' + scorer,
              all(row[k] == v for k, v in metrics[(job, scorer)].items()))
        check('original DoRA reference ' + job + ' ' + scorer,
              cell['reference'] == row['actual_reference'] == row['left_run_id'] == BASELINE and row['right_run_id'] == job + '/dora')
        left, right = vectors([BASELINE, row['right_run_id']], scorer)
        check('recomputed localization means ' + job + ' ' + scorer,
              abs(left.mean() - float(row['left_mean'])) < 1e-12 and abs(right.mean() - float(row['right_mean'])) < 1e-12 and
              abs((right - left).mean() - float(row['difference'])) < 1e-12 and abs(float(row['difference']) - float(cell['difference'])) < 1e-12)
        effect = dict(row, method=cell['method'], target=cell['target'],
                      estimand='final-checkpoint intervention minus original PEFT DoRA accuracy',
                      source_grid='docs/analysis-preparation/2026-10-11/02-interventions/tables/localization_grid.csv')
        effects.append(effect)
        for reference in [BASELINE, 'gsm8k-quality-greedy/base', 'gsm8k-quality-greedy/lora']:
            a, b = vectors([reference, row['right_run_id']], scorer)
            counts = dict(correct_to_correct=int(np.sum((a == 1) & (b == 1))),
                          correct_to_wrong=int(np.sum((a == 1) & (b == 0))),
                          wrong_to_correct=int(np.sum((a == 0) & (b == 1))),
                          wrong_to_wrong=int(np.sum((a == 0) & (b == 0))))
            check('transition total ' + job + ' ' + scorer + ' ' + reference, sum(counts.values()) == N)
            check('transition net change ' + job + ' ' + scorer + ' ' + reference,
                  abs((counts['wrong_to_correct'] - counts['correct_to_wrong']) / N - (b - a).mean()) < 1e-12)
            if reference == BASELINE:
                old = saved_transitions[(job, scorer)]
                check('saved and C transitions ' + job + ' ' + scorer,
                      all(value == int(old[k]) == int(row[k]) for k, value in counts.items()) and
                      old['left_path'] == row['left_path'] and old['right_path'] == row['right_path'])
            transitions.append(dict(method=cell['method'], target=cell['target'], job_id=job, metric=scorer,
                                    left_run_id=reference, right_run_id=row['right_run_id'], n=N,
                                    reference_mean=float(a.mean()), intervention_mean=float(b.mean()), difference=float((b-a).mean()),
                                    **counts, reference_correct_n=int(a.sum()), reference_wrong_n=int(N-a.sum()),
                                    break_rate_given_reference_correct=counts['correct_to_wrong'] / a.sum(),
                                    repair_rate_given_reference_wrong=counts['wrong_to_correct'] / (N-a.sum()),
                                    subset_scope='counts cover all 1319 cases; outcome-conditioned rates are descriptive only',
                                    generated_text_changes_vs_original_DoRA=row['generated_text_changes'],
                                    generated_text_change_scope='saved original-DoRA pair only, not base/LoRA pair',
                                    source_scores='docs/analysis-preparation/2026-10-11/02-interventions/tables/per_example_scores.csv.gz'))
    write_csv(out / 'localization-effects.csv', effects)
    check('all-case transitions for 14 conditions x 2 scorers x 3 references', len(transitions) == 84)
    write_csv(out / 'paired-outcome-transitions.csv', transitions)

    prepared = {(r['method'], r['interaction'], r['metric']): r for r in descriptive}
    interactions = []
    for method in METHODS:
        for group, t1, t2 in [('QK', 'q', 'k'), ('VO', 'v', 'o')]:
            for scorer in METRICS:
                row = prepared[(method, 'I_' + group, scorer)]
                run_ids = [row[k] + '/dora' for k in ['joint', 'single1', 'single2']] + [BASELINE]
                joint, single1, single2, original = vectors(run_ids, scorer)
                z = joint - single1 - single2 + original
                stat = bootstrap(z, 2026101111 + len(interactions))
                check('interaction mean matches frozen descriptive ' + method + ' ' + group + ' ' + scorer,
                      abs(stat['difference'] - float(row['value'])) < 1e-12 and int(row['n']) == N)
                # The four scalar effects also reproduce the same estimand.
                by_target = {r['target']: float(r['difference']) for r in effects if r['method'] == method and r['metric'] == scorer}
                check('interaction equals joint minus single effects ' + method + ' ' + group + ' ' + scorer,
                      abs(stat['difference'] - (by_target[group.lower()] - by_target[t1] - by_target[t2])) < 1e-12)
                interactions.append(dict(method=method, group=group, metric=scorer, **stat,
                                         formula='mean(Y_joint-Y_single1-Y_single2+Y_original_DoRA)',
                                         joint_run_id=run_ids[0], single1_run_id=run_ids[1], single2_run_id=run_ids[2], reference_run_id=BASELINE,
                                         aligned_run_ids=';'.join(run_ids), run_paths=row['run_paths'],
                                         joint_mean=float(joint.mean()), single1_mean=float(single1.mean()), single2_mean=float(single2.mean()), reference_mean=float(original.mean()),
                                         historical_inferential_statistics='none existed for derived interaction; single-contrast p not inherited',
                                         source_descriptive='docs/analysis-preparation/2026-10-11/02-interventions/tables/localization_interactions.csv',
                                         exploratory=True, interaction_scale='binary correctness; ceiling/floor and nonlinear score mapping possible'))
    check('all eight interactions and fixed seed order', len(interactions) == 8 and [r['seed'] for r in interactions] == list(range(2026101111, 2026101119)))
    for row, p in zip(interactions, holm([r['raw_p'] for r in interactions])):
        row.update(holm_p=p, holm_family='eight exploratory method x joint-group x scorer interactions', holm_family_size=8,
                   family_scope='does not control the full adaptive research search')
    write_csv(out / 'joint-interactions.csv', interactions)

    # Standalone vector figure from conventional matplotlib, on server CPU.
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    plt.rcParams.update({'font.size': 10, 'svg.fonttype': 'none'})
    fig, axes = plt.subplots(1, 2, figsize=(12, 5.8), sharex=True)
    for ax, method in zip(axes, METHODS):
        for scorer, offset, color in [('author_em', -.10, '#275DAD'), ('final_em', .10, '#B24729')]:
            rows = [next(r for r in effects if r['method'] == method and r['target'] == t and r['metric'] == scorer) for t in TARGETS]
            means = np.array([float(r['difference']) * 100 for r in rows])
            lows = np.array([float(r['existing_ci95_low']) * 100 for r in rows])
            highs = np.array([float(r['existing_ci95_high']) * 100 for r in rows])
            ax.errorbar(means, np.arange(7) + offset, xerr=[means-lows, highs-means], fmt='o', markersize=4, capsize=3, label=scorer, color=color)
        ax.axvline(0, color='#555555', lw=.8)
        ax.axvline(-1, color='#888888', lw=.8, ls='--')
        ax.set_yticks(range(7), [t.upper() for t in TARGETS])
        ax.invert_yaxis()
        ax.set_title(method)
        ax.set_xlabel('Accuracy change vs original DoRA (percentage points)')
        ax.grid(axis='x', alpha=.2)
        ax.legend(loc='lower right')
    fig.suptitle('All 28 radial localization contrasts; original PEFT DoRA reference')
    fig.text(.5, .025, 'Saved pointwise paired-example 95% CI; fixed checkpoints. Dashed: −1 pp. No simultaneous guarantee.\nAll projection sets are across layers. Quality preservation does not imply function equivalence.', ha='center', fontsize=9)
    fig.tight_layout(rect=[0, .09, 1, .93])
    fig.savefig(out / 'localization-effects.svg')
    plt.close(fig)

    def pp(value):
        return f'{100 * float(value):+.3f}'

    lines = [
        '# Локализация финального вмешательства: все 28 сравнений', '',
        'Данные: Qwen3-4B, один публичный финальный DoRA checkpoint, GSM8K test, 1319 парных примеров, фиксированный greedy evaluator. Два scorer показаны отдельно. Все эффекты ниже — в процентных пунктах, вмешательство минус исходная PEFT DoRA; это не сравнение независимо обученных моделей. План составлен после получения данных, расчёты exploratory.', '',
        'Область вмешательства — соответствующий набор Q/K/V/O проекций во всех слоях. `remove_d` сохраняет обученные DoRA A/B и отключает DoRA dispatcher: W0+sBA. `base_magnitude` заменяет обученную норму на норму базы при сохранении направления W0+sBA. Эти операции различаются; сопоставление их эффектов не изолирует единственную обучаемую переменную. Активность радиального множителя после BF16 отдельно не измерена.', '',
        '| Метод | Область | author_em Δ [95% CI] | final_em Δ [95% CI] |',
        '|---|---|---:|---:|',
    ]
    by_key = {(r['method'], r['target'], r['metric']): r for r in effects}
    for method in METHODS:
        for target in TARGETS:
            cells = [by_key[(method, target, s)] for s in METRICS]
            desc = [f"{pp(r['difference'])} [{pp(r['existing_ci95_low'])}, {pp(r['existing_ci95_high'])}]" for r in cells]
            lines.append(f'| {method} | {target.upper()} | {desc[0]} | {desc[1]} |')
    lines.extend(['',
        'Оба метода дают положительный point estimate для Q и отрицательный для K на обоих scorers. Глобальное all вмешательство также имеет положительный point estimate. Это описательная неоднородность мест вмешательства, а не доказанная разница между Q и K: отдельного заранее заданного Q−K контраста здесь нет. Совместные QK/VO и all оценены непосредственно; складывать singles, чтобы получить эффект joint/all, нельзя.', '',
        'Сохранённые интервалы относятся к конкретным exact pairs. Исторические raw p/Holm сохранены буквально вместе с фактической семьёй и её размером в CSV; новая общая Holm40 чувствительность взята из независимо проверенного пакета C и не заменяет историю. Интервалы pointwise, по тестовым примерам при фиксированных checkpoints, без одновременной гарантии.', '',
    ])
    significant = sum(float(r['global40_holm_p']) < .05 for r in effects)
    loss_counts = [sum(r['pointwise_lower_gt_minus_' + label] == 'True' for r in effects) for label in ['0_5pp', '1pp', '2pp']]
    zero_excluded = sum(float(r['existing_ci95_low']) > 0 or float(r['existing_ci95_high']) < 0 for r in effects)
    lines.extend([
        f'После общей Holm40 поправки значимых при .05 localization contrasts: {significant}/28. Pointwise CI исключают ноль в {zero_excluded}/28 случаях. Поэтому знак отдельных средних не следует превращать в установленное улучшение или ухудшение.', '',
        f'Рабочий критерий сохранения accuracy: lower CI > −δ. Число удовлетворяющих ячеек для δ=0.5/1/2 п.п.: {loss_counts[0]}/{loss_counts[1]}/{loss_counts[2]} из 28. Это чувствительность к выбранным сейчас практическим границам, без одновременной гарантии, математической эквивалентности или равенства функции. p>0.05 не доказывает сохранение качества.', '',
        '## Совместные эффекты на бинарной шкале', '',
        'Estimand: I = mean(Y_joint−Y_single1−Y_single2+Y_DoRA). Все четыре score-вектора выровнены по test_row_index, source_id, prompt/input hashes и scorer; общие индексы эквивалентно ресемплируются через multinomial распределение уникальных z. B=50000, NumPy default_rng, фиксированные seeds 2026101111–2026101118, percentile CI95; двухсторонний centered bootstrap p с +1 коррекцией. Отдельная Holm family 8 не покрывает весь адаптивный исследовательский поиск.', '',
        '| Метод | Joint | Scorer | I, п.п. [95% CI] | raw p | Holm8 p |',
        '|---|---|---|---:|---:|---:|',
    ])
    for r in interactions:
        lines.append(f"| {r['method']} | {r['group']} | {r['metric']} | {pp(r['difference'])} [{pp(r['ci95_low'])}, {pp(r['ci95_high'])}] | {r['raw_p']:.4f} | {r['holm_p']:.4f} |")
    sig_i = sum(r['holm_p'] < .05 for r in interactions)
    lines.extend(['',
        f'Число interactions с Holm8 p<.05: {sig_i}/8. Наибольший point estimate — base_magnitude VO. Ширина интервалов показывает доступную точность; отсутствие значимости не устанавливает аддитивность. Даже ненулевой I на бинарной шкале не идентифицирует уникальный механизм attention: потолок/пол и нелинейное отображение внутренних изменений в correctness могут создавать interaction.', '',
        '## Переходы по всем примерам', '',
        '`paired-outcome-transitions.csv` содержит все 84 пары: 14 условий × 2 scorer × 3 references (исходная DoRA, база, LoRA). Каждая строка включает все 1319 cases: correct→correct, correct→wrong, wrong→correct, wrong→wrong. Приведённые ниже исправления/поломки относятся к исходной DoRA; outcome-conditioned доли в CSV только описательные и не являются внешними причинными стратами.', '',
        '| Метод | Область | author: исправления / поломки | final: исправления / поломки |',
        '|---|---|---:|---:|',
    ])
    for method in METHODS:
        for target in TARGETS:
            rr = [by_key[(method, target, s)] for s in METRICS]
            lines.append(f"| {method} | {target.upper()} | {rr[0]['wrong_to_correct']} / {rr[0]['correct_to_wrong']} | {rr[1]['wrong_to_correct']} / {rr[1]['correct_to_wrong']} |")
    lines.extend(['',
        'Исправления сосуществуют с поломками; малое изменение среднего не означает сохранения ответов. Saved generated_text_changes относятся к исходной DoRA и явно подписаны, для base/LoRA такие текстовые числа не достраиваются. Сохранение accuracy в этой задаче не устанавливает функцию на всех входах, перенос на другие задачи, преимущество обучения DoRA или необходимость/избыточность компонента вдоль обучающей траектории.', '',
        'Все 28 means повторяют immutable localization_grid; все восемь I повторяют подготовленные descriptive interactions до новых CI/p. Хеши frozen inputs и исходных manifest paths проверены read-only на сервере; пропусков, дубликатов и нарушений парного alignment нет. `localization-validation.json` содержит проверки и hashes точных входов/кода/выходов. Новых baseline tests, forward или SVD не выполнялось.', '',
    ])
    (out / 'localization-findings.md').write_text('\n'.join(lines))
    outputs = ['localization-effects.csv', 'joint-interactions.csv', 'paired-outcome-transitions.csv', 'localization-effects.svg', 'localization-findings.md']
    summary = dict(passed=all(r['passed'] for r in checks), package='L', n=N, localization_rows=len(effects), interaction_rows=len(interactions), transition_rows=len(transitions),
                   checks=checks, inputs=inputs, immutable_bundle_manifest_sha256=digest(bundle / 'manifests/bundle.json'),
                   code_sha256=digest(Path(__file__)), plan_sha256=digest(repo / 'docs/analysis/2026-10-11/PLAN.md'),
                   execution_spec_sha256=digest(repo / 'docs/analysis/2026-10-11/EXECUTION_SPEC.md'),
                   outputs={p: digest(out / p) for p in outputs}, python=platform.python_version(), numpy=np.__version__, matplotlib=matplotlib.__version__,
                   execution='CPU [private-context]; numerical thread limits supplied by launcher; no model computations',
                   seeds=[r['seed'] for r in interactions], bootstrap_resamples=B,
                   significant_global40_localization_rows=significant, significant_holm8_interactions=sig_i,
                   pointwise_loss_exclusion_counts=dict(zip(['0.5pp', '1pp', '2pp'], loss_counts)))
    (out / 'localization-validation.json').write_text(json.dumps(summary, indent=2) + '\n')
    print(json.dumps({k: summary[k] for k in ['passed', 'localization_rows', 'interaction_rows', 'transition_rows', 'significant_global40_localization_rows', 'significant_holm8_interactions', 'pointwise_loss_exclusion_counts']}))
    for row in interactions:
        print(json.dumps({k: row[k] for k in ['method', 'group', 'metric', 'difference', 'ci95_low', 'ci95_high', 'raw_p', 'holm_p', 'seed']}))


if __name__ == '__main__':
    main()
