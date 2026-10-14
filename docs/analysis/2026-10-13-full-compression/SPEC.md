# Full-adapter compression: заранее заданный screen

13 октября 2026, до новых scores. Пользователь разрешил полное сжатие,
сначала поиск существенной ошибки сравнительных методов, включая сохранение
структуры DoRA. Без агентов, нового обучения и автоматического Mistral.

## Постановка

Qwen3-4B/GSM8K nativeDoRA, прежние pinned revisions/software. Все144q/k/v/o
проекции36слоёв. Base weights неизменны и не входят в adapter budget.
Два заранее заданных factor budgets соответствуют ordinary-LoRA uniform
rank16/rank8: ожидаются11,796,480/5,898,240FP32elements против23,906,304source
A/B/m элементов (фактические shapes/counts сверить доscores).

Три comparative methods при каждом размере:
1. Raw SVD полного W−W0, uniform rank16/8.
2. W-SVD полного W−W0: прежний activation-weighted whitening objective,
   ridge=.001mean(diag(covariance)). Не полный SVD-LLM/AIR.
3. Structural W-SVD: сохранить sourceD=m/||W0+sBA|| точно как диагональ,
   сжать D*sBA, deploy D*W0+LR. Thin QR и SVD32×32 вместо dense SVD
   low-rank directional product. Нормировка sourceD после сжатия не меняется.

Метод3 — естественный структурный baseline, не новый алгоритм и не обычная
LoRA. Во всех6conditions точно одинаковый budget внутри данного размера:
учитывать diagonal overhead. Structural ranks ограничены r−1/r, выбрать
assignment с максимальной суммой ranks при exactbudget. Tieorder seeded20261013,
никаких scores/labels при выборе ranks. Мелкая rank неоднородность — цена D
overhead, не оптимизированное по результатам распределение. Сохранить все ranks.
Для обычных моделей ожидаются48modules сr−1 и96сr; проверить поshapes.

## Данные

Использовать прежние64calibration cases только для covariance/factors.
Capture последние32позиции native teacher inputs всех144проекций.
До новых scores заморозить32следующих допустимых train questions, исключая
первые232train, test content, calibration64, прежниеgeneric64/anchor64/budget16.
Прежнийфильтрprompt<=512,answer>=32. Evaluation goldprefix32targets.
Это данные новые для compression development, не обязательно для исходного
обучения адаптера. Не заявлять officialtest/generalization accuracy.

## Проверки

Unit tests exactstorage includingD, thinQR против dense weighted optimum,
full-rank structural reconstruction, tinyQwen144-type replacement/restore.
Доcapture точная сверка adapter tensors144modules, CPU FP32 SDPA.
Четыре nativecalreference побитно совпадают с прежним capture.
Доevaluation source/factor hash/versions/finite checks, каждыйbudget проверяется
по фактическимtensor shapes, D включён. Проверить rank32 structural source control и
factorized/dense control на2cases: floor<1% минимальногоcompressionRMS.
Controls не должны заниматьGPU: весь этапCPU на вычислительном сервере.

## Метрики и решение

Native reference +6conditions наодних32questions. Primary exploratory
teacherKL; NLL, RMS, argmax changes вторичные. Whole-question pairedbootstrap
descriptiveCI, без confirmatory заявки и выбора одногоудачногоcontrast.
Нет расширенияscalegrid. Никаких автоматических claims taskaccuracy/B/A.

Проектировать новое исправление только если у одного из сильных baseline
при данном полном budget проявится содержательная проблема: например >=1%
измененийtop-token либоmeanKL>=1e−4; порогиengineering, не универсальные.
Если простойstructural baseline уже устраняет её, фиксировать полезный
результат известного принципа; не объявлять его новымalgorithm. После этого
решение о task-level validation/новомcorrectivecandidate явно записать.
Если все ошибки малы, не продолжатьblindalgorithmsearch этойконфигурации.

## Ресурсы и приоритет

CaptureCPU16, prepareCPU4, evaluateCPU16, GPU0. По прошлым timings ориентир
20–45мин суммарно, уточнить по фактическим SVD; deadlines capture1800s,
prepare3600s,evaluate3600s. Всеweights/covariances/factors/logits насервере.
НаVMтолькокод и компактныеJSON/CSV. Не удерживатьGPUподCPUработу.

Known ingredients: [DoRA](https://arxiv.org/abs/2402.09353),
[LoRA-Squeeze](https://arxiv.org/abs/2602.10993),
[SVD-LLM](https://arxiv.org/abs/2403.07378), [AIR](https://arxiv.org/abs/2606.19993).
JointV/O ужеесть в[LatentLLM](https://arxiv.org/html/2505.18413v1);
их общийprinciple не наша новизна. Этотscreen не воспроизводит все эти методы.
