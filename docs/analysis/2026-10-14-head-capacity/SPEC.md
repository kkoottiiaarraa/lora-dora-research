# Screen на сохранённых активациях, до outputs

14 октября2026. Только готовая Qwen3-4B/GSM8K DoRA, source-r32.
Фиксированные слои0/17/35 и головы0/15/31: **9 голов**, не вся модель.
O-projection shape2560×4096,32queryheads×128. Используем уже сохранённые
2048 O-input rows из64OLDcalibration вопросов, без нового inference.
Важно: capture summary cases_sha256 обозначает отдельные32development cases;
активации были собраны именно на original calibration_cases, чей hash надо
взять из исходного manifest. Сохранить эту provenance раздельно.

Теория и limitations: [METHOD](METHOD.md). Считать:

- source head energy; энергию projection вне col(O0_h); tail после r32;
- tail/source energy и tail/outside energy; весь спектр128 значений;
- no-D O0+BA контроль с той же таблицей head inputs;
- повтор source gauge c=.995/1.005 с компенсацией O/c и X*c;
- floor от FP32 merged weight versus FP64 formula из тех же saved coefficients.

FP64 direction и row norm строятся заново из saved W0/A/B и исходного
magnitude m, прочитанного из pinned adapter safetensors. FP32 D изcapture
не подменяет исходный m. FP64 QR/eigh/SVD, CPU4, CUDA hidden, deadline15min. Перед настоящими файлами
два meaningful tiny теста: DoRA diagonal действительно создаёт rank>r outside
space, LoRA control его не создаёт; gauge не меняет output spectrum/bound.
Проверить exact module/capture hashes, inputs shape, finiteness и coverage.

Критерий **существенности для продолжения**, не статистический тест:
минимум3из9голов имеют одновременно tail/source>=1e−6,
tail/outside>=.05 и tail>=1000×FP32mergefloor. No-D tail/source<=1e−20;
gauge relative bound change<=1e−10. Все9publish, не выбирать лучший слой/голову.
При failed practical gate закрыть эту конкретную локальную гипотезу без
поиска новых голов/ranks. При success прежде новых model runs проверить,
что локальная граница ведёт к полезному вопросу, а не только новой таблице.
Это не доказательство превосходства DoRA, невозможности global LoRA match
или причин обучающей траектории. Никого не обучаем, GPU не занимаем.
