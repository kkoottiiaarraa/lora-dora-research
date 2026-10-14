# Подготовленные данные для последующего анализа

Техническая подготовка сохранённых результатов, 2026-10-11. Набор содержит 29 принятых полных runs: три baseline triples (9 runs) и 20 вмешательств. Научная интерпретация отложена. Новых модельных прогонов, p-values, CI или статистических тестов на этом этапе нет; проверки целостности данных выполнены.

- [Техническое задание](SPEC.md).
- [A: корпус, сопоставимость и базовое качество](01-corpus-quality/README.md): реестр 29 runs, 29 сопоставлений, исходные baseline statistics, MMLU subjects, scorer agreement/limits, baseline transitions и SQuAD answerability.
- [B: вмешательства и локализации](02-interventions/README.md): 40 metric/transition rows, 28 grid cells, 8 exploratory descriptive interactions, 12 numerical control rows; 60 674 score rows в gzip (23 GSM8K runs × 1319 examples × 2 scorers).
- [C: численные проверки и ресурсы](03-diagnostics/README.md): module ranks/energy/errors, matched-impact measurements, numerical fidelity, symmetry statistics, ресурсы 29 runs и availability.
- [Общий manifest](manifests/bundle.json) и [приёмка](validation/bundle.json).

Схемы и единицы описаны в README каждого пакета, для C также в manifests/schemas.json. Доли и scores находятся в [0,1]; разности right-minus-left. Существующие CI/p/Holm сохранены со своей исходной парой и семейством. Семейства вмешательств 8/9/3 содержат 16/18/6 scorer hypotheses. Новые описательные interactions не имеют p/CI/Holm. CI относятся к примерам при фиксированных checkpoints, не к training seeds.

Доступны compact per-example GSM8K scores, агрегаты всех baseline задач, явные SQuAD answerability strata и сохранённые диагностические measurements. Полные тексты, веса и spectrum не копировались на VM. Неизвестная quantization metadata, неизмеренная fixed-base admissibility, отсутствующие dtype/tolerances короткой проверки и wall time без start/end обозначены null/missing_reason в соответствующих пакетах; отсутствие не заменяется нулём. Неизвестные training metadata не восстановлены догадками. Полный no-op и полная V/O generation отменены, короткая V/O численная проверка учтена отдельно.

attempts.csv имеют различное покрытие: A содержит 32 невыбранных full/smoke каталога в двух job roots; C содержит 35 обнаруженных summaries/error artifacts/cancellations и короткую численную проверку в своём диагностическом покрытии. Это ожидаемое различие областей учёта, не единый дедуплицированный счётчик всей кампании. Inference seconds/3600 обозначают только inference GPU-hours. Последовательные memory peaks не суммируются; process RSS не является свободной RAM сервера.

Единая offline-проверка из корня checkout:

```bash
python3 execution/analysis-preparation/verify_bundle.py
```

Она последовательно вызывает offline-режимы A (`--verify-only`), B (`--check`) и C (`--check --verify-local`), проверяет JSON, обязательные таблицы/схемы, declared checks, streaming CSV row counts, hashes outputs и extractors, затем общий manifest. Ненулевой exit code означает несогласованность. Сохранённый validation обновляется при запуске.

Команда формирования нового snapshot после финализации всех файлов:

```bash
python3 execution/analysis-preparation/verify_bundle.py --build-manifest
```

Общий manifest покрывает README/SPEC, MEMORY.md/AGENTS.md, весь набор таблиц/package manifests/checks и Python extractors/verifier. Собственный manifest и volatile validation/bundle.json исключены для предотвращения рекурсивных hashes. Изменение любого покрытого файла требует нового явно сформированного snapshot.

Первичная сборка выполнялась на CPU ШАДа с stdlib и максимум двумя threads; точные серверные команды/пути — в package README/manifests. На финской VM (1 GiB RAM, 1 CPU) находятся только код и компактные outputs. Общая приёмка работает локально последовательно, хеширует streaming, не загружает long CSV целиком, не использует сеть, NumPy/Torch/CUDA или первичные predictions. Контроллеры старых очередей не являются инструкциями нового запуска.

Canonical local checkout: `/path/to/user/Documents/Codex/2026-10-09/dora-lora-https-github-com-kkoottiiaarraa/work/lora-dora-series`; server checkout S: `/path/to/user-user/lora-dora-series`. Набор доступен по одинаковому относительному пути `docs/analysis-preparation/2026-10-11/`, код — `execution/analysis-preparation/`. Серверная временная копия сборки: `/path/to/user-user/lora-dora-profiling/analysis-preparation/2026-10-11/`. HANDOFF не включён в bundle hashes.
