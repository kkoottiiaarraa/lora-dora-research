# Качество и численные контроли — пакет Q

Анализ exploratory: план составлен после сбора результатов. Все оценки относятся к сохранённым task-specific checkpoints Qwen3-4B, одной паре обучения на задачу. Все 29 принятых runs, 15 baseline metric contrasts и четыре dense/scorer comparisons проверены. Исходные hashes, accepted paths, полнота, provenance и парность проверены read-only; старый bundle не изменён. Новые baseline tests/CI не вычислялись.

## Базовое качество

| Задача/метрика | Base, % | LoRA, % | DoRA, % | DoRA−LoRA, п.п. | Исторический CI95, п.п. | Holm p |
|---|---:|---:|---:|---:|---:|---:|
| shadow_4b_mmlu/accuracy | 66.0518 | 70.3176 | 70.3746 | +0.0570 | [-0.4059, +0.5341] | 0.8301169883011699 |
| shadow_4b_squadv2/exact | 31.9296 | 86.0692 | 85.9345 | -0.1348 | [-0.4801, +0.2021] | 0.46625337466253375 |
| shadow_4b_squadv2/f1 | 46.5267 | 89.3081 | 89.0426 | -0.2655 | [-0.5597, +0.0236] | 0.1421857814218578 |
| gsm8k-quality-greedy/author_em | 1.2130 | 76.4973 | 77.5588 | +1.0614 | [-0.6065, +2.7293] | 0.47895210478952105 |
| gsm8k-quality-greedy/final_em | 63.8362 | 76.7248 | 77.7862 | +1.0614 | [-0.6065, +2.7293] | 0.47895210478952105 |


CI — исторические percentile paired-example bootstrap, B=10000, seed=42, без одновременной поправки. p сохранены из paired_sign_permutation_p, Holm точно внутри исходных файлов: MMLU 3 metric hypotheses, GSM8K 6, SQuADv2 6. Это не общая семья всех задач/исследовательского поиска. Интервалы не охватывают независимые обучения, seed, выбор гиперпараметров или выбор checkpoint.


GSM8K author scorer использует особый fallback первого числа; final scorer — альтернативное извлечение последнего числа. У base они расходятся на 846/1319 ответах (836 final-only correct и 10 author-only correct); у каждой адаптации на 3/1319. Поэтому 1.213% base author EM нельзя интерпретировать как чистое отсутствие арифметической способности. Результат final EM 63.836% тоже относится к тому же ограниченному greedy протоколу, а не к произвольной настройке генерации.

| Run | Input cap | New-token cap | Hit cap / n | Truncated prompts / n |
|---|---:|---:|---:|---:|
| shadow_4b_mmlu/base | 512 | 10 | 146/14042 | 136/14042 |
| shadow_4b_mmlu/dora | 512 | 10 | 135/14042 | 136/14042 |
| shadow_4b_mmlu/lora | 512 | 10 | 135/14042 | 136/14042 |
| shadow_4b_squadv2/base | 512 | 32 | 2800/11873 | 125/11873 |
| shadow_4b_squadv2/dora | 512 | 32 | 159/11873 | 125/11873 |
| shadow_4b_squadv2/lora | 512 | 32 | 156/11873 | 125/11873 |
| gsm8k-quality-greedy/base | 512 | 256 | 544/1319 | 0/1319 |
| gsm8k-quality-greedy/dora | 512 | 256 | 35/1319 | 0/1319 |
| gsm8k-quality-greedy/lora | 512 | 256 | 40/1319 | 0/1319 |


| MMLU role | micro, % | unweighted macro по 57 subjects, % |
|---|---:|---:|
| base | 66.0518 | 68.4687 |
| lora | 70.3176 | 72.3913 |
| dora | 70.3746 | 72.6095 |

Все 171 subject means представлены в quality-overview.csv, без новых p/CI и выбора «успешных» subjects. Subject macro равновесит subjects; micro взвешивает примеры. Subjects не являются независимыми обученными моделями.

