# Этапы1–3: выбор процедуры и проверка на новых примерах

Пользователь разрешил все три этапа подряд, использование ресурсов сервера и
обязал вернуться **до Mistral** с результатами и честной оценкой уровняB.
Агенты не используются. Нового обучения нет. Этот дизайн фиксируется до
method scores и раскрытия validation outputs.

## Этап1: результат discovery screen

772per-case rows и18spectra проверены. Таблицы discovery-quality.csv,
discovery-budget.csv, hashes — discovery-validation.json.
Original C32 KL1.489e−6, gold NLL delta+7.069e−5nat/token,0argmax flips/2048.
Два gauges даютKL2.359e−6/2.492e−6, NLL+1.001e−4/+1.366e−4, flips1/0.
Описательные case-bootstrap интервалы приведены в таблице, не independent
training replicates и не benchmark accuracy. Эффекты малы в абсолютной шкале.
E99 факторный бюджет6матриц меняется12,185,088→24,284,672/30,525,952 элементов:
в1.993/2.505раза. Это бюджет naively compressed full delta, не реальная потребность
native DoRA: её A/B/m в этих6модулях всего993,792элемента. Rank32 factors983,040.
Нельзя превратить эту разницу в заявление, что native DoRA неэффективна.

## Этап2: фиксированный набор процедур

Те же layers0/17/35,V/O,rank32 и gaugesc=1/.995/1.005. Остальные модулиnative.
Все conditions при одном dtypeFP32/backend внутри данного этапа.

