# Qwen3-8B на двух GPU и обновлённые прогнозы

Пользователь явно изменил общий лимит с 3 на **5 GPU на время Qwen3-8B**.
Это разрешённое исключение к прежнему AGENTS.md. После завершения двух-GPU
очереди её карты/слоты освобождаются; оставшиеся три очереди работают в лимите3.
Первая 4B оценка и её исходный evaluator/HEAD93cd828 не менялись.

Изолированный checkout GPU: /path/to/user-user/lora-dora-dual, VM work/lora-dora-dual.
Новая serial очередь только для двух существующих Qwen3-8B пар: GSM8K, затем
SQuAD v2; для каждой base/LoRA/DoRA, сначала smoke2, затем полный split.
BF16, batch1, greedy, input512, generation256 GSM8K/32 SQuAD, use_cache=False.
Никакого обучения, квантизации или CPU offload. Явная contiguous layer device_map:
embedding + первая половина decoder на cuda0; вторая половина + norm/head на
cuda1. Число слоёв берётся из pinned config. Проверяются все layer/adapter
parameter devices, exact saved-adapter tensor values и отдельные пики обеих GPU.
Реальный двухкарточный inference ещё не выполнялся: сначала assets, затем idle
pair, затем smoke; CPU tests не являются GPU успешным запуском.

Ожидание каждые10s: одна и та же пара должна быть свободна две проверки подряд,
без compute processes, <=1024MiB, <=10% utilization. GPU UUID locks берутся
для обеих карт сразу через ExitStack; любая ошибка освобождает весь частичный
захват. Нельзя держать одну карту, ожидая вторую. После захвата fresh nvidia-smi,
проверка обеих карт и два постоянных CUDA keeper contexts. Общие kernel slots
3/4 выделены только Qwen8B; старые очереди продолжают использовать0/1/2.
Это даёт максимум5 GPU вместе с удержанием между заданиями. Worker наследует
оба GPU и оба slot descriptors; guard исключает только проверенного direct-parent
keeper, сохраняя отказ при чужом процессе. Внутри очереди повторного idle wait
или смены карт нет. Ошибка останавливает очередь для разбора.

Новая очередь PID3743149, results/qwen8b-two-gpu/state.json; журнал
results/qwen8b-queue.log. Downloader PID3740640, results/qwen8b-download-state.json
и results/qwen8b-download.log. На 21:14МСК09.10 статус waiting_for_downloads;
GPU ещё не захвачены. Download max_workers2, только на GPU-сервер; база кешируется
один раз, повторный lookup и SHA verification для второй пары. Измерения download,
load/adapter/inference/RSS/per-GPU allocated/reserved раздельно.
Base revision b968826d9c46dd6066d109eabc6255188de91218. Adapter revisions из
checkpoint_inventory.json: GSM8K LoRA0ecc88a7f623f500cf0ea7f754b1c96280ed3647,
DoRA5e435461f6a2008dbde29b7624f2fa18b10f9660; SQuAD LoRAeed99fb0c206d9e7814d20c2655ec9670ece3eee,
DoRAecb67d5f30e8ad2308e87386d2d0c534667a523e. Manifest configs/shadow_8b_*.json
с размерами/LFS SHA; план configs/qwen8b_two_gpu.json записывается после assets.
Большие results остаются на GPU: results/qwen8b-two-gpu/jobs/<pair-id>/.

Обе8B пары удалены из старых двух очередей. Дополнительная1 PID3736760 начинает
MMLU/4B, дополнительная2 PID3736761 — SQuAD/4B. Ожидание из-за старого лимита3
снято. Обе сейчас ждут только первоначальной свободной карты, потом удерживают
её до завершения очереди. Оставшиеся пять main-pair jobs AnswerAI/LLaVA требуют
loader/access работы; резервные Mistral/PeRL не добавлялись.

CPU: 32 tests passed, results/cpu-dual-tests.log, существующая venv без установок.
Новые4 tests: stable same pair, complete contiguous map, old3+new2/sixth refusal,
rollback при занятой второй карте. Версии Python3.12.3 torch2.5.1+cu121,
transformers4.57.1 peft0.17.1 accelerate1.11.0 safetensors0.6.2.

Прогноз 21:14МСК09.10.2026, исключает ожидание карт и downloads:
- Original base421/1319, 11.833s/example на сотнях реальных примеров: ещё2.95h.
- Весь original baseline (remaining base + LoRA + DoRA):11–18h. LoRA/DoRA пока
  только smoke2, поэтому это диапазон прогноза, а не измеренный full runtime.
- Первая очередь вместе с22 posthoc jobs:96–168h (~4–7 суток). Центральный
  бюджет складывается из8 native DoRA оценок (no-op+7base magnitude),7 remove-D
  и7 dense/rank/symmetry/control; все по1319 и выполняются последовательно.
- Дополнительная1 готовая часть MMLU:3–8h; центральный proxy5h.
- Дополнительная2 готовая часть SQuAD:6–16h; центральный proxy11h.
- Полные proxy budgets старых дополнительных очередей после удаления8B:47h/39h
  (5h+3*14h и11h+2*14h). Это НЕ надёжный ETA: custom loaders/HF access ещё
  не готовы и14h на каждую такую пару не подтверждены measured inference.
  Прежние69h/59h включали8B и заменены этими отдельными бюджетами.
- Новый8B запуск: GSM8K20–35h, SQuAD15–30h, суммарно35–65h (~1.5–3 суток).
  Это extrapolation от4B, не measured8B timing. Две карты обеспечивают память;
  последовательное шардирование не обещает двукратного ускорения.
Численные параметры и срез источника: results/time-forecast.json.
После первого8B smoke и каждого full stage прогноз пересчитать по actual tokens/s.
Влияние одновременной работы5 карт на CPU/RAM/I/O пока не измерено.

HF access: текущая проверка обеих Meta баз дала401 GatedRepoError. Пользователю
нужно в своём HF аккаунте отправить запрос на страницах meta-llama/Llama-2-7b-hf
и meta-llama/Meta-Llama-3-8B, принять условия Meta, дождаться granted access.
Затем создать read-only token https://huggingface.co/settings/tokens и в терминале
Токен вводится интерактивно без --token в командной строке; Git credentials n.
Пароль/токен в чат, код или Git не присылать. После «готово» агент проверяет
config download обеих gated моделей, не читая/печатая содержимое token storage.
Регистрация сама по себе и один password не дают разрешения на gated weights.

Следующий шаг: проверить downloads/queue liveness; после двух свободных карт
проверить actual sharding/adapter values/VRAM на smoke, исправить runtime errors;
полная identical quality на обоих8B benchmarks. Исходную4B evaluation не менять.
После HF готовности — повторно проверить доступ и продолжить custom AnswerAI loaders.
