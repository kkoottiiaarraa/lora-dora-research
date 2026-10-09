# Расширенный аудит готовых пар LoRA / DoRA

Проверено 9 октября 2026 года. Дополняет `OPEN_CHECKPOINTS_AUDIT.md`.

## Вывод о достаточности

Достаточно для начала исследования уже обученных моделей без собственного обучения. Основной список содержит **10 пар-кандидатов из трёх релизных проектов**: четыре Answer.AI, пять ShadowPEFT, одну LLaVA. Шесть пар относятся к обычным LoRA / DoRA, четыре — к квантованным вариантам. Это десять условий, а не десять независимых повторений одного опыта.

Дополнительно обнаружены **16 физических пар файлов Mistral**, из которых одна имеет противоречие по learning rate, поэтому в резерв оставлены 15. Есть PeRL с одной полезной DoRA-траекторией и несколькими LoRA-контролями, но доступные сравнения имеют различия по learning rate либо рангу. Есть небольшие адаптеры DistilBERT и AraT5, а также дополнительные мультимодальные выпуски с неполной документацией.

Ни одна пара ещё не прошла локальное восстановление и повторную оценку качества. «Основной список» означает наличие весов, известной базы, открытых данных и кода с разумным основанием сопоставлять методы; это не сертификат одинаковых условий обучения. Большинство выпусков не содержит точного идентификатора базового snapshot или полного журнала параметров конкретного запуска.

Этот материал позволяет проверять повторяемость свойств конечных решений и роль компонентов при вмешательстве в готовую модель. Он пока не позволяет установить универсальную причину преимущества DoRA, восстановить все условия исходного VL-BART-опыта или провести чистое сравнение траекторий оптимизации во всех проектах.

## Что именно проверялось

- Поиск по статьям, авторским GitHub, GitHub Releases и branches, страницам исследовательских проектов, Hugging Face профилям и модельным каталогам.
- HF API: идентификаторы snapshot, фактические имена файлов, размеры и LFS SHA-256, когда доступны.
- Конфигурации адаптеров: база, rank, alpha, dropout, target modules, `use_dora`, `use_rslora`, остальные сохраняемые параметры.
- HTTP Range: заголовки safetensors, формы A/B и наличие тензоров магнитуды. Полные файлы весов не скачивались.
- Небольшие README, скрипты обучения/оценки, опубликованные аргументы и trainer states. Для PeRL `training_args.bin` проверен через чтение инструкций pickle как данных, без исполнения десериализации.
- Сохранены PDF Spectral Adapter, PeRL и ShadowPEFT; оригинальная DoRA и Calibrating and Rotating уже доступны локально.

Сырые результаты проверки находятся в `artifact-audit/`. Машиночитаемый список приоритетных пар — `checkpoint_inventory.json`. Инференс, SVD и новое обучение не запускались.

## 1. Основной список: Answer.AI — четыре пары

- Публикация: https://www.answer.ai/posts/2024-04-26-fsdp-qdora-llama3.html
- Код: https://github.com/AnswerDotAI/fsdp_qlora
- Исторический скрипт оценки: https://github.com/AnswerDotAI/fsdp_qlora/blob/e454d3180ef575654279d6ac444a86cb0bb3ff33/evaluate.py
- Коллекция: https://huggingface.co/collections/answerdotai/quantized-ft-orca-math-661eafb3db85e1ae77a3ffda
- Данные: https://huggingface.co/datasets/microsoft/orca-math-word-problems-200k

| База / обучение | QLoRA | QDoRA |
|---|---|---|
| Llama-2-7B / 10k | https://huggingface.co/answerdotai/llama-7b-orca-math-10k-bnb-qlora | https://huggingface.co/answerdotai/llama-7b-orca-math-10k-bnb-qdora |
| Llama-2-7B / 100k | https://huggingface.co/answerdotai/llama-7b-orca-math-100k-bnb-qlora | https://huggingface.co/answerdotai/llama-7b-orca-math-100k-bnb-qdora |
| Llama-3-8B / 10k | https://huggingface.co/answerdotai/llama-3-8b-orca-math-10k-bnb-qlora | https://huggingface.co/answerdotai/llama-3-8b-orca-math-10k-bnb-qdora |
| Llama-3-8B / 100k | https://huggingface.co/answerdotai/llama-3-8b-orca-math-100k-bnb-qlora | https://huggingface.co/answerdotai/llama-3-8b-orca-math-100k-bnb-qdora |

