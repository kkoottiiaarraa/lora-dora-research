# Критерий необходимости D не пройден: SmolLM2-B

14 октября2026. Приняты448greedy generations,64уникальных normalizedrequests,
7условий, общий frozen protocol/source/weights. Это development screen на
авторской validation, не independent test или проверенный predictor.

| Условие | Correct /64 | Gains / losses относительно native | Изменённых predictions |
|---|---:|---:|---:|
| dora | 32 | 0 / 0 | 0 |
| remove_d | 32 | 0 / 0 | 1 |
| base_magnitude | 32 | 0 / 0 | 1 |
| learned_only | 31 | 0 / 1 | 1 |
| scalar_d | 32 | 0 / 0 | 1 |
| centered_d | 32 | 0 / 0 | 0 |
| lora | 32 | 1 / 1 | 4 |

Полный removeD и base-magnitude не изменили правильность ни одного ответа.
Оба изменили ровно один неправильный ID на другой неправильный ID. Gate
требовал потерю>=4correct или>=8correctnessdiscordances; оба имеют0/0.
По этой конфигурации predictor не строим, test/новые модели/ранги не добавляем.
Ноль различий не доказывает population equivalence и не устанавливает
noninferiority с заданным допуском. Вопросы не все новые относительно обучения.

Learned-only потерял один правильный ответ, хотя среднее расхождение logits
меньше removeD. Это один development случай возле границы решения, а не
переносимый механизм необходимости m или статистически сильный результат.
Остальные scalar/centered counterfactuals не дают нового существенного эффекта
на correctness. Полные NLL/KL/RMS в quality.csv; ими не заменяем failedaccuracygate.
Сохранение D и необходимость его обучения — разные вопросы. По готовым весам
альтернативную trajectory без обучения m не наблюдали.

Нативные LoRA/DoRA имеют равные32correct, но это не доказательство равенства
методов, matched seed comparison или отсутствия пользы DoRA в других условиях.
Источники/неизвестные training revisions/seed и gradientcheckpointing confound
сохранены в readiness. Нельзя заявлять универсальное объяснение преимуществ.

## Приёмка и ограничения

Каждыйconditionпокрываеттеже64cases; unique request hashes64. Фактический
hashcases на сервере независимо совпал с frozen/summary. Exactloadedadapters
128modules/256LoRA или384DoRAtensors; source восстановлен побитно. Все scores
finite, invalid predictions0. Пересчитаны postrowaccuracy,counts,referenceNLL
alignment,гейтыиусловные агрегаты. Это приёмка данных, не новый статистическийанализ.

WorstcontrolRMS=9.37903926e-06; removeDmeanRMS=0.0473621754; floor/effect=0.019803%, ниже1%. CPU8wall=508.68s,peakRSS=3.478GiB,GPU0часов. Workerterminal,model/RAMreleased.

Split audit: full/semantic overlap0, но повторения requests с разными toolsets
часты междуtrain/val/test. Выбор64уникальных requests уменьшает внутренние
повторы, но не делает набор новой независимой естественной выборкой. Eightpilot
requests исключены, originaltest не оценивался. Условие остановки не менялось.

[validation.json](validation.json),[quality.csv](quality.csv),[contrasts.csv](contrasts.csv)
содержат actualversions/revisions/code/casehashes и все результаты.
Rawprivate:local-only/radial-necessity-results-20261014/; locator
local-only/radial-necessity-20261014-private.json. Основные weights/logits остаются
на compute host. НовогоBрезультата нет; статью пока не пишем, training/agentsнет.

Следующий идейный шаг требует нового конкретного нерешённого вопроса с primary
prior audit и дешёвой проверкой основания. Не продолжать эту конфигурацию
путём выбора другихслоёв/рангов/примеров послеfailedgate.