1. Обычный SVD полного delta.
2. W-SVD: input-activation-weighted low-rank approximation полного delta.
   Из2048input vectors на64calibration gold-prefix случаях строится
   C=E[xxᵀ]+lambdaI, lambda=.001*trace(E[xxᵀ])/d, Cholesky C=LLᵀ.
   Берём rank32 SVD(delta L), справа умножаем наL⁻¹ triangular solve.
   Это известный whitening objective из [SVD-LLM](https://arxiv.org/html/2403.07378v2),
   применённый к update. Не заявляем воспроизведение полного SVD-LLM с layer-wise
   update и не называем это новым методом. Forward-only baseline, без gradients.
3. Кандидат: тот же W-SVD с выбором одного общего c по минимальному mean full-vocab
   calibration KL из трёх фиксированныхc. Это простой калибруемый кандидат,
   его новизна не предполагается. Если выбранc=1, он совпадает с baseline.
4. Для честности вычислительного бюджета: SVD с таким же трёхточечным выборомc.
   Учитывать дополнительные forwards поиска, а не только финальный размер.

Все6method×c оцениваются только наcalibration. Нельзя выбирать c по новым
примерам или менять ridge после scores. При равных scores предпочитаетсяc=1.
Правильность приближения проверяется по weighted residual/SVD tail и CPUunit tests.
Gauge сохраняет V inputs, масштабирует O inputs наc; covariance дляO соответственно
масштабируется наc². Это scalar correction, без новых измерений под каждыйc.

## Этап3: независимые от выбора примеры

64новых train вопроса, исключены test, первые232oldcalibration и discovery64.
Берутся первые структурно подходящие записи: prompt≤512tokens, answer≥32tokens;
duplicates исключены по content hash. Фильтр фиксирован до scores; никаких
фильтров по правильности, margins или величине эффекта. Это train holdout для
выбора posthoc процедуры, не unseen training data модели и не official test.

Validation token IDs/hash фиксируются до method scoring. selection.json с
выбранными c/factor hashes записывается и хешируется **до** validation forward.
Проверяются original, SVDc1, W-SVDc1, selectedSVD и candidateW-SVD; точные дубликаты
условий не прогоняются повторно. Никакого выбора лучшего метода поvalidation.

Primary contrast: candidateW-SVD−W-SVDc1 mean KL на64целых вопросах;
paired case-bootstrap95,10000resamples,seed20261013. Relative gain и absolute KL
публикуются вместе. Secondary — rawSVD, matched-search SVD, NLL и argmax;
не объявлять их независимыми primary discoveries. Если candidate==baseline,
primary effect ровно0 по построению, никаких тестов ради значимости.
Рабочий screen пользы:≥10%relativeKL improvement и upperCI разницы<0.
Это engineering threshold, не универсальный критерий полезности/уровняB.
Даже успех на микроскопическом KL не доказывает практически значимую accuracy,
экономию memory/latency или самостоятельную новизну.

## Размещение и корректность

Для ускорения разрешены2GPU, исключая incident device по приватнымindex/UUID. Прежние criteria:
utilization<20%, used<7168MiB,2проверки через10с, cooperative locks.
Дополнительно: usable memory минус2GiBreserve на каждой карте, суммарно≥17GiB,
минимум4GiB на карту. Только FP32, TF32/autocast выключены, disk/CPU offload
в GPU reference запрещён. Не трогать чужие процессы.

Capture: native64calibration forwards, original logits, inputs6модулей и
effective matrices; validation inputs frozen. GPU процесс затем завершается
и locks отпускаются. Prepare: CPU4threads, whitening/SVD, без VRAM.
Evaluate: повторный допуск GPU и новый native reference на всех calibration cases;
не смешивать CPU/CUDA logits. После выбора методов новая validation reference.
CPU fallback после120с ожидания подходящей пары сохраняетFP32. Все GPU buffers
освобождаются при окончании phase процесса. Canary на каждой GPU и finite CPU
readback. Gauge-controls4cases до comparison. Source hashes frozen.

Бюджеты — защитные caps, не целевой расход: capture1800с,prepare1800с;
evaluate3600с CUDA или10800с CPU. Эксперимент не запускаетMistral автоматически.
При сбое сохранять attempt и исправлять причину без уничтожения прежних данных.

## Что должно попасть в итог

Полнота, независимость выбора отvalidation, effect/CI, actual parameter budget,
wall/GPU hours, overhead calibration search и ограничения prior art.
Отдельный ответ: исправление полезно? практически существенно? ново?
Только затем оценкаB и рекомендация поMistral. Простое добавление известных
whitening и grid selection не превращает работу в новый compression algorithm.

Ресурсное уточнение до method scoring: при занятой пареGPU модельные CPU phases
используют16потоков вместо4; prepare остаётся4. Первые10capture cases прежнего
4-thread attempt не используются, он сохранён как superseded. В новой попытке
все reference/condition logits получаются согласованно; метод/вопросы не меняются.
Auto balanced placement давалоdisk offload на неодинаково занятыхGPU; исправлено
на sequential placement с прежними измеренными caps. Первый failed attempt
сохранён, его scientific outputs отсутствуют.

## Дополнение до проверки нового кандидата: инвариантная привязка

Простой относительный grid не устраняет зависимость candidate set от исходной
записи. Поэтому отдельно проверяется base-anchored weighted procedure, без
изменения уже работающего сравнения. Формула для каждого выбранного слоя:
a_l=||W0V_l||F/||WV_l||F; V→a_l*V, O→O/a_l. После source gauge g_l>0
получаем a'_l=a_l/g_l, значит канонические V/O не меняются. Для O inputs
C'_O=g_l² C_O, поэтому после нормировки covariance тоже совпадает.
Три physical candidates задаются t=1/.995/1.005 поверх этой привязки; family
инвариантно к положительным scalar V/O gauges в точной арифметике.
Это не инвариантность относительно всех GL transformations или BF16 rounding.

Из capture reused matrices/inputs строятся weighted factors для этих3t;
сам t выбирается только поcalibrationKL. Сравнения: rawSVDc1, W-SVDc1,
anchor-onlyt1, выбранныйanchor, а также ранее выбранные matched-grid baselines,
если их calibration selection уже зафиксирован. Дубликаты не повторяются.
Фактическая близость quality проверяется, не предполагается из инвариантности.
Канонизация может ухудшать приближение — исходный toy warning сохраняется.

Для этой процедуры фиксируются ещё64новых train questions с исключением
первых232, discovery64, test и generic-validation64. Ни один anchor candidate
ещё не оценивался; новаяvalidation не используется для выбора или ridge.
Оба первичных контраста (generic иanchored противW-SVDc1) публикуются вместе;
для family2 дополнительноBonferroni97.5%CI каждого, без выбора удачного study.
Сравнения с raw/canonical/matched-grid —secondary. КритерийrelativeKL≥10%
иupperCI<0 оценивается для новогоanchor, но не является автоматическимB.

Новый отдельный CPU процесс:8threads длямодели,4дляподготовки; старый16thread
процесс не изменяется. Общаянагрузка24thread плюсчужаянагрузка
проверена до запуска, запасCPU/RAM достаточен. GPU не используется. Веса остаются насервере.
Unit-test independent per-layer gauges и covariance scalingPASS до запуска.
Простая нормировка/gauge fixing в общем виде известны; приоритет конкретного
PEFT применения не установлен. Нельзя объявить это новым принципом только из
формулы. Решение оB будет учитывать actual holdout пользу и prior art.
