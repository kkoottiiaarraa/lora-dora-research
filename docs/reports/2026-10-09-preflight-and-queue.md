# Preflight и отложенный pipeline — 9 октября 2026

## Фактические результаты

Чистые VM/GPU checkout обновлены с 3eb0442 до 4020b26. Локальных изменений
до начала работы не было. Сеть, CLI, VPN, глобальные пакеты и другой проект
не изменялись. Веса и полный test split находятся только на GPU-хосте.

7 RTX A4000 по 16376 MiB, driver 610.57.04. В preflight 15:23:10 UTC все GPU
заняты чужими compute-процессами. Available RAM 666174943232 B, disk free
89623554134016 B. Scheduler-команды squeue/sinfo/qstat/bjobs не найдены.
Это не доказывает отсутствия правил выделения ресурсов.

Python 3.12.3; torch 2.5.1+cu121; transformers 4.57.1; peft 0.17.1;
accelerate 1.11.0; safetensors 0.6.2; HF hub 0.35.3; numpy 1.26.4.
Pip check прошёл; 17 CPU tests прошли, включая PEFT roundtrip и merge на tiny
random Qwen3, guard от четвёртого worker, двух последовательных idle checks,
несопоставимых входов и частичных оценок. Это не GPU-инференс Qwen3-4B.

| Артефакт | Исходный download/cache, s | Исходная SHA verification, s | Повторная SHA verification, s |
|---|---:|---:|---:|
| Qwen3-4B | 782.102 | 22.859 | 42.490 |
| LoRA | 14.648 | 0.275 | 0.319 |
| DoRA | 15.304 | 0.272 | 0.265 |

Точные revisions и пути — `results/download.json`, `results/reverify-20261009.json`.
Никаких load/forward/generation timing, VRAM/RSS или метрик качества пока нет.

## Отложенный запуск

Пользователь явно разрешил проверку каждые 10 секунд и запуск после двух
подряд свободных проверок одной GPU. Waiter PID 3576396. На 61-й проверке (15:38:52 UTC)
свободных GPU нет. Ограничение: ни одного compute-процесса, <=1024 MiB и
<=10% utilization; probe failure сбрасывает последовательность. В worker
повторный guard перед Torch import. Base/LoRA/DoRA serial на одной GPU,
2 smoke examples, BF16, batch=1, context 256, new tokens 64, merge check.
Проверяются все сохранённые adapter keys/значения/target coverage/magnitudes.

Команды из `/path/to/user-user/lora-dora-research`, venv
`/path/to/user-user/.venvs/lora-dora-research/bin/python`:

```bash
python scripts/server_preflight.py --output results/preflight-20261009T1525Z.json
python scripts/download_pilot.py --cache /path/to/user-user/.cache/lora-dora-research/huggingface --output results/reverify-20261009.json
python scripts/prepare_gsm8k.py
python scripts/wait_for_pilot.py --output-dir results/deferred-pilot-20261009T1530Z
python scripts/continue_after_pilot.py --waiter-dir results/deferred-pilot-20261009T1530Z --output-dir results/pipeline-20261009T1535Z
```

Не запускать второй waiter/continuation: per-user locks предотвращают дубли.
Существующие output directories не перезаписываются. Waiter и continuation
запущены detached с stdout/stderr в `results/*.log`. При ошибке нужен разбор
`waiter.json`, `state.json`, per-role `.log`/`.json`; слепых перезапусков нет.

## Единая оценка качества

Author code: ShadowLLM/shadow-peft revision
b667348c51e24d21f67c329c5f514f80e2c124d4.
`experiment/data_utils.py:load_gsm8k_dataset`: Question/Answer prompt,
thinking=false. `run_experiments.py:GSM8KTrainer`: greedy, use_cache=false,
256 new tokens, BF16 autocast, suite input limit 512. Наш matched протокол фиксирует эти
настройки для всех трёх ролей. `run_eval.py:eval_gsm8k` меняет prompt и scorer
для base на boxed; этот путь нельзя напрямую использовать как matched baseline.

Авторский scorer ищет ####, иначе первое число, и сравнивает строки. Сохраняем
его для воспроизведения; отдельно заранее фиксируем sensitivity scorer:
####, boxed, иначе последнее число с Decimal normalization. Выводы должны
учитывать оба scorer и долю ответов, достигших лимита токенов. Без #### первый
scorer может извлечь число из промежуточного рассуждения. Не выбирать scorer
по победителю. Это matched re-evaluation, не доказанное точное воспроизведение
всех неизвестных per-checkpoint training/eval настроек авторов.

Canonical OpenAI test JSONL revision 3101c7d5072418e28b9008a6636bde82a006892c:
1319 задач, SHA256 3730d312f6e3440559ace48831e51066acaca737f6eabec99bccb9e4b3c39d14.
На GPU `datasets/gsm8k-matched-v1/`. Восемь HF fixtures совпали, полное
равенство HF parquet не заявляется. Dataset не загружался на VM.

После завершения пилота continuation автоматически сохраняет его измерения
в HANDOFF, запускает 2-case runtime smoke для evaluator всех трёх ролей,
затем три полных прогона и comparison. Перед каждым worker снова ждёт две
свободные проверки; максимум одна GPU. Предсказания сохраняются по задачам,
со временем, token counts, truncation, gold, обоими извлечёнными ответами и
hash входов. Матched comparison отклоняет partial/unmatched runs и сохраняет
paired bootstrap CI разницы. Три заранее выбранных контраста; CI unadjusted,
это не familywise подтверждение и не оценка разброса training seeds.

## Следующий этап

Дождаться первого пилота; при runtime ошибке исправить её по логам. После
полной matched оценки реализовать численно проверенные вмешательства из
RESEARCH_PROTOCOL и дополнительные пары, включая без преимущества DoRA.
Готовый rank/magnitude NumPy helper ещё не является интеграцией с реальными
весами. Не обучать новые модели. Конечные абляции не устанавливают механизм
обучающей траектории; критика корреляции не опровергает выигрыш в качестве.

Continuation PID 3586457 подтверждён живым, статус waiting_for_pilot. Код: d3fd304 + b5f5275; safety stash на GPU сохранён.

## Сохранение Git и публикация

Код и состояние сохранены на VM и GPU в ветке research/prepare-checkpoint-study
(код d3fd304/b5f5275; запись состояния 24742b4). GitHub push обычным HTTPS
не выполнен: нет настроенной GitHub write-аутентификации (`could not read Username`).
Сеть/CLI/аутентификация не перенастраивались. Исследовательские фоновые задания
от этого не зависят. Полная резервная копия коммитов — Git bundle в outputs
этой сессии и `results/research-continuation.bundle` на GPU. Следующему чату
использовать существующие checkout и GPU HANDOFF, а не только свежий origin.

Последний подтверждённый snapshot: 15:39:55 UTC / 18:39:55 Москва, waiter
проверка 67, idle_uuids пусто. Continuation ждёт пилот. GPU load/inference,
полная accuracy, вмешательства и дополнительные пары пока не получены.
