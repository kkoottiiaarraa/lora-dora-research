# Технический pilot принят: SmolLM2-B

14 октября2026. После tokenizer compatibility fix завершились40forward rows
и32greedy generations на8author-validation cases. Все веса/source/configs
проверены; LoRA256иDoRA384savedtensorsточносовпалипослезагрузки,
128QKVOmodules,r16/alpha32/scaling2. Все parameters CPUFP32finite.
Три tokenizers имеют одинаковые vocab49152/specialIDs/template. GoldID — один
токен с проверенной full-conversation boundary для всех8cases.

Native repeat/restoration bitwise. Sourcegauges RMS6.37e−6/6.23e−6,
dense-control6.65e−6 против removeD RMS.043203: controlfloor<=.0155%effect,
существенно ниже gate1%. Это техническая допустимость вмешательств, не научный
результат о значимости компонентов.

Smoke правильных ответов: base1/8,LoRA6/8,DoRA6/8,removeD6/8.
GoldNLL3.68198/.995143/1.009495/1.017512 соответственно. Не делать выводов о
превосходстве/равенстве методов или необходимости D из восьми примеров.
Авторская validation51%уобоих относится ко100cases и здесь не воспроизведена.

CPU8 wall62.16s, peakRSS3.725GiB,GPU0часов. Base loads.26–.40s,
adapterattach+exactverifyLoRA.221s/DoRA.321s. Суммарные8forwards:
base5.15s,LoRA5.31s,DoRA6.03s,removeD5.00s; generation6.44/5.81/7.27/5.55s.
Измерения зависят от prompt lengths и текущей CPUнагрузки, не GPUforecast.
Downloadonly70.92s отдельно; failedsetup3.51sдоmodels/outputs.
Workers terminal, модели/RAM освобождены, очередейGPUнет.

Версии/source/case hashes: [pilot-validation.json](pilot-validation.json);
построчные compact результаты: [pilot-cases.csv](pilot-cases.csv).
Private raw/locators: local-only/smollm-pilot-results-20261014/ и
local-only/smollm-pilot-20261014-private.json. Полный авторский prompt и
operational identifiers в Git не копируются. Следующий этап — научная
спецификация с prior search и audit author splits до новой полной оценки.
Агенты/обучение не использовались, статью пока не пишем.
