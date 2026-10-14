# Локальная проверка метрики и первый joint affine prototype

14 октября2026. Это две локальные проверки; преимущества на задачах пока нет.

Соглашение нижнего Cholesky в проверенном авторском KFAC-SVD коде не минимизирует
стандартный `tr(E^T G E C)` для собранного G. На12заранее выбранных проекциях
слоёв0/17/35 фактическая ошибка кодового решения выше правильного минимума
в среднем2.438раза, максимум10.098. Проверены реальные Gram matrices из8старых
calibration вопросов. Правильная формула уже есть в OBD-LLM Eq.17; новизна
перестановки transpose не заявляется. Это также не опровержение качества
опубликованного KFAC-SVD: другая метрика может случайно оказаться полезнее.

Послеtiny FP64тестов выполнен ограниченный prototype на4проекциях слоя17:
5фиксированных block cycles jointly fitting D и L/R, с тем же row metric.
Критерий уменьшился на25.54%против fixed-D; агрегатная ошибка составила79.28%
от ordinary rank8two-sided approximation. Выигрыши против fixed-D по O/V/K/Q:
32.55%/7.70%/16.80%/23.49%. Это local objective, не teacherKL/accuracy.

В prototype применены source-independent structural ranks7/8 из полного
бюджета. Отдельные4module бюджеты не равны ordinary rank8; поэтому отношение
79.28% **не является полноценным matched-storage сравнением**. Максимальные
изменения D малы, но изменение L/R может существенно влиять на objective.

Generic alternating least-squares известен; novelty exact DoRA application
не установлена. Данные дают основание ровно для одного полного кандидата,
который должен превзойти и fixed-D, и ordinary influence-aware baseline
на новых вопросах при одинаковом общем размере адаптера.

Orientation capture/decomposition280.30s CPU; affine prototype195.09sCPU4,
GPU0часов. Оба завершены, новых validation данных не использовали.
Численные проверки coupled diagonal solve против explicit design least-squares,
weighted SVD tail и monotonic block descentPASS.

Артефакты: [local-diagnostics.json](local-diagnostics.json),
[validation.json](validation.json), [AFFINE_PROTOTYPE_SPEC](AFFINE_PROTOTYPE_SPEC.md),
[авторский code audit](../../literature/2026-10-14-lems-code-audit.md).
Сохранённые prototype факторы и статистики находятся на сервере; locators приватные.
