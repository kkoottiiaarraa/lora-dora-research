# PeRL: нормированная роль падает, абсолютная почти постоянна

Screen завершён:3published checkpoints × 3conditions × 16common questions,
144rows, CPU8 FP32/SDPA, 324.68s, peak RSS19.18GiB, GPU0.
Exact588savedtensors/196modules на каждом шаге; repeat/restoration bitwise;
Qwen2 biased-projection compatibility tiny test PASS до admission.
Два native/dense controls накаждый шаг, maxRMS1.817e−5;
floor<0.174% каждого effect. Technical acceptance PASS, scientific gates FAIL.

| Step | KL(native||removeD) | KL(native||base) | Их отношение | Gold ΔNLL removeD |
|---|---:|---:|---:|---:|
| 64 | 0.00003733 | 0.0001361 | 0.2743 | −0.001854 |
| 512 | 0.00003636 | 0.0026894 | 0.01352 | −0.001803 |
| 1024 | 0.00003641 | 0.0052361 | 0.006953 | −0.001801 |

Относительный показатель падает39.44раз; paired question-bootstrap95
для log early/late ratio [3.387,3.944]. Это не39кратное ослабление абсолютного
эффекта D: absolute KL почти постоянен, а denominator растёт38.47раз.
Заранее заданный absolute threshold1e−3 не достигнут: early effect в26.8раз
меньше него. Primary transient-scaffold gate FAIL; opposite growth FAIL.
Threshold — решение о продолжении exploration, не установленная граница
полезности/эквивалентности для accuracy. Эквивалентность также не доказана.
Не расширять n/checkpoints только ради более красивой normalized curve.

## Что найдено в самих весах

645120m coordinates во всех196modules bitwise одинаковы междуsteps64/512/1024.
Все точно равны FP32norm(base)→BF16. Поэтому здесь **не наблюдается эволюция
сохранённой обучаемой magnitude**. Утверждение о transient changes внутри
межчекпоинтных интервалов или master weights этим не проверяется.
Контраст `base_magnitude` в worker означает FP32norm(base), а исходная stored
magnitude BF16. Его KL3.63–3.74e−5 — **rounding counterfactual**, не удаление
обучившейся magnitude. Возврат к rounded initial m был бы exact weight no-op;
полный inference для такого no-op не запускался. Аналогичные KL двух условий
согласуются с важностью округления, но не доказывают идентичности их outputs.

Новые данные не устанавливают пользу/вред D для generation accuracy, механизм
его обучения или преимущества/недостатки DoRA против LoRA. Выпущенная LoRA
имеет другой LR, поэтому не была использована как causal method comparator.
Одна trajectory — один run, bootstrap по16questions не заменяет seeds.
GSM gold-prefix diagnostic не воспроизводит авторский PeRL math benchmark.

## Provenance, ресурс и решение

Exact public revisions/config/history hashes: provenance.json.
Base3.554GB и3×75.23MBadapter скачаны только сервером; whole-fileLFS SHA256
проверены; download+verification328.33s отдельно от model324.68s.
Base source lastModified2025-02-24 предшествует checkpoint run directory date,
но точная training base revision в adapterconfig неизвестна.
Versions/source/case/provenance hashes — validation.json.
Cases/logits/full rawrecords server-only; private locator вне Git.

PeRL future adapter-dynamics question: [paper](https://arxiv.org/abs/2512.23165).
Intermediate weight correlations уже есть в
[DoRA](https://proceedings.mlr.press/v235/liu24bn.html);
precision issue известна в [DoRAFactors](https://sockeye44.github.io/dorafactors-docs/how-it-works/).
Ни кривая сама по себе, ни BF16 arithmetic не заявлены нашей новизной.
Основной полезный результат этого stage — ограничение объяснений готовых
артефактов и предотвращение misleading normalized-role интерпретации.
Это не готовая статья уровняB. Новая model/GPU очередь по этой ветке не назначена.
