# У опубликованных адаптеров различается не только архитектура

Обнаружено конкретное различие: у PeRL все сохранённые magnitude совпадают с
округлёнными исходными нормами; у трёх наших Qwen это практически никогда не так.
Следовательно, название DoRA не гарантирует наблюдаемое обучение обеих компонент.
Это ограничение механистической интерпретации готовых весов, не вывод о качестве.

| Готовый адаптер | m storage | Совпадение с rounded norm(base) |
|---|---|---:|
| Qwen4B/GSM8K | FP32 | 0.00128% |
| Qwen4B/MMLU | FP32 | 0% |
| Qwen4B/SQuADv2 | FP32 | 0.000319% |
| Mistral7B/r16 | BF16 | 99.99275% |
| PeRL1.5B steps64/512/1024 | BF16 | 100% на каждом |

PeRL:645120coordinates/196modules, все значения также bitwise одинаковы
между тремя опубликованными шагами. Это сильнее сравнения одного endpoint,
но не наблюдение каждого optimizer step. Mistral:786432coordinates/160modules,
только57 отличаются от CPU reference; maximum relative residual0.755%
по масштабу сопоставим с BF16 округлением;
не объявлять их57 реально обучившимися координатами: другие reduction order,
initialization backend или неизвестная training base могут объяснить различие.
Сравнение CPU native-BF16 norm и FP32norm→BF16 здесь дало одинаковые counts.
Qwen:313344coordinates/144modules накаждый, maximum relative residual против
rounded norm 9.20/10.84/16.98%; это явно больше одного округления.

## Что меняется в научной интерпретации

Пусть U=W0+sBA, source W'=diag(m/||U||)U.
Удаление D даёт U. Оно удаляет **и learned magnitude, и direction normalization**.
Возврат m к initial stored magnitude — другое вмешательство.
У PeRL возврат к rounded m0 оставляет все weights точно теми же: новых forwards
для доказательства этого не нужно. Но возврат к **FP32** norm(W0) меняет rounding,
поэтому такой контраст нельзя называть удалением обученного m в этом случае.
Наш trajectory screen сохраняет имя `base_magnitude` как formula label,
однако для PeRL интерпретирует его как rounding counterfactual.

Объяснять прошлую малую реакцию Qwen отсутствием learned magnitude не получилось:
их m заметно отличаются от обоих initialization references. Переносить
механистическое объяснение Qwen на Mistral/PeRL без этой оговорки нельзя.
Само наличие fixed m не делает DoRA обычной LoRA: normalization сохраняется.
И наоборот, разница между семействами не доказывает, что precision вызвала
разницу качества, gauge response или optimization trajectory.

## Что уже известно и чего этот audit не доказывает

[DoRAFactors](https://sockeye44.github.io/dorafactors-docs/how-it-works/)
прямо требует FP32 magnitude и обсуждает округление gain около1.
[Scaling DoRA](https://arxiv.org/abs/2603.22276) также рассматривает precision
коррекций. Новизну общего low-precision freeze не заявляем. Наши данные —
artifact-specific проверка применимости объяснений на реально выбранных весах.
Без master weights/optimizer logs нельзя доказать отсутствие промежуточных
изменений, ненулевых gradients или установить training cause.

4existing adapters read-only CPU2 audit12.23s, GPU0/model-forwards0;
предыдущий проход11.06s сохранён отдельно. PeRL read-only audit2.30s.
Полные counts, revisions, adapter-file SHA и per-module rows в audit.json;
PeRL в соседней trajectory папке. Operational manifests вне Git.
Это полезный результат, но сам по себе не устанавливает материал уровня B.
