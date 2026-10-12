# Математический аудит и границы литературных утверждений L1–L9

11 октября 2026. Пакет T. План составлен после получения данных; это
exploratory аудит готовых checkpoints. Ни новых модельных прогонов, ни
обучения, ни SVD весов для него не выполнялось. Точные сведения о V/O,
provenance и численной проверке находятся в [symmetry-scope.md](symmetry-scope.md).
Основное ограничение: доступна одна архитектура Qwen3-4B и три task-specific
пары без независимых повторов обучения; вмешательства — только GSM8K.

**Итог.** Forward-алгебра и posthoc вмешательства позволяют обсуждать роль
компонентов конкретного конечного решения. Они не идентифицируют причину
обучающей траектории. Высокий ранг, entropy, quality и magnitude/direction
correlation — разные объекты; ни один из них сам по себе не устанавливает
остальные. Литературные числа из другой постановки не опровергаются нашими
Qwen результатами.

## 1. Формулы, необходимые для интерпретации

В PyTorch linear weight имеет ориентацию `(out,in)`. Обозначим
`L=sBA`, `Z=W0+L`, `n_i=||z_i||₂`, `D=diag(m_i/n_i)`. При ненулевых n_i
эффективный DoRA вес и его полное обновление:

`W=D(W0+L)`,
`ΔW=(D−I)W0+DL`.

В статье с column convention D стоит справа; это та же структура после
согласования ориентаций. Ограничен ранг L, а не обязательно ΔW.
Ранг ΔW **может** превышать r, но не обязан: при D=I остаётся L;
возможны также нулевые scale corrections и компенсации. Поэтому наличие
диагонального члена не доказывает ненулевой хвост каждого отдельного
checkpoint, величину этого хвоста или полезность для функции.

Сохранённый `rank_symmetry.effective_weight` использует FP32 base,
FP32 A/B, FP32 нормы и magnitude; затем dense Linear получает dtype базы.
Спектр этой FP32 реконструкции, спектр уже округлённого dense BF16 delta и
реальный PEFT forward не обязаны совпадать побитово. Особенно нельзя
трактовать мельчайшие численные singular values как свидетельство новых
функциональных степеней свободы. Rank32 и E95/E99 относятся к полному
FP32 ΔW, а не только BA; их pre-intervention fidelity — контроль dense
conversion, не fidelity результата компрессии.

Два радиальных вмешательства различны:

| Вмешательство | Вес в вещественной арифметике | Что проверяется posthoc |
|---|---|---|
| `base_magnitude` | `diag(||w0_i||/n_i) Z` | роль learned m при сохранённом нормированном направлении |
| `remove_d` | `Z=W0+L` | роль всего итогового D, включая нормализацию |

`remove_d` не означает «заморозить m на начальном значении»: нормы его
строк равны n_i, а не ||w0_i||. `base_magnitude` не обучает новое решение:
факторы остаются выбранными исходным обучением. Реальный code
`lora_dora_study/interventions.py` отключает также PEFT variant dispatcher
для remove_d, а для base_magnitude копирует нормы базовых строк.

Для одной строки `w=m z/||z||`, `u=z/||z||`, upstream gradient g,
полная производная даёт
`∇z ℒ=(m/||z||)(I−uuᵀ)g`, `∇m ℒ=uᵀg`.
При detached denominator первая формула заменяется на
`∇z ℒ=(m/||z||)g`. Это разные backward, хотя forward одинаков.
Далее факторизация передаёт gradient G_L в `s BᵀG_L` для A и
`s G_LAᵀ` для B; ни один row-level аргумент сам по себе не описывает
AdamW/learning rates/всю траекторию.

Прочитанный текущий PEFT
`artifact://local/.venvs/lora-dora-research/lib/python3.12/site-packages/peft/tuners/lora/dora.py:66–101`
отделяет weight_norm через detach и собирает residual как
`(g−1)*base_result+g*lora_result*scaling`; SHA256
`07d514fd057d8aa9ec7b89bec3f3fbd04862951c1a8ff73153e833096481ecf5`.
Это подтверждает текущую inference implementation, но не неизвестный
backward при обучении опубликованных checkpoints. В частности, отсутствие
радиальной компоненты полной производной нельзя автоматически приписывать
detached реализации.

## 2. Регистр проверенных первичных источников

Ниже source statements отделены от предлагаемых operational tests. Все
ссылки указывают на прочитанные версии; verdict о качестве требует
соответствующих принятых outputs Q/C/L, а не подменяется литературным аудитом.