Все восемь `model_state_dict.safetensors` доступны; проверены заголовки. У QDoRA по 576 тензоров, в том числе 192 вектора магнитуды. У QLoRA по 675 тензоров, магнитуд DoRA нет. Ранг направляющей добавки 64. Базы: `meta-llama/Llama-2-7b-hf` и `meta-llama/Meta-Llama-3-8B` (точное имя нужно брать из выбранного исторического загрузчика); действуют условия доступа Meta.

Размеры: QLoRA Llama-2 около 4.05 ГБ, Llama-3 около 5.89 ГБ на файл; QDoRA соответственно 289 и 305 МБ. Файлы QLoRA содержат и базовые параметры; это не восемь маленьких стандартных PEFT-адаптеров. Применять нужно предусмотренный кодом способ восстановления квантованной базы.

В публикации для Llama-2: exact match 10k — 0.098 / 0.176, 100k — 0.118 / 0.312 (QLoRA / QDoRA). Есть полный fine-tuning как дополнительный контроль. Статистика из публикации ещё не воспроизведена.

Ограничения: квантование, одна математическая обучающая выборка, вложенные 10k / 100k, отсутствие серии seed и промежуточных весов. Эти четыре условия нельзя считать четырьмя независимыми датасетами.

## 2. Основной список: ShadowPEFT — пять обычных пар

Это **новая основная находка**: чужая работа о другом PEFT-методе публикует оба нужных базовых метода.

- Статья: https://arxiv.org/abs/2604.19254
- Код: https://github.com/ShadowLLM/shadow-peft
- Коллекция: https://huggingface.co/collections/shadow-llm/shadow-peft-models
- Код обоих методов: https://github.com/ShadowLLM/shadow-peft/blob/main/experiment/run_experiments.py
- Подготовка данных: https://github.com/ShadowLLM/shadow-peft/blob/main/experiment/data_utils.py

| База / задача | LoRA | DoRA |
|---|---|---|
| Qwen3-4B / GSM8K | https://huggingface.co/shadow-llm/Qwen3-4B-GSM8k-LoRA | https://huggingface.co/shadow-llm/Qwen3-4B-GSM8k-DoRA |
| Qwen3-4B / SQuAD v2 | https://huggingface.co/shadow-llm/Qwen3-4B-SquadV2-LoRA | https://huggingface.co/shadow-llm/Qwen3-4B-SquadV2-DoRA |
| Qwen3-4B / MMLU | https://huggingface.co/shadow-llm/Qwen3-4B-MMLU-LoRA | https://huggingface.co/shadow-llm/Qwen3-4B-MMLU-DoRA |
| Qwen3-8B / GSM8K | https://huggingface.co/shadow-llm/Qwen3-8B-GSM8k-LoRA | https://huggingface.co/shadow-llm/Qwen3-8B-GSM8k-DoRA |
| Qwen3-8B / SQuAD v2 | https://huggingface.co/shadow-llm/Qwen3-8B-SquadV2-LoRA | https://huggingface.co/shadow-llm/Qwen3-8B-SquadV2-DoRA |

Проверены все десять конфигураций и заголовков весов. В каждой паре совпадают база, rank 32, alpha 32, dropout 0.05, четыре attention-проекции Q/K/V/O. `use_dora=false` у LoRA, `true` у DoRA; `use_rslora=false` у всех. В LoRA 288 тензоров, в DoRA 432, включая 144 магнитуды. Адаптеры Qwen3-4B примерно 94–96 МБ, Qwen3-8B примерно 123–124 МБ. Все десять суммарно около 1.07 ГБ; базы скачиваются отдельно.

Открытые базы: https://huggingface.co/Qwen/Qwen3-4B и https://huggingface.co/Qwen/Qwen3-8B . Данные: `openai/gsm8k`, `squad_v2`, `cais/mmlu`; для MMLU код использует auxiliary train и раздельные оценочные поднаборы. Chat templates и извлечение ответа заданы в коде.

В таблице 1 статьи для GSM8K Qwen3-4B: LoRA 76.80, DoRA 77.86; для Qwen3-8B: LoRA 79.76, DoRA 78.39. Для SQuAD v2 DoRA немного уступает LoRA. Это даёт полезные случаи выигрыша и проигрыша, не отобранные по одному исходу. Разницы ещё не проверены статистически.

Ограничения: карточки большинства моделей шаблонные, полных аргументов конкретного запуска/состояний оптимизатора нет; paper сообщает подбор learning rate. Конфигурация адаптера не содержит LR и не доказывает одинаковую настройку всего обучения. В таблицах 1 и 2 есть несогласованность значения LoRA/GSM8K/4B (76.80 против 72.37): перед использованием опубликованной метрики надо восстановить её связь с конкретным checkpoint. Таблицы блог-поста от сентября 2026 относятся к другим опытам Llama-3.2/FLUX и не являются метриками этих пяти пар.

