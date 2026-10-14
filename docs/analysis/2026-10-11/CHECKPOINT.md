# Актуальная точка продолжения — 11 октября 2026

Пользователь явно возобновил анализ; историческая остановка ниже отменена.
Помощники gpt-6.1-sol: L/I high, T xhigh; max/ultra не использовались.
ТЗ продолжения RESUME_SPEC.md. Новых моделей, forward, SVD весов, обучения,
GPU-часов или зависимостей не добавлено. Исходный bundle/evaluator сохранён.

## Текущий научный статус

- Q принято:946checks; C принято:1507checks; L завершено и принято:1213checks,
  28effects/8interactions/84transitions. T независимо принято с уточнениями:
  results/theory-review.md. Техническая целостность и полнота итогового
  snapshot проверяются `verify_analysis.py --final`; фактический результат,
  counts/checks/errors — results/integration-validation.json, hashes —
  results/analysis-manifest.json. Они не подменяют научную приёмку.
- Итоговый синтез results/REPORT.md, регистр всех L1–L9 claim-evidence.csv,
  ограничения limitations.md. Локализации: localization-findings.md и SVG.
  Все29runs/20interventions учтены, обе схемы GSM8K сохранены.
- Убедительного DoRA−LoRA выигрыша на трёх задачах нет. Глобальные radial
  вмешательства сохраняют близкую среднюю accuracy по pointwise критерию,
  но исправления компенсируют поломки. Remove_D-all — additive LoRA-r
  endpoint с DoRA-trained A/B, не результат обычного LoRA training.
- Локальная Q/K специализация не установлена; все8interactionCI содержат0,
  Holm8p=1. Это недостаточная точность, не доказанная аддитивность.
- V/O scalar map algebraically fixed-base DoRA-r admissible; Pearson
  FP32precast0.0972336→0.0913035, без смены знака. BF16dense short64error0
  отдельное наблюдение; deployedBF16rho и PEFT-map fidelity не измерены.
  Pattern исходной статьи — аргумент о learning capacity; инвариантность
  функции — наше более сильное следствие. Trainingcauses не идентифицируются.

## Воспроизведение и известная оговорка provenance

Python3.12.3/NumPy1.26.4, CPU существующего исследовательского сервера,
не более двух numerical threads на задачу; dependency-free SVG. Отсутствие
matplotlib исправлено генерацией SVG, статистические методы/seeds сохранены.
Исторический SPEC пакета Q:3ddd31cf7ea359d495793276e9bf4098ddab88a4ad03ba11de73d488deb7574a;
текущий C/L:9123f1a73138cbb544be223c3f1b3e0cfa6d6cf4b8c5da1b136d59e7e83d17c7.
Это документированная эволюция ТЗ; старые bytes не восстановлены и validation
не переписана. Исходные Q tables/hashes отдельно проверены по immutable bundle.

## Следующий шаг и публикация

Обсудить выводы и достаточность их для научного рассказа. Существующие данные
не устанавливают причину обучения или универсальный механизм. Answer.AI —
отдельное решение о точечной проверке, не автоматический запуск. Qwen3-8B
и LLaVA исключены. Новые модели/прогоны без решения не добавлять.

Публикация очищенного старого snapshot выполнена commitd3e324a на GitHub
research/prepare-checkpoint-study. Приватная история не push. Продолжение
анализа сохранено локально и на исследовательском сервере; новая публичная
публикация этим продолжением не выполнялась. Операционный файл остаётся
local-only/OPERATIONS_PRIVATE.md внеGit. Пароли/ключи/токены не сохранять.

---

# Архив: остановка и точка продолжения до возобновления

Работа остановлена по явному указанию пользователя; анализ автоматически не
продолжать. Ни новых модельных прогонов, ни обучения, ни очередей не запускать.