| ID | Что действительно поддерживает первичный источник | Доступная операционализация | Граница допустимого вывода |
|---|---|---|---|
| L1 | [DoRA v6, §§4.1–4.3](https://arxiv.org/html/2402.09353v6): norm/direction forward; полная производная отдельно от detached-denominator варианта, применённого в последующих опытах статьи. | Сверить формулы и текущий code; раздельно интерпретировать base_magnitude/remove_d. | Forward подтверждён. Причина обучения и training backward наших public checkpoints не восстановлены. |
| L2 | [SORA v1, Analysis and Insights / Weight Conditioning](https://arxiv.org/html/2511.00051v1): диагональная реформулировка полного ΔW. | Проверять сохранённые спектры FP32 полного delta там, где они имеются. | Структура допускает rank>r. Это не необходимость высокого ранга и не объяснение качества. |
| L3 | [SORA v1, Theorem 1 и Remark 1](https://arxiv.org/html/2511.00051v1): модель двух/трёх ступеней спектра с равной суммой квадратов minor values; авторы предлагают entropy как основное объяснение gains. | Rank32/E95/E99 quality относительно dense DoRA проверяют роль совместно удалённых компонент. | Это не изолированное вмешательство в entropy и не общая репликация theorem. Потеря качества не доказывает entropy-механизм, сохранение не опровергает theorem. |
| L4 | [PoLAR v1, §2.1, §4.1, Appendix F.1](https://arxiv.org/html/2506.03133v1): low stable rank и directional diversity collapse, связь роста stable rank с качеством; одновременно меняются parameterization и optimizer. | Описать nominal/energy ranks и ошибки, сопоставить с quality в данном checkpoint. | Stable rank, algebraic rank, energy threshold rank и entropy не взаимозаменяемы. Нельзя оценивать причинную rank–quality связь по 144 слоям или трём уровням компрессии. |
| L5 | [DeLoRA v1, Appendix C, Table 10](https://arxiv.org/html/2503.18225v1): предварительный опыт freezing magnitude **во время обучения**; fixed/standard DINO=.681/.683, CLIP-I=.822/.820. Frozen magnitude не исправляет все robustness проблемы. | Наш posthoc reset m и remove_D рассматриваются как отдельные вопросы конечной необходимости. | Ни положительный, ни отрицательный posthoc эффект не является репликацией freezing; факторы могли бы компенсировать отсутствие learned m при другом обучении. |
| L6 | [BiDoRA v2, §§4–5](https://arxiv.org/html/2410.09758v2): bilevel train/validation, orthogonal regularization, retraining. [DoRAN v2, §§3–4](https://arxiv.org/html/2510.04331v2): denominator offset и hypernetworks/shared Q/V. [LoRA+ v2, §§3–4](https://arxiv.org/html/2402.12354v2): разные learning rates в large-width анализе. | Зафиксировать конкурирующие optimization explanations и неизвестную training metadata. | Неидентифицируемо нашими данными. Конечный checkpoint не определяет overfitting, стабильность, LR adequacy или причинный вклад совместной оптимизации. |
| L7 | [EVA v5, Appendix B, Table 8](https://arxiv.org/html/2410.07170v5): Gemma-2-9B LoRA/DoRA GSM8K 83.4±.9/82.5±.6, MATH 40.7±.2/39.7±.4; три seeds. | Сохранить все три наших baseline triples и все основные метрики, включая отрицательные сравнения. | Универсальная победа DoRA литературой не поддерживается. Чужие mean±SD не дают формального p и не предсказывают причин наших отличий. |
| L8 | [LoRA-Squeeze v1, §2–3](https://arxiv.org/html/2602.10993v1): post/in-tuning сжатие стандартной LoRA; сложные адаптеры оставлены будущим расширениям. [Shortcuts in the Tail v1, §2, §4](https://arxiv.org/html/2606.07596v1): posthoc полный ΔW, top/bottom/random-k и отдельное matched-rank LoRA training; partial reversion явно остаётся альтернативой части эффектов. | Интерпретировать наши rank interventions как posthoc тесты; сравнивать с dense reference и ограниченным attenuation control. | Наш matched-impact LoRA не matched-rank training. Bottom/random-k и отдельная partial-reversion серия у нас отсутствуют. Нельзя приписывать себе их идентификацию. |
| L9 | [DoRA v6, §§3.2/4.1, Fig.2/Appendix A.1](https://arxiv.org/html/2402.09353v6): descriptive slope/correlation по слоям и training steps; наше измерение — другой, final-only V domain. | Специфическая scalar V/O symmetry плюс fidelity и algebraic admissibility; точные числа в symmetry-scope. | Финальная ρ не определяется одной функцией; это не опровержение исходного training pattern и не доказательство причинной роли ρ. |

## 3. Что особенно важно не усилить

**L2/L3.** Высокий rank или H не является гарантией качества. Для произвольной
матрицы высокий rank совместим с почти всей энергией в одном singular
direction, а удаление небольшой энергии может сильно изменить решение на
редких входах. Без общего контроля ориентации, scale, активаций и quality
изменение H не является отдельным estimand. Сохранённые rank module
summaries имеют равный вес модулей; это не model-global энергия.

Принятый [пакет C](component-findings.md) уточняет operational результат:
для rank32 unweighted median идеальной H снижается с 1.771339 до
1.393077 nats при median retained energy=.963051. Dense-relative
GSM8K эффект +0.682/+0.834 п.п. для двух scorers имеет pointwise lower
CI −0.455/−0.303 п.п. Прямое сравнение с исходной PEFT DoRA даёт
+0.152 п.п., CI [−0.986,+1.289] п.п. у обоих scorers. Поэтому ограничение
«нет потери более .5 п.п.» относится к dense reference; относительно
исходного адаптера данные исключают потерю более 1 п.п., но не .5 п.п.
Это ограничивает сильную operational необходимость удалённого хвоста,
а causal entropy explanation остаётся неидентифицируемым. Фактический
rank уже материализованного BF16 delta не измерен. Источники чисел:
[spectral-entropy.csv](spectral-entropy.csv),
[compression-quality.csv](compression-quality.csv),
[compression-original-reference.csv](compression-original-reference.csv).

Глобальные base_magnitude/remove_d также проходят pointwise .5 п.п.
критерий относительно исходной DoRA, однако сохранённые диагностики не
показывают величину D−I, m−base_norm или активность удаляемого множителя
в BF16. Следовательно, нельзя усиливать «не наблюдаем material accuracy
loss» до «существенно активные radial degrees были dispensable»,
и тем более до утверждения о freezing during training.
[component-necessity.csv](component-necessity.csv).

В displayed Weyl inequality SORA для хвоста стоит верхняя оценка; сама она
не доказывает ненулевой хвост. Для аккуратной формулировки достаточно
«может превышать r», доказуемого из структуры. Это замечание к логическому
шагу, а не эмпирическое опровержение SORA. В entropy theorem равная minor
энергия и ступенчатые спектры существенны; нельзя убрать эти предпосылки
и назвать произвольный DoRA checkpoint частным случаем доказательства.

**L6/L9: slope и Pearson.** Если x=D, y=M, OLS slope с intercept равен
`k=Cov(D,M)/Var(D)=ρ·SD(M)/SD(D)`. Он имеет единицы M и меняется при смене
единиц M. Pearson безразмерен и лежит в [−1,1]. BiDoRA Fig.3 приводит
`k=−8.042` и `−1.784`, называя их correlation; Appendix D описывает slope.
Без independently verified fit code это slope-like k с не полностью
установленной процедурой, заведомо не Pearson. Наши 0.0972/0.1686/0.0913
вычислены явной centered Pearson формулой. Их нельзя сравнивать по
абсолютной величине с k или выдавать за репликацию query/step выборки.

**L9: fixed-base correction.** Для сохранённого scalar map DoRA-r
допускает ту же W0 и BA через `mV′=c mV`, `mO′=mO/c`. Историческое
«fixed-base rank unknown» недостаточно различает DoRA directional-rank
и LoRA additive-rank. Сохранённая fixed-base ρ изменилась с
0.09723358447518415 до 0.09130353155912735; знака не поменяла.
Совместная смена базы дала 0.16864084241274216. Эти наблюдения показывают
representation dependence данного scalar statistic, но не величину или
знак эффекта в training trajectories.

Проверены 64 коротких dense-reference forwards с нулевой наблюдённой
ошибкой, а не полный GSM8K или исходная PEFT функция. PEFT→dense отдельно
имел error=1.34375 на первом 54-token prompt. Алгебраический same-class
map не обещает совпадения FP32 statistic с BF16 deployed weights.
Также независимый [Scaling DoRA v1, §3.1](https://arxiv.org/html/2603.22276v1)
разбирает finite-precision sensitivity near-unity scales; его Qwen2-VL
измерения не являются измерениями D или m нашего Qwen3.

## 4. Граница возможной новизны

Норма/направление, detached denominator, diagonal higher-rank delta,
спектральные метрики и posthoc SVD уже имеют прямой prior art. Generic
«разные модули требуют разной radial/directional adaptation» тоже не
новое утверждение: original DoRA §5.6/Table 6 уже обучает QKV magnitude
и direction, а остальные linear modules — только magnitude, отдельно
меняя гранулярность обучения. Это отличается от нашего удаления learned
компонентов **после** общего обучения, но ограничивает generic novelty.

Кандидат на дополнительный результат — конкретное разделение конечных
ролей m, D и хвоста полного delta на Qwen/GSM8K с dense controls,
scorer sensitivity и Q/K/V/O взаимодействиями. Это кандидат, не
установленная первая демонстрация. «Не нужен после такого обучения»,
«можно не обучать», «можно заменить LoRA того же r» и «обучение пришло
сюда по этой причине» — четыре разных утверждения.

Скалярная V/O проверка даёт узкую математически корректную иллюстрацию
неинвариантности ρ, причём в fixed-base DoRA-r классе; она не доказывает
новизну самого symmetry аргумента. Для итогового REPORT следует приводить
реальный размер изменения ρ и различать exact algebra, short BF16
observation и непроверенные training claims. Все неизвестные причины и
непроверенные controls должны оставаться явно неизвестными.