Наличие результатов для Qwen3-0.6B в статье не означает, что опубликованы нужные пары: в проверенном HF-профиле доступны преимущественно Shadow-веса 0.6B, поэтому они не включены в счёт.

## 3. Основной список: LLaVA-1.5-7B — одна обычная пара

Подробная проверка в `OPEN_CHECKPOINTS_AUDIT.md`, §2.

- DoRA: https://huggingface.co/sliuau/DoRA-weights/tree/main/llava-v1.5-7b-dora-release
- LoRA: https://huggingface.co/liuhaotian/llava-v1.5-7b-lora
- Код: https://github.com/NVlabs/DoRA/tree/main/visual_instruction_tuning

Есть adapters и `non_lora_trainables.bin`, configs, trainer states. Rank 128, alpha 256, dropout 0.05 и target modules совпадают. База Vicuna-7B-v1.5 + CLIP. Открыты аннотации смеси и исходные источники данных; для оценки можно выбрать открытый поднабор.

Ограничения: обучение отдельно обновляет мультимодальный проектор; только адаптера недостаточно. Это чужой LoRA baseline, а не автоматически одинаковые seed/обучение. Модель тяжелее остальных приоритетных неквантованных вариантов. Для универсальности нельзя трактовать семь оценочных benchmarks одной обученной пары как семь независимых обучений.

## 4. Резерв: Spectral Adapter / Mistral — 15 пригодных к дальнейшему аудиту пар

- Статья: https://arxiv.org/abs/2405.13952
- Код: https://github.com/pilancilab/spectral_adapter
- Опыт Mistral: https://github.com/pilancilab/spectral_adapter/tree/main/mistral_tune
- Авторские выпуски: https://huggingface.co/fzzhang и https://huggingface.co/fangzhaoz

Профили принадлежат Fangzhao Zhang, автору Spectral Adapter. Найдены и проверены **32 файла адаптеров**, составляющие 16 именных пар. Заголовки подтверждают LoRA / DoRA, ранги и магнитуды; конфигурации задают одну базу `mistralai/Mistral-7B-v0.1`, Q/K/V/O + gate, dropout 0.05, alpha=2r. Карточки содержат LR, эпохи, seed=0 и версии библиотек. Код проекта открыто использует GSM8K и lm-evaluation-harness.

Имена пар: в каждом имени заменить `{method}` на `lora` / `dora`.

| Автор | Имена |
|---|---|
| `fangzhaoz` | `mistralv1_{method}_r24_1e3`, `r24_1e4`, `r24_1e5`, `r4_1e-4_e5`, `r8_25e5_e3`, `r8_2e4_e3` |
| `fzzhang` | `mistralv1_{method}_r16_25e5_e01`, `r16_25e5_e03`, `r16_25e5_e05`, `r16_5e5_e03`, `r32_25e5_e05`, `r4_25e5_e05`, `r8_1e4_e05`, `r8_1e5_e05`, `r8_25e5_e05` |

Пример: https://huggingface.co/fzzhang/mistralv1_lora_r16_25e5_e03 и https://huggingface.co/fzzhang/mistralv1_dora_r16_25e5_e03 .

Исключённая 16-я пара: `fangzhaoz/mistralv1_{method}_r24_1e6`. README LoRA сообщает LR=0.001, DoRA — 0.000001, несмотря на одинаковый суффикс. Без восстановления настоящих параметров нельзя считать их сопоставимыми по LR.

Размер каждого адаптера примерно 12–94 МБ. Пары покрывают несколько рангов, LR и длительностей, но одну модель и, предположительно, один датасет/seed; профили одного автора нельзя считать независимыми группами воспроизведения.

Почему резерв: карточки самих checkpoints обозначают dataset как `None`; принадлежность именно этих файлов конкретным опытам статьи выводится из автора, названий и кода, а не явного per-run manifest. Текущий пример скрипта задаёт r=8 и 2 эпохи, что не соответствует всем релизам. Нужно восстановить конкретный preprocessing, базовый snapshot, параметры и оценку. Проверенные совпадения в карточках не устраняют эту неопределённость.

## 5. Резерв с динамикой: PeRL — DeepSeek-R1-Distill-Qwen-1.5B

- Статья **Evaluating Parameter Efficient Methods for RLVR**: https://arxiv.org/abs/2512.23165
- Проект PeRL: https://github.com/MikaStars39/PeRL
- Веса: https://huggingface.co/MikaStars39/PeRL
- Открытые обучающие данные: https://huggingface.co/datasets/open-r1/DAPO-Math-17k-Processed
- База: https://huggingface.co/deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B
- Оценка: https://github.com/MikaStars39/MikaEval

