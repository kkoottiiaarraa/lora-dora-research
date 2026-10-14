# Навигатор для следующего исследовательского агента

Контрольная дата: **14 октября 2026**. Ветка передачи: `research/two-extra-series`.
Исследование остановлено пользователем; передача сохраняет результаты,
а не разрешает продолжить вычисления. Прочитать навигатор перед выбором идеи.

## 1. Цель и текущий предел результатов

Исходная задача — объяснить различия DoRA и LoRA на готовых публичных адаптерах,
отделив качество от корреляций весов и механизма обучения. Далее приоритетом
стал самостоятельный научный результат уровня конференции B: полезный метод
или содержательный вывод с проверенными границами применимости.

Такой результат пока не установлен. Не объявлять успехом количество GPU-часов,
новые таблицы старых средних, известную симметрию или очередной малый отрицательный
тест. Результаты не пусты: есть ограниченный контрпример интерпретации абляций,
численные controls и ошибки публичного кода. Возможная учебная работа по
воспроизводимости не заменяет исходную научную цель без решения пользователя.
Статью пока не пишем.

## 2. Маршрут чтения

1. [README](../README.md), [AGENTS](../AGENTS.md), [MEMORY](../MEMORY.md).
2. **Начало**, а не весь исторический журнал [HANDOFF](HANDOFF.md).
3. [RESUME](research-direction/2026-10-14-pause/RESUME.md) и
   [RESULTS_AUDIT](research-direction/2026-10-14-pause/RESULTS_AUDIT.md):
   последний сводный статус, отрицательные направления, ограничения выводов.
4. [Последний REPORT](analysis/2026-10-14-component-decision/REPORT.md),
   его [SPEC](analysis/2026-10-14-component-decision/SPEC.md) и
   [PRIOR](analysis/2026-10-14-component-decision/PRIOR.md).
5. Затем тематическая карта ниже. Если старый отчёт предлагает следующий шаг,
   проверить поздний REPORT: этот шаг мог уже завершиться неудачей.

[Исходный контекст](../LORA_DORA_RESEARCH_CONTEXT.md),
[протокол](RESEARCH_PROTOCOL.md), [CONTINUE](CONTINUE_RESEARCH.md) и
[история пяти направлений](research-direction/2026-10-14-status/FIVE_DIRECTIONS.md)
нужны для происхождения решений, но не являются более свежим планом запуска.

## 3. Данные и сопоставимость

Основное полное сравнение — **три пары одной семьи Qwen3-4B** на GSM8K (1 319),
MMLU (14 042), SQuADv2 (11 873), с base / LoRA / DoRA. Это не три независимые
архитектуры или несколько seeds одного контролируемого обучения.

- [Каталог кандидатов](../CHECKPOINT_INVENTORY_2026-10-09.md) и
  [machine-readable inventory](../checkpoint_inventory.json) описывают кандидатов,
  не число принятых прогонов. Условия обучения известны не полностью.
- [Основной корпус](analysis-preparation/2026-10-11/01-corpus-quality/README.md),
  [comparability](analysis-preparation/2026-10-11/01-corpus-quality/tables/comparability.csv),
  [сводка качества](analysis/2026-10-11/results/quality-overview.csv).
- [Дополнительные источники](checkpoint-candidates/2026-10-14-additional-sources/REPORT.md)
  фиксируют несовпадающие recipes и недоступные веса. PeRL LoRA/DoRA имеют разные LR;
  label `dora` у одной серии не заменяет проверку `use_dora`.
- [SmolLM2 readiness](checkpoint-candidates/2026-10-14-smollm/READINESS.md) и
  [pilot report](checkpoint-candidates/2026-10-14-smollm/PILOT_REPORT.md) — подготовка
  отдельной проверки, не новая полная независимая matched benchmark серия.
- Qwen3-8B и LLaVA исключены; Answer.AI отложен после отказов в доступе.
  Не обучать отсутствующие пары самостоятельно и не повторять запросы автоматически.

## 4. Карта проверенных идей и гипотез

`FAIL` означает провал заранее выбранного критерия в конкретной постановке,
а не невозможность всей области. Реестр условий пересмотра находится в
[RESULTS_AUDIT](research-direction/2026-10-14-pause/RESULTS_AUDIT.md).

