# Завершение анализа имеющихся данных

11 октября 2026. Последнее решение пользователя: статью сейчас не писать;
закончить анализ имеющегося корпуса, затем отдельно определить следующие
эксперименты и запустить их. Новые GPU-опыты ожидаются позже, не отменены.
Этот этап выполняет существующий план прямых сравнений, изменений ответов
и устойчивости выводов. Он не включает paper outline, текст статьи, новые
weights/forward/quality runs/SVD или обучение.

## Ограничения, входы и размещение

Основной repo локально: work/lora-dora-series. На gpu-host:
/path/to/user-user/.venvs/lora-dora-research. Ничего не устанавливать.
Все численные расчёты — CPU gpu-host, максимум 2 numerical threads на пакет.
VM 1GB/1core только управление/код/малые результаты. GPU не использовать.
Не трогать чужие процессы, evaluator, исходные predictions и frozen bundles.
AGENTS.md/MEMORY.md неизменяемы; новые предпочтения в MEMORY_CONTINUATION.md.

Неизменяемые входы: docs/analysis-preparation/2026-10-11/ и выбранные файлы
docs/analysis/2026-10-11/results/. Особенно 02-interventions/tables/
per_example_scores.csv.gz, intervention_metrics.csv, paired_transitions.csv,
localization_grid.csv; bundle manifest manifests/bundle.json.
Новая activity диагностика: docs/diagnostics/radial-activity-2026-10-11/.
Сверять SHA выбранных frozen inputs с bundle manifest, выровнять source_id,
test_row_index, prompt_sha256, input_ids_sha256, metric, полные 1319 примеров.
Scores бинарны. Не считать отдельные строки/матрицы независимыми обучениями.

Новый код: execution/existing-data-followup/. Новые outputs исключительно
docs/analysis-followup/2026-10-11/ с отдельными пакетами A/B/C. Существующие
отчёты/CI/p/manifest не переписывать. Документировать точные hashes кода/inputs/
outputs, версии Python/NumPy, runtime/RSS/threads, seeds и проверки.
Каждый пакет имеет METHOD.md, FINDINGS.md, validation.json, manifest.json.
Scientific prose на русском. Основной агент интегрирует/интерпретирует и
обновляет HANDOFF. Технические задачи делегируются gpt-6.1-sol, high/xhigh.

Весь новый этап exploratory: выбор сравнений сделан после просмотра данных.
Семьи ниже фиксируются до новых расчётов, это не пререгистрация и не контроль
всей истории адаптивного поиска. Нельзя трактовать checkpoint CI как seed CI.

## A — прямые сравнения

Владелец только A-direct-contrasts/ и build_direct_contrasts.py.
Четыре направленных контраста × author_em/final_em = ровно 8 гипотез:

1. remove_D-all минус отдельно обученная LoRA.
2. base_magnitude-all минус отдельно обученная LoRA.
3. remove_D-Q минус remove_D-K.
4. base_magnitude-Q минус base_magnitude-K.

Run IDs: gsm8k-remove_d-all/dora, gsm8k-base_magnitude-all/dora,
gsm8k-quality-greedy/lora, gsm8k-remove_d-q/dora, gsm8k-remove_d-k/dora,
gsm8k-base_magnitude-q/dora, gsm8k-base_magnitude-k/dora.
Подтвердить IDs по frozen scores, без угадывания замен.

Для каждого: means/difference right-minus-left с явно записанными run IDs,
четыре перехода правильности; pointwise paired percentile bootstrap CI95,
B=50000, multinomial resampling распределения z=Y_changed−Y_reference,
seed 2026101140+порядок (контрасты как выше, scorer author затем final).
Two-sided exact McNemar p = min(1,2*Pr[Bin(n01+n10,.5)<=min(n01,n10)]),
при отсутствии discordance p=1. Holm по ВСЕМ 8 exact p — единственная новая
inferential семья A. Не переносить старые bootstrap p; не вычитать старые CI.
Пометить pointwise CI и отдельно Holm p, чтобы их scope не путался.
Сверить переходы remove_D/reset vs LoRA с принятыми paired-outcome-transitions.
Q−K проверяет различие двух вмешательств по accuracy, не причинную роль Q/K.
Если появляется значимость, вывод только об этих checkpoints и этих задачах.
Выход direct-contrasts.csv и короткие FINDINGS; без обещания нового обучения.

## B — совместные изменения ответов

