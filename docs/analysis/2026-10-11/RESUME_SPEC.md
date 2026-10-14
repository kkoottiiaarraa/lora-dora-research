# Возобновление и завершение анализа — 11 октября 2026

Пользователь явно возобновил научный анализ. Модель помощников gpt-6.1-sol;
reasoning не выше xhigh («очень высокий»), max/ultra не использовать.
Остановка в CHECKPOINT.md историческая; прежние выходы сохраняются как исходная
точка продолжения. Публикация очищенного snapshot уже выполнена: d3e324a,
research/prepare-checkpoint-study. Приватную Git-историю не публиковать.

Общий план PLAN.md и estimands/seeds EXECUTION_SPEC.md сохраняются. Только
анализ существующих данных; никаких новых модельных запусков, SVD весов,
обучения, GPU-очередей, зависимостей или автоматической Answer.AI проверки.
Вычисления на CPU существующего исследовательского сервера, максимум два
потока на задачу; VM только код и компактные результаты. Неизменяемый bundle,
evaluator, predictions и старые validation не менять.

## L: завершить локализации

Входы и метод — пакет L в EXECUTION_SPEC.md. Сохранённый build_localizations.py
проверить и исправить только при необходимости; завершить на CPU. Обязательные
выходы в results/: 28 localization-effects, восемь joint-interactions,
paired-outcome-transitions, localization-effects.svg, localization-findings.md,
localization-validation.json. Сохранять обе схемы ответов, исходные CI/p и их
семьи, новый paired bootstrap 50000 с заданными seeds и Holm8 для interactions.
Сверить alignment, source hashes, transitions, все 14 условий и means. Не
объявлять взаимодействие на шкале точности уникальным механизмом сети.
Исполнитель владеет только build_localizations.py и перечисленными L-выходами.

## T: независимая приёмка математической области

Входы symmetry-scope.md, theory-audit.md, сохранённый фактический код V/O и
пакет 03, PLAN L1–L9, обзор литературы. Проверить V/O/GQA, fixed/joint base,
DoRA-r против additive LoRA-r, FP32 pre-cast против BF16 deployed, rho против
slope, detached denominator против итогового forward. Проверять уже доступные
тексты/код; не считать новые модели. Выход theory-review.md с явным списком
принятых/исправленных тезисов и точными file:line либо source URLs. Если правки
нужны, исполнитель меняет только symmetry-scope.md/theory-audit.md. Цитировать
реальный тезис статьи, не усиленный нами. Отсутствие training data/траекторий
фиксировать как неидентифицируемость. Новизну не объявлять доказанной.

## I: техническая интеграция

Создать execution/scientific-analysis/verify_analysis.py — read-only verifier,
не перезаписывающий входы/validation. Проверить bundle manifest и Q/C output
hashes, counts, schemas, exact references, диапазоны значений, L после готовности.
Новый analysis-manifest.json: inputs/plan/spec/code/outputs с SHA256 и статусами;
собственный hash и volatile verification report исключить во избежание цикла.
Сначала можно реализовать и проверить Q/C, затем после сообщения основного
агента добавить L/T/REPORT/claim-evidence. Запуск на CPU сервера. Выход
integration-validation.json фиксирует checks/errors и scope. Без повторного
bootstrap принятых Q/C без основания. Исполнитель владеет verifier/manifest/
integration-validation, не изменяет научные findings и исходные validation.

## Итог основного агента

Принять L/T, завершить claim-evidence L1–L9 и REPORT/limitations, отделить
подтверждённые наблюдения, ограничения, известную алгебру и кандидатов вклада.
Главные conclusions должны учитывать отсутствие установленной DoRA-победы,
scorer/dense conversion, pointwise/exploratory scope. Обновить HANDOFF,
CHECKPOINT и краткую сводку для ментора. Публикация новых изменений отдельно
от вычислений; текущую приватную историю не push.
