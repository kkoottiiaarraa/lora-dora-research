# Исполнение анализа: входы, расчёты и приёмка

11 октября 2026. Пользователь явно разрешил начать научный анализ и выбирать
уровень reasoning агентов; модель всех помощников — **gpt-6.1-sol**. Это более
позднее решение заменяет ограничение low в историческом PLAN/MEMORY.
План написан после сбора данных; новые расчёты exploratory, не пререгистрация.

## Неизменяемые входы и размещение

План: PLAN.md. Вход: `docs/analysis-preparation/2026-10-11/`, все пакеты 01–03.
Сверять hashes с bundle manifest read-only, не запускать verifier, который
переписывает volatile validation. Оригиналы брать только по manifest paths.
Не менять старый bundle, evaluator, исходные predictions, старые p/CI.

Код: `execution/scientific-analysis/`. Выходы:
`docs/analysis/2026-10-11/results/`. Вычисления/plotting — CPU gpu-host через
Ни GPU, ни новых forward, ни новых SVD весов, ни обучения, ни зависимостей.
На VM — текстовый код и компактные готовые артефакты.

## Пакет Q: качество и численные контроли

Входы: 01 целиком; 02 numerical_control_contrasts/intervention_metrics/
paired_transitions; 03 numerical_fidelity. Выходы quality-overview.csv,
numerical-controls.csv, quality-and-controls.svg, quality-findings.md,
quality-validation.json; код build_quality.py.

Включить все три triples и все 15 metric contrasts. Показать baseline means,
DoRA−LoRA и остальные contrasts, старые CI/p с точным историческим scope.
GSM8K оба scorers, MMLU micro/macro и subjects описательно, SQuAD exact/F1 и
answerability strata. Обозначить token limits. Два dense controls: эффект и
число исправлений/поломок, ошибки logits с правильным этапом измерения.
Новых baseline tests нет. Приёмка: 29 accepted runs, исходные hashes/alignment,
15 contrasts, 4 dense scorer rows, точные references, отсутствие смешения
интервалов по примерам с независимыми обучениями. Содержательные выводы
написать с неопределённостью; определить ограничения перехода к компрессии.

## Пакет C: глобальные компоненты и компрессия

Входы: 02 intervention_metrics/paired_transitions/per_example_scores; 03
rank_modules/rank_job_summary/matched_impact_checks/numerical_fidelity.
Выходы component-necessity.csv (две all radial conditions × два scorers),
compression-quality.csv (r32/e95/e99/matched × два scorers),
all-intervention-evidence.csv (все 40 строк), compression-difference-in-differences.csv,
matched-control-limitations.json, compression-quality.svg, component-findings.md,
component-validation.json; код build_components.py.

Старые contrasts/p/CI воспроизвести буквально с references. Отдельно новый
Holm по всем 40 сохранённым raw p, не заменяя историческую поправку. Для
каждой строки показать pointwise критерий lower_CI > −δ для δ=.005/.01/.02,
явно без одновременной гарантии и без утверждения математической эквивалентности.

Новый estimand: (Y_r32−Y_denseD)−(Y_matchedL−Y_denseL), отдельно для каждого
scorer, n=1319. Его CI/p считать методом ниже; семья Holm ровно два contrasts.
Это различие чувствительности при ограниченном calibration matching, не чистый
эффект ранга. Для rank/energy/error честно подписать unweighted module summaries;
проверить, исходные ли spectra. Не вычислять correlation по трём точкам.
Приёмка: все 40 contrasts без пропусков, proper references, независимые
recomputations means/transitions из scores, проверка calibration scope 1 prompt/
54 tokens, никаких выводов из pre-intervention fidelity о конечной компрессии.

