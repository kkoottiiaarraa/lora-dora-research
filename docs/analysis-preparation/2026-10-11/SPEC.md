# ТЗ: подготовка существующих результатов к анализу

Дата: 2026-10-11. Заказчик разрешил реализацию тремя агентами gpt-6.1-sol / low.
Сейчас только техническая подготовка; содержательная интерпретация выполняется позднее.
Новых результатов модели пока не будет. Не запускать inference, обучение, CUDA,
скачивание моделей, SVD весов, новые bootstrap/permutation tests или поиск значимости.

## Цель и границы

Создать воспроизводимый компактный набор CSV/JSON и описаний, достаточный для
последующего анализа качества, локализаций, сжатия и численных контролей.
Включать все имеющиеся направления эффектов; не ранжировать по значимости,
не выбирать выгодные DoRA примеры, не формулировать объяснения или гипотезы.
Детерминированные сводки сохранённых scores допустимы. Новые описательные
контрасты помечать exploratory/descriptive; не представлять их заранее заданными.
CI относятся к тестовым примерам при фиксированных checkpoints, не к training seeds.
Три задачи одной архитектуры не являются тремя независимыми seed-повторами.

## Источники и воспроизводимость

На сервере S=/path/to/user-user/lora-dora-series,
D=/path/to/user-user/lora-dora-profiling/distributed-important.
Авторитетны status.json -> outputs['full/ROLE'], а не выбор последнего каталога.
Относительные пути разрешать относительно S.
Два корня: S/results/first-series-greedy/jobs и S/results/extra-series-greedy/jobs.
Состав вмешательств: D/plan.json (17) + D/night-plan.json (3).
Базовые triples: gsm8k-quality-greedy, shadow_4b_mmlu, shadow_4b_squadv2 (9 runs).
Итого ожидаем 29 полных принятых runs, 20 intervention contrasts, 3 baseline triples.
Проверять это ожидание, а не подгонять факты; отменённые и неуспешные попытки
учитывать отдельно. Answer.AI отложен, Qwen3-8B и LLaVA исключены, полный no-op и
полная V/O генерация отменены. Короткая V/O проверка существует отдельно.

Проверить JSON parsing, complete/full_evaluation, predictions_sha256,
rows/expected_rows/predictions_completed, уникальность и порядок test_row_index.
Перед любым парным счётом проверить dataset, generation_config, versions,
source_sha256, prompt_sha256 и input_ids_sha256 (по каждому примеру).
Несовместимость = явная ошибка/отдельный статус, никогда скрытая агрегация.
Не исправлять первичные данные. Если неизвестно, писать null + missing_reason;
не превращать отсутствие величины в ноль. Не выдумывать training metadata.
Доли хранить в [0,1], разности right-minus-left; percentage points только
в отдельных явно названных полях. GiB=2^30 bytes, GPU-hours=seconds/3600.
Не называть inference GPU-hours общей стоимостью кампании: smoke, вмешательства,
ошибки и ожидание учитывать раздельно, где возможно.
Записать SHA256 всех использованных входных файлов, извлекателя и выходов,
UTC времени экспорта, точные пути источников и команду воспроизведения.
Не переносить на VM веса, полные тексты ответов или токены доступа.

## Каталоги и владение файлами

