# Проверка, чему соответствует сохранённая magnitude

Предпосылка найдена при PeRL audit: все645120 сохранённых m равны между
steps64/512/1024 и rounded base norms. Проверить существующие три основных
Qwen adapters и уже имеющийся Mistral-r16, без новых models/forwards/training.

Для каждой magnitude coordinate сравнить exact значения с двумя вычислениями:
FP32 norm(base) и этой norm, округлённой к dtype исходной base weight.
Также учесть dtype сохранённого m. Полные per-module counts/relative residuals.
Это проверка сохранённых весов, не optimizer state: exact agreement с rounded
initialization не доказывает отсутствия transient/master-weight changes.
Совпадение только конечных m не равнозначно наблюдаемой траектории PeRL.
Не выводить universal cause или качество из совпадений. Не включать Qwen8B.

Проверить объяснения перед новой гипотезой:
[DoRAFactors precision contract](https://sockeye44.github.io/dorafactors-docs/how-it-works/)
уже описывает проблему округления near-unity gain;
[Scaling DoRA](https://arxiv.org/abs/2603.22276) сохраняет FP32 intermediates.
Не выдавать стандартную BF16 арифметику за новый алгоритм.
