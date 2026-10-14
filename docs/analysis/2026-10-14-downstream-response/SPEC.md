# Что подавляет эффект D: ограниченная проверка downstream response

14 октября 2026. Задано до новых outputs. Пользователь просит сначала
неалгоритмические направления, без агентов/обучения/письма авторам.

## Вопрос и приоритет

Малое изменение функции после удаления конечного D может означать малую
локальную дозу, немедленную нормировку либо downstream attenuation.
Общая self-repair известна: [Hydra](https://arxiv.org/abs/2307.15771),
[Rushing/Nanda ICML2024](https://proceedings.mlr.press/v235/rushing24a.html),
[Every Ablation Is a Dose, 2026](https://arxiv.org/abs/2610.02173).
Новый общий принцип компенсации не заявляется. Здесь проверяется, есть ли
**особая** downstream attenuation радиального вмешательства против простого
контроля той же локальной силы. Это exploratory gate, не механизм обучения.

## Фиксированный дизайн

Qwen3-4B/GSM8K готовая DoRA, source W0/A/B/m pinned как в прежних опытах.
CPU FP32 SDPA, общий dense reference после native/dense controls.
Три заранее заданных attention блока: layers0/17/35.
Joint removeD **V и O в одном блоке**, остальные параметры исходные.
Это вмешательство инвариантно к прежде проверенной scalar V/O gauge.
Не повторять отдельные V/O ranking checks и не выбирать новые layers по эффекту.

Первые8 из прежних64 calibration questions — только dose fitting;
следующие16 — evaluation, без отбора по ответам или эффекту.
На32 gold-prefix позициях source forward сохраняет attention output выбранных
блоков и pre-final-RMSNorm residual. Для каждого блока сравнить:

1. Joint removeD-VO в этом блоке с обычным дальнейшим исполнением.
2. Scalar attenuation исходного attention output: `(1-alpha_l)*a_l`.
   Один alpha на блок; выбрать по суммарной L2 энергии локального изменения
   removeD на8calibration inputs, затем freeze до evaluation.
3. Для каждого вмешательства frozen-downstream counterfactual:
   `final_norm(h_final_source + delta_attention_local)` и исходный lm_head.
   Это точно реализует сохранение исходных outputs всех последующих residual
   branches при переносе local delta; final norm остаётся действующей.
   Вычисляется из захваченных tensors без дополнительных model forwards.

Калибровка delta делается на неизменном input конкретного блока: все более
ранние блоки native. Dose match проверяется и на evaluation, но не подгоняется.

## Метрики и границы

На каждом вопросе full-vocab teacher KL actual и frozen counterfactual.
Attenuation `A=1-sqrt(KL_actual/KL_frozen)`; нулевой denominator помечается,
не заменяется удобной константой. Дополнительно RMS логитов и gold NLL.
Разделить actual изменение final residual на local delta и оставшийся
downstream response; проверить точное сложение. Это bookkeeping, не уникальная
причинная attribution и не доказательство активного ремонта или backup circuit.
Изолировать вклад final RMSNorm сравнением с source-denominator readout;
его не выдавать за downstream нейронную компенсацию.

Primary exploratory gate: D attenuation больше scalar attenuation минимум
на .25 в среднем **в двух из трёх блоков**, и paired question-bootstrap95
для этих разниц не включает0. Только вопросы — sampling units, не токены.
Дополнительно finite/coverage, dose evaluation ratio в[.5,2], numerical floor
<1% от effects. Wide dose tolerance — screening limitation, не точный match.
Если ratio не проходит, вывод D-specific не разрешён; не тюнить alpha задним числом.

При positive gate: отдельная замороженная проверка на Mistral, с тем же
порядком слоёв (first/middle/last), новыми evaluation questions и controls.
При negative gate: не расширять n/layers/strength; сохранить вывод, что
особая защита D этим тестом не подтверждена. Общая attenuation остаётся
описательным результатом. Accuracy/training cause не проверяются.

## Ресурсы и приёмка

Новых weights/downloads нет, GPU0. CPU8, один worker, защитный cap20мин.
Проверить available RAM перед загрузкой. Tiny CPU test frozen-residual identity
и RMSNorm partition до модели. Native adapter exact tensor checks, FP32 finite,
repeat/source restoration, full source hashes. Численные controls до contrasts.
Модельный screen — около160forwards плюс controls, без generation.
После фазы все model objects/RAM released, никаких holders/ожидающих очередей.
Public reports только compact values/hash/provenance; operational paths private.
