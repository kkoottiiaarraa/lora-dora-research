# Ограниченная проверка знаменателя DoRA на CUDA

Дополнение к SPEC.md, 11 октября 2026. CPU proxy не устанавливает реальные
CUDA-значения коэффициента g. Пользователь разрешил корректировать план и
использовать частично занятые GPU; этот короткий контроль закрывает точность
знаменателя, без полного forward модели, генерации или обучения.

## Задача и границы

Агент gpt-6.1-sol/high реализует отдельный
execution/radial-activity/probe_cuda_norm.py. Не редактировать CPU script,
исторический evaluator или frozen artifacts. Использовать уже скачанные
GSM8K веса и pinned config/manifest из SPEC/INVENTORY. Проверить их SHA256,
144 набора A/B/m и dtype/shape; scale=1. Никаких скачиваний/установок.

Сначала tiny toy и4 модуля первого слоя; при успехе144 последовательно.
Одна GPU через CUDA_VISIBLE_DEVICES до import torch, максимум2 CPU threads.
Перед запуском проверить nvidia-smi; использовать карту с >=4GiB свободной
памяти, предпочтительно5 при сохраняющемся запасе. Запуск не запрещён при
чужом compute process (явное разрешение пользователя), чужие процессы не
трогать. Проверить известные scheduler/allocation правила; если обнаружено
обязательное распределение, соблюдать. Без фонового удержания карты; выйти
сразу по завершении, записать освобождение своей памяти.

Пиковый VRAM ориентировочно <1GiB; установить ограничение allocator2GiB и
прервать свой процесс при превышении бюджета или изменившемся запасе перед
пилотом. Не продолжать при неизвестном состоянии устройства.

## Численная процедура

Прямой B@A не заменяет реальный путь. Под torch.autocast('cuda',BF16):
I=eye(in_features,dtype=FP32), L_id=F.linear(F.linear(I,A),B).T;
U_cuda=W_BF16.float()+L_id*1, n_cuda=rownorm(U_cuda) вFP32,
g_cuda=m_F32/n_cuda. Сохранить dtype каждой стадии и проверку против
установленного DoraLinearLayer.get_weight_norm. FP32sum/n/g не округлять.
Зафиксировать CUDA matmul/TF32/determinism/autocast/backend flags, GPU,
driver, Torch/CUDA/PEFT, hashes исходников. Настройки не менять ради результата.

Для каждой строки сравнить g_cuda с idealFP32(B@A) и CPU BF16 identity
surrogate из принятого CPU output (если он ещё не готов, временно сохранить
CUDA row arrays, выполнить join после готовности; ждать без GPU процесса).
РезультатCPUjoin не вычислять на VM. Ненулевой/finite знаменатель проверять
без eps/clamp; m=0 отдельно flag, relative g errors тогда null.

Пер module/all/Q/K/V/O сохранить: rows; g==1, g<1/g>1, m==0;
min/median/p90/p99/max abs(g-1), signed g-1; CUDA-vsCPU/ideal absolute и
relative ошибки, sign-crossings относительно1; BF16(g)==1 отдельно как
контрфактический cast. Глобальные quantiles из всех строк, не modulemedians.
Добавить ||(g_cuda-1)U_cuda||/||g_cuda U_cuda-W0|| из суммsquares и
аналогичный numerator/denominator ideal reference; отличие нормы коэффициента
не подменять эффектом на функцию. Сравнение с fixedbaseNorm endpoint отдельно
от неизвестного training initializer. Без p-values по строкам/модулям.

## Выходы и приёмка

Новые compact файлы только в docs/diagnostics/radial-activity-2026-10-11/:
cuda-module-activity.csv(144), cuda-group-activity.csv(5),
cuda-validation.json, cuda-manifest.json, cuda-resource-use.json,
CUDA_METHOD.md. Сырые rows/logs только на сервере; указать пути/hash.
Манифест включает code/spec/input/library/output hashes без циклов.
Файлы CPU package не менять. Mirror compact outputs и свой код локально.
Разрешено зеркалировать root SPEC/INVENTORY/PRECISION_REVIEW/этот addendum
на сервер исключительно в новой diagnostic папке.

Toy g=1 и known g scaling;4module pilot проверяет dtype/finite/sourcehash,
сверку n с установленным PEFT, VRAM budget, timings. Сообщить root пилотные
измерения до полного144run. Идентичные pilot/fullrows должны совпадать с
допуском, обозначенным по precision, не под результат. Сохранить время
CUDA tensors отдельно от CPU join/hash/IO; GPU-seconds не называть всем
временем процесса. Норма-only проверка не устанавливает logits/quality,
численное равенство полной функции или причину обучения.