Уточнение C до расчёта entropy: `spectral-entropy.csv` из уже сохранённых
singular values четырёх spectrum jobs. Для каждого модуля H=−Σp log(p),
p=σ²/Σσ², natural log, effective_rank=exp(H); отдельно исходный спектр и
идеальный спектр, усечённый до recorded kept_rank с перенормировкой p.
Это ideal pre-BF16 approximation, не измерение фактических post-cast весов.
Повторяющийся исходный DoRA по трём jobs не считать независимыми образцами.
Если источник не позволяет связать спектр и retained rank, оставить missing.
Никаких новых SVD, корреляционных tests или inference из 144 псевдоповторов.
Для matched-impact фактическая операция — attenuation полного LoRA delta,
если это подтверждает код. Предварительные SVD rank/energy, не использованные
в конечной операции, маркировать отдельно. При ненулевом uniform scale
нормированная spectral entropy не меняется; энергия масштабируется квадратом
scale. Не подменять эту операцию truncation по диагностическому rank.

Уточнение C после обнаружения dense shift, до новых расчётов: шесть прямых
парных contrasts r32/e95/e99 − original PEFT DoRA, оба scorers. Выход
`compression-original-reference.csv`. Они нужны, чтобы проверить перенос
dense-relative вывода; арифметика старых CI/p этого не решает. Метод ниже,
seeds 2026101121–2026101126 в порядке job=(r32,e95,e99), scorer=(author_em,
final_em), отдельная exploratory Holm family 6. Наличие этих дополнительных
проверок явно указать; historical families не менять. Это анализ уже имеющихся
scores, без модельного прогона. Practical criteria те же .5/1/2 п.п.

## Новые статистики — метод фиксируется до расчёта

Для каждого нового контраста собрать четыре выровненных score-вектора, затем
вектор z_i с коэффициентами (+1,−1,−1,+1). Сначала проверить source_id,
input/prompt hash и scorer, n=1319. Ресемплировать **общие индексы** четырёх
векторов; эквивалентно ресемплировать полученный z. Допустим multinomial bootstrap
по частотам уникальных z: это в точности то же эмпирическое распределение,
без потери парности. B=50000, NumPy default_rng, seed указан ниже.

CI95 — percentile [2.5%,97.5%] bootstrap mean. Двусторонний p для нулевого
среднего — centered bootstrap: (1 + count(abs(mean_boot−mean_obs) >=
abs(mean_obs)−1e−12))/(B+1), capped at 1. Это приближённый iid bootstrap test,
не exact randomization и не неопределённость обучения. Для полностью нулевого
z: CI=[0,0], p=1. Сохранять method/B/seed, распределение z и aligned run IDs.

Seeds difference-in-differences: author_em=2026101101, final_em=2026101102.
Seeds interactions: 2026101111–2026101118 в порядке method=(remove_d,
base_magnitude), group=(QK,VO), scorer=(author_em,final_em). Отдельные Holm
семьи 2 и 8; они не контролируют весь адаптивный исследовательский поиск.

## Пакет L: локализации, после приёмки Q/C

Входы: 02 localization_grid/localization_interactions/paired_transitions/
per_example_scores и all-intervention-evidence нового пакета C.
Выходы localization-effects.csv (28 строк), joint-interactions.csv (8 строк),
paired-outcome-transitions.csv, localization-effects.svg,
localization-findings.md, localization-validation.json; код build_localizations.py.

Все методы × all/q/k/v/o/qk/vo × scorers. Reference исходная DoRA.
Восемь estimands mean(Y_joint−Y_single1−Y_single2+Y_DoRA) считать методом выше;
проверить совпадение means с подготовленными descriptive interactions.
Не наследовать p от single contrasts. Переходы correct↔incorrect на всех
примерах; разбиения по baseline исходу только описательные. В plots pointwise
CI маркировать; interaction на score scale не уникальный механизм архитектуры.

## Пакет T и интеграция

Независимый математический аудит фактической V/O symmetry и соответствия L1–L9
литературе можно делать параллельно Q/C без новых вычислений модели.
Выходы symmetry-scope.md и theory-audit.md. Проверить действительный код
преобразования, GQA/head layout, определения correlation/slope, base transform,
fixed-base rank unknown. Не приписывать отсутствующие контроли.

После приёмки всех пакетов основной агент пишет REPORT.md, limitations.md,
claim-evidence.csv: все L1–L9, отрицательные и неопределённые результаты,
известные результаты отдельно от кандидатов новизны. Manifest связывает
inputs, plan/spec, code и outputs; отдельный read-only verifier. Каждый этап
фиксировать в HANDOFF; оригиналы остаются неизменными.
