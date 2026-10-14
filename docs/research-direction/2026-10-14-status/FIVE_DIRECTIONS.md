# Пять направлений: что осталось после проверок

14 октября2026. Обновление исходного тирлиста13октября по фактически сохранённым
результатам. Порядок исходный, а не новая оценка вероятности публикации. Ни одно
направление пока не дало законченного материала уровняB. Отрицательные проверки
закрывают конкретную конфигурацию или процедуру, не доказывают невозможность темы.

| Направление | Сделано | Решение |
|---|---|---|
| 1. Ошибки выбора рангов/слоёв по геометрии | Сохраняющая функцию симметрия меняет E99 budget до2.51раза. Полная spectral allocation при одинаковом бюджете уменьшает локальную ошибку, но ухудшает teacherKL в2.55–2.68раза. | Этот способ allocation закрыт. Изменение proxy подтверждено, полезное исправление не найдено. Не считать другие предложения статьи опровергнутыми без точной репликации. |
| 2. Новый алгоритм сжатия | Проверены scale search, base anchor, local jointV/O; полные D-refit и jointD+lowrank; разные конструкции/сильные baselines. | Испытанные исправления не прошли benefit gates. Joint выигрывает у W-SVD, но лишь1.66% против KFAC-SVD, CI содержит0. Не расширять прежнюю сетку. Вся область не закрыта. |
| 3. Надёжность абляций | Qwen KLordering V/O меняется при сохранении source/fullremoveD, есть точное объяснение через branchgain. Mistral128NLL подтверждение не прошло. Precision отдельно меняет величину, не знак средних. | Методологический результат есть; переносимый практический вывод уровняB не показан. Precision-only ветка закрыта по данному screen. Перепараметризация не опровергает абляцию как вопрос о конкретной записи весов. |
| 4. DoRA→меньшая обычная LoRA без обучения | Полный144module adapter compression, разные цели/бюджеты; structural fixedD controls; фактический safetensors byte audit. | Нет нового конкурентоспособного конвертора. Более высокий rank при меньшей точности хранения намного сильнее FP32rankreduction при том же bytecap. FixedD INT8 остаётся DoRA-structured/custom archive, а не стандартным PEFTLoRA checkpoint. |
| 5. Предсказать необходимость D | Исходные локальные/полные абляции; bounded head-capacity diagnostic на9heads. | 64-request SmolLM2-B screen: removeD/baseMagnitude не изменили correctness ни одного ответа; gate не пройден, predictor для этой конфигурации не строим. Предиктор ещё не проверен; тема целиком не опровергнута. |

## Прямые доказательства

- [Compression candidates](../../analysis/2026-10-13-compression-followup/REPORT.md).
- [Full-adapter compression](../../analysis/2026-10-13-full-compression/REPORT.md).
- [Allocation](../../analysis/2026-10-14-allocation-diagnosis/REPORT.md).
- [Joint affine candidate](../../analysis/2026-10-14-affine-candidate/REPORT.md).
- [Storage precision baseline](../../analysis/2026-10-14-byte-budget/REPORT.md).
- [Qwen ablation](../../analysis/2026-10-14-ablation-commutation/FRESH_REPORT.md),
  [точное объяснение](../../analysis/2026-10-14-ablation-commutation/MECHANISM.md).
- [Mistral confirmation](../../analysis/2026-10-14-mistral-ablation/FRESH_REPORT.md).
- [Backend/precision](../../analysis/2026-10-14-precision-ablation/REPORT.md).
- [Head-capacity gate](../../analysis/2026-10-14-head-capacity/REPORT.md).

## Следующий шаг и допустимые развилки

Новая ungated пара [SmolLM2-B](../../checkpoint-candidates/2026-10-14-smollm/READINESS.md)
выбрана структурно, не по DoRA advantage. Сначала техническая приёмка, не новый
full benchmark. Короткий pilot не отвечает на необходимость D.

При успешной приёмке следующий вопрос: различимы ли эффект общего branchgain
и относительных rowpatterns на реальных правильных ответах? Сначала проверить
приоритет/точные определения и исходный author split. Predictor/generalization
требуют отдельного замороженного протокола, train/validation/test audits и
контролей. Новый checkpoint сам по себе не даёт новизны.

Резерв: показать не только зависимость KL, а ошибку конкретного решения из
абляции и полезное исправление на новых данных. Ещё один неизвестный компрессор
допустим только после установленного ограничения сильного baseline, включая
простое уменьшение точности хранения. Статью пока не пишем, агентов не создаём,
обучение запрещено, GPU1 исключена. Универсального превосходства DoRA и причины
обучающей траектории конечные checkpoints не устанавливают.

Обновление после screen: [radial necessity REPORT](../../analysis/2026-10-14-radial-necessity/REPORT.md). В этой конфигурации расширения закрыты; новогоBрезультата нет.
