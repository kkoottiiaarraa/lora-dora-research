# При фиксированном бюджете практический сбой пока не найден

13 октября 2026. Завершён самостоятельный bounded CPU screen после одобрения
пользователем подхода «найти реальную ошибку, затем разрабатывать исправление».
**Результат отрицателен для продвижения этой локальной конфигурации:** зависимость
ошибки от представления есть, но она пока не дала изменения выбранных рангов
или верхнего токена. Новый алгоритм в этом этапе не изобретён/не проверен.

## Что изменилось относительно предыдущей попытки

Ранее rank32 приближение полного update почти не сокращало исходный nativeDoRA
адаптер. Здесь factor budget ровно491,520 элементов во всех12условиях против
993,792 у исходных шести модулей: осталось49.46%, сокращение50.54%.
В checkpoint эти source tensors FP32, как и новые factors; tensor payload
3,975,168 →1,966,080 bytes. Это не измерение peak RAM/VRAM, latency или размера
всего адаптера: остальные138модулей и base model не сжимаются.

Четыре процедуры при каждом из прежних source scales1/.995/1.005:
raw SVD и activation-weighted W-SVD, каждое с равномерным rank16 и с
exact-budget spectral-energy allocation, ranks0..32. Старые nested rank32
factors переиспользованы, новых SVD не потребовалось. Allocation — наш
диагностический локальный proxy, не реализация авторского rank allocator AIR
или полного SVD-LLM. Не заявляем опровержение опубликованных compressors.

## Результаты

16вопросов train, ранее не использованных в нашем compression development,
после исключения calibration64, двух validation64, первых232train и test hashes.
Каждый вопрос —32gold-prefix target positions:512позиций на условие.
Это новые вопросы для posthoc method development; исходная адаптация могла видеть
train. **Это не свободная генерация и не GSM8K accuracy.**

| Процедура | KL приc1 | KL приc.995 | KL приc1.005 |
|---|---:|---:|---:|
| Raw SVD, равномерныйrank16 | 2.461e−6 | 2.679e−6 | 3.760e−6 |
| Raw SVD, распределениерангов | 2.360e−6 | 2.556e−6 | 3.254e−6 |
| W-SVD, равномерныйrank16 | 2.789e−6 | 4.023e−6 | 5.187e−6 |
| W-SVD, распределениерангов | 6.386e−6 | 6.877e−6 | 9.775e−6 |

KL — ошибка воспроизведения распределения native original; меньше лучше.
Во всех12условиях **0/512** изменений argmax. Это одни и те же512позиций,
не6144независимых наблюдения; совпадение не доказывает эквивалентность ответов
при свободной генерации. NLL изменения против original: +.000120..+.000431nat/token,
приблизительно+.012..+.043% prefix perplexity, не процентные пункты accuracy.

Ранги не изменились ни при одном из двух source perturbations:

| Слой | Raw:V / O | W-SVD:V / O |
|---|---:|---:|
| 0 | 10 / 20 | 2 / 3 |
| 17 | 14 / 21 | 14 / 13 |
| 35 | 11 / 14 | 32 / 32 |

Это оптимум соответствующего локального energy objective при точном бюджете
и rank cap32, не глобальный optimum функционального сжатия. В W-allocation
cap активен; это дополнительное ограничение интерпретации.

Относительные KL изменения заметны: например, raw fixedc1.005 +52.80%, weighted
fixedc1.005 +86.01%. Weighted allocation приc1 хуже weighted fixed на128.99%.
Но абсолютная разница мала. Uniform weighted baseline в этой конфигурации
не превосходит raw: разница+13.33%, descriptive pairedCI включает0.
Оба локальных objectives не гарантируют минимальной end-to-end KL.
Все12paired contrasts и exploratory bootstrapCI опубликованы вvalidation.json:
10000whole-question resamples,seed20261013, без confirmatory multiple-testing
заявки. Не выбираем один nominally positive contrast как научный результат.

## Решение об алгоритме

Предварительно записанный exploratory gate не пройден: relative effects есть,
но во всех условиях meanKL<1e−5 и fraction argmax changes<1%.
Численный порог — engineering screen, не универсальная граница полезности
и не доказательство отсутствия эффекта. Основная причина остановки — пока
нет наблюдаемой ошибки рангов/выходных решений, которую новый метод должен
практически исправить. Потенциал всей области сжатия этим не опровергнут.

**Не продолжаем эту локальную scale/norm ветку и не запускаем Mistral автоматически.**
Готовое исправление или статья уровняB/A из этого screen не следуют.
РезультатE99-budget sensitivity прежней работы сохраняется, но его нельзя
автоматически переносить на ухудшение качества при одинаковом малом бюджете.

Следующая обоснованная постановка, если продолжать compression направление:
полное сжатие адаптера с реальным ограничением размера, чтобы сначала найти
значимую ошибку сильного baseline. До нового алгоритма включить естественный
structural control: сохранять DoRA diagonal D и сжимать directional part,
с учётом D overhead. Только затем выбирать между fixed-base block correction
и более точным распределением рангов. Не выдавать перенос известных методов
наDoRA за установленную новизну. Конкретные constraints/prior/gates:
[CANDIDATES.md](CANDIDATES.md).

## Проверки, воспроизводимость и ресурсы

До model screen прошли2exact-budget tests (сверка с полным перебором) и4tiny
Qwen/compression tests. Reference execution совпал побитно на4calibration cases
со старым capture; adapter tensors сверены точно,144adaptedmodules.
Source-dense gauges и factorized/dense controls на2cases: maxRMS7.69e−6,
минимальный compressionRMS.007879; floor<.1% compressioneffect, ниже gate1%.
Все192per-case строки приняты независимым stdlib analysis, метрики конечны,
одинаковые budgets и полнота условий проверены, ранее использованные validation
questions исключены. Case hashes/versions/source hashes —validation.json.

Accepted preparation4.30s CPU4, evaluation854.53s (14мин15с) CPU16,
peak model-worker RSS20,418,670,592bytes. **GPU0часов**, обучение отсутствует,
worker завершён; карты не удерживались. Этиwall seconds не CPU core-hours.

Первый prepare attempt остановился до model answers: absolute off-diagonal
orthogonality tolerance1e−8 была слишком строгой для cachedFP32 SVD columns.
Измеренные relative residuals<=7.86e−7; guard исправлен на relative<=1e−5
до model scores, failed attempt сохранён. До evaluation добавлен ранний
control-floor guard. Поправки/provenance в private manifest; outputs не отброшены.

Артефакты: SPEC.md,CANDIDATES.md,quality.csv,decisions.json,validation.json,
manifest.json. Raw compact records/operational locator —local-only; matrices,
factor/logit caches и raw records остаются на вычислительном сервере.
Код: budget_screen.py,rank_budget.py,analyze_budget_screen.py,test_rank_budget.py.