| Вопрос / идея | Где доказательства | Последний исход и границы |
|---|---|---|
| DoRA стабильно лучше отдельно обученной LoRA? | [Quality overview](analysis/2026-10-11/results/quality-overview.csv), [follow-up](analysis-followup/2026-10-11/ANALYSIS_SUMMARY.md) | Общее преимущество не установлено. Не опровергает DoRA на других задачах. |
| Нужен ли конечный радиальный множитель D для качества? | [Full interventions](analysis-followup/2026-10-11/ANALYSIS_SUMMARY.md), [new controls](analysis/2026-10-12-next-experiments/REPORT.md) | Малые средние изменения могут скрывать перестановку правильных ответов. Не доказывает ненужность D в обучении. |
| Специализация Q/K и взаимодействия Q/K, V/O | [Localization](analysis/2026-10-11/results/localization-findings.md), [direct contrasts](analysis-followup/2026-10-11/ANALYSIS_SUMMARY.md) | Q−K зависит от scorer и поправки. Все 8 CI взаимодействий включают 0; аддитивность не доказана. Это проекции во всех слоях, не отдельные нейроны. |
| Геометрия обновлений инвариантна при одинаковой функции? | [THESIS](research-direction/2026-10-13/THESIS.md), [FP32 fidelity](analysis/2026-10-13-fidelity-audit/REPORT.md) | Entropy/effective-rank меняются при сохраняющей функцию V/O-симметрии. Сам принцип известен; trained-checkpoint correlation и training cause не опровергнуты. |
| KL-рейтинг отдельных V/O абляций определяется только функцией? | [Математика](analysis/2026-10-14-ablation-commutation/MECHANISM.md), [Qwen64](analysis/2026-10-14-ablation-commutation/FRESH_REPORT.md), [Mistral128](analysis/2026-10-14-mistral-ablation/FRESH_REPORT.md) | На Qwen ranking reversal подтверждён; NLL/accuracy reversal не установлен. На Mistral подтверждающий gate FAIL. Не искать удобные масштабы задним числом. |
| Всё объясняется BF16 или стабильной normalization? | [Precision screen](analysis/2026-10-14-precision-ablation/REPORT.md), [fidelity](analysis/2026-10-13-fidelity-audit/REPORT.md) | Разделены вычислительные ошибки и эффект представления; простой precision-only вывод не подтверждён. BF16 no-op нельзя предполагать. |
| Scale search, base anchor, локальное joint V/O сжатие | [Compression follow-up](analysis/2026-10-13-compression-followup/REPORT.md), [budget](analysis/2026-10-13-budget-screen/REPORT.md) | Нового преимущества против сильных comparator не установлено. Не продолжать прежнюю сетку масштабов. |
| D-refit и полное сжатие | [Radial recalibration](analysis/2026-10-13-radial-recalibration/REPORT.md), [full compression](analysis/2026-10-13-full-compression/REPORT.md) | Gates пользы не пройдены. Fixed-D представление не равняется standard LoRA. |
| E99 / спектральное распределение ранга | [Allocation diagnosis](analysis/2026-10-14-allocation-diagnosis/REPORT.md), [restoration](analysis/2026-10-14-allocation-diagnosis/RESTORATION_REPORT.md) | Улучшение локальной ошибки не переносится на teacher KL; прежняя allocation ухудшала его. |
| KFAC orientation / совместное D+low-rank приближение | [Orientation](analysis/2026-10-14-kfac-orientation/REPORT.md), [affine candidate](analysis/2026-10-14-affine-candidate/REPORT.md) | Против KFAC benefit gate не пройден. Разница EF/teacher-Hessian известна; не новый алгоритм. |
| Сохранить ранг и снизить точность при byte cap? | [Byte budget](analysis/2026-10-14-byte-budget/REPORT.md) | На development данных INT8 fixed-D лучше конкретного FP32 rank8 baseline. Известный precision/rank tradeoff, не новый compressor, speed или VRAM result. |
| Есть head-capacity основание для компрессора? | [9-head screen](analysis/2026-10-14-head-capacity/REPORT.md) | Внеранговые хвосты ничтожны; gate FAIL. Не расширять выбор голов по просмотренному исходу. |
| Можно предсказывать необходимость D? | [SmolLM2-B64](analysis/2026-10-14-radial-necessity/REPORT.md) | Первичные вмешательства не меняют correctness; gate FAIL. Предиктор с проверенной полезностью не построен. |
| Особая downstream компенсация радиального вмешательства? | [Downstream response](analysis/2026-10-14-downstream-response/REPORT.md) | Gate FAIL: last-block contrast ниже порога, ранние эффекты численно неразрешены. |
| Радиальная опора меняется во время обучения? | [PeRL trajectory](analysis/2026-10-14-perl-trajectory/REPORT.md), [magnitude provenance](analysis/2026-10-14-magnitude-provenance/REPORT.md) | Относительный эффект падает из-за denominator; абсолютный мал, gate FAIL. Stored m идентичен на 3 steps; про master weights/gradients причинный вывод невозможен. |
| Малый removeD скрывает большую компенсацию magnitude и normalization? | [Последний factorial screen](analysis/2026-10-14-component-decision/REPORT.md) | На 8 случаях оба gates FAIL, все teacher KL < .001; validation64/Mistral не запускались. Не снижать порог после результата. |
| Ошибки SORA меняют научный вывод статьи? | [Code audit](analysis/2026-10-14-sora-code-audit/REPORT.md), [claim screen](analysis/2026-10-14-sora-code-audit/CLAIM_SCREEN_REPORT.md), [артефакты](analysis/2026-10-14-sora-code-audit/ARTIFACT_ACCESS.md) | Подтверждены export/unmerge/loading дефекты pinned кода; restricted entropy theorem выдержала проверку. Веса не получены; качество статьи не опровергнуто, знак исправления неизвестен. Письмо не отправлено. |

