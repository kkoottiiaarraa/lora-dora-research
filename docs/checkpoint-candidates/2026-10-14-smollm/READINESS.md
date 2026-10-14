> Обновление14октября: [технический pilot принят](PILOT_REPORT.md); [64-request necessity screen](../../analysis/2026-10-14-radial-necessity/REPORT.md) не прошёл gate. Ниже сохранён исходный metadata audit до скачивания.

# Готовые открытые пары SmolLM2: полезный кандидат, не чистый training experiment

14 октября2026. Найдены четыре пары обычных LoRA/DoRA одной
[коллекции автора](https://huggingface.co/kon172verma/intent-classifier-experiments),
HF revision `225a5766f66d752de4090ea228611418c7847a7b`. База
[HuggingFaceTB/SmolLM2-360M-Instruct](https://huggingface.co/HuggingFaceTB/SmolLM2-360M-Instruct),
revision `a10cc1512eabd3dde888204e902eca88bddb4951`: публичная, ungated.
Метаданные получены анонимно, без HF-токенов; веса пока не скачаны.

A: r8,Q/V; B: r16,Q/K/V/O; C: r16,attention+MLP; D:r32,attention+MLP.
Внутри каждой пары одинаковы rank/alpha/dropout/targets, reported200steps/4epochs.
**Это не чистая rank grid:** между A/B/C/D также меняются LR, targets, dropout
и batch settings. B/C отличаются набором модулей при одинаковых r/LR/dropout,
но отдельные авторские training runs не заменяют контроль причин обучения.
Параметры и hashes всех восьми конфигураций: [pairs.csv](pairs.csv).

[Авторский training repository](https://github.com/kon172verma/intent-classifier/tree/d0196d9122f84597eec8b44254a48d6885e1b90f)
содержит actual training reports и общий trainer; DoRA — его wrapper с use_dora=True.
Логи связаны с конкретными HFsubfolders, есть шаги/валидация. Это улучшает
traceability относительно пустых model cards. Но seed/init и точная revision
базы в отчётах не записаны; current code не доказан точным кодом запуска.
DoRA использует gradient checkpointing, LoRA в этих runs нет. Не называть пары
рандомизированным сравнением методов или независимыми seeds.

Задача — выбор одного инструмента из списка, ответ в виде позиционного ID.
1k mode:800train(sample0002–0009),100val(0010),100test(0001).
[Исходное split правило](https://github.com/kon172verma/intent-classifier/blob/d0196d9122f84597eec8b44254a48d6885e1b90f/finetune_LoRA/src/prepare_lora_data.py).
Остальные публичные файлы могут дать дополнительные unseen-by-1k-run примеры,
но сначала нужны content/dedup audits и учёт синтетического происхождения.
Нельзя автоматически объявить их независимыми естественными задачами.

Есть важная деталь воспроизведения: текущий отдельный inference repo вставляет
дополнительную пустую строку перед User Request, а training/eval callback — нет.
Для первого pilot использовать **training/callback формат**, сравнить его строки
и tokenizer с исходником, не полагаться на комментарий «exact reproduction».
Авторский generation callback: greedy,max_new_tokens8. Не подменять его произвольным
first-token классификатором, пока границы/способ извлечения ответа не проверены.

Первым кандидатом выбираем **B**, потому что всеattentiontargets соответствуют
нынешним intervention helpers и допускают coupled V/O gauge; выбор основан
на структуре, не выигрыше DoRA. В авторских validation logs B имеет51%уобоих;
это не наши измерения. A/C/D остаются metadata-only reserve, не новая очередь.
Для A O не адаптирован: magnitude-only V/O gauge нашего текущего аудита недоступна.

Минимальный следующий этап — pinned download только базы и двух B адаптеров
на вычислительном сервере, проверки SHA/точной загрузки/токенизации и восемь
validation smoke examples на CPUFP32. Это технический pilot, не fullquality
или новая статья. Большую сетку не запускать без конкретного эффекта/гипотезы.
[metadata.json](metadata.json) фиксирует доступность и неизвестные поля.
