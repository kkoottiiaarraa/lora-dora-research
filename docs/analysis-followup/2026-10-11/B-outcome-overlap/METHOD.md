# Метод пакета B: совместная правильность ответов

Этап exploratory: условия выбраны после просмотра прежних данных. Используется
одна фиксированная пара checkpoints GSM8K и сохранённые 1319 test examples;
весов, обучения, установок, p-values, CI или subgroup search здесь нет.

Вход per_example_scores.csv.gz проверяется по SHA256 frozen bundle; выбранные
baseline/intervention таблицы также сверены с ним. Принятые paired-outcome и
compression-original таблицы сверены с analysis-manifest.json. Перед расчётом
проверены уникальность и полнота test_row_index 0..1318, binary scores и совпадение
source_id/prompt_sha256/input_ids_sha256 всех восьми run IDs и обоих scorers.
Хеши входных manifest сохраняются, но они не заменяют внешнюю доверенную подпись.

Единый reference repairs/breaks — gsm8k-quality-greedy/dora (original PEFT DoRA),
включая r32/e95/e99. Dense DoRA — явный численный контроль. Исторические SVD
переходы от dense проверяются отдельно, с их actual_reference, и не переносятся
в summary от original. LoRA — отдельно обученный опубликованный checkpoint,
не remove_D и не дополнительный seed. Здесь нет оценки training uncertainty.

repair_i = (original_i=0, run_i=1), break_i = (original_i=1, run_i=0);
changed-correctness = repair ∪ break. Summary даёт counts, score, разницу к
original и условные rates repair/original_wrong, break/original_correct.
Pairwise содержит четыре совместных исхода для всех 28 пар на scorer;
названия correct_to_wrong и wrong_to_correct читаются слева направо.
difference = right_score − left_score = (wrong_to_correct−correct_to_wrong)/1319.
Порядок пар фиксирован порядком run IDs ниже, а не величиной эффекта.

Overlap содержит все 21 пары non-original условий на scorer: для repairs,
breaks и changed-correctness показаны размеры обоих множеств, intersection,
union, Jaccard=intersection/union и intersection/размер каждого множества.
При нулевом знаменателе записывается literal undefined. Нулевой union не
подменяется единицей; условные доли также undefined при пустом множестве.
Все показатели описательные, без inferential тестов и поправок.

case-patterns.csv.gz содержит 2638 строк (1319×2): metric, aligned IDs/hashes
и 8-битный correctness_vector. Текстов ответов нет. Позиции битов:
1. original_DoRA: `gsm8k-quality-greedy/dora`
2. trained_LoRA: `gsm8k-quality-greedy/lora`
3. dense_DoRA: `gsm8k-dense-dora/dora`
4. remove_D_all: `gsm8k-remove_d-all/dora`
5. base_magnitude_all: `gsm8k-base_magnitude-all/dora`
6. r32: `gsm8k-r32/dora`
7. e95: `gsm8k-e95/dora`
8. e99: `gsm8k-e99/dora`

Упаковка gzip детерминирована (mtime=0). Seeds не используются: расчёты
детерминированны, resampling отсутствует. Код запускается существующей venv
входные проверки, расчёты и запись таблиц/отчётов до финальной validation.

Проверки: hashes, alignment/binary/full N, saved marginals и transitions,
все pairwise маргинальные суммы, identities множеств, пустой union, обратное
восстановление vectors из case-patterns и чтение сжатой таблицы. Выбранные
неизменяемые входы повторно хешируются после записи результатов.

Ограничения: совпадение correctness не означает совпадение текстов, logits или
функции. Пересечение repairs/breaks не устанавливает общий механизм, смысловую
причину изменений, специфику D или необходимость компонента при обучении.
Нет сравнения норм вмешательств как причинного доказательства. Выводы ограничены
этими checkpoints, фиксированным evaluation и scorers; строки теста и матрицы
не являются независимыми обучениями. Текущий пакет не является текстом статьи.
