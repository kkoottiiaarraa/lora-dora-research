# Полный адаптер: loss появился, сохранение D не решает его при четверти размера

13 октября 2026. Все6условий завершены и приняты независимымstdlib analysis.
Все144q/k/v/o матрицы,36слоёв Qwen3-4B/GSM8K nativeDoRA. GPU0часов,
обучение и агенты не использовались. Это full-adapter compression, не сжатие
base model. Source95,625,216bytes tensor payload,23,906,304FP32elements.

## Результаты на32новыхдляcompression development train questions

Каждый case32gold-prefix positions;1024позиции наусловие. Не официальная
GSM8Kaccuracy, не свободнаягенерация, не новые training seeds.
Всеmethods имеютодинаковый adapter storage budget внутристроковогоразмера:
rank16-equivalent11,796,480elements (49.34%source),rank8-equivalent5,898,240
(24.67%source). Structural включаетDoverhead;48проекцийсrankr−1,96сr.
Ridge.001,calibration64прежние,32screenquestions исключаютвсе старыеdevelopment
sets иtestcontent. МетодW-SVD не полнаяреализацияSVD-LLM/AIR.

| Budget / метод | Mean teacher KL | ΔgoldNLL,nat/token | Argmax changes /1024 |
|---|---:|---:|---:|
| Половина / RawSVD | .00037265 | +.008721 | 7 |
| Половина / W-SVD | .00039059 | +.010016 | 5 |
| Половина / StructuralW-SVD | .00028478 | +.008148 | 5 |
| Четверть / RawSVD | .00192975 | +.020372 | 11 |
| Четверть / W-SVD | .00191677 | +.022040 | 14 |
| Четверть / StructuralW-SVD | .00211808 | +.022723 | 14 |

Все6contrasts опубликованы вvalidation.json, exploratory pairedwhole-question
bootstrap10000seed20261013. CIописательные, не confirmatory послеmultipletesting.
Приполовинномбюджете сохранениеDуменьшаетKLна27.09%противW-SVD,
pairedΔCI95[−.00015425,−.00006492],и goldNLLна.001868.
Причетвертибюджета StructuralхужеW-SVDпоKLна10.50%,CI95[+.00004875,+.00041150].
GoldNLLразница+.000683,CIвключает0. Не заявляемуниверсальнуюполезностьD.
TeacherKLневзаимозаменяемсgoldNLL/правильностьюрешениязадачи.

## Какую конкретную ошибку имеет смысл пытаться исправить

В отличиеотлокальных6матриц, полныйquarter-size target проявляет заметную
ошибкудаже уW-SVD иfixed-Dstructural. Простое сохранениеDне устраняетloss.
Не считаемэтоошибкойсамогоSVD:онооптимальноподсвоимлокальнымobjective.
Fixed-Dbaselineнеоптимизируетрадиальнуючастьпослеудалениячастинаправления.
SourceDподходитисходномуrank32,необязательнолучшемуrank7/8приближению.

Следующий **один** candidate:проекцияresidualнаfrozenbase output иclosed-form
пересчётDприfixedL/R,томжебюджете. Выведенexactlocalleast-squares objective,
необещаетсяend-to-endgain. SPECзаморожендоcandidate scores,новыеvalidation64
непересекаютсясэтими32questions. См.[SPEC.md](../2026-10-13-radial-recalibration/SPEC.md).
Еслиcandidateневыиграет,неподбиратьiterations/scalesпоновомуvalidation.
Содержательнаяновизнаэтойcalibrationпроцедурынеустановлена;положительный
результатсампосебенеозначаетB/AилипреимуществоDoRAнадLoRAпообучению.

## Проверки и ресурс

3remoteCPUtestsPASS:точныйbudgetсD,thinQRпротивdenseweightedSVD,
tinyQwenполнаязаменапроекцийиrestore. Capture144modulesadapterexact,
4calreferencebitwise;hashes/versionsзафиксированы. Savedfactorsfinite/dtypes/
shapes/counts иunchangedDнезависимопроверенынасервере;budgetsпересчитанынаVM.
Source-controlrank32 иfactorized/densecontrolsmaxRMS9.61e−6противминимального
compressionRMS.051674:floorниже.02%effect.192per-caserowsполны,метрикиконечны.

Capture366.43sCPU16,prepare592.73sCPU4,evaluate391.64sCPU16;
суммапринятыхphasewall≈22.51мин. GPU0ч. Контроллер/workerзавершены.
Этоwalltime,неCPUcorehours. Baseweights/covariances/factors/logitsнасервере;
наVMтолькоcompactrecords. МоделиMistral/AnswerAIнезапускались.

Артефакты:SPEC.md,quality.csv,ranks.json,validation.json,manifest.json.
Revisions/versions/sourcehashes/inputhashes/CIвvalidation; rawrecords/operational
locatorprivatelyвlocal-only/full-compression-20261013-private.json.