R = docs/analysis-preparation/2026-10-11/ внутри рабочего checkout.
Каждый агент создаёт только свой каталог:
A: R/01-corpus-quality/; B: R/02-interventions/; C: R/03-diagnostics/.
Внутри: README.md, tables/*.csv, manifests/*.json, validation/*.json.
Код: execution/analysis-preparation/build_corpus_quality.py (A),
build_interventions.py (B), build_diagnostics.py (C).
Корневой README.md, SPEC.md, MEMORY.md и HANDOFF меняет только основной агент.
Не менять frozen scripts/, configs/, lora_dora_study/, первичные results,
старые execution controllers, очереди и чужие процессы. Git commits делает
основной агент. Не читать секреты и не добавлять пароли в артефакты.
На сервере допустимы только CPU-чтение источников и собственный маленький
извлекатель во временном каталоге profiling/analysis-preparation/2026-10-11.
Ограничить OMP/BLAS threads до 2, никакого Torch/Transformers/CUDA.
Финская VM имеет всего 1 GiB RAM / 1 CPU: всё чтение больших исходников,
выравнивание, SHA256 и агрегацию выполнять на CPU ШАДа. Локально только
компактные таблицы/манифесты и код. При больших scored CSV использовать gzip.
Пользователь дополнительно разрешил CPU/GPU ШАДа, включая частично занятые GPU,
но GPU для этой стадии не требуются; запрет новых inference остаётся в ТЗ.
Готовые компактные артефакты должны находиться локально в R; серверная копия
допустима, её расположение указать. При сборке иметь явный режим проверки.

## Пакет A: реестр корпуса и базовое качество

1. run_inventory.csv: принятый run, job/task/role/intervention/targets,
   пути summary/predictions/status, строки, SHA256, dataset revision,
   base/adapter revision (только известные), dtype/quantization, tokenizer,
   generation/source/version fingerprints, complete/full flags.
2. coverage.csv: запланировано/выполнено/отменено/отложено, источник решения.
   Не считать smoke и failed attempts отдельными репликациями.
3. comparability.csv: проверка сопоставимости каждого готового контраста,
   имена совпавших/несовпавших полей, matched_rows, причина отказа.
4. baseline_metrics.csv: все метрики трёх triples, n, роль, original score.
5. baseline_contrasts.csv: все существующие baseline contrast CI/p/Holm,
   left/right, difference direction, family/adjustment/resamples/seed/scope.
   Не пересчитывать CI/p и не переносить Holm между задачами/семействами.
6. mmlu_subject_metrics.csv: по subject и роли n и mean; отдельно micro/macro,
   не смешивать. Проверить существующие per_subject/subject_macro если есть.
7. gsm8k_scorer_agreement.csv: author_em/final_em для базовых runs,
   все четыре сочетания 0/1 и n; лимиты токенов и обрезания отдельными counts.
8. baseline_pair_transitions.csv: для каждого существующего baseline contrast
   binary correct/wrong переходы; для небинарных метрик (SQuAD F1) counts
   increase/equal/decrease и средняя разность, не бинaризовать F1.
9. squadv2_answerability.csv: n и mean каждого baseline role/metric отдельно
   для answerable/unanswerable при наличии явной разметки в dataset;
   provenance label/source обязателен. Не выводить answerability из предсказания.
   Если соответствующие поля недоступны, явный missing_reason, не гадать.
10. validation/integrity.json: результаты проверок, ожидаемые и фактические
   количества, а не только общий passed. Манифест входных/выходных SHA256.

## Пакет B: вмешательства, изменения ответов и локализации

1. intervention_metrics.csv: все 20 вмешательств и метрики, actual reference,
   left/right mean, difference, existing CI/raw p/Holm p, family size,
   targets, full run paths. Семейства 8/9/3 отдельно, обе GSM8K метрики.
2. paired_transitions.csv: для каждого контраста/метрики counts correct->correct,
   correct->wrong, wrong->correct, wrong->wrong; также changes of generated
   text как отдельный описательный count. Правильно ответившие и одинаковые
   тексты не тождественны. Суммы=n, разность= (wrong->correct-correct->wrong)/n.
3. localization_grid.csv: remove_d/base_magnitude × all/q/k/v/o/qk/vo × scorer.
   Явно отметить отсутствующие клетки, reference и направления дельт.
4. localization_interactions.csv: описательные I_QK=mean(Y_QK-Y_Q-Y_K+Y_0),
   I_VO=mean(Y_VO-Y_V-Y_O+Y_0), для обоих методов/скоров. Y_0 именно
   unmodified DoRA reference. Только выровненные per-example scores.
   Без новых p/CI/деклараций синергии; exploratory, families singles/joint
   перечислить, не назначать этому контрасту чужую Holm поправку.
5. numerical_control_contrasts.csv: descriptively adjusted quality differences
   rank32/E95/E99 versus dense-DoRA; matched-impact LoRA versus dense-LoRA;
   отдельно отличие dense от original. Использовать per-example alignment,
   existing contrast statistics только когда именно эта пара уже рассчитана;
   иначе difference без p/CI, пометка newly_derived_descriptive.
6. per_example_scores.csv: компактная длинная таблица GSM8K run_id/index,
   source_id, metric/score, hit_token_limit, prompt_truncated, tokens/time,
   prompt/input hashes; без question/gold/generated text. Это основа будущих
   графиков/проверок, без выборки удачных примеров.
7. validation/checks.json: суммы переходов, reproduction means/differences,
   точное совпадение семейства с сохранёнными contrasts/Holm, проверки
   всех four-run alignments и reference происхождения. На ошибке fail clearly.

## Пакет C: сжатие, симметрии, ресурсы и технические ограничения

1. rank_modules.csv: имеющиеся module-level rank, shape, adapter rank,
   retained energy, Frobenius/activation errors, calibration provenance,
   intervention job/role/targets из intervention.json. Не вычислять матрицы.
   Для spectrum допустимы детерминированные energy@r и ranks95/99 из
   уже сохранённых сингулярных чисел; явно обозначить derived и denominator.
   Не экспортировать миллион строк полного spectrum на VM.
2. rank_job_summary.csv: min/median/max ranks/errors/energy и число модулей;
   unweighted module summary маркировать, не подменять global energy.
3. matched_impact_checks.csv: фактические target/achieved воздействия,
   absolute/relative mismatch и источник; объяснить единицы/методику,
   отсутствующие measurement не объявлять равенством воздействий.
4. numerical_fidelity.csv: dense controls и короткая V/O проверка,
   reference, dtype, measured max/logit errors и прочие сохранённые
   показатели/толерансы; algebraic symmetry != bitwise equivalence.
5. symmetry_statistics.csv: сохранённые magnitude/direction correlations
   before/after, transform parameters, fixed-base/rank admissibility;
   если admissibility не измерена — unknown, не делать вывод по имени.
6. resources.csv: все 29 full accepted runs с load/intervention/inference
   time, peak allocated/reserved VRAM, process RSS, tokens и rate; smoke,
   guard_refused/failed отдельно в attempts.csv с reason. Не складывать
   max_memory между последовательными runs, не считать host RAM процесса
   свободной RAM сервера. Wall time неизвестно если нет start/end.
7. availability.csv: наблюдаемые/отсутствующие диагностические поля с
   конкретными путями; заранее обозначить пределы дальнейшего анализа.
8. README: словарь единиц, правила агрегации, воспроизведение, никакой
   интерпретации качества, преимущества метода или механизма обучения.

## Приёмка

Каждый агент: реализовать извлекатель, реально собрать таблицы из существующих
артефактов, провести содержательные проверки согласованности, записать README
со схемами колонок/командой и manifest. Не ограничиваться заготовкой.
Отчитаться основному агенту: список файлов, размеры/количества, проверки,
отсутствующие поля и препятствия. Не публиковать исследовательские выводы.
Основной агент проверяет только комплектность, происхождение и воспроизводимость,
обновляет HANDOFF и указывает пользователю пути. Сам научный анализ отложен.

## Пакет D: интеграция и независимая приёмка (после A/B/C)

Исполнитель: агент пакета B после его завершения. Добавить единый лёгкий
execution/analysis-preparation/verify_bundle.py, без сетевых вызовов и зависимости
от источников/NumPy/Torch. Он последовательно запускает --check трёх извлекателей,
проверяет наличие всех обязательных таблиц, деклараций/схем/manifest и выходных
SHA256, JSON parse и ожидаемые counts из package validations. Не выполнять
генерацию, научный анализ или новые статистические тесты. Команда должна давать
ненулевой exit code при несогласованности. Хеширование streaming, одна операция
за раз, не загружать весь long CSV в память. Новые файлы: R/manifests/bundle.json,
R/validation/bundle.json, единый CLI verifier. Манифест охватывает README/SPEC,
таблицы, package manifests/checks, код извлекателей, MEMORY.md; исключить собственный
manifest и volatile validation, чтобы не создать рекурсивный hash.
Обновить только R/README.md: навигация, команды единой проверки, описание пакетов,
доступные/отсутствующие виды данных, ресурсы VM/server; никаких выводов качества.
Пакет D не меняет содержимое A/B/C. Приёмку запускать после их готовности.