**Публикация не выполнена.** Локальный scientific snapshot закоммичен
(`c8e7707`), далее отдельным коммитом сохранён статус остановки/публикации.
не авторизован. GitHub-коннектор имеет write access, но автоматическая проверка
дважды отклонила первый blob AGENTS.md как публикацию operational/infrastructure
context. Проверка показала, что исходный публичный commit уже содержал эти
ограничения и адрес сервера, а AGENTS изменён лишь тремя строками ссылок;
повторный auto-review всё равно отклонил действие. Blob/tree/ref не опубликованы,
GitHub ветка осталась на `4020b26`. Не обходить отказ. Для полного публичного
push требуется явное разрешение пользователя на включение таких сведений.
Резервная история сохранена Git bundle в outer `outputs/analysis-stop.bundle`
и на сервере `P/analysis-stop.bundle`; это локальная/серверная копия, не GitHub.
Состояние GPU проверено около **12:25 МСК**. Частота загрузки/VRAM MiB:
GPU0 0%/5056; GPU1 87%/8987; GPU2 99%/9957; GPU3 91%/10424;
GPU4 46%/871; GPU5 75%/8552; GPU6 71%/8586. Каждая карта 16376 MiB.
Это моментальный снимок, не резервирование. Во время научного анализа GPU
не использовались. На момент остановки процессов build_quality/components/
localizations на сервере не обнаружено; чужие процессы не изменялись.

## Что сделано за весь пайплайн

1. Аудированы готовые публичные LoRA/DoRA пары, provenance, загрузчики и
   ограничения сопоставимости; новые модели не обучались. Веса и тяжёлые
   вычисления размещены на gpu-host; финская VM использовалась для управления.
2. Проверены загрузка Qwen3-4B и адаптеров, фактические ресурсы и время.
   Выполнены три одинаково оцениваемые task-specific triples base/LoRA/DoRA:
   GSM8K, MMLU, SQuADv2. Дополнительно выполнены 20 GSM8K условий вмешательств
   и численных контролей, короткая V/O проверка. Все утверждённые GPU-очереди
   закончились, карты были освобождены. Qwen3-8B/LLaVA исключены; Answer.AI отложен.
3. Исправлены устаревшие статусы removeD-K/V. Подготовлен проверенный immutable
   bundle: 29 runs, 25 CSV, 43 manifested files, обе GSM8K схемы, source hashes,
   paired scores, transitions, rank/error/resource diagnostics. Путь:
   `docs/analysis-preparation/2026-10-11/`.
4. Сохранены обзор литературы с первичными ссылками, аудит новизны/хронологии
   и план научного анализа. Общие идеи norm/direction, full-rank delta и SVD
   уже известны; готовые checkpoints не устанавливают причину обучения.
5. Начат научный анализ силами gpt-6.1-sol; effort выбирался по задаче согласно
   последнему решению пользователя. Q и C приняты основным агентом; все
   вычисления по сохранённым данным выполнялись на CPU ШАДа, без новых weights,
   SVD весов, forward, GPU-часов или зависимостей.

## Промежуточные результаты

- **Q / качество и dense controls — принято.** 946 checks, 29 runs, 15 baseline
  contrasts, четыре dense/scorer строки. Все DoRA−LoRA CI включают ноль:
  GSM8K +1.061 п.п. [−0.607;+2.729], MMLU +0.057 [−0.406;+0.534],
  SQuAD exact −0.135 [−0.480;+0.202], F1 −0.266 [−0.560;+0.024].
  Это не equivalence. Scorer/лимит сильно влияют на GSM8K base.