Файлы DoRA: `dapo_dora_qwen2_5_1_5b_20251126_115730/checkpoint-{step}/adapter_model.safetensors`.

LoRA-контроль с тем же рангом: `dapo_lora_lr5_20251129_222821/checkpoint-{step}/adapter_model.safetensors`.

Для каждого доступны **16 состояний**, steps 64, 128, …, 1024. У DoRA файлы по 75,228,904 байта; у LoRA-r32 по 73,911,504. В просмотренных checkpoints также присутствуют trainer logs, scheduler и DeepSpeed optimizer states. Заголовки первых/последних состояний проверены: DoRA 588 тензоров, из них 196 магнитуд; LoRA 392, магнитуд нет. Сохраняются BF16-адаптеры. Это реальная возможность изучать динамику, а не только финальную точку.

**Существенное ограничение:** из опубликованных `training_args.bin` DoRA LR=1e-5, LoRA-r32 LR=5e-6. У обоих seed=42, batch per device=4, accumulation=8, steps=1024. Другой опубликованный LoRA-контроль `dapo_lora_qwen_1_5b` имеет r=16, alpha=32, тогда как DoRA r=32, alpha=64. Его нельзя объявлять тем же рангом.

В проекте есть скрипт LoRA-r32 с LR=1e-5, но наличие скрипта не заменяет отсутствующий однозначно соответствующий выпуск весов. В 7B-каталогах часть файлов весов отсутствует; проверенная конфигурация внутри `dapo_dora_7b_...` имеет `use_dora=false`. 7B-пару не включать без отдельной проверки.

Статья прямо оставляет математическое объяснение преимуществ структурных адаптеров открытым (§4, Mechanistic Interpretability of Adapter Dynamics). Это соответствует исследовательскому вопросу пользователя. Однако её headline-сравнение нельзя без аудита приписать конкретной r32/LR5 паре. RL генерирует ответы самой обучаемой моделью: одинаковые исходные вопросы не означают одинаковые обучающие токены у LoRA и DoRA.

16 checkpoints — одна пара траекторий, не 16 независимых экспериментальных пар.

## 6. Дополнительные небольшие/другие пары: пока только резерв

| Материал | Что подтверждено | Чего не хватает / отличие |
|---|---|---|
| DistilBERT, `Benuehlinger/my-peft-distilbert` / `my-DORA-distilbert` | Веса около 7.7 / 7.9 МБ, одинаковые r16/alpha32/dropout0.1 и 36 target modules; LoRA 76 тензоров, DoRA 112 с 36 магнитудами; обе сохраняют classifier и pre_classifier | https://github.com/benuehlinger/LoRA-finetune содержит SST-2 и LoRA-код, но не идентифицирован точный DoRA-запуск/его параметры и оценка. Датасет DoRA не подтверждён отдельно |
| AraT5, `yasmineee/araT5-Base-with-LoRA` / `araT5-Base-with-DoRA` | Веса 4.46 / 4.93 МБ, одинаковые r5/alpha32/dropout0.06, LR=2e-4, 5 эпох, seed42; заголовки подтверждают методы; BLEU в карточках 12.5314 / 13.0059 | Dataset в карточках неизвестен; нужны код, точная выборка перевода и split. Наличие других OPUS100-выпусков автора не доказывает данные этой пары |
| NLLB, `yasmineee/NLLB_LoRA` / `NLLB_DoRA` | Есть обе модели r8 и карточки с результатами | Разные batch/число шагов; неизвестный точный dataset/split |
| Qwen2-VL-7B, `Hosseinka/qwen2-vl-Rad_dataset_lora` / `..._dora`, и `...-Patch_dataset_lora` / `..._dora` | Две пары реальных adapters по 110 МБ, одинаковые r64/alpha32/dropout0.05, Q/K/V. Заголовки подтверждены | Название Rad/Patch не устанавливает точный dataset/revision/split; полные условия и публичный evaluation-код не восстановлены |
| ProtBERT, `Chinjuj/protebert-protfam-peft-lora` / `...-Dora` | Оба адаптера r8 для `Rostlab/prot_bert`, с обученным classifier | Alpha 16 / 8, dropout 0.1 / 0.05; карточки шаблонные, точные данные и код не найдены |
| Quantum Assistant, `samuellimabraz/Qwen3-VL-8B-lora` / `...-dora` | Открытая база, https://github.com/samuellimabraz/quantum-assistant , датасет `samuellimabraz/quantum-assistant`, полные слитые модели по 17.53 ГБ, args/YAML/logs | В README заявлено одинаковое r16, но реальные args: LoRA r8/use_rslora=false; DoRA r16/use_rslora=true. Это сравнение изменяет три фактора. В адаптерную основную выборку не включён |
| FactorJEPA, `anonymousML123/factorjepa-peft-lora-vjepa21-vitG-2B-poc` / `...-dora-...` | Опубликованы encoder, loader, best checkpoint и logs | Нужная общая continual-pretrain база и публичность Indian-context clips не установлены; полный training pipeline не предоставлен в просмотренном выпуске. Нельзя считать комплектом с открытыми всеми данными |

