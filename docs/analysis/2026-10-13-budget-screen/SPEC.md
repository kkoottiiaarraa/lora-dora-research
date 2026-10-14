# Проверка решений при реальном сокращении адаптера

Зафиксировано до новых scores, 13 октября 2026. Авторизация: пользователь
одобрил проверку практической ошибки, затем обоснованное исправление.
Агенты, обучение, Mistral и расширение scale grid не используются.

## Вопрос и предел

Сохраняющая исходную функцию V/O scalar symmetry уже проверена в FP32.
Теперь проверяем, меняет ли она качество сжатия и решения о распределении
рангов при одинаковом **числе хранимых факторных элементов**.
Три заранее выбранных слоя 0/17/35, шесть V/O matrices, Qwen3-4B/GSM8K DoRA.
Это локальное сокращение адаптера, не двукратное сжатие всей модели/адаптера.

Бюджет: sum(input_dim+output_dim)*16; приблизительно половина исходных
A/B/m элементов этих шести модулей. Scales 1/.995/1.005 — прежние controls,
не расширение сетки и не оптимизируемый кандидат.

## Условия

Используем уже подготовленные rank32 raw/W-SVD factors, fitted по 64 calibration
cases. Усечение вложенных факторов даёт ranks <=32 без новых SVD и без обучения.
W-SVD — прежняя адаптация whitening objective, не полный SVD-LLM или AIR.

Для каждого scale сравнить четыре процедуры:
1. Raw SVD, rank16 на каждом модуле.
2. W-SVD, rank16 на каждом модуле.
3. Raw SVD, ranks 0..32 распределены exact knapsack по суммарной энергии
   singular values полного update при том же точном factor budget.
4. W-SVD, такое же распределение по энергии whitened update.

Последнее — более сильный локальный proxy control, не новый алгоритм.
В W-SVD O input covariance корректно масштабировалась при исходной подготовке.
Lexicographic rank tie rule. Хранить source hashes, ranks, точный расход.
Не сравнивать E99 процедуры с разными бюджетами как методы одинакового размера.

## Примеры и метрики

До новых scores заморозить первые 16 допустимых train cases после исключения
первых 232, calibration64, обеих прежних validation64 и test content hashes.
Фильтр prompt<=512 и answer>=32 tokens прежний. Все эти примеры новые для
разработки compression procedure; базовая адаптация могла видеть train.
32 gold-prefix target positions, FP32 CPU SDPA, одинаковая модель/исполнение.
Reference пересчитать, adapter weights сверить точно до ответов.
Primary screening metric: mean full-vocabulary teacher KL. Также NLL,
argmax disagreements, RMS; per-case данные сохранять. Это НЕ GSM8K accuracy.

Перед основной оценкой: четыре fresh reference совпадают с capture cache,
source-dense original/gauge не превосходит 1% compression RMS, factorized/dense
контроль одного условия на двух cases. При провале guard прервать.
Скрининг exploratory, не подтверждающая проверка после выбора методов.

## Решения и остановка

Практический screening signal: >=20% difference mean KL между representations
или allocations, paired interval показать описательно; отдельно показать
абсолютный KL и fraction changed argmax. При mean KL<1e-5 у всех условий и
<1% changed argmax сильную практическую заявку не делать, даже при больших ratios.
Порог engineering, не универсальный критерий публикации/качества.
Если signal есть, следующий этап — исправление конкретного источника ошибки
с проверкой на независимых случаях; алгоритм фиксируется до его validation.
Если signal слаб, отчёт и stop этой экспериментальной ветки, без автоматического
Mistral/расширения grid/дорогой free-generation серии.

Ресурсы: cache preparation CPU4; evaluation CPU16, deadline 3600s.
Все tensors на вычислительном сервере; на VM только код/компактные metrics.
Ни одна GPU не резервируется под CPU работу. Возможное продолжение требует
нового заранее записанного дизайна и оценки полезности, а не поиска удачного p.

## Ближайший prior

[LatentLLM](https://arxiv.org/html/2505.18413v1), §4.2 и Appendix G уже рассматривают
joint V/O compression, включая attention-aware objective. Само совместное
приближение V/O не наша новизна. Fixed-base adapter constraints и DoRA structure
требуют отдельного сравнения; отсутствие точного prior не установлено.
[FLAT-LLM](https://aclanthology.org/2026.findings-eacl.156/) — дополнительный
близкий источник, найденный при поиске; полнота сопоставления ещё не установлена.
