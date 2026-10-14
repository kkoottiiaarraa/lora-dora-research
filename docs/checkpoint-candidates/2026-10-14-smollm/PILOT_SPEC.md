# Технический pilot B: до новых outputs

14 октября2026. Выбор B описан в READINESS. Только одна новая база360M и два
B адаптера с pinned revisions; все веса/вычисления на compute host. CPU8/FP32,
SDPA, CUDA hidden, no training/quantization/dependencies installation.

Проверить sourceSHA всех weights через HF LFS metadata и фактические файлы;
sourceconfigs r16/alpha32/targetsQKVO/no bias совпадают, use_dora ожидаемо различен.
Base Llama/GQA32layers/15Q-5KVheads/hidden960, attention_biasFalse. Ожидаем
128adapted modules,256LoRAtensors/384DoRAtensors, plusD81,920parameters.
Сопоставить фактический PEFT load со всеми saved values. Параметры inferenceFP32.

Cases: первые8 author-validation rows sample0010; test sample0001неиспользовать.
Проверить schema, lowercase-name→case-sensitive positionalID mapping/no-tool '-'.
Training/callback messages и их newline строго воспроизвести. SourceSYSTEM_PROMPT
хранить в private protocol, не копировать весь внешний текст в public reports.
DoRA/LoRA tokenizer vocabulary, special IDs и chat template должны совпасть.
Whole prompt/full-answer tokenization проверяет boundary, gold ID должен быть
одним токеном; при иной токенизации остановиться и описать фактическое отличие.

Три serial native load: base/LoRA/DoRA. У каждого8single forwards последнего
logit (fullvocab goldNLL) и8greedygenerations max_new_tokens8; одинаковые
prompt/generation/scorer. Это smoke, не оценка accuracy. Сохранить predictions
и raw output. Падения/нечисла ловить на CPU, не декодировать invalid scores.

Для DoRA repeat2bitwise; полное native removeD на8forward и8generation;
две source V/O gauge c=.995/1.005 на первых2forward только, чтобы принять
численную допустимость без полного повторного no-op прогона. Gauge sourceRMS
<1%meanremoveD RMS и восстановление native побитно. Native/dense контроль
только2forward, бездополнительнойgeneration. Чужиепроцессы/репозиториине трогать.

Downloads max_workers2, anonymous tokenFalse. Измерить download/load/attach/
forward/generation time отдельно, peakRSS. Deadline30min(неETA). На pilot
GPU0часов. После приёмки сохранить версии, пути(private), source/case/codehashes.
Не делать статистику по8smokecases и не предполагать превосходство DoRA.
Дальнейший научный протокол фиксируется отдельно; этот pilot его не разрешает.
