#!/usr/bin/env python3
"""Package A: frozen GSM8K paired direct contrasts; CPU only, no model imports."""
import os
for _v in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS', 'NUMEXPR_NUM_THREADS', 'VECLIB_MAXIMUM_THREADS', 'BLIS_NUM_THREADS'):
    os.environ[_v] = '2'
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

PREP = Path('docs/analysis-preparation/2026-10-11')
RESULTS = Path('docs/analysis/2026-10-11/results')
OUTPUT = Path('docs/analysis-followup/2026-10-11/A-direct-contrasts')
CODE = Path('execution/existing-data-followup/build_direct_contrasts.py')
SCORERS = ('author_em', 'final_em')
CONTRASTS = (
    ('remove_D_all_minus_LoRA', 'gsm8k-quality-greedy/lora', 'gsm8k-remove_d-all/dora'),
    ('base_magnitude_all_minus_LoRA', 'gsm8k-quality-greedy/lora', 'gsm8k-base_magnitude-all/dora'),
    ('remove_D_Q_minus_K', 'gsm8k-remove_d-k/dora', 'gsm8k-remove_d-q/dora'),
    ('base_magnitude_Q_minus_K', 'gsm8k-base_magnitude-k/dora', 'gsm8k-base_magnitude-q/dora'),
)
N = 1319
B = 50000
BASE_SEED = 2026101140
CHECKS = []
CASE_CHECKS = {}

def check(label, condition, **details):
    case_category = next((prefix for prefix in ('Binary unique', 'Aligned identifiers/hashes') if label.startswith(prefix)), None)
    if case_category and condition:
        CASE_CHECKS[case_category] = CASE_CHECKS.get(case_category, 0) + 1
    else:
        CHECKS.append({'check': label, 'passed': bool(condition), **details})
    if not condition:
        raise AssertionError(label + ': ' + repr(details))