**Не смешивать checkpoints:** Mistral gauge validation —
`fzzhang/mistralv1_dora_r32_25e5_e05`, magnitude audit —
`fzzhang/mistralv1_dora_r16_25e5_e03`. Наблюдение о magnitude второго
не объясняет отсутствие переноса на первом.

## 5. Ближайшая литература и границы новизны

- [LoRA / DoRA mechanisms](literature/2026-10-11-lora-dora-mechanisms.md).
- [Аудит adapter compression](literature/2026-10-14-adapter-compression-audit.md)
  и [сравнительная таблица](literature/2026-10-14-adapter-compression-comparison.csv):
  цели методов, бюджеты, активации, структуры DoRA и код.
- [Affine novelty](literature/2026-10-14-affine-novelty-addendum.md),
  [Fisher objective](literature/2026-10-14-fisher-objective-audit.md),
  [LEMS code](literature/2026-10-14-lems-code-audit.md),
  [radial scale](literature/2026-10-14-radial-scale-addendum.md).
- В [component PRIOR](analysis/2026-10-14-component-decision/PRIOR.md) учтён
  DeLoRA appendix C: fixed-magnitude training и compensation не новые идеи.
  Совместное V/O сжатие встречается в LatentLLM, precision tradeoffs — в
  Scaling DoRA / DoRAFactors. Ссылки и уточнения в указанных обзорах.

Обзоры — отправная точка, не гарантия полноты. Перед новой гипотезой проверить
свежие первоисточники, предпосылки и авторскую реализацию. Не считать неудачу
нашего baseline недостатком опубликованного метода без проверки корректности
загрузки, задачи и допустимого бюджета.

## 6. Отчёты, код и артефакты

| Часть репозитория | Как использовать |
|---|---|
| [analysis-preparation](analysis-preparation/) | Исходные таблицы, inventory, checks целостности; подготовка не равна интерпретации |
| [analysis-followup](analysis-followup/) и [analysis](analysis/) | Читать SPEC → REPORT → validation / manifest → rows |
| [execution/scientific-analysis](../execution/scientific-analysis/) | Анализаторы и audits соответствующих исследований |
| [execution/next-experiments](../execution/next-experiments/) | Screen / validation workers и schedulers. Conditional validation мог не состояться |
| [lora_dora_study](../lora_dora_study/) | Загрузчики и математические реализации; [tests](../tests/) проверяют отдельные свойства |
| [configs](../configs/) | Рецепты и revisions; конкретный результат определяет его SPEC / manifest |
| [HANDOFF](HANDOFF.md) | Хронология исправлений и решений. Верхние записи актуальнее нижних |

Manifest hashes фиксируют provenance; не переписывать исторический SPEC
или evidence для понравившегося вывода. Исправление оформлять отдельной записью.
В Git — код, отчёты и компактные данные. Веса, datasets, большие logits,
raw generations и приватные locators находятся вне Git. Без приватного доступа
можно читать и анализировать этот пакет, но нельзя объявлять полное модельное
воспроизведение выполненным. Сведения о серверах не возвращать в публичные файлы.

## 7. Условия продолжения после явного разрешения

1. Выбрать **один** самостоятельный вопрос, ещё не закрытый в нужной постановке.
   Сформулировать пользу и границы, а не просто очередной прогон.
2. Проверить ближайшие работы и решения; записать различие с ними.
3. Для алгоритма сначала показать существенную локализованную ошибку сильного
   допустимого comparator. Сейчас такого основания для нового compressor нет.
4. Записать минимальный screen, numerical controls, независимую validation,
   бюджет и критерии остановки до результата. Учитывать scorer, multiplicity,
   происхождение cases и отсутствие независимых seeds.
5. Проверить прошлые отрицательные попытки. Не менять c, threshold, слой или
   датасет только для спасения проваленной гипотезы.
6. После каждого разрешённого этапа обновлять HANDOFF: результат, версии,
   публичные артефакты, приватный locator отдельно, дальнейшее решение.

Никаких автозапусков по этому списку. Документация готова для передачи;
выбор следующего вопроса и возобновление — отдельный шаг.
