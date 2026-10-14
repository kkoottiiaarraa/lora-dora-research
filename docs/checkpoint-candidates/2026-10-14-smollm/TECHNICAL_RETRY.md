# Tokenizer compatibility before inference

Первая попытка завершилась через3.51s до загрузки моделей и outputs. Настоящая
ошибка — AttributeError в Transformers4.57.1: extra_special_tokens ожидается
как named mapping, а новые adapter tokenizer_configs хранят list BOS/EOS.
Последующая жалоба на отсутствие protobuf маскирует эту исходную ошибку;
ничего не устанавливаем и pinned файлы не изменяем.

У обоих адаптеров list содержит только уже заданные bos_token/eos_token.
В loader передаётся empty extra mapping только после явной проверки этого
условия; неизвестные дополнительные tokens отклоняются. Реальная read-only
проверка всех трёх tokenizers: vocabulary49152полностьюравны, specialIDs[1,2,0],
bos1/eos2/pad2, chat_templateSHA256
872be49dbb638044ad01b60388f48d469ff2980e5f0dccdc22ec907db54d0788 одинаков.

Не меняем prompt/gold/generation/intervention протокол. Первая попытка сохранена
private; retry получает отдельный root и новые source hashes до outputs.
