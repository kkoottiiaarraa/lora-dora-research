# Метод: устойчивость существующих accuracy contrasts

Семья заранее фиксирована в SPEC данного продолжения: все 40 строк принятого
all-intervention-evidence.csv плюс все 6 строк compression-original-reference.csv.
Это 46 signed contrasts (23 пары ×2scorers), без отбора по выгодному результату.
Каждая строка сохраняет exact left/right run IDs и свой reference; эффект
всегда right-minus-left. Выбор этой семьи после просмотра прежних результатов
делает анализ exploratory, а фиксация сейчас не является пререгистрацией.
Семья 46 не охватывает всю историю адаптивного поиска и не объединяет автоматически
8 тестов пакета A. CI условны на фиксированные checkpoints, не на training seeds.

## Выравнивание и provenance

Бинарные scores всех run/scorer сверены по source_id, test_row_index,
prompt_sha256, input_ids_sha256; в каждом 1319 примеров, индексы 0..1318.
Means/effects каждой строки сверены с принятыми таблицами до 1e−12,
четыре перехода и их маргинальные суммы — с scores и прежними counts.
Выбранные frozen inputs проверены по bundle/analysis manifest; activity CSV и
проверены после расчётов. manifest.json содержит точные SHA и размеры.
Неизменяемые evaluator/predictions/bundle/старые CI/claim CSV не переписаны.

## Joint paired bootstrap

Пусть Z_ij=Y_right,ij−Y_left,ij, i=1..1319,j=1..46. Обе метрики
входят в одну матрицу Z. Один paired bootstrap использует общие индексы i
для всех 46 столбцов. B=50000, seed=2026101160, NumPy default_rng/PCG64,
multinomial chunk≤256. Квантили np.quantile(method='linear').

Получено 187 совместных patterns. Если pattern k встречается
c_k раз, при iid resampling1319 индексов число выбранных строк этого pattern
имеет Multinomial(1319,c_k/1319). Поэтому один общий вектор counts, умноженный
на pattern matrix, даёт ровно то же совместное распределение всех 46 bootstrap
means, что и resampling индексов. Нельзя resample каждый столбец отдельно:
это разрушило бы сохранённую зависимость вмешательств/scorers. Toy enumeration
всех 27 index sequences для 3 примеров подтверждает совпадение распределений.
shape=[50000, 46],dtype=float64.
Порядок столбцов: contrast_index0..45 в robustness.csv и полный column_order
в manifest.json/external_artifacts. НаVM матрица не копируется.

Новые pointwise интервалы: квантили .025/.975 каждого столбца из этих же draws.
Для simultaneous bands вычислено M_b=max_j |mu*_bj−mu_hat_j|,
q95=quantile_.95(M_b)=0.017437452615617893 accuracy units (1.743745 п.п.).
Для всех 46 применяется один общий интервал mu_hat_j±q95; clipping[-1,1]
разрешён, здесь не активен. Это приближённые двусторонние simultaneous95%
bootstrap bands на общей accuracy шкале: maximum ABSOLUTE UNSTUDENTIZED
deviation, **не max-t**. Студентизация или отдельные критические q не применялись.

Исторические pointwise CI сохранены отдельными колонками вместе с source,
старым seed/B и scope. Их отличие от новых pointwise связано с другим seed/B;
добавление simultaneous scope не переписывает исторические результаты.

## Margins и проверки

Для old/new pointwise/simultaneous отдельно вычислено строгое lower>−delta
при delta=.005/.01/.02 (0.5/1/2 п.п.). Эти допуски posthoc; это описательная
проверка совместимой потери, без noninferiority p-value и без утверждения
functional equivalence. CI, включающий ноль, не доказательство equivalence.

Проверены all-zero toy family с нулевой шириной; одинаковые/противоположные
столбцы; совпадающие scorers; exact pattern-weighted means; Monte Carlo means
в пределах 6MCSE; marginal bootstrap variances в пределах 5% эмпирической iid
цели; конечность, bounds, transition margins и неизменность input SHA.
Доля bootstrap draws, попавших во все 46 bands одновременно, 0.951240.
Порог≥95% проверен с допуском 1e−15 для floating/discrete quantiles. Это
**проверка конструкции bootstrap**, не проверка истинной частотной coverage
неизвестного распределения. Никаких independent datasets/seeds здесь не создано.

