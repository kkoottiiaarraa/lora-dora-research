# Контрольная точка: исследование приостановлено пользователем

Дата: 14 октября 2026, пользовательский часовой пояс — Москва.
Ветка: `research/two-extra-series`. Предшественник публикации handover:
`1174626fa36819dd80e606e0f1f18f57636c63ba`; актуальный commit смотреть в Git.
На момент остановки были незакоммиченные исследования; пользователь затем
разрешил их commit/push вместе с навигацией. Это сохраняемые результаты,
а не мусор. Не использовать git clean/reset для их удаления.
Новая точка входа: [RESEARCH_NAVIGATOR](../../RESEARCH_NAVIGATOR.md).

## До продолжения

Пользователь остановил исследование. Не запускать модели, скачивания, очереди,
обучение, авторские письма или старые автономные контроллеры без нового указания
продолжить работу. Текущих исследовательских workers/GPUholders нет.
Два исторических CPUмонитора намеренно остановлены. Их исходники сохранены
приватно; автоматически перезапускать их не нужно: они относятся к старым очередям
и исторически писали в несколько рабочих копий.

## Что читать

1. AGENTS.md, MEMORY.md, начало docs/HANDOFF.md и docs/CONTINUE_RESEARCH.md.
2. [Аудит всех результатов и отрицательных направлений](RESULTS_AUDIT.md).
3. [Последний завершённый эксперимент](../../analysis/2026-10-14-component-decision/REPORT.md).
4. [Первоначальные пять направлений](../2026-10-14-status/FIVE_DIRECTIONS.md)
   и ссылки на их конкретные проверки. Последний audit имеет приоритет над
   устаревшими предложениями расширения в исторических отчётах.

## Сохранённые данные

- Полные baseline/intervention/localization bundles: docs/analysis-preparation,
  docs/analysis/2026-10-11/results, docs/analysis-followup.
- Последующие controlled experiments: docs/analysis/2026-10-12*–2026-10-14*.
- Source/code/claim audits SORA, literature/prior audits и inventory кандидатов
  сохранены полностью, включая отрицательные исходы и rejected comparator recipes.
- execution/ и lora_dora_study/ содержат как успешные, так и не прошедшие gates
  реализации; tests/ — их проверки. Prepared conditional validation код не равен
  выполненному validation: проверять статус соответствующего REPORT/manifest.
- Публичные файлы содержат revisions/hashes/условия/версии. Веса, datasets,
  большие logits, rawgenerations остаются на вычислительном сервере.
- Operational доступ и точные пути: outer `local-only/OPERATIONS_PRIVATE.md`
  и experiment `*-private.json` / `locator-private.json`. Не копировать их вGit.
- Локальный снимок всех текущих tracked+nonignored untracked files, diff/status
  и архивный manifest: outer `local-only/pause-audit-20261014/`.
  Этот снимок не содержит .git, cache, weights или private infrastructure context.

## Как не начать ходить по кругу

В RESULTS_AUDIT перечислены закрытые постановки и условия пересмотра.
Не менять порог/слой/масштаб после отрицательного gate для получения сигнала.
Не выдавать повторение известной симметрии, отрицательныеaccuracycontrasts,
многоGPUчасов или новую модель за научную новизну.
Не путать Mistralr32 gauge validation и Mistralr16 magnitude audit.
SORA code errors не доказывают ошибки publishedqualitytable; restricted entropy
теорема не опровергнута. Endpoint вмешательства не устанавливают trainingcause.

После явного возобновления сначала выбрать законченный вопрос: учебная работа
по воспроизводимости/ограничениям интерпретации или новый самостоятельный
научный тезис с основанием. Для compressor нужно сначала локализовать failure
сильного допустимого baseline. НовоеGPUgeneration без такого вопроса не нужно.
