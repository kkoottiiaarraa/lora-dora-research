# Ограниченная проверка SORA и продолжение основных направлений

14 октября2026. Выполнен весь текущий запрос пользователя: маленький formal/
loader-impact screen, затем неалгоритмические исследования. Письма, агенты,
новое обучение и GPU не использовались. Итог не является готовой статьёйB.

## Результаты и решения

| Ветка | Реальная проверка | Результат | Решение |
|---|---|---|---|
| SORA formal/loader impact | independent entropy formula, equal-energy rank counterexample, Weyl/rotation bounds, tiny loader accuracy sign, eval call-site scope | Restricted entropy theorem выдерживает проверку; rank-only sufficiency не следует. Loaderfix может как улучшить, так ухудшить accuracy; GLUE in-memory eval автоматически не затронут. | Bounded ветка закрыта; таблицы качества статьи не опровергнуты. |
| D-specific downstream attenuation | Qwen3-4B jointVO removeD vs scalar той же дозы, blocks0/17/35,8fit/16eval,96rows | Last-block contrast+.160CI[.078,.252], ниже .25gate; early frozen effects numeric floor fail. | Сильная D-specific защита не подтверждена; без Mistral/grid expansion. |
| Transient radial role | PeRL1.5B3publishedsteps ×3conditions ×16fixedquestions,144rows | Normalized role падает39.44x, absoluteKL~3.6e−5 почти постоянен; absolute-effect gate fail. | Не объявлять ratio transient scaffold; не расширять trajectory ради curve. |
| Artifact magnitude applicability | Safe-tensor comparisons3PeRLsnapshots+3Qwen+Mistralr16 | PeRL645120storedm одинаковы на3steps и равныroundednorm(base); Mistral99.99275% совпадений; QwenFP32m существенно отличаются. | Различать inference role learnedm, normalization и storage rounding. Причина обучения не установлена. |

### Самое содержательное новое наблюдение

Слова «готовая DoRA» недостаточно для утверждения, что в этом артефакте
наблюдается изменение обеих обучаемых компонент. В проверенных PeRL snapshots
сохранённая magnitude не меняется, но direction normalization остаётся частью
функции. Поэтому removeD не является чистой абляцией обучения magnitude.
У наших Qwen наблюдение иное; нельзя объяснить их endpoint устойчивость
отсутствием magnitude changes на основании PeRL/Mistral.

Второй практический результат — prespecified absolute-effect gate предотвратил
ложно сильный сюжет из39кратного normalized decrease: вырос denominator, а не
исчезла абсолютная D-реакция. Это не доказывает нулевой эффект на accuracy.

## Граница новизны и статьи

Общая self-repair известна: [Hydra](https://arxiv.org/abs/2307.15771),
[Rushing/Nanda](https://proceedings.mlr.press/v235/rushing24a.html),
[Every Ablation Is a Dose](https://arxiv.org/abs/2610.02173).
Intermediate weight correlations уже есть в
[DoRA](https://proceedings.mlr.press/v235/liu24bn.html).
Precision risk near-unity DoRA gain прямо обсуждается в
[DoRAFactors](https://sockeye44.github.io/dorafactors-docs/how-it-works/) и
[Scaling DoRA](https://arxiv.org/abs/2603.22276).
[PeRL](https://arxiv.org/abs/2512.23165) оставляет mechanistic adapter dynamics
открытым, но это не гарантирует новизны любого trajectory plot.

Наш новый вклад этого цикла — конкретная проверка применимости explanations
к выбранным реальным артефактам и её ограничения. General BF16freeze не наша
новизна; causality, independent-run replication и quality effect не установлены.
Этого недостаточно честно объявить материалом основной conferenceB paper.
Техническая приёмка расчётов и статистический contrast сами по себе уровень
конференции не определяют. Исходные результаты качества DoRA не опровергнуты.

## Почему compressor не переоткрыт

Предыдущие сильные fixedD+INT8/activation-aware comparators уже выиграли у
испробованных кандидатов. Этот цикл не установил новый существенный failure
такого comparator, который исправлял бы новый принцип. Проблема artifact m
и precision не является failure compression baseline. Поэтому условие
пользователя для возврата к алгоритму пока не выполнено. Новый grid не назначен.

Следующий содержательный вопрос: при каких released-training/precision режимах
mechanistic описание «обучаемая magnitude помогает» действительно проверяемо?
Нужны наблюдаемое m-motion, correct saved initialization и provenance precision;
для причинного объяснения — подходящие training artifacts/controls, которых
этот цикл не заменяет. Не повторять full accuracy или correlations ради отчёта.

## Артефакты, приёмка, ресурсы

- [SORA claim report](../../analysis/2026-10-14-sora-code-audit/CLAIM_SCREEN_REPORT.md), machine-readable claim-screen.json.
- [Downstream report](../../analysis/2026-10-14-downstream-response/REPORT.md), SPEC/validation/layers/manifest.
- [PeRL report](../../analysis/2026-10-14-perl-trajectory/REPORT.md), SPEC/provenance/magnitude-audit/validation/trajectory/manifest.
- [Magnitude report](../../analysis/2026-10-14-magnitude-provenance/REPORT.md), SPEC/audit/manifest.

All model workers terminal, process sessions drained, no holder/waiter/GPUqueue.
CPU8 model wall365.86+324.68=690.54s, около11.5мин. Это wall двух model workers,
не общее время агента и не точное CPU time. Peak RSS19.50/19.18GiB.
Read-only magnitude runs11.06+12.23+2.30s, отдельно от model wall.
PeRL download+whole-LFS-SHA verification328.33s, server-only~3.78GB.
Tiny CPU tests: downstream2, biasedQwen2compatibility1 до model admission.
GPUhours0, training0. Existing weights доступны серверу; большие logits/raw
records там же. Compact hashes/reports в repo; operational locators private.
Torch2.5.1+cu121/Transformers4.57.1/PEFT0.17.1/Safetensors0.6.2/Accelerate1.11.0.
No install/VPN/API setup, чужие процессы/репозитории не затрагивались.
Git commit/push в этом запросе не выполнялись; прежние localchanges сохранены.
