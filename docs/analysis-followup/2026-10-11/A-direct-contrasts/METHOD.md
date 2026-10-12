# Метод пакета A

Используется неизменяемый `02-interventions/tables/per_example_scores.csv.gz` из подготовки 2026-10-11. SHA256 четырёх выбранных frozen таблиц сверены с `manifests/bundle.json`; SHA принятой `paired-outcome-transitions.csv` — с `analysis-manifest.json`. Точные зависимости и hashes записаны в новом manifest. Frozen входы повторно хешируются после расчёта. Старые CI/p не переиспользуются и не переписываются.

Семья зафиксирована в текущем SPEC до новых расчётов: remove_D-all−LoRA, base_magnitude-all−LoRA, remove_D-Q−remove_D-K, base_magnitude-Q−base_magnitude-K, каждый author_em затем final_em. В CSV left всегда reference, right changed: эффект `right_mean-left_mean`. Индексы гипотез 0..7, seeds 2026101140..2026101147. Направление эффекта подписано, но тест McNemar двусторонний. Run IDs подтверждены по frozen scores без замен.

Для всех семи условий и двух scorers проверяются ровно 1319 уникальных test_row_index 0..1318, бинарность и полное равенство source_id/prompt_sha256/input_ids_sha256 по индексам. Четыре перехода: n00 wrong→wrong, n01 wrong→correct, n10 correct→wrong, n11 correct→correct; `difference=(n01-n10)/1319`.

Парный percentile bootstrap, B=50000, отдельно для каждого контраста: z=Y_right−Y_left ∈ {−1,0,+1}; один draw — multinomial(N; n10/N,(n00+n11)/N,n01/N). Это точное распределение обычной выборки N индексов с возвращением для среднего z. Среднее draw равно (count_plus−count_minus)/N. CI — квантили .025/.975, NumPy method=linear, PCG64/default_rng. CI pointwise, не скорректированы за поиск/восемь гипотез.

Двусторонний exact McNemar: `min(1,2*sum_{k=0}^{min(n01,n10)} C(n01+n10,k)/2**(n01+n10))`; отсутствие discordance даёт 1. Сумма считается точными Python integers, финальный результат float. Holm stepdown применяется совместно ровно к восьми exact p, монотонные скорректированные p; alpha .05. Старые bootstrap p не переносятся. Новая семья A не контролирует всю историю адаптивного анализа, не относится автоматически к семье C, выбор scorer/контрастов уже posthoc.

Toy проверки: exact известные McNemar значения/симметрия, Holm известные значения/равные p, полное перечисление 3^3 indexed resamples и сравнение с multinomial кратностями, константные z, ожидание/дисперсия/bootstrap determinism. На данных проверяются marginals, aligned means против frozen metrics, четыре accepted перехода radial-vs-LoRA, finite CI/bounds, bootstrap mean consistency с допуском шесть Monte Carlo SE. Проверяется сохранность входов после расчёта. Число проверок включает бинарность и alignment каждого примера и не является числом независимых наблюдений.