| SQuADv2 stratum / metric | n | Base, % | LoRA, % | DoRA, % | DoRA−LoRA, п.п. |
|---|---:|---:|---:|---:|---:|
| answerable/exact | 5928 | 16.8860 | 83.4177 | 83.7888 | +0.3711 |
| answerable/f1 | 5928 | 46.1221 | 89.9048 | 90.0140 | +0.1092 |
| unanswerable/exact | 5945 | 46.9302 | 88.7132 | 88.0740 | -0.6392 |
| unanswerable/f1 | 5945 | 46.9302 | 88.7132 | 88.0740 | -0.6392 |

Answerability задана исходным answers.text, не результатом модели. Разбиения описательные, без subgroup tests или причинных объяснений. DoRA−LoRA exact положительна на answerable (+0.3711 п.п.), отрицательна на unanswerable (−0.6392 п.п.); итог зависит от состава evaluation set. Три task-specific пары не устанавливают универсализацию на архитектуры и задачи.

## Численные контроли и переход к компрессии

| Dense control / scorer | Δ, п.п. | CI95, п.п. | Исправлено | Сломано | Changed text /1319 |
|---|---:|---:|---:|---:|---:|
| gsm8k-dense-dora/author_em | -0.5307 | [-1.5940, +0.6065] | 24 | 31 | 511 |
| gsm8k-dense-dora/final_em | -0.6823 | [-1.7437, +0.3810] | 22 | 31 | 511 |
| gsm8k-dense-lora/author_em | +0.0000 | [-1.0614, +1.0614] | 25 | 25 | 526 |
| gsm8k-dense-lora/final_em | -0.0758 | [-1.1372, +0.9856] | 25 | 26 | 526 |

Исторические dense p/CI скопированы только для точной пары dense−соответствующий исходный PEFT. Семья intervention-family-holm.json: 8 contrasts ×2 scorers =16 гипотез. Все четыре CI включают ноль; это не equivalence. Различия ответов и ненулевые logits errors исключают утверждение подтверждённой функциональной идентичности.

Dense DoRA: max abs logits error 1.34375; dense LoRA: 1.578125; argmax agreement каждого 0.9814814925. Эти числа относятся к original-adapter→dense проверке на одном calibration prompt/54 input positions, не к полному test set, не к autoregressive sequence agreement, не к изменённому rank32/E95/E99 решению. dtype в fidelity summary явно не записан; BF16 provenance полного evaluator не подменяет эту отсутствующую запись. Source paths и этапы имеются в numerical-controls.csv.

**Gate к компрессии: условно пройден.** Integrity/provenance совместимы, dense references известны. Downstream rank/energy comparisons следует оценивать относительно сохранённой dense DoRA; matched-LoRA — относительно dense LoRA. Автоматический перенос результата на исходный PEFT checkpoint и использование pre-intervention fidelity как fidelity сжатого решения запрещены. CI dense DoRA допускает ухудшение около 1.59–1.74 п.п.; это существенная неопределённость для утверждения о сохранении исходного качества. Номинальный нулевой тест не устанавливает noninferiority.

## Пределы происхождения и воспроизведение

Проверены точные pinned evaluation revisions и hashes сохранённых inputs. Они не восстанавливают неизвестные training revisions/seeds, оптимизаторные траектории, обучение и выбор гиперпараметров. Quantization отсутствует как явное поле summaries; неизвестное не превращено в подтверждённый факт. Независимых training repeats нет. Финальные checkpoints и posthoc вмешательства не идентифицируют причину различий во время обучения.

`quality-overview.csv` содержит исходные fraction values, все 15 contrasts с точными историческими references/families и описательные means. `numerical-controls.csv` содержит 4 dense rows с transitions и fidelity source. `quality-validation.json` связывает read-only input hashes, код, PLAN/SPEC и outputs. SVG показывает только DoRA−LoRA и dense controls; полный набор таблицы не отобран по значимости.

```bash
```

