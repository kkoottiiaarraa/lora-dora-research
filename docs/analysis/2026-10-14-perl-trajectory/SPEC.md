# Роль радиальной части на опубликованной траектории PeRL

Задано до загрузки весов и outputs, 14 октября2026.

## Почему это другой вопрос

Конечная dispensability D не показывает его inference role в промежуточных
состояниях. Готовые PeRL checkpoints дают проверку без нового обучения.
[PeRL](https://arxiv.org/abs/2512.23165) сам оставляет adapter dynamics будущей
работой. [DoRA ICML2024](https://proceedings.mlr.press/v235/liu24bn.html) уже
изучает weight correlations на промежуточных шагах; одна новая кривая норм
не новизна. [BiDoRA TMLR2025](https://openreview.net/forum?id=v2xCm3VYl4)
изучает раздельную оптимизацию компонентов. Наша ограниченная проверка —
inference interventions на фиксированных одинаковых inputs по траектории.
Она **не** показывает необходимости компонента при обучении или causal
преимущества метода. Один seed не становится множеством независимых опытов.

## Provenance и фиксированный дизайн

MikaStars39/PeRL revision3056decc9b83357fc50993aea984e2028704f833.
DoRA directory dapo_dora_qwen2_5_1_5b_20251126_115730, steps64/512/1024,
r32 alpha64, все7 attention/MLP targets, 196 modules/588 tensors.
Config идентичны; JSON training histories64/512 точно совпадают с префиксами
1024. LR1e−5. LoRA-r32 в release LR5e−6: не matched method comparator,
в этот screen не включается. 7B misleading folder use_dora=false исключён.

Ungated base deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B,
revisionad9f0ae0864d7fbcd1cd905e3c6c5b069cc8b562.
Adapter training base revision неизвестна; не считать current pinned revision
доказанным авторским training revision. SHA256 файлов проверяется.

CPU FP32 SDPA8threads, no GPU/training/generation. По16 одинаковых GSM8K train
questions начиная с прежнего index232; исключить test duplicates и повторы.
Только структурные filters: ответ≥32tokens, input≤512tokens. Base chat template,
32 первых gold answer targets, teacher forcing. Это диагностическая область,
не PeRL benchmark reproduction/independent quality test; training overlap unknown.

Условия: исходная base; для каждого шага native DoRA, removeD(D=1),
baseMagnitude(m=m0, сохраняет normalization). Сохранить A/B, m и base norm
summaries для всех196modules, но не объявлять корреляции причиной.
Full-vocab KL относительно native, gold NLL, source-vs-base KL на тех же inputs.
Norm decomposition отделяет learned magnitude от direction normalization.
Native source repeat, restore, exact saved tensors, finite checks,
2-case native-vs-independent-dense control для каждого шага до contrasts.

## Gate и остановка

Primary hypothesis: временная радиальная опора — normalized removeD role
R_t=mean KL(native_t||removeD_t)/mean KL(native_t||base) наstep64
как минимум в2раза вышеstep1024; paired whole-question bootstrap95 для
log(R64/R1024) исключает0. Требуются early mean removeD KL≥1e−3 и
численный floor<1% всех сравниваемых logit effects. Не делить на epsilon:
нулевой/negligible base drift делает normalized inference неопределённым.
Midpoint фиксирован как descriptively проверяющий форму, не новый primarytest.

Заранее заданное противоположное наблюдение: рост роли≥2раз с late meanKL≥1e−3
и CI исключает0 — primary hypothesis опровергается на этой траектории; отдельная
exploratory эволюция, не подтверждение transient scaffold. Не выбирать метрику
по результатам. Bootstrap over questions не даёт uncertainty across runs.

Только при прошедшем содержательном gate — фиксированное продолжение на
остальных опубликованных шагах и новых inputs, без выбора удачных шагов.
При negative/inconclusive gate не расширять эту траекторию ради графика.
Никакого нового алгоритма из одной кривой; он требует конкретного failure
сильного comparator. Protective CPU cap20min, downloads bounded to4filesets.

## Дополнительный audit до outputs: наблюдаемая эволюция magnitude

До inference сравнить exact stored m между тремя steps и с norm(base),
округлённой к storage dtype. Это отличает реальные изменения сохранённого m
от direction normalization/initial rounding. Если m не меняется, это само по
себе не доказывает frozen gradients/master weights и не объясняет training.
Проблема low-precision DoRA gain известна: авторский
[DoRAFactors precision contract](https://sockeye44.github.io/dorafactors-docs/how-it-works/)
и [Scaling DoRA](https://arxiv.org/abs/2603.22276). Не заявлять открытие BF16freeze.
Это проверка applicability именно released trajectory, без нового обучения.
