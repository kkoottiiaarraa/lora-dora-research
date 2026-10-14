# Разделение численного пути абляции: короткий screen

14 октября2026, до новых outputs. Основание: прежний64-case аудит одновременно
менял CPU/FP32 на CUDA/BF16, поэтому не установил причину изменения removeD.
[Scaling DoRA](https://arxiv.org/html/2603.22276v1) уже рассматривает near-unity
масштабы и устойчивую композицию; мы не изобретаем kernel и не объявляем общий
факт чувствительности BF16 новой идеей. Проверяется содержательный контраст
вмешательства при явно заданном численном пути.

## Три клетки и четыре условия

Восемь OLD calibration вопросов, первые32gold-tokens, EXACT как byte-budget
screen; это development/engineering, не новый тест или task accuracy.

- CPU FP32 transformer.
- CUDA FP32 transformer.
- CUDA BF16 base/activations + FP32 PEFT adapter (обычный mixed contract).

Во всех трёх клетках embedding lookup и lm_head выполняются на CPU FP32.
Embedding после lookup явно переводится в dtype/device transformer.
Это экономит GPU память и держит выходной head одинаковым. У исходной базы
сохранённые BF16 веса точно представлены FP32. GPU/CPU сравнение относится
к transformer, не ко всем операциям сети. CPU BF16 не запускается: сервер
не имеет AVX512_BF16/AMX_BF16. Это треугольный дизайн, не полный2×2factorial:
отдельно можно оценить precision contrast наCUDA и backend contrast приFP32,
но не произвольное взаимодействие dtype×backend.

В каждой клетке четыре условия: native source, native removeD, dense source,
dense removeD. Считаем paired ΔNLL относительно source **своего** представления,
а также цену native→dense source и ошибочно смешанного контраста для диагностики.
Не утверждать, что старые результаты использовали смешанный путь, без аудита
конкретного старого runner. Все source parameters и PEFT casts документировать.

Dense weight вычисляется через effective_weight в FP32, затем приводится
к dtype базы. Слияние streaming по одному модулю, чтобы не держать второй
набор всех проекций в VRAM. Официальный PEFT merge — byte/fidelity control:
отдельная загрузка, все144projection hashes и первые2logits должны совпасть
с custom. Повтор source и восстановление после without_d — bitwise controls.
Native CPUFP32 первые4 соответствуют старым cached outputs.

Критерий screen: mean ablation ΔNLL меняется между matched представлениями
или точностями на >max(.001nat/token, .5*abs(CPUFP32nativecontrast)).
Знак и все значения публиковать;8casesне дают значимости. Прохождение требует
отдельного fresh-case протокола перед научным выводом; при отрицательном
результате не расширять клеток/точностей/слоёв. Разница logits сама по себе
недостаточна. FP32 native/dense RMS floor <1%FP32 native removeD RMS;
для BF16 не притворяться, что native/dense различие — функциональный no-op.

## Исполнение

До большой модели meaningful tiny Qwen3/PEFT CPU tests: offload wrappers,
FP32 эквивалентность, native restoration, official/custom dense bytes.
Одна GPU, GPU1исключена. Повторно используем admission controller:2свободные
проверки через10s, util<20%, memoryused<7GiB и дополнительно free>=14GiB
для этогоFP32pilot. Частично занятая карта разрешена пользователем;
не трогать чужие процессы. Никакого удержания после GPUфазы: процесс заканчивает
обаCUDAусловия, карта освобождается, CPUфаза идёт отдельным процессом.
Защитные пределы GPU30мин/CPU20мин, это не ETA. Canary GPU→CPU readback
и checks конечности; при сбое остановить только свой процесс, сохранить ошибку.
Короткая проверка не обучает модель и не обещает готовый материал уровняB.
