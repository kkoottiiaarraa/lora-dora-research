# Проверка сохранения и повторной загрузки custom SORA

Фиксируется после arithmetic screen, до loader outputs. CPU2, FP64, tiny3×4,
без обучения и моделей. Исполнить весь pinned `SoraLinear` с установленным
PEFT0.17.1, не его авторским fork0.14.1.dev0. Совместимость версий — ограничение.

Создать одну toy linear модель. Через custom mapping обернуть её SoraLinear,
задать те же два набора коэффициентов, что в arithmetic screen. Сохранить
настоящий PEFT safetensors checkpoint. Отдельно загрузить в две копии строго
той же базы: (a) обычным PeftModel.from_pretrained без mapping,
(b) с повторной регистрацией mapping и переданным config.

Проверить фактический класс слоя, все сохранённые adapter tensor keys/values,
совпадение outputs с native и с независимой плотной формулой. Правильная
загрузка обязана сохранять все5тензоров и совпадать до1e−12. Сохранить warnings,
не подавляя их. Проверка initialization важна: B=0,C=D,diagonal=1 может скрыть
ошибочную загрузку даже при правильном выходе. Вторая проверка фиксирована
заранее и включает все компоненты. Никаких ответов LLM/benchmark выводов.

Static call-site evidence: finetune_math.py регистрирует SoraLinear, но
evaluate_gemma_math.py этого не делает. В опубликованном lm-evaluation-harness
custom mapping регистрируется только для polar/rplora. В author LoraConfig
_custom_modules инициализируется None, а default dispatcher не выбирает SORA
по adapter_name. Это кодовое основание риска, а не доказательство происхождения
авторских чисел. Нужны готовые checkpoints/logs и точная execution revision.

## Уточнение после первого loader screen, до проверки author fork

На установленном PEFT0.17.1 обе положительные проверки прошли, plain loader
сохранил только2из5тензоров. Чтобы исключить различие версии dispatcher,
повторить тот же frozen tiny пример на **неизменённом авторском PEFT0.14.1.dev0**
из того же commit. Все124Python-файла сверить по Git blob SHA1 с pinned tree.
Импорт через отдельный PYTHONPATH; ничего не устанавливать и не менять venv.
В конфигурации явно сохранить author `adapter_name=sora`. Torch/Transformers
останутся текущими, поэтому это проверка dispatcher/serialization, не полная
репликация авторского training stack. Не менять коэффициенты/входы/критерии.