- **C / глобальные компоненты и компрессия — принято.** 1507 checks; 40
  сохранённых contrasts, четыре radial строки, восемь compression строк,
  два новых sensitivity DID, шесть direct-original contrasts, 576 entropy rows.
  remove_D/base_magnitude all дают около +0.9 п.п.; pointwise CI исключают
  потерю >0.5 п.п. Это не доказательство ненужности magnitude при обучении.
  Численная активность D в BF16 не измерена в сохранённых diagnostics.
  Rank32/E95 удовлетворяют pointwise допуску 0.5 п.п. против dense, но только
  1 п.п. против original DoRA; E99 против original требует 2 п.п.
  DID DoRA/LoRA не устанавливает разницу чувствительности; global Holm40
  не оставляет p<.05. Matched LoRA — attenuation, не аналогичное SVD;
  calibration лишь один prompt/54 tokens. Rank/entropy после фактического
  BF16 cast не измерены.
- **T / теория и V/O — сохранено, полная интеграция не принята.**
  `symmetry-scope.md`, `theory-audit.md`. Важная поправка к старому unknown:
  положительное scalar V/O преобразование допустимо в DoRA-r при той же
  W0 через mV'=c mV, mO'=mO/c. Для additive LoRA-r это автоматически не следует.
  64 коротких dense numerical cases имели max error0; это не полный benchmark
  и не проверка обучающей траектории. Статистики FP32 pre-cast отдельно от
  фактической deployed correlation.
- **L / локализации — не завершено и не принято.** Код сохранён;
  с сервера сохранены частичные `localization-effects.csv`,
  `joint-interactions.csv`, `paired-outcome-transitions.csv`. Финальные
  findings/SVG/validation отсутствуют на момент остановки. Наличие CSV
  не означает успешную приёмку. Не использовать их как подтверждённый итог.
- `results/REPORT.md` — промежуточный авторский синтез Q/C, явно не финальный.
  `results/limitations.md` фиксирует пределы выводов.

## Откуда продолжать после нового указания пользователя

1. Прочитать этот checkpoint, актуальный HANDOFF, PLAN и EXECUTION_SPEC.
   Не перезапускать завершённые модельные очереди. Последняя preference:
   агенты gpt-6.1-sol, reasoning по содержательной необходимости; старое low
   в MEMORY/PLAN overridden. Immutable bundle не переписывать ради этого.
2. Завершить и проверить L на CPU по уже записанным method/seeds: 28 effects,
   восемь aligned interactions, переходы; сохранить validation и reproducible
   outputs. Не наследовать p/CI singles для interactions.
3. Основному агенту проверить математический аудит T, особенно различие
   DoRA-r и LoRA-r admissibility, fixed/joint base и FP32/BF16 scope.
4. Довести evidence ledger L1–L9, интегрировать L/T в REPORT, отделить
   репликацию известного, дополнительное наблюдение и неидентифицируемое.
   До этого не объявлять механизм, новизну или преимущество DoRA установленными.
5. Создать общий manifest/read-only verifier и провести интеграционную
   приёмку. У Q validation исторический SPEC SHA отличается от финального
   расширенного SPEC; это эволюция ТЗ, не повод изменять старую validation.
6. После обсуждения выводов отдельно решить, нужна ли целевая Answer.AI
   проверка. Автоматического разрешения на новый исследовательский запуск нет.

## Размещение и воспроизведение

Локальный checkout `work/lora-dora-series`, рабочая ветка
`research/two-extra-series`; целевая ветка для будущей разрешённой публикации —
исходная GitHub `research/prepare-checkpoint-study` (fast-forward, без force).
S=`/path/to/user-user/lora-dora-series`, P=`/path/to/user-user/lora-dora-profiling`.
Код `execution/scientific-analysis/`, результаты
`docs/analysis/2026-10-11/results/`, ТЗ `EXECUTION_SPEC.md` рядом с этим файлом.
Результаты и код сохранены локально и на S. Torch2.5.1+cu121,
Transformers4.57.1, PEFT0.17.1, Accelerate1.11.0; зависимости/evaluator не менялись.
Подробные оригинальные paths/hashes — в bundle manifests и пакетных validation.
Секретов и весов в Git нет. Каталог results попадает под общий gitignore;
для этого компактного отчётного snapshot использован адресный `git add -f`.
