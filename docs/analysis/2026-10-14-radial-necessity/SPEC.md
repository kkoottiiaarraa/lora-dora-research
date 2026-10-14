# Ограниченный development screen: что именно делает D?

14 октября2026. Зафиксировано до outputs этого опыта. Это проверка основания
для идеи5, не подтверждающая проверка предиктора, не новый алгоритм, не оценкаB.

## Основание и приоритет

Восемь технических примеров SmolLM2-B имеют6/8correct уLoRA/DoRA/removeD.
Необходимость D этим не решена. Исходный Qwen имеет малое отклонениеD, и
перенос прежней сетки не оправдан. Следующий ограниченный вопрос: есть ли
вообще существенный эффект D на реальных ответах нового готового checkpoint,
и относится ли он к обученным величинам, нормировке направления или rowshape?

При PyTorch orientation U=W0+sBA, m0=rownorm(W0), n=rownorm(U):
D=m/n=(m/m0)*(m0/n). Поэтому удалить D не равно удалить learned m.
Пусть g=exp(mean(logD)), barD=D/g. Последние — условное разложение на общий
масштаб и относительные значения, не единственно верная causal convention.

[DoRA §4.1/5.6](https://arxiv.org/html/2402.09353v3) уже обучает m и исследует
разную granularity. [Weight Normalization](https://arxiv.org/abs/1602.07868)
— предшественник разложения. [Learnable Multipliers §4.1/C.2](https://arxiv.org/html/2601.04890v1)
уже описывает row/column scales, избыточность Q/K и V/O и зависимость training
от scales. Нового общего принципа множителей/симметрий здесь не заявляем.
[SORA §3](https://arxiv.org/html/2511.00051v2) связывает high-rank conditioning
с quality, но изменения конечных весов не устанавливают training mechanism.
Наш screen отвечает более узкому checkpoint counterfactual вопросу.

## Источник и данные

Одна база/параB из pinned SmolLM2 readiness, CPU8FP32SDPA, без обучения/GPU.
Все128QKVOmodules меняются вместе, W0/A/B/r/alpha остаются фиксированы.
LoRA — отдельный готовый baseline, не доказательство causal effect метода обучения.

Из author-validation sample0010 выбрать первые64rows после первых8pilotrows,
с уникальными normalized user_request (lowercase+whitespace collapse); исключить
также все8pilotrequeststrings. Не выбирать по labels/исходам/длинам. Если64нет,
остановиться; не дополнять test. Source Git revision d0196d9122f84597eec8b44254a48d6885e1b90f.
Content hashes/indices сохранить доoutputs. Выборка development, уже использованная
автором для validation при обучении исходных checkpoints, не independent test.

Pinned split audit:800train/100val/100test, full и sorted-tool semantic duplicates
между splits0. Но normalized requests совпадают train↔val в82из86uniqueval и
train↔test в73из78uniquetest. Поэтому не заявлять обобщение на новые формулировки
и независимость произвольных100строк. Различные toolsets создают разные задачи;
повтор request не равен тождеству полных примеров. Точная очистка не исключает
near duplicates. Source synthetic, seed/base-training SHA неизвестны.

## Ровно семь условий

1. Native DoRA (reference).
2. Полный removeD: effective weight U.
3. Base magnitude: m←m0, effective D=m0/n (нормировка направления без learned m).
4. Learned-only: m←(m/m0)*n, effective D=m/m0 (learned factor без norm correction).
5. Scalar-D: m←g*n, effective D=gI.
6. Centered-D: m←m/g, effective D=barD.
7. Native LoRA, та же база/prompt/generation/scorer.

Не складывать effects по loss: сеть нелинейна. Scalar/centered constructions
эквивариантны к положительному модульному scaling; coupled V/O sourcegauge
сохраняет их функции. Это частная группа, не all-gauge causal invariance.
Base-magnitude/fullremoveD при allQKVO также не зависят от изменения source m.
Learned-only при V/Osourcegauge эквивариантен, оба компонента масштабируются
сопряжённо. Не менять A/B/base и не подбирать g по данным.

У всех64case greedy generation maxnew8 с source trainingcallback prompt;
scorer case-sensitive ID, no-tool '-', invalid output считается ошибкой.
Full-vocabulary первый generation score используется для goldNLL/KL;
это отдельная метрика, не замена accuracy. Та же generation path у reference
и всех условий. Сохранить raw tokens/output/predictions/validity/timings.
Измерить all parameters finite, exact adapters128modules/256or384tensors,
tokenizer/gold boundaries, source2repeat/restoration bitwise; контролировать
source gauges .995/1.005 только2cases и dense control2cases. Не делать fullno-op.
Floor<1%meanremoveD RMS; иначе scientific interpretation не принимается.

## Gate и остановка

Заранее ограниченный engineering gate: для removeD или base-magnitude относительно
nativeDoRA либо потеря минимум4correct из64, либо correctness меняется минимум
на8из64cases. Публиковать и gains и losses; это не значимость и не noninferiority.
NLL/KL изменения сами по себе не проходят gate. Выбор gate after8smoke явно exploratory.
Если gate не пройден, не строить predictor и не расширять эту конфигурацию/ранги/
модели ради положительного результата. Если пройден, разобрать whichfactor и
независимо зафиксировать predictor+heldout test; не использовать этот набор для
доказательства обобщения и не запускать автоматически test/другие пары.

Только448generations, 12tinyforward controls; защитныйtimeout20min, не целевой
расход. По8casepilot ориентирCPU8около5–10min, зависит от длин/нагрузки;
GPU0часов. При technical failure сохранитьattempt, исправить до новыхoutputs,
guardнеослаблять. Версии/source/weights/casehashes/resourcewall сохраняются.
Агенты не используются. Модели после worker exit освобождаются.
