# Запущенный Qwen compression screen

13 октября2026. Пользователь явно разрешил подготовить и запустить согласованный
план. Один CPUFP32 процесс на вычислительном сервере, четыре потока, nice5,
CUDA_VISIBLE_DEVICES пуст. GPU не занимает, включая исключённую карту.
Обучения, новых downloads и Mistral прогона нет. Точные deployment paths приватны.

## Зафиксированный состав

- Pilot:4примера, V/O слоя0. Screen:64примера, V/O слоёв0/17/35.
- Во всех случаях c=1/.995/1.005, target rank32. Gauge применяется **только
  к выбранным V/O парам**, остальные слои/модули остаются native DoRA.
  Это явное уточнение области к плану; симметрия допустима независимо в каждом слое.
- Входы — те же frozen64train×32gold-prefix positions предыдущего аудита,
  без test, новых calibration selections и свободной генерации.
- База Qwen/Qwen3-4B@1cfa9a7208912126459214e8b04321603b3df60c;
  DoRA shadow-llm/Qwen3-4B-GSM8k-DoRA@07f6a59c2ab6b36b1cecb5feb66187638202521d.
- Pilot и screen находятся в одном процессе; переход к64 происходит только
  после технического успеха pilot. Практический gate на4примерах не используется
  для отмены64: основной тест охватывает ещё два заранее выбранных слоя.

Сохраняются original, native gauge, source-dense reconstruction, factorized C32
и compressed-dense контроль. Полные native gauge/dense/C32 comparisons на64;
compressed dense против factorized — только4примера для каждого c.
Original logits переиспользуются из FP32 аудита **только** при тех же версиях,
revisions/input hashes и побитном совпадении4свежих forwards; иначе пересчитываются.
Результаты, полученные из кэша, помечены явно; повторный64original forward не нужен.

C32 вычисляется как base(x)+left(right(x)), с реальными rank32 factors.
Сначала SVD полного delta=W−W0 в FP32, затем left=U32*sqrt(S32),
right=sqrt(S32)*Vh32. Измеряются оба произведения и их расхождение с плотной формой.
Глобального dense merge всей модели нет: компрессируются только указанные модули.
Всего18SVD; результаты слоя0 переиспользуются междуpilot/screen.

## Технические и научные gates

1. Полное точное соответствие загруженного adapter и144модулям. Все параметры
   действительно CPUFP32, bias-free модель,36слоёв; outputs/spectra конечны.
2. Source gauge и source-dense residual mean RMS каждый ≤1% среднего FP32
   эффекта полного removeD из предыдущего frozen аудита (.06072994768).
   Это practical fidelity screen, не универсальная error guarantee.
3. Остаточная Frobenius energy после truncation согласуется с SVD tail.
4. Factorized/dense compressed mean RMS на4примерах ≤max(1e−5,1% среднего
   действия соответствующего C32). При провале остановка, а не scientific result.
5. Исходные adapter parameters и native модули восстанавливаются после каждого c;
   исходные tensors повторно проверяются по adapter checkpoint.
6. Практический gate для каждого c≠1: drift(C32(S_c),C32) >10×native gauge RMS
   **и** >20% RMS исходного C32. Публиковать оба результата, не подбиратьc.
   Все case metrics, KL/NLL/argmax/max/RMS и E95/E99 spectra сохраняются.

Rank32 здесь уменьшает ранг **полного** delta, но исходная DoRA уже хранится
как rank32 A/B плюс magnitude. Поэтому экономия относительно native adapter
в этом тесте в основном ограничена magnitude; сравнение с размером плотного
delta не означает большого выигрыша по размеру адаптера. Сохраняются реальные
source A/B/m elements и target factor elements. RSS эксперимента с временными
копиями/кэшами не является измерением VRAM/latency оптимизированного deployment.

## Проверки, ограничения расхода и продолжение

До запуска прошли4CPU unit tests: строгие границы gate/NaN/нулевой denominator,
аналитический diagonal SVD optimum, фактический factorized execution без dense
update, tiny Qwen3/DoRA scope/full-rank fidelity и точное восстановление приexception.
Код: lora_dora_study/compression_audit.py,
execution/next-experiments/compression_audit.py, tests/test_compression_audit.py.
Заморожены SHA256 этих файлов, зависимостей, cases/reference summary и64cache files.
Версии должны совпасть с аудитом: torch2.5.1+cu121, transformers4.57.1,
peft0.17.1, safetensors0.6.2, accelerate1.11.0.

CPU бюджет14400с; внешний watchdog14460с с kill-after30с. Это защитный cap,
не план расходовать4часа. По предыдущему FP32 аудиту native forward≈8.8с/case,
новый тест содержит572свежих forwards плюс18SVD и дополнительные metrics;
начальный ориентир около1–1.5часа, уточнять по фактическому pilot.
Текущий run не добавляет GPU-часов. Большие caches остаются на сервере внеGit.

После завершения: принять полноту и gates, проверить практическую величину
drift и связь с E99 decisions. Успешный screen допускает проектирование исправления,
но не запускает автоматически другую модель, полную генерацию или grid.

Живая проверка14:40МСК:4свежихoriginal outputs побитно совпали сreference;
c=1 pilot source-dense RMS8.26e−6, factor-dense RMS8.48e−6, gatesPASS.
Следующее pilot условие выполняется. Реальные4-case forwards≈35.6–35.8с;
уточнённый предварительный конец16:00–16:20МСК, ещё не замер полного pilot.

Завершение подтверждено16:01МСК: wall5028.64с, все technical gatesPASS,
18SVD, оба full64 practical gatesPASS. См.screen-status.json.
Детальный научный разбор и исправление ещё не выполнены; новых runs нет.
