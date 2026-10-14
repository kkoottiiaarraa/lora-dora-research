# Две дополнительные серии — 9 октября 2026

Пользователь разрешил две дополнительные последовательные очереди на двух
других свободных GPU, не меняя текущую серию. Scope подтверждён: основные
пары и вмешательства; резервные Mistral/PeRL не включаются. Всего максимум
3 GPU. Проверки через 10 s, одна и та же GPU свободна 2 проверки подряд;
перед загрузкой повторный guard и общий gpu_lease из существующего проекта.

## Изоляция

Текущий checkout `/path/to/user-user/lora-dora-research`, его процессы,
код, Git HEAD, datasets, venv и generation settings не менялись. Новый код:
`/path/to/user-user/lora-dora-series`, ветка `research/two-extra-series`.
Это важно: текущий evaluator проверяет одинаковые hashes кода между ролями.

Venv существующая `/path/to/user-user/.venvs/lora-dora-research`, без изменений.
Только для подготовки parquet добавлен pyarrow==19.0.1 через pip --target
`/path/to/user-user/.cache/lora-dora-series/python`; PYTHONPATH задавался
только отдельному preparation process. Загрузки max_workers=2 последовательно.
Большие данные/веса не скачивались на VM.

## Уже полученные факты первого запуска

Пилот завершился на attempt 351; paths:
`results/deferred-pilot-20261009T1530Z/pilot-attempt-351/` в исходном checkout.
Все adapter tensors прошли сверку, 144 модуля в каждой роли с адаптером.

| Роль | Base load, s | Adapter attach, s | Peak allocated VRAM, bytes | Max RSS, bytes | Два 64-token generation, s |
|---|---:|---:|---:|---:|---|
| base | 27.352 | — | 8075097088 | 4724047872 | 3.146 / 2.871 |
| LoRA | 3.215 | 1.815 | 8233698816 | 4734803968 | 4.148 / 4.076 |
| DoRA | 2.865 | 2.267 | 8404743680 | 4734369792 | 10.227 / 10.157 |

Load times зависят от файлового кеша; по одному прогону нельзя сравнивать
скорость загрузки методов. Merge: top1 одинаков на одном проверенном токене,
не bitwise; max absolute logits error 0.296875/0.3125, KL 0.000925/0.001460.
Это ограниченная fidelity-проверка, не универсальная эквивалентность.
Текущая полная оценка base работает на GPU UUID a50d0c3b…; на прочитанном
snapshot 167/1319, 1982 s. ETA текущего base около 3.8 h, всей серии около
12–14 h по короткому timing LoRA/DoRA; возможна разница сложности вопросов.

## Задания и балансировка

Точный immutable план: `configs/two_series.json`, 27 заданий.
17 имеют исполняемый код (2 новые полные пары, повторный DoRA no-op,
14 вмешательств), 10 пока имеют явные причины неготовности:
7 остальных пар-кандидатов и rank/activation/symmetry операции.

Серия 1 начинает с Shadow Qwen3-4B/MMLU, серия 2 — с Shadow
Qwen3-4B/SQuAD v2. Для каждой: короткий runtime smoke base/LoRA/DoRA,
затем полные одинаковые прогоны, matched comparison и paired uncertainty.
MMLU: 14042 задач, 10 new tokens; SQuAD: 11873, 32 new tokens;
везде input<=512, BF16 autocast, greedy, use_cache=false, thinking=false.
Авторские prompts/scorers адаптированы из ShadowLLM/shadow-peft revision
b667348c51e24d21f67c329c5f514f80e2c124d4. MMLU micro и subject macro
сообщаются отдельно. SQuAD EM/F1 соответствует span normalization и
максимуму по gold answers; no-answer aliases фиксированы до запуска.
Не обещаем точного воспроизведения неизвестных per-run аргументов авторов.

После завершения текущей полной GSM8K-оценки серия 1 повторяет неизменённую
DoRA в новом evaluator. Если входы или тексты отличаются от исходного DoRA,
вмешательства не допускаются без разбора. Обе очереди ждут этот контроль.
Затем распределены base_magnitude и remove_d, каждый для all/QK/VO/Q/K/V/O.
Общее вмешательство и отдельные группы предзаданы, не выбираются по победителю.
При успешном завершении всей семьи — Holm correction jointly over all
14 contrasts and both scorers. CIs сами по себе unadjusted.

Исходный прогноз исполняемой GPU-нагрузки около 42 и 41 h на серию,
разница порядка нескольких процентов. Это pilot-seeded proxy, не измеренный
wall time, не гарантия окончания одновременно. Runtime smoke и реальные
summaries уточнят скорость новых tasks. Отдельно распределены неопределённые
дальнейшие работы; их proxy не следует трактовать как достоверный ETA.
Зависимости/ожидание чужих GPU в GPU-hours не входят.

## Явно неподготовленная часть очереди

Qwen3-8B GSM8K/SQuAD: сначала проверка вместимости BF16 + адаптер +
активации на одной A4000. Автоматического перехода к quantization/offload нет.
Четыре Answer.AI: специальный quantized state loader и проверка доступа к базе.
LLaVA: multimodal loader, обученный projector, изображения и evaluator.
Rank-r, matched perturbation controls и normalization-aware Q/K symmetry:
нужна численно проверенная реализация. Эти записи входят в backlog обеих серий,
но не держат GPU и не обозначаются как уже работающие эксперименты.
Их активация требует отдельного изменения проверенного кода/плана; GPU wait
не заменяет отсутствующий loader. Резервы не запускать.

## Проверка и управление

22 CPU tests прошли, включая реальные PEFT формулы base_magnitude и remove_d,
group coverage, общий 3-slot guard, чужие процессы, приоритет текущей карты,
float F1 bootstrap и Holm. В PEFT 0.17.1 обнаружено и исправлено:
use_dora=False недостаточно, нужно также убрать DoraLinearVariant dispatcher.
Это относится только к новому checkout; текущий запуск не менялся.
Compileall и CLI проверены; новые benchmarks ещё требуют GPU runtime smoke.

Два запуска из нового checkout:

```bash
/path/to/user-user/.venvs/lora-dora-research/bin/python -u scripts/run_series_queue.py --series 1
/path/to/user-user/.venvs/lora-dora-research/bin/python -u scripts/run_series_queue.py --series 2
```

Запускаются detached; состояние `results/extra-series/series-{1,2}.json`,
логи `results/series-{1,2}.log`, результаты по задачам в
`results/extra-series/jobs/<job-id>/`. Safety locks общие с первым pipeline;
каждая очередь одновременно имеет только одного worker. Race guard refusal
возвращает 75 и ждёт снова; runtime ошибки модели сохраняются без blind retry.
Перед запуском исключается текущая primary GPU; между primary workers ей
даётся приоритет. Никаких чужих процессов не останавливают.

HANDOFF нового checkout обновляется после этапов под отдельной файловой
блокировкой. Исходный HANDOFF содержит ссылку на эту ветку/состояние.
Конечные абляции показывают роль компонентов решения, не причину обучения.