Владелец только B-outcome-overlap/ и build_outcome_overlap.py.
Восемь run IDs: original DoRA, отдельно обученная LoRA, dense DoRA,
remove_D-all, base_magnitude-all, r32, e95, e99; оба scorer, все 1319 примеров.
Радиальные и SVD вмешательства сравнивать по единому original DoRA reference
для repairs/breaks; dense оставить явным численным контролем. Отдельные
исторические SVD-vs-dense counts не смешивать с SVD-vs-original counts.

Выходы: run-summary.csv (16 строк), pairwise-outcomes.csv (28×2=56),
overlap.csv (21×2=42 пары семи non-original условий, в т.ч. LoRA/dense),
case-patterns.csv.gz (aligned IDs/hashes и correctness vectors, без текстов).
Для summary repairs/breaks относительно original, changed-correctness count,
score, исправления/поломки условно на original wrong/correct.
Для pairwise четыре совместных исхода и направленная difference.
Для overlap repairs intersection/union/Jaccard и доля общих для каждого run;
то же breaks и всего changed-correctness. Empty union обозначить undefined
(не автоматически 1), указать counts. Эти показатели описательные: p-values,
подгрупповой поиск и mechanism/semantic claims не нужны.
Проверить counts по frozen/accepted таблицам и все маргинальные суммы.
Не называть сходство correctness векторов совпадением текстов или функций.
Не сравнивать нормы возмущений как доказательство общности механизма.

## C — устойчивость выводов и новый реестр

Владелец только C-robustness/ и build_robustness.py.
Семья ровно 46 signed accuracy contrasts: все 40 строк принятого
all-intervention-evidence.csv (20 jobs ×2 scorers), плюс 6 строк принятого
compression-original-reference.csv (r32/e95/e99 ×2). Сохранять exact run IDs
и references каждой строки. Не отбирать только удачные вмешательства.
Сверить means из aligned scores с принятыми таблицами (<=1e-12).

Новые joint bootstrap intervals: общие индексы 1319 примеров для ВСЕХ 46
контрастов и обоих scorers, B=50000, seed=2026101160. Объединять строки
по совместному correctness/difference pattern и multinomial counts допустимо
при доказанном равенстве распределения индексов; chunks <=256, без огромных
B×N×46 массивов. При каждом resample получить 46 means; сохранить небольшую
B×46 матрицу для validation/quantiles при нужде, не обязательно в Git.
q95=quantile_0.95(max_j(abs(mu_star_j−mu_hat_j))). Интервалы mu_hat±q95
(можно clip [-1,1]) — приближённые simultaneous two-sided 95% intervals
на общей accuracy шкале, unstudentized maximum deviation; не называть max-t.
Критический q общий для всей семьи, не отдельно под результат. Percentile95
pointwise intervals из тех же bootstrap draws показать отдельно. Исторические
pointwise CI сохранить отдельными колонками с source scope, не заменять.

robustness.csv: 46 строк, точные пары/means/effects, old pointwise intervals,
new pointwise intervals, simultaneous intervals, флаги lower > −delta для
delta=.005/.01/.02 отдельно для old/new pointwise/simultaneous, все scopes.
Отдельная summary: что меняется у remove_D-all/reset/r32/e95/e99 в зависимости
от scorer и original/dense reference. Нет p-value noninferiority и нет
превращения posthoc margins в пререгистрированный стандарт.
Проверки: нулевой toy даёт нулевую ширину; duplicated columns/identical scorers
имеют одинаковые intervals; common-bootstrap mean consistency, finite bounds,
все 46 одновременно входят в bands >=95% bootstrap draws (с дискретной оговоркой).
Это проверка конструкции bootstrap, не частотной истинной coverage.
В METHOD указать, что приближённая семья46 не покрывает всю историю поиска,
не uncertainty обучения, не equivalence функций и не автоматически 8 тестов A.

claim-update.csv: 9 строк исходного claim-evidence.csv с original statement,
prior disposition, new observations/source links, current bounded conclusion,
what remains unknown. Обязательно обновить L5 с activity FINDINGS/validated
group CSV, без переписывания original CSV; не делать универсальных заявлений.
Если исходные claim IDs отличаются, остановить только ledger часть и сообщить.

## Приёмка и следующий шаг

После A/B/C — независимая read-only проверка выбранных inputs/outputs, formulas,
согласования общих переходов/means и frozen hashes. Root пишет отдельный
ANALYSIS_SUMMARY.md с итоговыми выводами и незакрытыми вопросами. Это отчёт
анализа, не текст статьи и не paper outline. Обновить HANDOFF после этапов.

Завершение текущего этапа: все три пакета приняты, результат проверки и точные
пути сохранены локально/на сервере, выводы сформулированы без overclaim.
Затем с пользователем определять следующий набор GPU-экспериментов;
в текущем этапе их не запускать и не объявлять отменёнными.