def sha(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()

def rows(path):
    with open(path, newline='') as f:
        return list(csv.DictReader(f))

def dump(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')

def exact_mcnemar(n01, n10):
    """Integer binomial sum, avoiding floating-tail underflow for n <= 1319."""
    d = n01 + n10
    if d == 0:
        return 1.0
    numerator = 2 * sum(math.comb(d, k) for k in range(min(n01, n10) + 1))
    return min(1.0, numerator / (1 << d))

def holm(ps):
    order = np.argsort(ps, kind='stable')
    result = np.empty(len(ps), dtype=float)
    previous = 0.0
    for rank, ix in enumerate(order):
        previous = max(previous, min(1.0, (len(ps) - rank) * ps[ix]))
        result[ix] = previous
    return result

def paired_bootstrap(z, seed, draws=B):
    counts = np.bincount(z.astype(np.int64) + 1, minlength=3)
    rng = np.random.default_rng(seed)
    sampled = rng.multinomial(len(z), counts / len(z), size=draws)
    mus = (sampled[:, 2] - sampled[:, 0]) / len(z)
    return np.quantile(mus, [0.025, 0.975], method='linear'), mus, counts

def toys():
    check('McNemar no discordance', exact_mcnemar(0, 0) == 1.0)
    check('McNemar all six discordances one direction', exact_mcnemar(0, 6) == 0.03125)
    check('McNemar balanced', exact_mcnemar(10, 10) == 1.0)
    for a in range(8):
        for b in range(8):
            check(f'McNemar symmetry {a}:{b}', exact_mcnemar(a, b) == exact_mcnemar(b, a))
    check('Holm known ordered example', np.allclose(holm([0.04, 0.001, 0.01]), [0.04, 0.003, 0.02], atol=0, rtol=1e-14))
    check('Holm ties', np.array_equal(holm([0.01, 0.01, 1.0]), [0.03, 0.03, 1.0]))
    z = np.array([-1, 0, 1], dtype=np.int64)
    enum = {}
    for indexes in itertools.product(range(3), repeat=3):
        c = tuple(np.bincount(z[list(indexes)] + 1, minlength=3))
        enum[c] = enum.get(c, 0) + 1
    for c, count in enum.items():
        multinomial_ways = math.factorial(3) // math.prod(math.factorial(int(k)) for k in c)
        check('Exact indexed/multinomial bootstrap distribution ' + str(c), count == multinomial_ways)
    for val in (-1, 0, 1):
        ci, means, _ = paired_bootstrap(np.full(7, val, dtype=int), 7, 1000)
        check(f'Constant z={val} bootstrap', np.all(ci == val) and np.all(means == val))
    _, means, counts = paired_bootstrap(z, 211, 50000)
    expected_var = np.var(z) / len(z)
    check('Toy bootstrap mean', abs(float(means.mean())) < 6 * math.sqrt(expected_var / len(means)))
    check('Toy bootstrap variance', abs(float(means.var()) - expected_var) < 0.01)
    ci1, mu1, _ = paired_bootstrap(z, 9, 100)
    ci2, mu2, _ = paired_bootstrap(z, 9, 100)
    check('Bootstrap deterministic repeated seed', np.array_equal(mu1, mu2) and np.array_equal(ci1, ci2))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--repo-root', type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    root = args.repo_root.resolve()
    os.chdir(root)
    start = time.perf_counter()
    OUTPUT.mkdir(parents=True, exist_ok=True)
    toys()
    sources = [PREP / '02-interventions/tables' / name for name in ('per_example_scores.csv.gz', 'intervention_metrics.csv', 'paired_transitions.csv', 'localization_grid.csv')]
    accepted = RESULTS / 'paired-outcome-transitions.csv'
    bundle_path = PREP / 'manifests/bundle.json'
    analysis_manifest_path = RESULTS / 'analysis-manifest.json'
    frozen = {r['path']: r for r in json.loads(bundle_path.read_text())['files']}
    inputs = []
    for path in sources:
        actual = sha(path)
        check('Frozen hash ' + str(path), actual == frozen[str(path)]['sha256'])
        inputs.append({'path': str(path), 'sha256': actual, 'bytes': path.stat().st_size, 'verified_against': str(bundle_path)})
    am = json.loads(analysis_manifest_path.read_text())
    accepted_matches = [r for r in am['files'] if r['path'].endswith('/' + str(accepted)) or r['path'] == str(accepted)]
    check('Accepted transitions manifest entry unique', len(accepted_matches) == 1)
    check('Accepted transitions frozen hash', sha(accepted) == accepted_matches[0]['sha256'])
    inputs.append({'path': str(accepted), 'sha256': sha(accepted), 'bytes': accepted.stat().st_size, 'verified_against': str(analysis_manifest_path)})
    for p in (bundle_path, analysis_manifest_path, Path('docs/analysis-followup/2026-10-11/SPEC.md')):
        inputs.append({'path': str(p), 'sha256': sha(p), 'bytes': p.stat().st_size})
    required = {run for _, l, r in CONTRASTS for run in (l, r)}
    vectors = {(run, m): {} for run in required for m in SCORERS}
    with gzip.open(sources[0], 'rt', newline='') as f:
        all_runs = set()
        for row in csv.DictReader(f):
            all_runs.add(row['run_id'])
            key = (row['run_id'], row['metric'])
            if key not in vectors:
                continue
            ix = int(row['test_row_index'])
            score = float(row['score'])
            check(f'Binary unique {key}/{ix}', score in (0.0, 1.0) and ix not in vectors[key])
            vectors[key][ix] = (row['source_id'], row['prompt_sha256'], row['input_ids_sha256'], int(score))
    check('Exact required run IDs present', required <= all_runs, runs=sorted(required))
    aligned = {}
    anchor = vectors[(CONTRASTS[0][1], SCORERS[0])]
    for key, values in vectors.items():
        check('Complete indices ' + str(key), set(values) == set(range(N)))
        for ix in range(N):
            check('Aligned identifiers/hashes ' + str(key) + '/' + str(ix), values[ix][:3] == anchor[ix][:3])
        aligned[key] = np.array([values[ix][3] for ix in range(N)], dtype=np.int64)
    metrics = rows(sources[1])
    for run in sorted(required - {'gsm8k-quality-greedy/lora'}):
        for metric in SCORERS:
            matches = [r for r in metrics if r['job_id'] + '/dora' == run and r['metric'] == metric]
            check('Frozen metric unique ' + run + metric, len(matches) == 1)
            check('Frozen metric mean ' + run + metric, abs(aligned[(run, metric)].mean() - float(matches[0]['right_mean'])) <= 1e-12)
    outcomes = rows(accepted)
    output_rows = []
    for order, (name, left_run, right_run) in enumerate(CONTRASTS):
        for metric_order, metric in enumerate(SCORERS):
            ix = order * 2 + metric_order
            seed = BASE_SEED + ix
            left, right = aligned[(left_run, metric)], aligned[(right_run, metric)]
            z = right - left
            n00 = int(np.sum((left == 0) & (right == 0)))
            n01 = int(np.sum((left == 0) & (right == 1)))
            n10 = int(np.sum((left == 1) & (right == 0)))
            n11 = int(np.sum((left == 1) & (right == 1)))
            check(name + metric + ' transition marginal sums', n00+n01+n10+n11 == N and n10+n11 == int(left.sum()) and n01+n11 == int(right.sum()))
            ci, means, counts = paired_bootstrap(z, seed)
            check(name + metric + ' bootstrap counts', np.array_equal(counts, [n10, n00+n11, n01]))
            check(name + metric + ' bootstrap finite/bounded', np.isfinite(means).all() and np.all(np.abs(means) <= 1) and ci[0] <= ci[1])
            se_mean = math.sqrt(float(z.var()) / N / B)
            check(name + metric + ' bootstrap mean consistency', abs(float(means.mean()) - float(z.mean())) <= 6 * se_mean + 1e-15)
            if order < 2:
                matches = [r for r in outcomes if r['left_run_id'] == left_run and r['right_run_id'] == right_run and r['metric'] == metric]
                check(name + metric + ' accepted transition row unique', len(matches) == 1)
                old = matches[0]
                for field, new in [('wrong_to_wrong', n00), ('wrong_to_correct', n01), ('correct_to_wrong', n10), ('correct_to_correct', n11), ('n', N)]:
                    check(name + metric + ' accepted ' + field, int(old[field]) == new)
                for field, new in [('reference_mean', float(left.mean())), ('intervention_mean', float(right.mean())), ('difference', float(z.mean()))]:
                    check(name + metric + ' accepted ' + field, abs(float(old[field]) - new) <= 1e-12)
            output_rows.append(dict(hypothesis_order_zero_based=ix, contrast=name, metric=metric, left_reference_run_id=left_run, right_changed_run_id=right_run, difference_direction='right-minus-left', n=N, left_mean=float(left.mean()), right_mean=float(right.mean()), difference=float(z.mean()), wrong_to_wrong=n00, wrong_to_correct=n01, correct_to_wrong=n10, correct_to_correct=n11, discordant_n=n01+n10, pointwise_bootstrap_ci95_low=float(ci[0]), pointwise_bootstrap_ci95_high=float(ci[1]), exact_mcnemar_two_sided_p=exact_mcnemar(n01, n10), bootstrap_B=B, bootstrap_seed=seed, bootstrap_rng='numpy.PCG64/default_rng', quantile_method='linear', ci_scope='pointwise paired percentile CI95; no multiplicity adjustment', inference_scope='exploratory family A, exactly eight two-sided exact McNemar tests; fixed checkpoints and paired evaluation cases'))
    ps = [r['exact_mcnemar_two_sided_p'] for r in output_rows]
    adjusted = holm(ps)
    check('Exactly eight hypotheses', len(output_rows) == 8)
    check('Holm bounds', np.all((adjusted >= ps) & (adjusted <= 1)))
    for r, adj in zip(output_rows, adjusted):
        r.update(holm8_p=float(adj), holm8_reject_alpha_0_05=bool(adj <= 0.05), holm_family_size=8)
    table = OUTPUT / 'direct-contrasts.csv'
    with table.open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(output_rows[0]))
        w.writeheader()
        w.writerows(output_rows)
    # Recheck every frozen dependency after analysis before publishing new outputs.
    for item in inputs:
        check('Input unchanged after run ' + item['path'], sha(item['path']) == item['sha256'])
    findings = ['# Прямые парные сравнения: пакет A', '', 'Все восемь сравнений выполнены на 1319 общих примерах GSM8K. Выбор сравнений сделан после просмотра корпуса: анализ exploratory.', '', '| Контраст (правый минус левый) | Scorer | Разница, п.п. | Pointwise CI95, п.п. | exact p | Holm8 p |', '|---|---|---:|---:|---:|---:|']
    for r in output_rows:
        findings.append(f"| {r['contrast']} | {r['metric']} | {100*r['difference']:.4f} | [{100*r['pointwise_bootstrap_ci95_low']:.4f}; {100*r['pointwise_bootstrap_ci95_high']:.4f}] | {r['exact_mcnemar_two_sided_p']:.6g} | {r['holm8_p']:.6g} |")
    findings.extend(['', 'В этой семье единственное значимое сравнение после Holm8 — remove_D-Q−remove_D-K по author_em: Q выше на 1.7437 п.п. (23 дополнительных правильных ответа в signed сумме). Для final_em аналогичный эффект +1.5163 п.п. после Holm8 не значим (p=0.083497). Номинальные выигрыши radial-all относительно LoRA около 1.97–2.05 п.п. имеют положительные pointwise CI, но после Holm8 не проходят порог .05. Это различие scope CI и p необходимо сохранять при интерпретации.', '', f"После Holm по всем восьми гипотезам значимы {sum(r['holm8_reject_alpha_0_05'] for r in output_rows)} из 8 сравнений при alpha=0.05. CI в таблице pointwise; они не имеют одновременного покрытия восьми контрастов и не подменяют Holm p.", '', 'remove_D-all и base_magnitude-all оставляют обученные в DoRA A/B; сравнение с отдельно обученной LoRA не является переобучением аблированной модели. Переходы этих четырёх строк побитно согласованы с принятыми целочисленными переходами paired-outcome-transitions.csv; means/effects согласованы в допуске 1e−12.', '', 'Q−K измеряет разницу accuracy между двумя конкретными вмешательствами, а не причинную роль Q и K. Даже значимая разница относится к этим checkpoints и оценочным примерам; нет uncertainty по seeds обучения, независимой репликации или общего превосходства метода. Отсутствие значимости не доказывает эквивалентность. Holm8 охватывает только новую семью A, не всю историю адаптивного поиска и не семью 46 пакета C.', '', 'Тексты ответов, weights и forward не использовались. Новых GPU-прогонов, загрузок или установок зависимостей нет. Следующие GPU-эксперименты этим пакетом не запускаются.'])
    (OUTPUT / 'FINDINGS.md').write_text('\n'.join(findings)+'\n')
    method = '''# Метод пакета A

Используется неизменяемый `02-interventions/tables/per_example_scores.csv.gz` из подготовки 2026-10-11. SHA256 четырёх выбранных frozen таблиц сверены с `manifests/bundle.json`; SHA принятой `paired-outcome-transitions.csv` — с `analysis-manifest.json`. Точные зависимости и hashes записаны в новом manifest. Frozen входы повторно хешируются после расчёта. Старые CI/p не переиспользуются и не переписываются.

Семья зафиксирована в текущем SPEC до новых расчётов: remove_D-all−LoRA, base_magnitude-all−LoRA, remove_D-Q−remove_D-K, base_magnitude-Q−base_magnitude-K, каждый author_em затем final_em. В CSV left всегда reference, right changed: эффект `right_mean-left_mean`. Индексы гипотез 0..7, seeds 2026101140..2026101147. Направление эффекта подписано, но тест McNemar двусторонний. Run IDs подтверждены по frozen scores без замен.

Для всех семи условий и двух scorers проверяются ровно 1319 уникальных test_row_index 0..1318, бинарность и полное равенство source_id/prompt_sha256/input_ids_sha256 по индексам. Четыре перехода: n00 wrong→wrong, n01 wrong→correct, n10 correct→wrong, n11 correct→correct; `difference=(n01-n10)/1319`.

Парный percentile bootstrap, B=50000, отдельно для каждого контраста: z=Y_right−Y_left ∈ {−1,0,+1}; один draw — multinomial(N; n10/N,(n00+n11)/N,n01/N). Это точное распределение обычной выборки N индексов с возвращением для среднего z. Среднее draw равно (count_plus−count_minus)/N. CI — квантили .025/.975, NumPy method=linear, PCG64/default_rng. CI pointwise, не скорректированы за поиск/восемь гипотез.

Двусторонний exact McNemar: `min(1,2*sum_{k=0}^{min(n01,n10)} C(n01+n10,k)/2**(n01+n10))`; отсутствие discordance даёт 1. Сумма считается точными Python integers, финальный результат float. Holm stepdown применяется совместно ровно к восьми exact p, монотонные скорректированные p; alpha .05. Старые bootstrap p не переносятся. Новая семья A не контролирует всю историю адаптивного анализа, не относится автоматически к семье C, выбор scorer/контрастов уже posthoc.

Toy проверки: exact известные McNemar значения/симметрия, Holm известные значения/равные p, полное перечисление 3^3 indexed resamples и сравнение с multinomial кратностями, константные z, ожидание/дисперсия/bootstrap determinism. На данных проверяются marginals, aligned means против frozen metrics, четыре accepted перехода radial-vs-LoRA, finite CI/bounds, bootstrap mean consistency с допуском шесть Monte Carlo SE. Проверяется сохранность входов после расчёта. Число проверок включает бинарность и alignment каждого примера и не является числом независимых наблюдений.

Вычисления только CPU исследовательского сервера в готовом окружении. Numerical threads принудительно <=2, CUDA_VISIBLE_DEVICES пуст. Модели, веса, Torch, forward, GPU, downloads и установки не используются. Resources содержит версии, runtime, RSS и настройки threads. Manifest исключает свой собственный hash; зеркальная идентичность проверяется отдельно после копирования. Эти checkpoint CI отражают resampling оценочных примеров, не вариацию обучения. Q−K не идентифицирует причинную роль групп, нулевая значимость не устанавливает эквивалентность функций.

Воспроизведение на сервере:
`./artifacts execution/existing-data-followup/build_direct_contrasts.py --repo-root ./artifacts`
'''
    (OUTPUT / 'METHOD.md').write_text(method)
    runtime = time.perf_counter() - start
    resources = dict(created_utc=datetime.now(timezone.utc).isoformat(), hostname=socket.gethostname(), python=platform.python_version(), numpy=np.__version__, executable=os.sys.executable, runtime_seconds=runtime, peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss, cpu_only=True, gpu_used=False, numerical_thread_cap=2, environment={v: os.environ.get(v) for v in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS','VECLIB_MAXIMUM_THREADS','BLIS_NUM_THREADS','CUDA_VISIBLE_DEVICES')}, script_sha256=sha(CODE), bootstrap_resamples_per_contrast=B, seeds=list(range(BASE_SEED, BASE_SEED+8)), run_scope='CPU research server; no models/forward/downloads/install')
    dump(OUTPUT / 'resources.json', resources)
    for category, count in CASE_CHECKS.items():
        CHECKS.append({'check': category, 'passed': True, 'case_checks': count})
    total_checks = len(CHECKS) - len(CASE_CHECKS) + sum(CASE_CHECKS.values())
    dump(OUTPUT / 'validation.json', dict(passed=all(c['passed'] for c in CHECKS), complete=True, checks=total_checks, failed=0, hypotheses=8, aligned_examples=N, accepted_transition_rows_verified=4, input_hashes_unchanged=True, records=CHECKS))
    output_files = [OUTPUT / name for name in ('direct-contrasts.csv','FINDINGS.md','METHOD.md','resources.json','validation.json')]
    dump(OUTPUT / 'manifest.json', dict(schema_version=1, created_utc=datetime.now(timezone.utc).isoformat(), scope='exploratory package A only; no frozen writes', code={'path':str(CODE),'sha256':sha(CODE),'bytes':CODE.stat().st_size}, inputs=inputs, outputs=[{'path':str(p),'sha256':sha(p),'bytes':p.stat().st_size} for p in output_files], exclusions=['manifest.json: self hash','mirror-verification.json: verification added after local/server copy'], bootstrap_B=B, seeds=list(range(BASE_SEED,BASE_SEED+8)), family_size=8, difference_direction='right-minus-left'))
    print(json.dumps({'passed':True,'checks':total_checks,'runtime_seconds':runtime,'peak_rss_kib':resources['peak_rss_kib'],'contrasts':[{k:r[k] for k in ('contrast','metric','difference','pointwise_bootstrap_ci95_low','pointwise_bootstrap_ci95_high','exact_mcnemar_two_sided_p','holm8_p')} for r in output_rows]}, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