## 7. Отсечённые находки и проверка других релизов

- `NiiCole/vit-base-patch16-224-in21k-dora_food101`, `...-lora_food101`, `...-lora_food101-actual-lora`: **все три DoRA**, по конфигам и 24 векторам магнитуды. Первый r16, остальные r8. Именная пара не является LoRA / DoRA.
- `kuei1026/3d-icon-sdxl-dora-rank-64` / `...-lora-rank-64`: оба проверенных `pytorch_lora_weights.safetensors` содержат 560 тензоров DoRA-масштаба. Это два DoRA-файла, не проверенная пара методов.
- `PriyadarshiniTamilselvan/...-distilbert-lora`: в проверенном HF-каталоге файлов весов нет; DoRA-публикация сама по себе пары не даёт.
- Medical VQA Google Drive: прямая публичная ссылка https://drive.google.com/drive/folders/1Y_zvc7aqt1fogymPh5SxwpCKkREsGoTB перенаправляет на вход Google. Содержимое не удалось подтвердить публичным чтением, поэтому в счёт не включено.
- `EvalData/tsfm-peft-bench`: публично доступны результаты сотен запусков, код и конфиги. В просмотренном HF-каталоге нет файлов весов; README указывает `checkpoints/` как symlink на NAS автора. Полезно для анализа таблиц/межзадачных закономерностей, но не готовое множество пар для вмешательств в веса.
- SORA, DeLoRA, BiDoRA: у проверенных авторских GitHub нет Releases, по одной основной ветке. Расширенный веб-поиск не дал подтверждённого внешнего релиза нужных пар. Это предел проведённого поиска, не доказательство отсутствия файлов где-либо.
- PoLAR: Releases **есть** — четыре архива `polar_rank*.zip` для Llama-2-7B и `polar_metamathqa.zip` для Gemma-3-27B. Это расширяет доступные материалы PoLAR, но пары LoRA / DoRA в этих релизах не подтверждены. Архивы целиком не скачивались/не проверялись.
- Interpreting-LoRA-Fine-Tuning и shreyassks/DoRA: Releases отсутствуют, одна main-ветка; внешние парные весовые выпуски в выполненном поиске не подтверждены.

## 8. Как трактовать достаточность и независимость

Основные источники покрывают квантованное SFT, обычное SFT, разные размеры, арифметику, QA, knowledge benchmark и мультимодальные инструкции. Резерв PeRL добавляет RL и промежуточные состояния; Mistral — ранг/LR/длительность. Это уже материал для проверки переносимости гипотезы между условиями.

При этом:

1. Несколько размеров/рангов на одном dataset/seed — связанные условия, не независимые воспроизведения.
2. Тысячи матриц внутри модели — внутренние измерения, не тысячи независимых экспериментальных единиц.
3. Несколько benchmark-метрик одной пары — несколько наблюдений поведения одних весов.
4. Для объяснения преимущества нужны также пары с ничьей и обратным преимуществом; иначе отбор только DoRA-побед создаёт систематическое смещение.
5. Вмешательство в финальный checkpoint показывает роль компонента в этом решении. Оно не устанавливает, что при другом обучении LoRA не могла достичь того же результата.
6. Публикационный вывод лучше формулировать как проверяемый механизм/условия применимости, а не универсальное утверждение «DoRA лучше LoRA».

Следующий этап подготовки: выбрать несколько основных пар, восстановить модели и повторить ограниченную оценку; зафиксировать hash баз/данных/кода; проверить связь опубликованных чисел с checkpoints. Только после этого считать пары допущенными в эксперимент. Полный train dataset не нужен для спектров; для функциональных проверок нужны реальные оценочные входы, preprocessing и метрика.

Не нужно заранее переобучать четыре-семь миллиардов параметров. Анализ матриц можно проводить по слоям, а инференс — последовательно по базам. Точное время и память на двух A4000 пока не измерены.
