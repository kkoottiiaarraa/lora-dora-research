# Два дополнительных источника: согласованная готовая пара не найдена

14 октября2026. Только публичные metadata/code: веса не скачаны, модельных
прогонов нет, GPU0. [Provenance](provenance.json) фиксирует revisions,
полные нетронутые tree responses проверены локально без исполнения train scripts.

| Источник | Что найдено | Решение |
|---|---|---|
| [Remilia-Kirisame/ELEN90088-SOML](https://github.com/Remilia-Kirisame/ELEN90088-SOML/tree/2504b35dcbbcd4e7e1201beae9051d92147262fc/mini-project-DoRA) | Mistral-7B-Instruct-v0.3, LoRA/DoRA, ranks4/8/16, несколько seeds; configs/metrics/logs опубликованы, adapters исключены из Git. | Не готовая коллекция весов. В проверенных README/tree/releases нет ссылки на их выпуск. HF поиск по GitHub handle пуст, но идентичность аккаунтов неизвестна; отсутствие весов где-либо не доказано. Не воспроизводить обучением. |
| [Benjamin-Pong/PEFT-Multilingual-Content-Safety-Moderation](https://github.com/Benjamin-Pong/PEFT-Multilingual-Content-Safety-Moderation/tree/760261036df0c0cb000074ab7e563ff4a3b56a41) | DoRA опубликована на HF; обычная LoRA в сравнении — PolyGuard другого автора. | Не принять как согласованную пару методов. Доступность двух названий недостаточна для контроля обучения. |

У первого источника разделение answer format/task correctness уже явно
исследовано; простая чувствительность scorer не наша новая идея. Авторские
средние и seed std не заменяют собственную статистическую проверку или веса.

## Проверенный HF кандидат и причина отказа

[Benjaminpwh/qwen2.5-7b-instruct-poly-QDpra-1](https://huggingface.co/Benjaminpwh/qwen2.5-7b-instruct-poly-QDpra-1/tree/c7d4fd542b286ce2c0cfba0b600f3666c7233397):
ungated, adapter86,381,480байт; `use_dora=true`, r8, alpha16, dropout.1,
q/k/v/o/gate/up/down. **Base config указывает
unsloth/qwen2.5-7b-instruct-unsloth-bnb-4bit**, revision=null.
Не подменять её без проверки обычной FP32 Qwen2.5.
Второй опубликованный DoRA revision сохранён в provenance; его не считать
LoRA control или независимым seed без training provenance.

[PolyGuard-Qwen](https://huggingface.co/ToxicityPrompts/PolyGuard-Qwen/tree/644bfe73ff498c9a14818b72a11187eaf23f0ff1)
опубликован как полная модель, не извлечённая согласованная LoRA.
[PolyGuard, Appendix C](https://arxiv.org/html/2504.04377v2#A3): LR2e−4,
sequence8192, totalbatch128, epoch1; в проверенном DoRA script LR2e−5,
batch8×16, epoch1, продолжение из уже существующего адаптера и повторный вызов
resume training. Одинаковый rank8/alpha16 не устраняет эти различия.
Точная execution history и base-trainingSHA неизвестны.

Кандидат остаётся metadata reserve для отдельного исследования inference
portability QDoRA, если появится конкретный новый вопрос. Само обнаружение
ещё одного checkpoint не повод запускать новый necessity screen после failed
SmolLM2-B. Никаких внешних сообщений авторам и запросов доступа не отправляли.
