## 2026-10-14 — передача репозитория следующему агенту

По новому указанию пользователя подготовлены публикация научных материалов
и навигация; это не возобновление исследования. [README](../README.md) описывает
цель, состояние и структуру; [RESEARCH_NAVIGATOR](RESEARCH_NAVIGATOR.md) связывает
проверенные гипотезы, отрицательные исходы, литературу, код и условия пересмотра.
AGENTS обновлён: устаревшие first-pilot/three-GPU инструкции больше не являются
текущим заданием. Последний научный checkpoint — pause/RESUME и RESULTS_AUDIT.

В публикацию включаются накопленные отчёты, компактные данные, реализации и tests,
в том числе неудавшиеся идеи. Приватные сведения о доступе, operational locators,
локальные архивы и веса остаются внеGit. Ветка передачи research/two-extra-series;
точный commit смотреть вGit. Проверки перед публикацией:95локальныхссылокPASS,
175PythonfilesASTPASS, diff-checkPASS(сохраненыCSVCRLF/историческиеEOF). Текстовыефайлы, gzipтаблицы и исходящий
rootcommit проверены на private infrastructure/token/key patterns: совпаденийнет.
Единственныйbinary — неизменённыйpublicDoRApdf; егоstreamsпровереныотдельно.
Следующий шаг для
нового агента — чтение навигатора; вычисления требуют явного возобновления.

## 2026-10-14 — ПАУЗА ПО ПРЯМОМУ УКАЗАНИЮ ПОЛЬЗОВАТЕЛЯ

Исследование остановлено. Новые модели/вычисления/скачивания/очереди/письма/
агентов не запускать до нового указания продолжить. Работают только операции
сохранения и документации этой контрольной точки; научные workers завершены.
Два старых служебных CPUмонитора нашего исследования остановлены; holders и
активных исследовательских GPUработ нет. Private запись остановки внеGit.

Главная точка входа: [RESUME](research-direction/2026-10-14-pause/RESUME.md).
Полный [RESULTS_AUDIT](research-direction/2026-10-14-pause/RESULTS_AUDIT.md)
сохраняет positive/negative/inconclusive результаты, ссылки, границы claims,
неудавшиеся идеи и условия их пересмотра. Отдельно отмечено различие Mistralr32
validation и Mistralr16 magnitudeaudit. Не связывать их причинным объяснением.

Очистка: удалены только4__pycache__ dirs,69regenerable.pyc files (~.78MiB).
Ни source, ниtests, ниreports/raw scientific evidence/failed candidates не удалены.
Незакоммиченные tracked/untracked исследования сохранены; snapshot/diff/status
в outerlocal-only/pause-audit-20261014. Не принимать untracked results за мусор.
Commit/push/переписываниеGitистории в этом запросе не выполнялись.

Материал: законченная содержательная курсовая реалистична; база для бакалаврской
ВКР поML есть, но нужны единая постановка, собственный вклад, воспроизводимая
выборка и оформление. Это экспертная оценка, не решениеМКН/руководителя.
Научный механизм DoRA/новыйлучшийcompressor/готоваяконференционнаяBстатья
не получены. Подробности и источники в audit. Никакого автоматического продолжения.

## 2026-10-14 — объединённый component/decision screen завершён, обаgatesFAIL

[REPORT](analysis/2026-10-14-component-decision/REPORT.md), SPEC/PRIOR,
development/validation.json и полные компактныеrows/controls/factors сохранены.
8OLDcalibrationquestions×6conditions=48rows; CPU8FP32wall252.67s/peak24.06GiB,
GPU0. Exact432tensors/144modules,17controlsPASS(maxRMS1.63e−5, floor<.080%),
nativerepeat/restorationbitwise.2tinytestsPASSдоadmission.

TeacherKL removeD=.00017058; resetMFP32=.00022575; removeNFP32=.00002350;
resetMrounded=.00021134; removeNrounded=.00004914. Все<заданногоbudget.001.
Primaryfalse-permissiongateFAIL, secondarystrongcancellationgateFAIL.
LogL/Ncosine−.130; logD/separateenergy=.955: неalmostcompletecancellation.
Большиеmaxmchangesнеозначаютбольшогоtypicaleffect; RMSlogL~.385%.

ПоSPECvalidation64/Mistralнеlaunch: нельзяпереоткрыватьthreshold/gridпослеFAIL.
Старыеfull1319qualityпереиспользованы, негонялисьзаново: resetM/removeDоба1038,
междуними31/31correctnessdiscordances. Этоoldcontext, неноваянаходка/confirmation.
DeLoRAappendixCпрочитанвprimaryarXivHTML: fixedmtraining/compensationужеизвестны;
нашendpointtestнеопровергаетtrainingmechanism/qualityadvantages.

ПрактическогоновогоwitnessуровняBнет; этотконкретныйcombinedscopeзакрытпоgate,
необъявлятьтемупринципиальноневозможной. Алгоритмнепереоткрыт: failureсильного
comparatorнеустановлен. Preparedconditionalfreshcaseaudit/validationcodeневызывался.
Всеworkers/sessionsзавершены, CPUmodelobjectsreleased, queues/holdersнет.
Private locator outerlocal-only/component-decision-20261014/locator-private.json.
Ниагентов/обучения/новыхweights/писем/commit/push. Следующийшаг — отдельныйновый
нерешённыйвопроссдоказаннымоснованием, нерасширениетогожеотрицательноготеста.

## 2026-10-14 — объединённая проверка component semantics / ablation decision

Latestuser: объединить2первыхнаправлениятирлиста, вернутьсясобщимрезультатом.
[Замороженный SPEC](analysis/2026-10-14-component-decision/SPEC.md): factorial
L=m/||W0||, N=||W0||/||U||; можетлиremoveDproxyошибочноразрешатьresetmagnitude
приteacherKLbudget.001? ОбаFP32/roundedreferences, глобальныесовместныеV/O,
нестарыйgaugerankinggrid. Native/dense/formula/gaugecontrols и2tinytestsPASS
доadmission. Old1319GSMaccuracyresetM/removeD переиспользуется, негонятьповторно.
CPU8development8oldcases×6conditionsRUNNING/GPU0. Еслиpositivegate — fixed64fresh
validationсindependentcaseaudit; иначеstopбезподборапорога. Mistralnegativecontrol
толькопослеpositivevalidation. Ниагентов/обучения/новыхweights/писем.
Private locator outerlocal-only/component-decision-20261014/locator-private.json.

## 2026-10-14 — весь ограниченный цикл SORA + неалгоритмические screens завершён

Latest user chain выполнен без агентов/обучения/писем: bounded SORA math screen,
затем downstream response и released PeRL trajectory, дополнительный targeted
stored-magnitude audit существующих Qwen/Mistral. Всеworkers terminal; holders/
waiters/GPUqueues нет; GPUhours0. Большие веса/logits только сервером.

Общий итог и решение: [CYCLE_REPORT](research-direction/2026-10-14-status/CYCLE_REPORT.md).
[PeRL REPORT](analysis/2026-10-14-perl-trajectory/REPORT.md):144rows/16questions,
3steps64/512/1024, exact588tensors/196modules, control/repeat/restore PASS.
CPU8wall324.68s/peak19.18GiB, download328.33s отдельно.
Normalized removeD role падает39.44x, absoluteKL~3.6e−5 почти постоянен;
transient/growth gates FAIL из-за заданного absolute-effectthreshold.
Не считать denominator-driven ratio падением абсолютной роли D.
645120storedm совпадаютbitwiseна3steps и с roundedinitialnorm: наблюдаемого
обучения сохранённогоm здесь нет. base_magnitude=FP32norm контраст здесь
rounding counterfactual; roundedinitialm возвращение было бы exactweightno-op.

[Magnitude audit REPORT](analysis/2026-10-14-magnitude-provenance/REPORT.md):
Qwen3pairsstoredmFP32 явно отличаются отinitialreferences, Mistralr16BF16
99.99275% совпадений с roundednorm; не доказывает precision-caused trainingfreeze.
Read-only2CPU/GPU0/forwards0,12.23s (предыдущий проход11.06s сохранён).
Не переносить Mistral/PeRL объяснение отсутствием m-motion на Qwen.

Compressor не переоткрыт: локализованного failure сильного comparator с
обоснованным новым исправлением не установлено. Отрицательные screens не
разрешают новый random grid. УровеньB не установлен, опубликованные quality
преимущества DoRA не опровергнуты. Продолжение: отдельный вопрос applicability
mechanistic claims по artifact precision/m-motion; для causal verification
нужны подходящие trajectory/optimizer artifacts, а не ещё mean-accuracy table.
Operational locators: outerlocal-only/downstream-response-20261014-private.json,
perl-trajectory-audit-20261014/locator-private.json,
magnitude-provenance-20261014/prepare.py. Gitcommit/push не выполнялись.

## 2026-10-14 — downstream screen завершён; PeRL trajectory preflight

[Downstream REPORT](analysis/2026-10-14-downstream-response/REPORT.md):
96rows/16cases, CPU8 wall365.86s/peak19.50GiB/GPU0, exact144modules,
repeat/restoration bitwise. Dose controls pass. Primary gate FAIL0/3layers:
last-layer D−gain attenuation+.160CI[.078,.252] ниже заданного.25;
early frozen effects numerical floor FAIL, не интерпретировать ratio.
Не расширять сетку; Mistral confirmation не запускается.

Следующий неалгоритмический [PeRL SPEC](analysis/2026-10-14-perl-trajectory/SPEC.md):
3published DoRA checkpoints64/512/1024, один реальныйlogged RLrun, identicalconfigs,
training histories exactprefix. Не сравнивать LR1e−5DoRA с LR5e−6LoRA какmatched.
Transient radial role vs oppositegrowth gate заморожены доoutputs.
Ungated1.5Bbase+3smalladapters download/verification сервером; никакихinstall,
training/GPU. Tiny Qwen2 biased-projection compatibility test до admission.
Private locator local-only/perl-trajectory-audit-20261014/.

## 2026-10-14 — малый SORA claim screen закрыт; начат неалгоритмический этап

Latest user: ограничить SORA math/loader branch, затем исследовать основные
неалгоритмические направления; вернуться к compressor только при локализованном
failure и обоснованном исправлении. Без агентов, обучения, писем авторам.
Вернуться с общим итогом, не останавливаться после первой части.

[CLAIM_SCREEN_REPORT](analysis/2026-10-14-sora-code-audit/CLAIM_SCREEN_REPORT.md):
restricted entropy theorem подтверждена; rank-only sufficiency counterexample
не опровергает её предпосылки. Weyl upper bound не даёт nonzero lower bound.
Theorem2 notation inconsistent, но corrected skew bound стандартен/верен;
code scaling не наследует его. Loader correction не имеет предсказуемого знака
accuracy. GLUE visible in-memory eval не попадает автоматически под reload bug;
Gemma/harness paths уязвимы. Stdlib CPU/GPU0, weights/training/contacts нет.
Нельзя объявлять всю статью опровергнутой. Эта ограниченная ветка закрыта.

Следующий stage: [downstream-response SPEC](analysis/2026-10-14-downstream-response/SPEC.md).
Qwen joint-VO removeD в blocks0/17/35 против dose-matched scalar attenuation,
8fit/16evaluation старых calibration cases, frozen-downstream/finalnorm controls.
Общий self-repair известен; проверяем D-specific difference. CPU8/cap20min,
без GPU/generation/алгоритма. Два tiny CPU tests passed до модельного запуска;
worker назначен после RAM preflight и frozen-source manifest. Private locator:
local-only/downstream-response-20261014-private.json. Следующий шаг — monitor
до terminal, проверить controls/gates и продолжить по условной развилке SPEC.

## 2026-10-14 — повторно проверен доступ к SORA артефактам, найден контакт

[ARTIFACT_ACCESS](analysis/2026-10-14-sora-code-audit/ARTIFACT_ACCESS.md):
официальные main/branches/releases/tags, final AAAI PDF/presentation,
персональный сайт автора и целевые HF metadata searches не дали готовых весов.
Не утверждать, что их нигде нет в интернете. Публичные email первого и
corresponding автора подтверждены первоисточниками; минимальный запрос — один
SORA DeBERTaV3-Base RTE/MRPC checkpoint с head/config/base revision/eval provenance.
Matched LoRA/DoRA и seeds нужны дополнительно для method-quality comparisons.

Письмо подготовлено вне Git: local-only/sora-artifact-request-draft-20261014.txt.
НЕ отправлено; внешних сообщений без отдельного указания пользователя нет.
DeBERTaV3-base HF API gated=false, текущий SHA в access note; не принимать
его за авторский trainingSHA. Без авторских весов можно продолжать формальный
аудит и independently reproduce обучение, но последнее запрещено текущим
условием пользователя. Ничего не обучали/не скачивали, compute/queues нет.
Предыдущая остановка — пауза соответствующей empirical ветки, не исчерпание
всех возможностей и не доказательство отсутствия перспектив. B не установлен.

## 2026-10-14 — source audit и SORA export/loader проверки завершены

[SORA REPORT](analysis/2026-10-14-sora-code-audit/REPORT.md): в pinned официальном
коде export возвращает KM вместо (I+K)M; initialization экспортируется в нулевой
вес. Tiny FP64 forward совпадает с независимой формулой до1.18e−16,
исправленный export совпадает, исходный unmerge не восстанавливает базу.
Это арифметика выбранных методов в явном harness, не full lifecycle certification.

Реальное сохранение/загрузка tiny checkpoint: обычный loader молча сохраняет
только A/B (2/5), proper custom mapping все5/5 точно. Ненулевой пример:
relative output error .195897 против0; initialization ошибку маскирует.
Повторено на неизменённом авторском PEFT0.14.1.dev0 и installed0.17.1;
124author Python files verifiedGitblobSHA1, безinstall, CPU2FP64/GPU0.
Scaling rule кода также не даёт near-orthogonality bound статьи; это synthetic
counterexample, не измерение learned факторов. Benchmark numbers не опровергнуты.
В проверенных eval paths merge нет, а custom SORA mapping отсутствует.

Revision `MaeChd/SORA@24f62bfe84741e5613ae2e9f387f2e1f9bb64ba8`.
Torch2.5.1+cu121, Transformers4.57.1. Результаты, SHA, source hashes, протоколы
и limits в linked folder. Main wall3.37/4.03/3.80s; import/download/retry отдельно.
Private locator: local-only/sora-code-audit-20261014-private.json.
Все workers terminal, CPU objects released, GPU/queues/holders не запускались.

[Новые пары](checkpoint-candidates/2026-10-14-additional-sources/REPORT.md):
Remilia mini-project имеет несколько seeds, но weights не найдены в проверенных
release sources; Benjamin QDoRA ungated, но другая quantized base/training recipe
относительно PolyGuard LoRA. Веса не скачаны; не считать matched method pairs.
Provenance/revisions сохранены. Ни обучения, ни сообщений авторам, ни commit/push.

[CLAIM_SCOPE](research-direction/2026-10-14-status/CLAIM_SCOPE.md) отделяет endpoint
критические примеры от training mechanism claims. B по-прежнему не установлен.
[Fisher audit](literature/2026-10-14-fisher-objective-audit.md) также выполнен:
мы и inspected LEMS path используем empirical gradient metric, не точный
teacher-KL Hessian. Различие известно с NeurIPS2019, обсуждается AIR/FACTS;
простая замена estimator не новый алгоритм. Нового compute не назначено.
Следующий вопрос — обоснованная rank/operation-limited deployment постановка
и failure сильного comparator, которому не помогает прежний byte-efficient
INT8 baseline. Без этого не переоткрывать failed grid.
Подробно [NEXT_QUESTION](research-direction/2026-10-14-status/NEXT_QUESTION.md).

## 2026-10-14 — сохранена точка продолжения; autonomous controller usageLimited

Все назначенные в этом этапе workers terminal, CPUmodels/RAM released,
GPUjobs/waitersнет. Scientific goal не достигнут/непомеченcomplete.
Системныйget_goal возвращаетusageLimited; агентне можетresumestatusинструментом.
Не отождествлятьэтотстатусснепровереннымпятичасовымлимитомаккаунта.
Private checkpoint:local-only/autonomous-resume-checkpoint-20261014.json.

Следующее действие без model/GPUcompute:
[точный нерешённый вопрос](research-direction/2026-10-14-status/NEXT_QUESTION.md).
Проверитьclaims ближайшихgauge-audit/scale-placementстатей; полныеOpenReviewPDF
были недоступны challenge, indexedprimaryfragmentsнеравныпрочтениювсейработы.
SORA publication подтвержденаofficialAAAI2026page:
https://ojs.aaai.org/index.php/AAAI/article/view/40267 . Не заявлятьопровержение
качества/обученияSORAизgeometrywitness. Новыхэкспериментовподследующийвопрос
не назначено. Не возобновлятьfailedgates/SmolC/rankgridавтоматически.

## 2026-10-14 — radial necessity screen отрицателен, конфигурация закрыта

[REPORT](analysis/2026-10-14-radial-necessity/REPORT.md):448generations/64unique
requests/7conditionsPASS. NativeDoRA/removeD/baseMagnitude/scalarD/centeredD/
LoRA32correct, learned-only31. RemoveDиbaseM:0gains/0losses, по1wrong→wrong
IDchange. Primarygateобаfalse; нестроитьpredictor/добор/test/новые модели для
этойконфигурации. Нольdiscordancesнеравенpopulationequivalence.

Exactadapter/tokenboundary/source/hash/referencealignmentPASS, finite/validall,
repeat/restorationbitwise; floor<1%meanremoveDeffect. CPU8wall508.68s,GPU0,
workerterminal/RAMreleased. Всеversions/metrics/frozenhashesвlinkedvalidation,
rawprivate:local-only/radial-necessity-results-20261014/;
locatorlocal-only/radial-necessity-20261014-private.json. Первые8pilotrequests
исключены; author testнеоценивался. Splitlimitations сохранены.

[Prior addendum](literature/2026-10-14-radial-scale-addendum.md): scalars/row
scales/symmetriesужеизвестны, RoPEограничениятоже. Не переносить произвольный
per-coordinateQKscaling наRoPEи не считатьrawentropyсобственнымfunctional
объяснениембезусловий. Нужен новыйидейныйвопроссобоснованиемдоочередей.
Никаких активныхнашихCPUmodel/GPUjobsилиwaitersпослеэтапанет.

## 2026-10-14 — 64-request radial necessity development gate запущен CPU8

[SPEC](analysis/2026-10-14-radial-necessity/SPEC.md) зафиксирован доoutputs.
448generations/7conditions: nativeDoRA/removeD/baseMagnitude/learned-only/
scalarD/centeredD/nativeLoRA. Сначала64уникальныхrequestизauthorvalпослеpilot,
неtest; gate≥4netcorrectlossили≥8correctnessdiscordances дляremoveD/baseMagnitude.
Этоexploratoryengineeringgate,неp-value/доказательствонеобходимости/предиктор.
УдалениеDнеравноудалениюlearnedm: D=(m/m0)*(m0/normU). Полнаяsourceфункция,
8-token greedy/scorer/tokenboundary/adapterchecks общие. Numericcontrols<1%effect.
Два tinyTorchtestsPASSсерверCPU2; CPU8/noGPU/no training,protective20min.

[Split audit](checkpoint-candidates/2026-10-14-smollm/split-audit.json):1000rows,
0full/semanticcrosssplitduplicates, ноtrain↔val82общихnormalizedrequestsиз86,
train↔test73из78. Разныенаборыtoolsнеравныduplicatefullcase; нельзяутверждать
переноснановыеформулировки. Все10sourcefilesverifiedGitblob+SHA, download2workers.
PriorDoRA/WeightNormalization/LearnableMultipliers/SORAперепроверен доэтогошага;
scalars/symmetries/разложениенепредъявляютсяновымалгоритмом.

Private locator:local-only/radial-necessity-20261014-private.json.
Следующийшаг:monitorдоterminal/исправлятьtechnicalerrors, затемпроверитьgate
и решитьнуженливообщеpredictor. Приfailedgateнерасширятьконфигурациюради
положительногочисла. GPUочередейнет. Статью/commit/pushне делали,агентовнет.

## 2026-10-14 — SmolLM2-B technical pilot PASS

[Отчёт](checkpoint-candidates/2026-10-14-smollm/PILOT_REPORT.md):40forwardrows,
32generations,8author-validationcases. ТочнаяLoRA256/DoRA384tensorзагрузка,
128targets/r16/alpha32/scaling2,tokenizers/boundaries/finiteparametersPASS.
Repeat/restorationbitwise,gauge/densefloor<=.0155%removeDeffect. Smoke1/6/6/6
из8дляbase/LoRA/DoRA/removeD — неfullquality. CPU8wall62.16s,RSS3.725GiB,
GPU0,workerterminal. Download/versions/hashesвlinkedvalidation; rawprivate
local-only/smollm-pilot-results-20261014/. Следующийшаг: source-split/dedup
и конкретный научныйprotocol,безавтоматическогоbenchmarkgrid.

[Пятьнаправлений](research-direction/2026-10-14-status/FIVE_DIRECTIONS.md)
сверены с исходным тирлистом:4существеннопроверены,necessitypredictorещёнет.
Закрыты конкретные неуспешные процедуры, не доказана невозможностьтем.
Нового алгоритма/практическогоBрезультата пока нет; агенты неиспользуются.

## 2026-10-14 — SmolLM2 weights verified; tokenizer retry before model load

Download-only этап complete70.92s, GPU0: base723,674,912bytes,
LoRA13,141,032, DoRA13,486,264; все pinnedLFS SHA/размерысовпали.
[Provenance](checkpoint-candidates/2026-10-14-smollm/download-provenance.json).
Workerterminal. Pilot перваяпопытка failed3.51s доmodel/answers: новыйformat
extra_special_tokenslist(BOS/EOS) несовместимсо старымTransformersnamedmapping.
[Retry](checkpoint-candidates/2026-10-14-smollm/TECHNICAL_RETRY.md) описывает
провереннуюcompatibilityбезinstall/pinnedfileedits. Все3vocab/templates/specialIDs
реально совпали. Следом отдельныйCPU8retryпоисходной8-caseSPEC; scientific
полного запусканет. Private locators:local-only/smollm-readiness-20261014-private.json,
local-only/smollm-pilot-first-failed-20261014-private.json. Агенты неиспользуются.

## 2026-10-14 — SmolLM2 metadata принято для ограниченного технического pilot

[READINESS](checkpoint-candidates/2026-10-14-smollm/READINESS.md) и
[PILOT_SPEC](checkpoint-candidates/2026-10-14-smollm/PILOT_SPEC.md) фиксируют
одну ungated базу SmolLM2-360M-Instruct и пару B/r16/QKVO. Авторские reports
связаны с HFsubfolders; validation51% у обоих — авторская цифра, не наш результат.
Seed/base-training revision неизвестны; DoRA checkpointing отличается, поэтому
не считать пару контролируемым сравнением обучения. Выбор B структурный.

Стандартные prompt/parser helpers прошли два маленьких CPU unittest локально:
case-sensitive ID, перестановка, none, ошибочные/дублирующиеся toolnames.
Weights пока не скачаны и модели не загружены. Следующий этап — скачать только
base+B-LoRA+B-DoRA с pinned SHA и max_workers2 на compute host, затем восемь
validation smoke cases CPU8/FP32. GPU/обучение не нужны, test не трогать.
Полную оценку и новую исследовательскую гипотезу фиксировать отдельно после
технической приёмки. Авторский длинный prompt хранится только private.

## 2026-10-14 — local head-capacity screen отрицателен по практическому gate

[REPORT](analysis/2026-10-14-head-capacity/REPORT.md): девять заранее выбранных
голов0/15/31 в слоях0/17/35, source-r32,2048 O-inputrows из64OLDcalcases.
Projected head-output rank bound — необходимое локальное условие дляLoRA-r,
не network expressivity/accuracy bound. Заbase-head columnspace хвостпосле32
составляет .00493%–1.13564% outsideenergy и9.76e−8–2.591e−6sourceheadenergy.
Это вышеnumericfloor, но0из9 проходитзафиксированные thresholds. Не выбирать
новыеголовы/ranksи не назначатьдляэтогоновыйmodel/grid.

Exactmпрочитанизpinnedweights,FP64formulaнеподмененаcaptureD32. Module/casehashes
приняты; sourcecalhashнепутатьс32developmentcaseshashcapture. ДваtinytestsPASS,
no-Dtail<=2.11e−31source,gauge relativechange<=7.14e−14. CPU4wall4.12s,
RSS~.831GiB,GPU0часов,модельнезагружалась,workerterminal. Версии/revisions
вvalidation. Raw/locatorprivate:local-only/head-capacity-20261014-private.json,
local-only/head-capacity-results-20261014/. МатериалсохранёнбезB-claim.

Следующийread-onlyвопрос — естьлидоступнаясразуготоваяпарадругогосемейства
сболееяснымtrainingprovenance, включаяавторскиерелизы. Толькоmetadata/cards/code,
безскачиваниявесов/новыхGPUочередей. НайденкандидатSmolLM2intentclassification;
этоещёнепринятаяпараи незапуск. Критериивыборасначала,качествоитенсоры
проверятьдоисследовательскихвыводов. Статьюнепишем,агентовнеиспользуем.

## 2026-10-14 — precision/backend screen завершён; новые GPU очереди не нужны

[REPORT](analysis/2026-10-14-precision-ablation/REPORT.md):108строк,3клетки
приняты. Native/dense ΔNLLremoveD CPUFP32=.00119298/.00119363,
CUDAFP32=.00119312/.00119314, CUDAmixedBF16=.00246614/.00342844.
FP32backend разницы~1e−7, pureCUDAprecisionразницы .001273/.002235 проходят
engineeringthreshold. Все средние+; significance/сменакачества/новизнаBнепоказаны.
Embedding/headCPUFP32вездеобщие,адаптерыFP32; неfullfactorial и нестарыйaccuracy.

Native repeats/restoration/cache4bitwise, official/customall144bytes+2logits
каждойклеткибитоворавны. FP32floor<1%эффекта. GPU116.51s+failedsetup16.51s
=.03695GPUч, CPU141.92sCPU16. PeakCUDAallocatedFP32 13.963GiB/BF167.177GiB;
будущемуFP32screenнуженfreeзапас>=14.5GiBсучётомcontext. GPUrelease передCPU
подтверждёнstate и завершениемпроцессов; controllerterminal. Failedattempt
releasedflagтакжеприведёнкфактическомуterminalstatus. Locatorprivate:
local-only/precision-ablation-20261014-private.json, rawresults
local-only/precision-ablation-results-20261014/. Source/revisions/версиивvalidation.

Engineeringgate положителен, но автодобор/fresh64/generationне назначаются:
общаяprecisionтемаизвестнаScalingDoRA, здесьвсеmeanзнакисохранились. Безfresh
не делатьscientificsignclaim. Следующиймалыйвопрос — gauge-инвариантное
действиеhead,а неэнтропияотдельнойматрицы. Сначалаprimaryлитература(LatentLLM,
A3,QKOV,ExpressivePowerLoRA) ипроверкасохранённыхO-inputactivationsнаCPU;
общийOVoperator/rankпринципсампосебенеобъявлятьновым. Покаещёне запущен.

## 2026-10-14 — precision/backend screen: loader исправлен до outputs

[Спецификация](analysis/2026-10-14-precision-ablation/SPEC.md):8OLDcal cases,
4matched native/dense source/removeD conditions; CPUFP32/CUDAFP32/CUDAmixedBF16,
embedding/headCPUFP32 общие. Это3клетки, неfullfactorial. CPUBF16не запускается:
нетAVX512_BF16/AMX_BF16. Новогоcomposekernelне заявляем; ScalingDoRA — prior.

Три tiny CPU теста прошли: явный CPUsave/reload, placement, FP32equivalence,
without_d restoration, official/custombytes/logits. Первый GPUsetup failed
через16.51s доoutputs: PEFT автоматическиredispatchCPUмодельвCUDA-visible
процессе и оставилmeta tensors. Guardне ослаблен; loaderисправлен наполныйCPU
безhf_device_map, explicitadapterCPU, затемmanualtransformerplacement.
[TECHNICAL_RETRY](analysis/2026-10-14-precision-ablation/TECHNICAL_RETRY.md).
Failedlocator:local-only/precision-ablation-first-failed-20261014-private.json.

Используется существующийadmit_queues controller с дополнительнымfree>=14GiB,
util<20%,used<7GiB,2checks/10s,GPU1исключена. ResourceSampler извлечён изpilot
без изменениястарогоevaluator: локальныйpilotимеетдругиеранниеизменения,
перезаписыватьимсерверныйфайлне стали. GPUrelease передотдельнойCPUфазой.
Новаяпопыткаготовится; приуспехе monitorlocal-only/check-precision-ablation.py
и выполнитьпослеcompletionанализвсехклеток,не делатьвыводыизоднихlogits.

## 2026-10-14 — byte-budget контроль завершён: простой INT8 намного сильнее

[REPORT](analysis/2026-10-14-byte-budget/REPORT.md): EXACT128development cases,
384 строки (128KFACreuse+256new) приняты. KL KFAC-r8FP32=.00151700,
fixed-D r15FP16=.00024122, r30INT8=.00000570: −84.10%/−99.624%,
Holm2p=.000200 оба; все128cases улучшены. ΔgoldNLL=.01614374/.00684693/
.00038921, argmax33/13/0 из4096gold-prefixpositions. Не accuracy и не
новая независимая testвыборка; архивы/ранги зафиксированы до screen.

Independentactualheader/fileauditPASS: source432FP32 tensors95,684,080байт;
FP16archive+JSON23,425,946, INT8archive+JSON23,496,391байт, оба ниже cap.
ВсеD/scalesучтены. Native8referencebitwise, factorizedcontrolfloor8.80e-6
vs mineffect.011759, source восстановлен. Byteworker369.32sCPU16,
screen121.47sCPU16,GPU0часов. Версии/revisions/sourcehashesвvalidation.
Raw: local-only/byte-budget-validation-results-20261014/; locator
local-only/byte-budget-validation-20261014-private.json. Worker terminal.

Решение: равный FP32 budget не задаёт сильный practical storage frontier.
Не повторятьjointFP32grid/Mistralcompression/долгуюgeneration ради слабой
прибавки. Это известный принцип LoRAQuant, не новый алгоритм и не B-результат.
Больший ранг/FP32decode не обещают меньшуюruntimeVRAM или latency.
Следующий нерешённый пункт старого road-to-B — отделить dtype/backend и
численный путь абляции. Сначала конкретная короткая спецификация и техническая
проверка; автоматической GPUочереди пока нет. Агенты не использовались.

## 2026-10-14 — byte-budget screen положителен; фиксированный128 контроль идёт

[Screen](analysis/2026-10-14-byte-budget/SCREEN_REPORT.md): KL KFAC-r8 FP32
.00196331; fixed-D r15 FP16 .00033711; fixed-D r30 INT8 .00000745.
На8 OLD calibration вопросах снижение82.83%/99.62%; significance не заявляется.
Реальные archive+config23,425,946/23,496,391байт, оба ниже cap23,592,960.
D/scales включены; decode/inferenceFP32 не даёт экономии runtimeVRAM/latency.
24строки/native4/controlfloorPASS. Wall121.47sCPU16,GPU0; screenterminal.

[VALIDATION_SPEC](analysis/2026-10-14-byte-budget/VALIDATION_SPEC.md) зафиксирован
до128новыхoutputs. Повторяем только2новыхусловия на EXACT128development
cases прежнего affineсравнения; это не новая независимая testвыборка.
Сохранённые128source caches и KFACrowsпереиспользуются,не пересчитываются;
проверяютсяихhashes/NLLalignment и native4old+4development bitwise reload.
Параметры/archivesне меняются. CPU16FP32SDPA,30minprotectivealarm,GPU0.
[ERRATA](analysis/2026-10-14-byte-budget/ERRATA.md) исправляет описательный
copyerror: уQwen432source tensors,480былоMistral. Кодпроверяетреальные432;
фrozenSPEC/runnerне менялись во времяrun. Raw/locator private:
local-only/byte-budget-validation-20261014-private.json; checker
local-only/check-byte-budget-validation.py --fetch. Послеcompletion выполнить
analyze_byte_budget.py и независимыйheader/filebyteaudit, сохранитьвсеусловия.

## 2026-10-14 — запущен короткий контроль сжатия по байтам

[Спецификация](analysis/2026-10-14-byte-budget/SPEC.md) фиксирует пропущенный
простой baseline: больший ранг при меньшей точности хранения. Сравниваем
прежний KFAC rank8 FP32 с fixed-D rank15 FP16 и rank30 INT8; учитываем
все D/scales, реальные safetensors и config. Payload cap 23,592,960 байт.
Декодированный inference остаётся CPU FP32: нельзя заявлять runtime VRAM
или ускорение. Восемь OLD calibration cases — инженерный screen, не качество
GSM8K и не подтверждающая статистика. Gate: минимум 20% KL выигрыша.

[Поиск](analysis/2026-10-14-byte-budget/PRIOR.md) нашёл прямой предшественник
LoRAQuant; SVD + квантизация адаптера не объявляется новым методом. Другие
общие идеи (true-Fisher substitution, shared subspaces, stable DoRA compose)
уже известны и без конкретного отличия не реализуются.

Три содержательных tiny codec теста прошли на CPU2 до model worker.
Проверены QR/SVD reconstruction, truncation error, FP16/INT8 roundtrip,
стоимость включая scales, нулевые компоненты и отказ при overflow/неполной записи.
Один CPU16 worker, FP32 SDPA, защитный предел 30 минут, GPU нет.
На preflight load average 12.31 / 13.13 / 17.80 при 80 логических CPU,
доступно 683.3 GiB RAM. Чужие процессы не трогались.

Raw/locator: local-only/byte-budget-20261014-private.json; checker
local-only/check-byte-budget.py --fetch. Следующий шаг — принять реальную
стоимость и все 24 строки, проверить fidelity floor, сохранить положительный
или отрицательный screen и решить, нужен ли фиксированный 128-case контроль.

## 2026-10-14 — Mistral128 завершён: NLL-подтверждение отрицательное

[Итог](analysis/2026-10-14-mistral-ablation/FRESH_REPORT.md): 128 новых вопросов,
8 условий, 1024 строки приняты. Все четыре основных Δgold-NLL интервала
98.75% включают ноль; Holm p = 1 / 1 / .4696 / .9209. Ни одна заранее
указанная V/O пара противоположных знаков не подтверждена. Не подменять
этот критерий разницей между c, не увеличивать выборку/масштабы/слои.
V остаётся сильнее O по KL: Qwen KL reversal здесь не воспроизведён.
Это отрицательное подтверждение, не доказательство нулевого эффекта вообще.

128 входов/токенизация/2111 исключений независимо проверены. Все 480 тензоров,
160 targets, SHA обеих частей базы и адаптера совпали; native4 bitwise,
36 controls max RMS 2.9722e-6 при min effect .00685563. CPU FP32 SDPA,
16 потоков, wall 2191.13 s, peak RSS 43.05 GiB, GPU 0 часов.
Torch 2.5.1+cu121 / Transformers 4.57.1 / PEFT .17.1 / safetensors .6.2 /
accelerate 1.11.0. Pinned revisions и полная приёмка — в fresh-validation.json.
Worker завершён; очередей и удержания GPU у этого этапа нет. Raw/locator:
local-only/mistral-ablation-validation-20261014-private.json и
local-only/mistral-ablation-validation-results-20261014/ (вне Git).

Назначенная пользователем пауза 2 ч 8 мин выполнена; работа возобновлена
14 октября около 01:29 UTC. Исследовательская цель активна. Следующий шаг —
выбрать конкретный нерешённый вопрос по имеющимся данным и ближайшей
литературе, с малым решающим тестом. Не повторять неудачное joint-сжатие,
не тратить GPU на неподтверждённый знак NLL и не заявлять уровень B.

## 2026-10-14 — Mistral128 cases приняты; аналитический механизм записан

Независимый [Mistralcaseaudit](analysis/2026-10-14-mistral-ablation/fresh-case-audit.json):
128distinct cases,2111excludedhashes, identity/whole-stringoffsettokens/BOS
всех128зановопроверены, dataset/casehashmatchPASS. Модельдляauditнезагружалась.
Inferenceworkerжив; source4oldnativecache ужеbitwiseaccepted, остальныеусловия
продолжаются. Доcompletion не изменятьn/c/centering и не делатьprimaryвывод.
Анализаторподготовлен:execution/scientific-analysis/analyze_mistral_ablation_validation.py;
послеchecker --fetch онпроверяет1024rows/36controls/primary4NLLtestsfamily.

[MECHANISM](analysis/2026-10-14-ablation-commutation/MECHANISM.md) даёт точное
branch-levelобъяснение:rawVoffпослеgaugeполучаетattentiongain1/c,rawOoff—c
вкаждомблоке. Это не scaling финальныхlogits и не причинаобучающейтраектории.
Критерийинвариантностивмешательств связансужеизвестнойcausalabstraction;
центрирование задаётоднуконвенцию, неuniquetruth. Не запускаемдополнительный
Taylor/gradient/COARgrid: общийpredictionprincipleизвестен, точнаяалгебрауже
объясняетисточникизменения; такаясетка неразрешаетглавнуюqualityнеопределённость.

Всеоперационныеlocator/rawfiles private; GPUjobs/holds отсутствуют. Следующий
шаг — дождатьсяMistral128, принятьNLLendpointsigngate(илиnegative), затем
оценитьреальнуюпрактическуюполезностьдоназначениябольшихGPUпрогонов.

## 2026-10-14 — Mistral screen принят; frozen128 NLL confirmation идёт

[SCREEN_REPORT](analysis/2026-10-14-mistral-ablation/SCREEN_REPORT.md):
KL ordering на Mistral НЕперевернулся (VсильнееOдлявсех3c). Зато заранее
предусмотренныйNLLscreen gate прошёл: Voff meanNLL .995/1.005=+.00067588/
−.00089181, Ooff=−.00039602/+.00099886. Это8cases, безsignificanceclaim.
80строк/40controlsPASS, floor2.981e-6 vs mineffect.007997, native4repeatbitwise,
все160targets/480tensors verified,2basehashes+adapterhashPASS.
Wall494.86sCPU16(include download11.21/hash62.37s), peakRSS43.06GiB,GPUнебыло.

До новых outputs [VALIDATION_SPEC](analysis/2026-10-14-mistral-ablation/VALIDATION_SPEC.md)
фиксирует128НОВЫХвопросов/8conditions/1024rows;2rawc1неповторяютсяполностью.
n128выбрандоvalidation поroughpilotvariance(powerO995~112,O1005~38), не
доборпослерезультатов64. Pilotn8ненадёжен; подтверждениенегарантировано.
Primary4NLLendpoint signs against0,Holm4+98.75%bootstrapintervals;
хотябыоднаполнаяprespecifiedVилиOпаразнаковдляconfirmation. Не заменять
failedendpointtests толькоgauge-to-gaugedifference. Неувеличиватьn/c/слоипри
uncertain/negative. Source/cases/предыдущиеопросыисключены, trainexposureunknown.

CPU16FP32SDPAодинworker,90minprotecteddeadline, неGPUqueue. Старыйscreen
terminal,calnative4cachedперезагружаютсяbitwise, allgateweightsfixed.
Locatorlocal-only/mistral-ablation-validation-20261014-private.json;
checkerlocal-only/check-mistral-ablation-validation.py --fetch.
Послеcompletionпринять1024rows/36controls/128freshcasesиNLLgate, сохранить
успешныеиотрицательныеметрики. B/accuracy/trainingmechanism пока неустановлены.

## 2026-10-14 — Mistral bounded8case CPU screen запущен

После подтверждённого Qwen fresh64 KL reversal заморожен отдельный
[Mistral SPEC](analysis/2026-10-14-mistral-ablation/SPEC.md). Это перенос вопроса
об интерпретации V/O абляций, не запуск неудачного joint compressor.
CPU16FP32SDPA,20minprotectedlimit,GPU0ч. Только public94MBDoRAadapter и
недостающие lightweighttokenizerfiles; база уже на диске. Веса/CPUвычисления
на compute host. До inference проверить SHA2base shards/adapter, все480
savedtensors/160targets/alpha64/r32/scaling2, в том числе неизменный gate_proj.

8первыхeligibleвопросов иззафиксированного Qwen fresh64, plain author-style
`question: ... answer: ...`, целаястрокатокенизируетсясoffsets/BOS дляточной
границыanswer. Теже10условий/c=.995/1/1.005, source/centered control4cases,
всего80rows. Native4repeats bitwise, native/densefloor<1%effects.
Samefixedscreen gate; отрицательныйслучайсохранить, c/слоинеискать.
Подтверждатькачество/новизну/B доoutputs нельзя. Locatorprivate:
local-only/mistral-ablation-20261014-private.json; checker --fetch
local-only/check-mistral-ablation.py. Приtechnicalfailureисправитьпоactualerror,
приготовомpositiveотдельноfreezefresh64, приnegativeнерасширятьсетку.

## 2026-10-14 — V/O KL ordering reversal подтверждён на fresh64; качество не доказано

[FRESH_REPORT](analysis/2026-10-14-ablation-commutation/FRESH_REPORT.md):
640строк/10условий приняты. V−O KL при c=.995=+1.9438e-5,
97.5%CI[1.4877e-5,2.4344e-5],60/64positive; при1.005=−1.4739e-5,
CI[−1.8095e-5,−1.1477e-5],58/64negative. Holm4 p=.000400оба.
Primary gate пройден. Secondary NLL opposite means неуверенны, Holm p=.50055;
свободнаягенерация/accuracy не проверялись. Не выдавать результат за B.

64questions/tokenization/exclusions independentlyPASS; source4oldbitwise,
36controls maxRMS1.186e-5 vs mineffect.01070, restoredsourcebitwise.
Wall876.88sCPU16,GPU0ч, worker завершён. ЦентрированныеV/Oshape иbranchgain
задают invariant convention; неуникальная, эффекты неоддитивны. Generic gauge
аудит и gain/decomposition priors существуют; training-механизм не установлен.

Большая Qwen generation пока не оправдана слабымNLL signal. Следующий
обоснованный перенос: fixed8case Mistral screen тех жеc/контрастов сnegative
stopcriterion, без поискаc/слоёв. Mistral авторский code audit pinned
3c182800f7854b156d63a3f1282713429bbf4942: проект Spectral Adapter2024,
НЕавтоматически SORA2025. Код использует GSM8K и текстовый prompt
`question: ... answer: ...`; defaults r8/alpha16/2epochs расходятся с
HFcheckpoint r32/alpha64/card5epochs. Dataset attribution checkpoint остаётся
неподтверждённой. Его DoRA forward rownorm(dim1) согласуется с нашей формулой.
Следующийшаг — заморозить отдельный Mistral SPEC, технически принять все160
native targets(includinggate), затем bounded8case CPU screen, не GPU queue.

## 2026-10-14 — fresh64 ablation validation идёт, case audit PASS

[VALIDATION_SPEC](analysis/2026-10-14-ablation-commutation/VALIDATION_SPEC.md)
заморожен до новых outputs: те же10условий/c=.995/1/1.005, CPU16FP32SDPA.
64новых вопроса, 640строк ожидаются. Primary: противоположные V−O KL signs
в .995/1.005, 97.5% marginal bootstrap intervals исключают0 и Holm p<.05;
Holm-family4 включает также2secondarygold-NLLконтраста. Не подбиратьc/слои.
Центрированные3контрфактических вопроса не суммировать без взаимодействий.

Независимый [case audit](analysis/2026-10-14-ablation-commutation/fresh-case-audit.json):
64distinct train questions не пересекаются с2047excluded hashes; SHA данных и
вопросов проверены, все input/target tokens заново построены tokenizer.
Модель для audit не загружалась. Рабочий inference процесс жив и продолжает
условия; GPU0ч. Locator приватный local-only/ablation-commutation-validation-
20261014-private.json. При завершении выполнить analyze_ablation_commutation_validation.py,
сохранить fresh tables/report и только затем решать о переносе.

Read-only Mistral readiness: скачанная база pinned revision27d67f1b5f57dc0953326b2601d68371d40ea8da,
32layers/GQA32Q-8KV/hidden4096, две safetensors shards14,483,498,040bytes.
Адаптер пока не скачан. Pinned авторская DoRA card декларирует lr2.5e-5,
seed0,5epochs, но dataset=None и описание отсутствует; это декларация,
не подтверждённые logs или причина обучающей траектории. Полный перенос пока
не запускали; gate_proj надо оставить неизменным/корректно загрузить среди160
native targets. Модельные данные/пути остаются private.

## 2026-10-14 — V/O ablation commutation screen прошёл effect gate

После назначенного ожидания 2ч8мин работа возобновлена. Joint compression
остаётся закрытым. Новая короткая проверка не расширяет его сетку:
[ablation SPEC](analysis/2026-10-14-ablation-commutation/SPEC.md),
[prior audit](analysis/2026-10-14-ablation-commutation/PRIOR.md).
На 8 OLD calibration questions /256 positions removeD-V vs removeD-O
меняет KL ordering при c=.995/1.005. В .995 KL V/O=5.733e-5/2.764e-5;
в1.005=3.135e-5/4.951e-5. Contrast range4.786e-5 превышает gate.
Gold NLL отдельных абляций знак не меняет; это не accuracy/статистический результат.

Три малых GQA algebra tests PASS. Native4cases bitwise, common dense FP32 path,
40numeric controls, maxRMS1.250e-5 при min effectRMS.01110 (floor0.113%effect).
80строк приняты; wall190.70s CPU16, GPU0ч, worker завершён. Центрированные
вмешательства сохраняют общий gain или относительные row scales отдельно и
численно инвариантны к этой симметрии; это выбор estimand, не единственный true
causal attribution. Близкий generic Gauge-Symmetry Audit уже найден; новизна
в целом не установлена, training механизм не опровергнут.

Следующий шаг: до outputs заморозить fresh64-case проверку тех же c/контрастов,
исключив все прежние/calibration/test/affine128 вопросы. Не искать другие c/слои.
Если подтверждается устойчивый reversal, оценить смысл invariant attribution
и необходимость целевой quality/architecture replication; B пока не установлен.

## 2026-10-14 — joint affine candidate завершён и закрыт по frozen gate

[Итог](analysis/2026-10-14-affine-candidate/REPORT.md): 6×128 cases, 768 строк,
независимые факторы/хеши/байты/покрытие/исключения PASS. Все варианты —
5,898,240 FP32 элементов. Joint KL=0.00149176 против W-SVD=0.00167901
(−11.15%, Holm p=.000500), но против сильнейшего KFAC=0.00151700 только
−1.66%, paired CI содержит0, Holm p=.4021. Практический gate≥10% не пройден.
Native-m controls не стали лучшим baseline. Не запускать для этого кандидата
генерацию/Mistral/сетку iterations-shrinkage. B-уровень не установлен.

Capture396.28s CPU16, prepare2888.73s CPU8, eval1460.70s CPU16; GPU0ч.
Worker/controller завершены. Первый native-reference failed attempt сохранён;
причина не установлена, обе диагностики и retry прошли bitwise guard без ослабления.
Все 128 вопросов и native factors между попытками совпадают.

Пользовательский timed wait начинается 23:20:18 UTC 13 октября (02:20:18 МСК
14 октября), длительность 2ч8мин, продолжение с 01:28:18 UTC (04:28:18 МСК).
Не считать goal complete/blocked: исследовательская цель остаётся открытой.
После ожидания сначала проверить статус существующих процессов, затем выбрать
следующий обоснованный вопрос по литературе и имеющимся данным. Не расширять
сетку только ради положительного числа. Кандидат joint закрыт; приоритет дальше —
конкретное practically useful failure или надёжность выводов из абляций.

## 2026-10-14 — свойство affine класса отделено от пользы кандидата

[Алгебраическая записка](analysis/2026-10-14-affine-candidate/SCALE_PROPERTY.md)
показывает замкнутость `D B+LR` относительно положительного скалярного V/O
масштабирования при той же базе и размере. При переносе C/G оба точных подшага
joint solver эквивариантны. Это также верно для более простого fixed-D решения;
не заявлять свойство уникальным преимуществом нового алгоритма.

Tiny CPU2 контроль: две синтетические матрицы 6x8/8x6, rank2, 5 cycles,
scales .995/1.005/2. Максимальная относительная ошибка композиции joint
после FP32 экспорта 5.40e-8, fixed-D FP64 2.68e-16. Это algebra/code check,
не модельный quality result и не equal-budget comparison. GPU0 ч.
Общая scale/compression идея известна; новизна точного применения не доказана.

Пользователь задал режим: ещё 20 минут работы с 23:00:18 UTC 13 октября,
затем 2 ч 8 мин ожидания без обращений к модели; продолжить с 01:28:18 UTC
14 октября. Серверная оценка остаётся независимой и выполняется во время
ожидания. Операционное расписание сохранено приватно в local-only.
Перед ожиданием записать актуальное состояние/следующий шаг; после пробуждения
сначала проверить существующий worker/controller, не создавать дубликат.

## 2026-10-14 — technical retry прошёл строгий native guard

Evaluation attempt 2 прошёл все 4 native reference проверки побитно и начал
новый 128-case teacher cache. Подтверждено, что вопросы совпадают с первой
попыткой и native-magnitude факторы не изменились; [приёмка retry](analysis/2026-10-14-affine-candidate/technical-retry-validation.json).
Причина одиночного первого несовпадения остаётся неизвестной. Не ослабляли
bitwise guard; обе отдельные диагностики тоже дали нулевое расхождение.
Рабочий процесс жив, CPU16; GPU0 ч. Далее дождаться всех 6×128 outputs,
выполнить независимую приёмку тензоров и парный анализ frozen gate.

## 2026-10-14 — native check прошёл в двух диагностических процессах; retry

Обычная загрузка и загрузка после native-magnitude подготовки каждая дали
побитное совпадение со старым эталоном на всех 4 случаях; повтор каждого
forward тоже побитен. Расход 39.08 и 88.46 с CPU16, GPU0 ч. Компактные метрики:
[native-reference-diagnostic.json](analysis/2026-10-14-affine-candidate/native-reference-diagnostic.json).
Причина первого сбоя не установлена; утверждать, что проблема исправлена,
пока нельзя. Подготовка сама по себе расхождения не воспроизвела.

Выполняется evaluation-only technical retry (attempt 2). Первый failed attempt,
его manifest/логи/cases/freeze и native factors сохранены отдельно приватно.
Все факторы кандидата, 128 вопросов, алгоритм и gate неизменны. В evaluator
добавлено лишь сохранение метрик/тензора и повторного forward при несовпадении;
строгий bitwise guard НЕ ослаблен. Новый source hash заморожен до outputs.
Если ошибка повторится, диагностировать сохранённое расхождение; не повторять
48-минутную подготовку и не принимать failed outputs за результаты качества.

## 2026-10-14 — оценка остановлена проверкой native reference

Первый запуск новой 128-case оценки завершился технической ошибкой
`ValueError: Native reference changed` через 63.84 с, на setup, до reference
cache новых вопросов и любых candidate outputs. Подготовка факторов успешна
и сохраняется; повторять её не требуется. Первый evaluate directory и manifest
сохранять как failed attempt, не удалять и не выдавать за качественные данные.
Контроллер завершился с failed; это не ожидающая/работающая очередь.

Запущена отдельная CPU16 диагностика pristine native loader на четырёх прежних
calibration cases: измеряет абсолютное расхождение с cached FP32 reference и
повторяемость двух forwards. Источник расхождения пока не установлен; нельзя
просто заменить bitwise guard на произвольный tolerance. Следующий шаг —
локализовать причину, сохранить диагностику и только затем возобновить оценку
с теми же факторами, вопросами и зафиксированным алгоритмом. GPU0 ч.

## 2026-10-14 — полный affine candidate подготовлен, новая оценка идёт

Подготовка всех 144 проекций завершена за 2888.73 с (48.15 мин), CPU8,
GPU0 ч. Четыре исходных варианта содержат ровно 5,898,240 FP32 элементов
каждый. Суммарная локальная ошибка joint_kfac ниже fixed-D KFAC на 16.36%;
отношение к ordinary rank8 KFAC — 0.97956. Это калибровочный критерий,
не свидетельство улучшения выходов или ответов.

Контроллер автоматически перешёл к оценке: CPU16, 128 новых вопросов,
6 условий после заранее внесённого native-magnitude дополнения. Код кандидата
и frozen SPEC не менялись. Новая read-only приёмка
execution/scientific-analysis/audit_affine_candidate.py пересчитывает фактические
тензоры/байты, хеши, покрытие, пересечения вопросов и агрегаты; запускать после
завершения оценки, без модели/GPU. Далее локальный analyze_affine_candidate.py
проверяет зафиксированный gate; не менять алгоритм по этим результатам.

Дополнительные предшественники: [RidgeLoRA и LoRA Decompose](literature/2026-10-14-affine-novelty-addendum.md).
Диагональная плюс низкоранговая структура и block coordinate descent известны;
различия постановок описаны, новая архитектура/общий оптимизатор не заявляются.
Следующий шаг — принять 768 строк и реальную пользу против всех пяти controls.
При отрицательном gate закрыть этот кандидат, без сетки iterations/shrinkage.

## 2026-10-14 — до128caseoutputs добавлены native-magnitude baselines

Candidate/5cycles/shrinkage НЕизменены. До созданияevaluate directory
установлен [BASELINE_ADDENDUM](analysis/2026-10-14-affine-candidate/BASELINE_ADDENDUM.md):
исходныеmagнитудыm сохраняются, D пересчитывается послеdirectiontruncation;
дваcheapcontrols native_m_input/native_m_kfac. Это отличаетсяотсохраненияD.
Tinyrownorm/direction/storage testPASS. Теперь6условий/128newcases, всеequal
5,898,240FP32elements. Семействоcandidatevscomparators=5 сHolm; gateagainst
bestofall5, не толькоoriginal3. OriginalSPEC/preparation/factors неизменны;
старыйevalmanifest сохранёнprivate, новыйsourcehash доoutputsзафиксирован.

Дополнительнаялитература: PermDoRA arXiv2606.11262v1 — multiadaptercomposition,
weakgeometrypredictors. Eq1описываетscalarFrobenius-normalizedBA, отличающийся
отнашейnativeDoRArow-normalizationW0+BA; коднепроверен, выводынепереноситьпрямо.
Genericgeometrycriticism ужеизвестна. Noveltyjointaffinecompressionнеустановлена;
сначалаactualquality противвсехсильныхипростыхcontrols. Controllerпродолжает
CPU8prepare→amendedCPU16evaluation, неостанавливался. GPUjobsнет.

## 2026-10-14 — K1 restoration завершён; основная потеря осталась

[RESTORATION_REPORT](analysis/2026-10-14-allocation-diagnosis/RESTORATION_REPORT.md):
3×64olddevelopmentcases,CPU16,289.69s,GPU0ч. NativeK1restore убирает лишь4.13%/
5.13%excessKL weighted/structuralallocation; уweightedpairedCIвключает0.
Hypothesisonezero-rankdominatesloss не поддержана. Параметров стало больше;
невыдаватьэтозаequal-budgetalgorithm. Полныйlayerrestorationgridнеобоснован.

FullaffinecandidateCPU8preparation продолжается, per-modulecheckpoints и
ждущийcontrollerCPU16validation128cases. Следующий шаг — дождаться результата
фиксированногоcandidate, не менять config по промежуточным результатам.
Mistralreplication [readiness](analysis/2026-10-14-affine-candidate/REPLICATION_READINESS.md):
проверенныеpinnedpublicconfigs r32/alpha64 включают gate_proj помимоq/k/v/o;
нашattention-onlyloaderтакойcheckpointнамеренноотклоняет. Припереносеучесть
всеtargetmodules/всюпамять,необещатьfulladapter75%economyдляsubsetattention.
Trainingdata/provenanceпо-прежнемунеустановлены. Mistraljobsпоканет.

## 2026-10-14 — full candidate подготовка и K1 restoration diagnostic

Full gradient capture принят:64×32tokens,144modules,CPU16,396.28s; Gcovariances
сохранены сhashes, параметров не обновляли. CPU8prepare выполняет144module
knownmetricbaselines + один5cyclejoint(D,LR)candidate; per-module checkpoints
сохраняются. Затем controller автоматически выполняет frozen128newcasesCPU16.
Не менять affine_compression.py/spec/config, пока идёт preparation/evaluation.

Дополнительно [restoration SPEC](analysis/2026-10-14-allocation-diagnosis/RESTORATION_SPEC.md)
заморожен доoutputs и запущенCPU16: триусловия на техже64allocationdevelopment
cases, cachednative teacher. RestoresnativeK1вweighteduniform/weightedallocated/
structuralallocated; дополнительныеnativeadapterelements считаются явно,
это НЕequal-budget algorithm comparison. Цель — проверить конкретноеcomposition
rescue, не делатьtrainingcausalityclaim. Locatorlocal-only/allocation-restoration-
20261014-private.json. Следующийшаг: принять3×64rows и fraction excessKLrescued;
продолжать мониторинг fullcandidate, ошибки исправлять автономно. GPUjobsнет.

## 2026-10-14 — allocation diagnostic принят; один full affine candidate идёт

Завершён [allocation REPORT](analysis/2026-10-14-allocation-diagnosis/REPORT.md):
при том же5,898,240element budget exact local allocation уменьшает proxy loss
на66.7%/83.7%, но teacherKLрастёт в2.684/2.553раза. На64freshdevelopmentcases
ухудшение63/64и62/64; Holm p≈.000200. Это известная proxy/fidelity проблема,
не новое опровержение любых rank allocation methods. Independentactualfactor
hashes/counts/FP32finite/caseexclusionPASS. Подготовка571.5sCPU4,
inference939.83sCPU16, GPU0ч; controller завершён.

Joint affine prototype4modules layer17 прошёл local gate: fixed-D metric
loss−25.54%, ratio ordinarytwo-sidedrank8=.7928; отдельные4module budgets
не равны, поэтому это не task/budgetmatched результат. 5blockcycles заранее
фиксированы, tiny mathematical testsPASS. НовизнаgenericALS не заявляется.

Запущен один [full candidate SPEC](analysis/2026-10-14-affine-candidate/SPEC.md):
все144modules,64oldcalibrationcases; G empiricaloutputgradient covariance,
rowshrinkage.3, C прежнийridge.001. CaptureCPU16complete396.28s, параметров
не обновляли. Controllerпослеcapture запускает CPU8prepare затемCPU16evaluate
на128НОВЫХ cases, исключая allocation64. Четыре equalstorage conditions:
weighted_uniform/kfac_uniform/structural_kfac/joint_kfac,5fixedjointcycles.
Primaryjointпротивтрёхcomparators сHolm; practicalgate≥10%KLagainstbestmean
baseline, парнаяопределённость и отсутствие тревожногоNLLtradeoff. Приnegative
неперебиратьiterations/shrinkage; приpositive независимаяgeneration/attribution
и другаяготоваяпара, до заявкиB. Операционныйlocatorlocal-only/affine-candidate-
20261014-private.json. Controllerиworkers мониторить, ошибкиисправлять;
неоставлятьqueuedjobбезнаблюдения. GPU1исключена, GPUпока неиспользуются.

## 2026-10-14 — первые локальные результаты автономного этапа

Allocation preparation complete571.50sCPU4,144modules, four exact equal-size
conditions5,898,240elements. Local weighted loss uniform→allocated25.00059→8.32005
(−66.72%); structural21.29353→3.46722(−83.72%). Это известный proxy optimum,
не новый метод и пока не вывод о качестве. Matched64freshcases CPU16 inference
идёт; cases/factors/sourcehashes заморожены до outputs, calibration прежняя64.

KFAC orientation probe complete280.30sCPU (16capture→4decompose),12modules,
8oldcalquestions/256positions, параметров не обучали, GPU0ч. На реальных Gram
кодовая lower-Cholesky convention хуже минимума стандартного G-weighted objective
в среднем2.438раза. Это не taskquality и не новый алгоритм: OBD-LLM уже явно
использует правильный transpose (arXiv2604.00821 Eq.17). Подробности:
[literature audit](literature/2026-10-14-lems-code-audit.md),
[local diagnostics](analysis/2026-10-14-kfac-orientation/local-diagnostics.json).
Данные не обосновывают заявления, что опубликованные результаты LEMS неверны.

Две tiny FP64 проверки coupled diagonal least-squares/weighted SVD/alternating
monotonicity прошли. Joint affine(D,LR) prototype пока не проверен на модели;
общий принцип block least-squares известен, новизна не заявлена. Следующий шаг:
закончить matched allocation outputs; при необходимости4module calibration-only
probe совместного исправления, до полного нового кандидата. ОчередейGPUнет.

## 2026-10-14 — автономное продолжение: allocation diagnostic запущен

Пользователь разрешил самостоятельное исследование и обоснованные CPU/GPU
прогоны, включая частично занятые GPU; новых агентов не создавать. GPU1 остаётся
исключена. Цель B — ориентир качества, не обещание принятия или новизны.
Перед каждым новым концептуальным кандидатом проверять литературу.

Заморожен [SPEC](analysis/2026-10-14-allocation-diagnosis/SPEC.md): четыре
условия на всех144проекциях, exact5,898,240FP32elements, local weighted-SVD
uniform/allocated и fixed-D structural uniform/allocated. Это известный
spectral allocation baseline, не новый алгоритм. CPU4 preparation запущен
после5численных unittest проверок. pytest в окружении отсутствует, использован
имеющийся unittest без установки пакетов. Операционный locator local-only.
Инференс пока не начат; предполагаются64новых developmentcases и CPU16.
Все7GPU сильно заняты; для этого этапа GPU не нужны. Не трогать чужие процессы.

Авторский LEMS/KFAC код прочитан на revision9eaf26243562f07c6261da8abbc8787ae655146c.
Изучены9небольших source/config файлов, без импортов/исполнения внешнего кода.
KFAC собирает forward-input и token-wise output-gradient covariances,
использует отдельные shrinkage0.1/0.3; LEMS калибрует spectral tail по single-layer
KL и ищет cross-layer depth coefficients через Optuna+ILP. Его перенос целиком
не является дешёвым или уже выполненным. Следующий шаг: принять спектры/бюджеты,
затем четыре matched outputs, анализ ошибки allocation proxy против fidelity.

## 2026-10-14 — аудит предшественников сжатия готовых адаптеров завершён

Обзор: [adapter-compression-audit.md](literature/2026-10-14-adapter-compression-audit.md).
Сравнение 11 работ/семейств: [comparison.csv](literature/2026-10-14-adapter-compression-comparison.csv).
Поиск 13–14 октября по первоисточникам, без Scite/Deep Research/агентов.
Новые близкие ориентиры: PARA (posthoc allocation для обычной LoRA),
LEMS/KFAC-SVD (глобальный error-aware allocation и Fisher-aware approximation),
ChainDoRA (компактная направляющая ветвь, но обучение нового адаптера).

Уточнение версий: 2403.07378v2 содержит closed-form recovery;
2403.07378v5 — последовательное LoRA-дообучение факторов. SVD-LLM V2
2503.12340 — отдельная работа. Наш W-SVD не полное воспроизведение ни одной.
PARA сравнивается с DoRA Mao et al. (dynamic rank), не с нашей weight-decomposed
DoRA Liu et al.; эти названия нельзя смешивать. Generic SVD/QR/adaptive rank,
whitening/scaling и joint QK/VO не считать нашей самостоятельной новизной.
Отсутствие точного предшественника fixed-base DoRA compression не доказано.

Результаты full-compression/radial-recalibration не изменены; кандидат остаётся
отклонённым. Следующий шаг — выбрать одну проверяемую причину ошибки
(allocation либо approximation) и ближайший сильный baseline до реализации
нового кандидата. Полный аудит LEMS objective/code ещё нужен, если выбираем
эту ветку. Обзор не разрешает автоматически запускать новую сетку/Mistral.
На этом этапе GPU/модельных вычислений 0; веса не скачивались, очереди не запускались.
Commit/push не выполнялись. Операционные данные сервера в отчёт не включены.

## 2026-10-13 — полное сжатие и corrective candidate завершены

Итог кандидата: [REPORT.md](analysis/2026-10-13-radial-recalibration/REPORT.md).
64 новых validation cases, 2048 позиций; raw/W/struct/recalibrated KL
.00221454/.00218669/.00236064/.00234155 при одинаковых5,898,240elements.
Primary recalibrated против fixed-D: KL−0.8089%, delta−1.9094e−5,
CI95[−3.1051e−5,−9.6172e−6]. Gain статистически различим, но ниже заранее
заданного10% practical screen. Против W-SVD кандидат хуже на7.0818%;secondary
CI положителен. Argmax flips19/28/27/26из2048, НЕtaskaccuracy.
Кандидат отклонён; нового лучшего компрессора/B/A преимущества не получено.
Local closed-form solve уже оптимален поD приfixedL/R и данномobjective;
не перебиратьnorms/scales/iterations по этомуvalidation. Общаяcompression
область не закрыта, потребуется другое обоснованное направление исправления.

Все256per-case rows иhashes/budgets/finite/disjoint checksPASS. Candidate
113.28sCPU4prepare,674.78sобщийwallCPU,modelCPU16,peakRSS21.18GB. GPU0ч.
Суммаfullscreen+candidate compute wall≈33.76мин. Обаworkers завершены;
Mistral/новыхочередейнет. Артефакты/code/версии вдвух новыхпапкахanalysis.
Операционныеlocators иrawcompactrecords вlocal-only внеGit,weightsнасервере.
Следующийшаг: сообщитьпользователю результаты и ограничение; не запускать
следующуюэкспериментальнуюветкуавтоматически послеэтогоnegativevalidation.

## 2026-10-13 — full-adapter screen принят; один corrective candidate запущен

Итог:[REPORT.md](analysis/2026-10-13-full-compression/REPORT.md).
Все6conditions/32freshcases/144modules complete, independentvalidationPASS.
Halfbudget:raw/W/structKL.000373/.000391/.000285;quarterbudget:.001930/
.001917/.002118. QuarterW/structоба14/1024argmaxchanges; fixedDнеустранилloss.
ПриhalfstructлучшеWна27.09%KL,приquarterхужена10.50%;CIexploratoryвvalidation.
Capture366.43s,prepare592.73s,evaluate391.64s CPUonly, GPU0ч;первыйworkerвышел.

Теперьодинобоснованныйcandidate:[SPEC.md](analysis/2026-10-13-radial-recalibration/SPEC.md).
Rank8quarter-size:closed-formcalibrationDпослеtruncationприfixedL/R,
exactweightedlocalobjective,тотжебюджет5,898,240. 2analyticaltestsPASS.
Новые64validationquestions исключаютиfullscreen32;source/procedurehashes
фиксируютсядоscores. CPU4prepare→CPU16evaluate, GPU0, неновоеобучение.
Новизнаgenericleast-squares/scalingнеобещается,совпадениесexactpriorнепроверено.
Операционныйlocatorlocal-only/radial-recalibration-20261013-private.json внеGit.
Следующийшаг:принятьlocalobjective/factorfreeze,затемheldoutqualityиprimary
candidatevsfixed-D;нетautomaticMistral/scalegrid/retryпослеvalidationfailure.

Candidatepreparation complete113.28sCPU4:144modules, L/Rbitwiseunchanged,
budget5,898,240;факторыи64новыхcasesзафиксированыдоmodeloutputs.
Калибровочнаясуммаlocalobjectivesулучшиласьна0.671%,medianmodulegain0.791%:
малыйproxygain,неподтверждённаяfunctionalпольза. NativevalidationCPU16идёт.

## 2026-10-13 — full-adapter compression screen запущен

Preparation принят:592.73s CPU4, все144modules; каждый из raw/W-SVD/structural
приrank16budget11,796,480elements, приrank8budget5,898,240. Structural D
overhead включён;48modules имеютr−1,96имеютr. Shapes/rank-derived totals
независимо пересчитанынаVM. EvaluationCPU16 начат, native reference собирается
на32новыхcases; qualityresultsпока нет. Всеweights/factorcaches насервере.

Capture принят:366.43s CPU16,64calibrationquestions,144source matrices иinput
covariance samples сохранены сSHA256; adapterexact и4native-referencebitwisePASS.
32новыхdevelopmentquestions замороженыдоscores. Independent safetensors header
audit:23,906,304sourceelements, всеF32, sourcepayload95,625,216bytes.
Preparation CPU4 идёт, первые3модуля~3.70s/module. Предполагаемыеbudgets
11,796,480/5,898,240elements. Никакиеqualityresults пока не получены.

Пользователь одобрил полный адаптер после отрицательного локального screen.
Дизайн доscores: [SPEC.md](analysis/2026-10-13-full-compression/SPEC.md).
Все144q/k/v/o, бюджетыordinary-LoRA rank16/8, триcontrols rawSVD/W-SVD/
structuralW-SVD с сохранениемD. D overhead включён в exactfactor budgets;
structuralranksr−1/r выбираются безscores. Это known-structure baseline,
не заявка на новыйalgorithm. Всеcalibration64 прежние;32developmentquestions
фиксируются доscores и исключают прежниеcal/validation/budget/testcontent.
3remoteCPUtestsPASS (equalstorage,thinQRoptimum,full tinyQwenrestore).
CaptureCPU16→prepareCPU4→evaluateCPU16, GPU0, никакогообучения/агентов/Mistral.
Операционныйlocatorlocal-only/full-compression-20261013-private.json внеGit.
Следующийшаг: принятьcapture, actualshapes/storage, затемpreparation и
парныеoutputs; приошибках сохранитьattempts и исправлять доответов.

## 2026-10-13 — бюджетный screen завершён, практический gate не пройден

Итог: [REPORT.md](analysis/2026-10-13-budget-screen/REPORT.md).
12conditions×16new development questions×32positions; во всехусловиях
491,520factor elements против993,792 у6исходныхмодулей (49.46% осталось).
Source и target tensorsFP32; selected payload3,975,168→1,966,080bytes.
Все12условий завершены: KL2.360e−6..9.775e−6, argmax0/512вкаждом,
allocated ranks одинаковы для всехтрёхsource gauges уraw иW-SVD.
Weighted allocation хужеuniform поKL, но абсолютные effects малы.
Это локальнаяteacher-forced оценка, не full-adapter compression/taskaccuracy.
Engineering gate не пройден; не разрабатывать исправление этой локальной
scale/norm ветки и не запускатьMistral автоматически. Общий поиск алгоритма
не закрыт. Следующая содержательная постановка —full adapter budget/task
сначала против сильных и structural DoRA baselines; см.CANDIDATES.md.
JointV/O сам по себе уже есть вLatentLLM; отсутствие приоритета не установлено.

Accepted CPU4prepare4.30s,CPU16evaluate854.53s,peakRSS20.42GB, GPU0ч.
Worker вышел; GPUs не резервировались. 2exact-budget и4tiny-model testsPASS;
referencebitwise4cases,adapterexact144,source/factor controlsPASS.
Первыйpreparefailed доanswers из-заabsoluteFP32orthogonalityguard; исправлен
наrelative после проверки residuals<=7.86e−7, всеattempts сохранены.
Raw per-case/source hashes/private manifests вlocal-only иserverrun,
операционныйlocator local-only/budget-screen-20261013-private.json внеGit.
Публичная папка содержитSPEC,CANDIDATES,REPORT,quality,decisions,validation,
manifest; версии/репозиторныеrevisions вvalidation.json.

## 2026-10-13 — начат бюджетный screen по новому решению пользователя

Пользователь одобрил поиск практической ошибки выбора представления, затем
обоснованное исправление. Дизайн до scores:
[SPEC.md](analysis/2026-10-13-budget-screen/SPEC.md).
Реализован exact-knapsack allocation по factor-element budget, проверен против
полного перебора на малых задачах. Переиспользуются старые rank32 factors:
fixed16 и ranks0..32 allocated, raw/W-SVD, прежние три source scales.
Бюджеты всех12условий точно равны; ожидается около50% параметров исходных
шести V/O модулей, а не всего адаптера/модели. 16 новых для compression
screen вопросов замораживаются до scores. CPU, GPU не резервируются.
LatentLLM уже рассматривает joint V/O compression: этот общий принцип
нельзя считать нашим новым методом. Алгоритм исправления пока не выбран.
Следующий шаг: принять preparation, bounded CPU model screen, проверить controls,
оценить абсолютные эффекты и решить, оправдано ли исправление/дальнейшая серия.
Mistral автоматически не запускается. Предыдущий отрицательный результат сохранён.

## 2026-10-13 19:05МСК — этапы1–3 полностью завершены, доMistral остановка

Итог: [REPORT.md](analysis/2026-10-13-compression-followup/REPORT.md).
Обаheldoutcomparison приняты независимымиstdlib checks;192distinct questions
(cal64+generic-val64+anchor-val64), selection/factor/data hashes проверены.
Genericgrid выбралc1, primarygain=0 точно. Base-anchored weighted procedure
выбралаt1, но на64новыхвопросах KL хужеW-SVD на3.4899%, delta+5.6542e−8,
family2CI97.5[+5.3786e−9,+1.1087e−7]. GoldNLL хуже+1.77045e−5,
secondaryCI95[+3.9530e−6,+3.1341e−5]. Исправление не прошло benefit criterion.
IdealFP64 canonical matrix residual≤9.52e−14: инвариантностьconstructionесть,
она не обеспечила лучшего компрессора. NativeFP32/BF16 universal bitwise claimнет.

Материалдляубедительнойmain-trackBзаявки текущимпакетомнеобоснован: candidateне
выиграл, ingredientsизвестны, одинcheckpoint/6матриц/shortprefixes, нетactual
quality/memory/latency выигрыша. ГеометрическийE99-budget sensitivity подтверждён,
не равен фактическойэкономиипротивnativeDoRA. Следующийшаг —вернутьсякпользователю
сфактами/оценкой; Mistral автоматическине запускать иgrid не расширять.

Accepted runs CPU only: capture316.81с,prepare82.81с,evaluate2827.32с,
anchor3083.47с, частичноparallel. Всеmodelprocesses вышли, GPUnotheld.
FailedGPULoad attempts≈.01772allocatedGPUч, scientificoutputsнет, cause второго
mismatchнеустановлена. Уточнение: supersededCPU4attempt содержит10outputs,
раньше5былоlatestsnapshotдоостановки;все10исключены. Всеattempts/caches сохранены.
Таблицы/validation records/versions/sourcehashes иmanualнаучныйразбор вновойпапке.
Rawinputsиoperationalpaths приватны. Статья не пишется, новыеочереди несозданы.

## 2026-10-13 18:39МСК — generic comparison принят

Первыйpipeline complete, independent validationPASS. Таблицыquality.csv и
validation.json вdocs/analysis/2026-10-13-compression-followup/.
Grid выбралc1 уrawSVD иW-SVD: primary improvement=0 точно, не отсутствие мощности.
На64newquestions W-SVD противrawSVD KL−21.5877%, pairedCI95delta
[−5.8210e−7,−2.1537e−7]; ноgoldNLL +7.7456e−5nat/token,
CI95[+1.5957e−5,+1.4061e−4]. Этоteacher fidelity улучшение, не task quality gain.
Accepted phases CPU: capture316.81с,prepare82.81с,evaluate2827.32с; GPU0ч.
FailedGPU attempts сохранены отдельно, не scientific data.
Anchor candidate выбранt1 поcalibrationдоегоvalidation; отдельные64newquestions
сейчасоцениваются, общийCPU8process. Остановитьсядопункта4послеanchorприёмки.
Mistral не запущен. Следующийшаг: дождатьсяanchorcomplete, принятьdisjoint192cases,
посчитатьprimaryfamily2CI и итоговуюоценкуB безпереводаKL вaccuracy.

## 2026-10-13 — этапы2–3 идут наCPU, добавлен корректный инвариантный кандидат

Generic comparison CPU16 выполняется послеexact adapter verification. GPUevaluate
был остановлен доответов: mismatch одногоadaptertensor, причинанеустановлена;
failed attempt сохранён, проверкинеослаблялись, GPU освобождены. CPUcapture и
weighted-factor preparation успешно завершены, повторятьнепотребовалось.

Доscoring новогоcandidate зафиксирован [SPEC.md](analysis/2026-10-13-compression-followup/SPEC.md)
сbase-norm anchored weighted procedure. В отличие отrelative grid, physical
candidate family инвариантно кpositive layer-wise V/O scalar gauges вточной
арифметике, включаяправильноеO covariance scaling. Этоизвестныйобщий принцип
canonicalization, неподтверждённаяновизнаконкретногопримененияPEFT.
ОтдельныйCPU8run запущен18:11:17МСК;4threads дляподготовки. СтарыйCPU16run
неизменялся. Егоvalidation64 исключеныизновойanchor-validation64. Обеданные
первичныхсравненийпубликуются; дляfamily2 считатьдополнительные97.5%CI.
Источникweights/активацийстарыйverifiedcapture, SHAпроверяются. Новыйunit-testPASS.

На18:12МСК anchor18factors подготовлены, nativecalibration reference выполняется;
generic4-еиз6calibration conditions ещёидёт. source/selection/validation frozen.
Никакогоtraining/Mistral. Продолжатьдополнойвалидацииобоихкандидатов, затем
честнооценитьзначимость,пользуиB, остановитьсядопункта4.
Операционныепути/PID впроектномignoredOPERATIONS_PRIVATE.md иworkspace local-only.

## 2026-10-13 — followup восстановлен после технического offload сбоя

Auto balanced GPU placement попыталосьdisk offload до первыхответов; run остановлен
guard, failed sources/logs сохранены. Исправленоsequential placement. Во второй
попытке GPU заняты чужимипроцессами; CPU4capture прерван после5примеров только
для перехода на16threads. Эти5outputs не используются. Никакие чужиепроцессы
не затронуты. Новаяпопытка запущена17:38:29МСК, новыйprivate pointer сохранён.
Модельные CPU phases16threads, whitening4; критериивыбора/validation прежние.
Контроллер ждётGPUпару120с, иначеCPU. GPU освобождаютсяпередprepare ипризавершении.
Продолжать до приёмкиэтапов2–3, Mistral не запускать. Следующийшаг: проверитьcapture,
затемfactors/calibration/замороженныйselection/validation. SPEC обновлён доscores.

## 2026-10-13 — пользователь разрешил этапы1–3, доMistral обязательный отчёт

Пункт1 выполнен: [DISCOVERY.md](analysis/2026-10-13-compression-followup/DISCOVERY.md).
Большой относительный drift сопровождается малым absolute KL/NLL и0/1argmax flips.
E99 parameter decision растёт1.99/2.51раза; nativeDoRA уже компактнее этихE99
представлений. Не обещать реальную memory/latency пользу из бюджетного proxy.
План сравнения доvalidation: [SPEC.md](analysis/2026-10-13-compression-followup/SPEC.md).

Новые CPU tests weighted objective2PASS. Pipeline capture→CPUprepare→evaluate
запущен16:41:46МСК. GPU admission после2проверок пройден, capture выполняется
вCUDAFP32 на2картах; incidentGPU исключена поindex/UUID. Послеcapture процесс
завершается и GPU locks освобождаются доCPUwhitening. При новомevaluate —
повторный admission. Backend reference пересчитывается, CPU/CUDA logits не смешиваются.
Методы: rawSVD и ridge-whitened W-SVD, c=1/.995/1.005, rank32/6матриц;
выборc поcalibrationKL, selection hash фиксируется до64validation cases.
Проверяются общиеbudget и matched-search SVD baseline, дубликаты не повторяются.

Все deployment сведения/private input paths в ignored OPERATIONS_PRIVATE.md.
Нового обучения нет; Mistral автоматически не запускается. Не заканчивать работу
на старте очереди: послеприёмкивалидации доложить пользу, значимость и перспективуB.
Следующий шаг: контролироватьcapture/prepare/evaluate, при ошибке сохранитьattempt
и исправить; затем провести paired heldout analysis и вернуться до пункта4.

## 2026-10-13 16:01 МСК — compression screen завершён

CPU run complete, wall5028.64с=1ч23мин49с, GPU0ч. Все technical gatesPASS,
условия полны,18SVD. Приватные compact raw inputs сохранены локально;
научный checkpoint: docs/research-direction/2026-10-13-road-to-b/screen-status.json.
На64cases/6матрицах оба practical gatesPASS: drift относительно исходногоC32
составляет86.58% и132.80% его действия, против native gauge RMS≈8e−6.
Это сравнение RMS logits, не проценты потери accuracy или доказательство уровняB.
Результат допускает следующий этап плана: проверить практические последствия
и проектировать исправление с сильным baseline; полноценный разбор ещё нужен.
Новых запусков автоматически не создано. Следующий шаг: принять per-case данные,
проанализировать E99/rank decisions и сравнения KL/NLL, зафиксировать следующий тест.

## 2026-10-13 14:49 МСК — прогноз compression screen

Pilot завершён за388.79с: все technical gatesPASS, оба practical gates такжеPASS
на4exploratory cases (не окончательный scientific результат). Screen реально
выполняется: первый свежий64-case dense контроль33/64,≈8.39с/case.
Остаётся около491forward плюсSVD/metrics: ориентир~70мин,
окончание≈16:00МСК, рабочий диапазон15:55–16:15. GPU не используется.
Следующий шаг: дождаться full screen и принять полноту/gates.

## 2026-10-13 — compression screen запущен по разрешению пользователя

Запуск в14:37:18МСК: CPUFP32,4threads,nice5, GPU не занимает.
Состав и условия: [RUN.md](research-direction/2026-10-13-road-to-b/RUN.md).
Pilot4cases/слой0 → при техническом успехе screen64cases/слои0/17/35;
c=1/.995/1.005,rank32, gauge только выбранныхV/O, остальные модулиnative.
Original cache используется после bitwise4fresh checks; иначе пересчёт.
Четыре новых CPU тестаPASS, включая tiny Qwen/DoRA и exception restoration.
Source/input hashes заморожены, веса/крупныеcachefiles на сервере внеGit.
Точные operational paths/PID сохранены в ignored OPERATIONS_PRIVATE.md.

Начальный ETA≈1–1.5часа по предыдущимFP32 timings; защитныйCPU cap4часа,
не целевой расход. Это exploratory compression screen, не новая accuracy оценка.
Rank32 полногоdelta не означает крупной экономии противnativeDoRA-r32;
source/target factor+magnitude element counts сохраняются явно.
Версии те же, что у предыдущего audit. Mistral/полные новые очереди не созданы.
Проверка14:40МСК: первые4fresh forwards побитно совпали с FP32 reference;
пилот реально выполняется, c=1 source-dense/factor-dense checksPASS.
Измеренные4-case условия≈35.6–35.8с; предварительный конец≈16:00–16:20МСК.
Следующий шаг: проверить полный pilot status, затем принять screen completeness,
fidelity gates и практический drift; при провале сохранитьfailed attempt.

## 2026-10-13 — выбран путь усиления научного вклада

Пользователь просит искать путь кB. Выполнены targeted literature search и
stdlib exact-rational CPU screen, новых model/GPU runs/обучения/агентов нет.
План: [PLAN.md](research-direction/2026-10-13-road-to-b/PLAN.md).
Артефакт compression-witness.json; код screen_compression_gauge.py.

Приоритет1: проверить практическую зависимость сжатия full delta от допустимой
V/O gauge, затем пользу исправления при равном параметрическом бюджете и
против activation-aware baseline. Два точных diagonal toy witnesses подтверждают
осуществимость; специально заданный близкий spectral gap усиливает эффект,
не выдавать его за найденную статистику Qwen. Простая pivot canonicalization
стабильна, но даёт28.57% operator error вместо0 в одном примере: отвергнута как
готовое решение. Прогноз качества реальной модели из toy не следует.

Приоритет2 резервный: проверить содержательные ablation contrasts в общем
backend и отделить dtype/backend. Generic precision уже занят ScalingDoRA и
precision-floor interpretability работами. Сам по себе рост entropy/ещё одна
модель не обеспечиваетB. CORE — рейтинг площадок, принятие не гарантируется.

Следующий шаг: минимальный CPUFP32 Qwen compression screen сначала4cases/
одна V/O пара, затем64cases/6матриц при фиксированныхc=.995/1/1.005 иrank32;
контроли dense reconstruction/gauge, проверка KL/RMS/реального бюджета факторов.
Предварительные engineering go/stop критерии прописаны вPLAN.md.
Короткая Mistral репликация отложена по приоритету до practically useful screen;
состав сохранён, очередь не создавалась. Новых вычислений автоматически не запускать
на основании этого поискового документа.

## 2026-10-13 — научный разбор fidelity/geometry завершён

Результат: [REPORT.md](analysis/2026-10-13-fidelity-audit/REPORT.md).
На6заранее выбранных V/O матрицах c=.995/1.005 увеличивает exp(H) в1.205–3.372раза;
H использует p=sigma²/sum(sigma²), определение SORA проверено по первоисточнику.
FP32 gauge RMS≈8.1e−6 против removeD.06073, 0/2048argmax flips.
Это checkpoint-level свидетельство неинвариантности геометрии при fixedW0/r,
не опровержение качества DoRA или корреляций на канонических training trajectories.

BF16 gauge RMS≈80% removeD RMS; официальный merge≈86%, а custom/official weights
побайтно одинаковы. Симметрия не служит BF16 numerical no-op. Эффекты removeD
между CPUFP32/CUDABF16 имеют pooled cosine.4835; dtype и backend confounded.
Не объявлять прежние accuracy эффекты artifacts. FP32 train-prefix NLL потеря
мала; BF16 интервал содержит ноль, уверенная смена знака не доказана.

Все per-case метрики/агрегаты/полнота пересчитаны stdlib-only на локальном CPU;
новых модельных запусков/обучения/агентов нет. Компактные raw inputs сохранены
приватно; научные таблицы, input/source hashes и версии — в новой папке анализа.
Код: execution/scientific-analysis/analyze_fidelity_audit.py. Версии прежние:
torch2.5.1+cu121, transformers4.57.1, peft0.17.1, safetensors0.6.2, accelerate1.11.0.

Следующий шаг: [MISTRAL_DECISION.md](analysis/2026-10-13-fidelity-audit/MISTRAL_DECISION.md)
рекомендует короткую64train×32prefix CPUFP32 репликацию, layers0/15/31,
c=.995/1.005, full-removeD включаяgate_proj; без full quality/grid.
Очередь не создана. Предыдущий полный Mistral блок заменён этим предложением.
Статью не пишем; подтверждённая новизна/готовность main conference не установлены.

## 2026-10-13 — аудит завершён, GPU освобождена

Проверка в 13:46 МСК: обе фазы thesis-audit завершились успешно, exit_code=0.
GPU: 134.18 с (0.0373 GPU-ч). CPU: 2357.76 с, четыре потока.
Всего около 41 мин 32 с без ожидания допуска. GPU освобождена перед CPU-фазой.
Новых запусков не создано. Ошибок и срабатываний canary не зарегистрировано.

Официальный и наш dense merge побайтно совпали по всем 144 attention-проекциям
в обеих фазах. FP32 fidelity gate пройден: средний RMS изменения logits
при V/O gauges .995/1.005 составил 0.01337%/0.01327% среднего RMS эффекта removeD.
Получены 18 спектральных измерений и 9 FP64 block checks.
Это техническая проверка на 64 train-примерах, не benchmark accuracy и не
окончательный научный вывод. CPU FP32 и CUDA BF16 различаются также backend.
Версии, hashes и полные summaries сохранены в артефактах очереди;
точные серверные пути находятся в приватном operational checkpoint вне Git.

Следующий шаг: разобрать fidelity/geometry совместно, проверить величину изменений
геометрии при сохранении функций и решить, оправдана ли проверка на Mistral.

## 2026-10-13 — аудит поставлен в отложенную очередь

Пользователь разрешил очередь и разумный бюджет вместо прежнего предложения2GPU-ч.
Подробный зафиксированный состав: [QUEUE.md](research-direction/2026-10-13/QUEUE.md).
Финальный контроллер запущен11:41МСК и проверен живым. Последний проверенный
статус: pending, подходящей GPU нет. Допуск прежний: utilization<20%,
used<7168MiB,2последовательные проверки через10секунд. Неисправная карта
исключена по индексу и UUID, точные deployment сведения приватны.

Одна GPU-задача Qwen fixed-prefix64train×до32target tokens: original,
локальные V/O magnitude gauges .995/1.005, removeD, custom/official dense merge.
Технические repeat/gauged-removeD checks только4примера, не полный no-op benchmark.
Измеряются full-vocabulary KL, max/RMS logits, margins, argmax, gold NLL,
байт-хеши144проекций и прямые official/custom logits на4примерах. Immutable
canary и CPU finite readback останавливают обнаруженную порчу.

После завершения GPU-процесса VRAM и lock освобождаются. CPU-процесс без видимых
GPU повторяет те же входы в FP32, до4threads. Если fidelity gate пройден —
18SVD selected V/O matrices, слои0/17/35, три c, и независимый FP64 block check.
GPU phase cap5400s, CPU cap14400s — защита от зависания, не ETA/целевой расход.
FP32 CPU vs BF16 CUDA меняет backend вместе с dtype, не выдавать это за чистое
доказательство причинности precision. Модели не обучаются, test не используется.

7реальных CPU тестов PASS: tiny Qwen3/DoRA, обе функции, exact state restoration,
official/custom bytes/logits, target alignment, NaN guard, admission boundaries
и GPU-lock release доCPU. Локальные3standard-library checks такжеPASS,
4model tests локальноSKIP из-за отсутствияTorch; на сервере прошли все7.
Код thesis_audit.py/fidelity_audit.py; существующий admit_queues переиспользован
с приватной спецификацией. Source hashes фиксированы до обеих фаз; не менять
их во время ожидания/исполнения без отдельного согласованного перезапуска.

Приватный operational checkpoint содержит controller, root, manifest и логи;
серверные сведения не добавлялись в научные файлы. Все большие logit caches
остаются на сервере внеGit. Старые данные и попытки сохранены. Первый pending
контроллер заменён до допуска любой GPU-задачи, чтобы добавить прямой merge check.

Следующий шаг: проверить admission и per-phase summary, при ошибке исправить
с сохранением failed attempt, затем принять результаты fidelity/geometry.
Полная Mistral очередь не создана; её состав зависит от конкретного итога.

## 2026-10-13 — поиск содержательного тезиса

Новый документ: [THESIS.md](research-direction/2026-10-13/THESIS.md).
Проведены целевой literature search и CPU screen существующих таблиц,
агенты/GPU/новое обучение не использовались. Кандидат — ограничение
геометрического объяснения необходимости D при сохранении fixed base/DoRA-r
и обеих функций пары original/full-removeD.

Выведено mV→c*mV,mO→mO/c с неизменными A/B/W0. В точной арифметике сохраняются
исходная функция и функция после совместного полного removeD. Точный рациональный
toy witness rank1→rank8 и рост entropy при тех же функциях проверен на CPU.
По сохранённым FP32 summaries Qwen отношение ||R||/||Delta|| при c=1.005
меняется17.938%→26.765%; это algebraic reconstruction, НЕ runtime verification.
Generic V/O symmetry известна; точное fixed-base/adapter-r/both-functions
уточнение остаётся кандидатом новизны, не доказанным приоритетом.
Неинвариантность не опровергает качество DoRA или причинность её обучения.

Дополнительно: custom dense conversion меняет53 правильности против64 уremoveD,
пересечение32. Это descriptive screen, не доказательство numerical causation
или ошибки официального PEFT merge. Код screen_thesis.py, artifacts в новой
папке с hashes. Новый proposed audit до2GPUч: module/FP64 proof checks,
64непересекающихся train fixed-prefix fidelity cases и сверка custom/official
merge/FP32. Он ещё не реализован/не запускался; потолок не ETA.

Полный Mistral блок отложен. Его следующий возможный смысл — короткая независимая
проверка конкретного тезиса после gate, не автоматическая новая quality серия.
Старое предложение трёх/четырёх full runs не считать активной очередью.
Следующий шаг: оценить новизну exact statement и подготовить ограниченный аудит
по THESIS.md; полные GPU-очереди автоматически не запускать.

## 2026-10-12 — анализ новых A/B/C завершён

Актуальный checkpoint: [REPORT.md](analysis/2026-10-12-next-experiments/REPORT.md),
решение о следующей паре: [MISTRAL_DECISION.md](analysis/2026-10-12-next-experiments/MISTRAL_DECISION.md).
Все восемь новых full jobs завершены: два контроля GSM8K, removeD MMLU/SQuAD,
четыре NLL. Полный свежий directional1319 принят для анализа; старый прерванный
прогон/префикс исключены. Агенты не использовались, GPU-прогоны не добавлялись.

Пересчитаны метрики111574ответов14файлов; полнота/prompt/token hashes, revisions,
общие исходники, версии, фактические hashes датасетов и отсутствие пересечения
232calibration/test проверены. Нет обнаруженного `!` вырождения; все принятые
summary относятся к устройствам, отличным от устройства с воспроизведённым
сбоем памяти. Это не полная сертификация hardware или finite arithmetic.
Версии torch2.5.1+cu121/transformers4.57.1/peft0.17.1/safetensors0.6.2/accelerate1.11.0.
Все hashes прочитанных scientific inputs/кода — validation.json и input-audit.json
в новой папке. Raw ответы и соответствие operational paths хранятся приватно.

Итог A: removeD1038/1319, permuted1029, directional1037, originalDoRA1026.
Два primary finalEM контраста Holm2 p=.671/1.0; специфичность D не установлена,
эквивалентность также не доказана. Heldout aggregate energy ratios1.0113/.9887;
идеальный/native радиальный RMS mismatch55.88% ограничивает геометрический вывод.
B: MMLU−.0356п.п.CI95[−.2335,+.1623]; SQuAD exact−.2190[−.4143,−.0237],
номинальноеp=.0342, exploratory transferHolm2=.0685. Скрытой компенсации между
answerable/unanswerable не найдено. C: NLLremoveD−DoRA+.0004987nat/token,
PPL+.0499%, block16CI[+.0001821,+.0008148]; эффект очень мал и precision-sensitive.
Новые принятые full jobs26.0983GPUч wall, без ошибок/пилотов — исходный25ч cap
уже превышен; исторические130.997635 были inference-only, не складывать напрямую.

Оценка: материал для узкой exploratory workshop-работы; готовность Findings/main
не установлена. Независимое семейство и численная проверка важнее новой сетки.
Mistral скачан и проверен, inference не выполнялся. Рекомендовано ядро
DoRA/removeD/matched-directional, LoRA дополнительный контекст при бюджете.
Охват gate_proj обязателен; авторский5-shot протокол фиксировать отдельно.
Provenance не закрыт: доступный авторский scriptr8/e02 отличается от выбранного
r16/e03. Без восстановления происхождения разрешён лишь ограниченный
within-checkpoint вывод. Потолок20GPUч — лимит, не измеренный ETA.

Следующий шаг: обсудить MISTRAL_DECISION, затем отдельный численный/временной
пилот и решение о полном блоке. **Новые очереди автоматически не запускать.**
Ни статья, ни новая сетка локализаций не готовились. Ниже — исторические записи.

Pending restart admission memory threshold updated at user request to strictly below 7 GiB (7168 MiB), retaining utilization below 20%, two consecutive checks, and excluded-device policy. Existing active evaluation unchanged. Evaluator retains its independent free-memory guard.

## Full restart queued after numerical incident

At user request, the diagnostic reservation was released and the directional evaluation scheduled for a fresh full run, including all 1319 questions and calibration. Provisional partial answers are retained separately and will not be reused. The original admission controller now supports an isolated output root and explicit device exclusions. Admission policy remains two consecutive idle checks. Admin report and operational identifiers are stored privately outside Git. Existing permutation evaluation continues independently.

## Partial response preservation

Saved the first 456 directional responses verbatim, with checksums and original calibration/summary snapshots, in private storage on both machines. First obvious degeneration occurs at zero-based index 456; subsequent 99 responses are excluded. Prefix is provisional: silent corruption onset is unknown. Screening of the first 421 permutation responses found no analogous degeneration. Independent memory verification could not run within remaining device memory. Operational details remain private.

## Numerical anomaly checkpoint

Directional control paused at explicit user request; partial predictions retained and not accepted as a completed quality evaluation. Disk checkpoint hash matches its source. A separate immutable-buffer test reproduced data corruption independently of the model and interventions. Exact system cause remains unresolved. A CPU finite-score guard now stops future generation on NaN/Inf; finite scores are returned unchanged. Operational evidence is private. No new full runs were started during this diagnosis.

## Mistral download initiated

Pinned Mistral-7B-v0.1 and the selected fzzhang r16/e03 LoRA/DoRA pair are downloading. Safetensors and tokenizer/config files only; duplicate PyTorch weights excluded. Integrity checks and shard-index completeness run automatically after download. Status is pending completion, not an inference result. Exact operational paths remain private.

## Clean publication completed

Public branch research/prepare-checkpoint-study was replaced with root commit 68e47ae51b95a104c24f058c3ee135cd3dc65606. Scientific code and reports were exported separately from private deployment records. All 19 published scientific tests passed. Execution state and access details remain in ignored OPERATIONS_PRIVATE.md.

Permuted control also restarted in a separate attempt directory after explicit user authorization. Existing memory safety guard retained; full evaluation not yet completed. Operational state is private.

## Control runner fix, 2026-10-12

Added missing math import used by realized-strength refinement. Eight runner tests passed. Directional control restarted in a separate attempt directory; original failure evidence preserved. Full evaluation has not yet completed. Operational details are in ignored OPERATIONS_PRIVATE.md.

## Existing-data followup completed; article writing deferred — 2026-10-11

## 2026-10-12 — очистка и подготовка публикации

Python caches удалены; временные pilot-checkpoint и незавершённый provisional
отчёт перенесены в local-only/cleanup-20261012 вне Git. На сервере исходные
артефакты и работающие очереди сохранены. .gitignore дополнен scratch patterns.
Полный локальный snapshot коммитится отдельно; публичная публикация создаётся
поверх d3e324a, без приватных ancestors. Публичные научные документы/код
обезличены; raw provenance/validation не экспортируются, исходные hashes
относятся к частным оригиналам. Публичный PUBLIC_EXPORT.md фиксирует это.


## 2026-10-12 — поставлены три полные очереди по прямому поручению

Прежняя остановка отменена новым поручением. Контроллер PID3275551 запущен
на сервере; очередьpermuted → directional → bundle(MMLU,SQuAD,4NLL).
Проверки10сек,2подряд utilization<20% иused<2048MiB, отдельнаяGPUнаочередь.
Код существующих admissions/evaluator переиспользован, агенты не создавались.
Подробности docs/experiment-plan/2026-10-11/QUEUES.md; состояние
/path/to/user-user/lora-dora-profiling/next-experiments-queues-20261012/admission.json.
CPUпроверкиPASS. Между заданиями внутреннегоidlewaitнет. Контроли получили
training-only refinement BF16силы; heldout32толькоаудит, не подбор.
Следующийшаг: читатьстатусы/результатыпоставленныхочередей, не создаватьдубликаты.


## 2026-10-11 23:53 МСК — работа остановлена пользователем

Точка продолжения docs/experiment-plan/2026-10-11/STOP.md.
MMLU/SQuAD short pilots завершены; GSM8K permuted partial сохранён и PID2430867
остановлен, VRAM освобождена. Directional/NLL GPU pilots не выполнены.
Итоговые прогнозы не приняты; refinement/forecast агентские задачи прерваны.
Локальные копии pilot-checkpoint/, сервер profiling/next-experiments-20261011/.
Новые/отложенные/полные очереди НЕ запускались. Продолжение только после
нового поручения пользователя; экономить лимиты, уровни снижены на1ступень.


## 2026-10-11 — план следующих экспериментов и замена закрытых баз

**Сделано:** подготовлен docs/experiment-plan/2026-10-11/PLAN.md с вопросом,
двумя контролями сопоставимой силы, переносом на MMLU/SQuAD, проверкой общего
текста, условной Mistral репликацией, бюджетами и критериями остановки.
Новые GPU/модельные прогоны не запускались, агенты для планирования не создавались.

**Доступ:** пользователь сообщил, что все HF заявки отклонены. Answer.AI/gated
Llama исключён из следующего блока. Анонимно проверены открытые Mistral база
и парные адаптеры fzzhang r16/3epochs; происхождение dataset конкретных файлов
ещё требует аудита. AraT5 доступный резерв, но dataset неизвестен. У snunlp
EXAONE/Qwen2 имена видны в API, README/config обеих пар HTTP401: не готовы.
Снимки revision/gating/config и короткие weight probes:
docs/experiment-plan/2026-10-11/open-candidates-audit.json. Проверка доступа
не означает успешную загрузку. Никаких зависимостей не меняли.

**Бюджет:** A/B/C предложены до25GPUч; дополнительный резерв5GPUч и Mistral
до20GPUч условные, не очередь и не измеренная ETA. Скорость нового кода измерить
пилотом. Фактические старые GPU-времена и ограничения выводов указаны в плане.

**Далее:** обсудить состав, затем короткое ТЗ пилота сопоставимых контролей и
ограниченный аудит Mistral. Не повторять полный перечень локализаций/сжатий,
не создавать инфраструктуру приёмки ради простых производных таблиц.
Статью не пишем, обучение не проводим. Предыдущий frozen bundle не изменён.


Latest user direction: finish analysis of existing data first, then choose and
launch next experiments. More GPU runs are expected later, not cancelled.
Do not write the article or paper outline in this stage. This supersedes the
older positioning document's suggestion to draft an outline next.

New explicit specification: docs/analysis-followup/2026-10-11/SPEC.md.
Three delegated packages (gpt-6.1-sol): A/high direct paired contrasts
remove_D/reset-vs-LoRA and Q-vs-K, 8 exact McNemar/Holm hypotheses with separate
paired bootstrap CIs; B/high common-reference repairs/breaks overlaps, all8
selected runs and both scorers; C/xhigh robustness across46 accepted contrasts
using shared-example bootstrap simultaneous bands and a fresh9claim ledger.
New code execution/existing-data-followup/, outputs A/B/C under newdocsdir.
All numerical work on serverCPU, <=2threads/package, no model/GPU runs or
weights/download/install. Frozen analysis/bundles/AGENTS/MEMORY stay unchanged.
A complete with37140checks/PASS, independently accepted with B/C below.
remove_D/reset-all vs LoRA final+1.9712pp, Holm8~.0994; no established gain.
remove_D Q-minus-K author+1.7437pp, Holm8=.03035; final+1.5163pp,
Holm8=.08350. Scorer-dependent signal, not robust Q/K mechanism. A codeSHA
8bedb47487d9c22a2c0485e4ba4597f093f7992198f8d749f7ccbe88890d2cd7,
manifestSHA16f84fbf4c99d6ef3db49bba9a1b5ab39b89cfc9f0d563dfc9fb07a37ddfbc91.
B complete with388checks/PASS and author650read-only crosschecks. On finalEM,
remove_D/reset both1038/1319correct but differ in correctness on62cases;
repairs shared20,breaks shared14,changedcorrectness Jaccard34/96=.3542.
Thus close means coexist with materially different changed-example sets,
not evidence of identical texts/functions or a shared/different mechanism.
B codeSHA19466bd9288a6bae4939defc141d91eb17d442141bc0205a43d9685f16b0a6a7,
manifestSHAaad3fd1da52493b69e9762496f0f59a3139a8988b8fa3c05096bfebca615ecfc.
C complete:424checks/PASS,46contrasts/50kcommonbootstrapdraws/187patterns,
q95=1.743745pp. removeD/reset simultaneous46 lower−.834pp(final):loss1pp
criterion survives, .5pp onlypointwise. rank32/E95vsoriginal lower−1.592/
−1.516pp:2ppcriterion only. E99vsoriginal final lower−2.047pp:not even2pp.
These are exploratory approximate family46 intervals, not whole-search or
training uncertainty; A8 is separate. Nineclaim newledger updatesL5activity.
C codeSHA8efaa2d56043c60d0415534de02ad2af48ed2eb44b95bc2c725bf6adc4dbb6bb,
manifestSHA36e573d437679f8966fdb4fd069c6724def935481629debdd2694fe7e59902b4.
Rawdraws onlyserverprofiling/analysis-followup/2026-10-11/C-robustness/,
SHA4727b80fbcd6d1bd9267506e62ba5cb65bacf7a5ddac8f735fcd2933fa6ce528.
Independent final A/B/C acceptance PASS/complete=true,659checks/zeroerrors,
mirror33checks/PASS. VerifierSHA
d90b7c1b618d08950b342b91e9c382e98b1645b45d66f33fb22f7787d212348b;
acceptanceManifestSHAcdfd7a54404c80768af19787285acf006d1b66bea8229fb8f9dd61085edfaf88.
Versions Python3.12.3/NumPy1.26.4, CPU<=2threads/package; no dependencies added.
All Abootstrap8 independently reproduced; B16/56/42tables and2638patterns
and9ledger verified. Root scientific synthesis accepted in
docs/analysis-followup/2026-10-11/ANALYSIS_SUMMARY.md. Acceptance artifacts:
acceptance/REVIEW.md,validation.json,manifest.json,mirror-verification.json.
Old verifier explicitly not run because it writes historical manifest/report.
Existing-data stage complete. Next: jointly choose hypotheses and the concrete
next GPU experiment set; no queues/models/conditions chosen or launched here.
Article/outline deferred by user. Frozen artifacts preserved; current stage0GPUh,
local/server compact mirrors; no Git commit/push.

---

## Publication positioning and primary-source claims audit — 2026-10-11

User asks whether further existing-data analysis and publication are worthwhile,
and which actual literature claims are supported/refuted. Completed primary-source
review, delegated to two gpt-6.1-sol/high agents, root accepted scientific synthesis.
New files: docs/positioning/2026-10-11/REVIEW_SPEC.md, COMPARATORS.md,
CLAIMS_RECHECK.md, POSITIONING.md. No changes to frozen analysis/manifests,
no model downloads, quality runs, training, GPU work or publication this stage.

Six officially accepted comparators checked across NeurIPS/ICLR/TMLR/ACL/Findings;
one workshop acceptance remains author-supported only. Main examples: Intruder
Dimensions NeurIPS2025 (posthoc intervention, neighboring-direction control,
forgetting endpoint), LoRA Learns Less TMLR2024 (empirical regime/control study),
How Much is Too Much Findings IJCNLP-AACL2025 (rank/transfer study). Official
review criteria permit analysis/negative findings without a new adapter or SOTA.
This is contribution-type evidence, not an acceptance probability or novelty score.

Literature correction: SORA is verified AAAI2026, not merely a preprint. Its
spectral theorem is not an accuracy/necessity theorem. No whole-paper refutation
claimed. DeLoRA AppC already freezes magnitude DURING training; our posthoc
remove_D is distinct and keeps DoRA-trained A/B. Generic posthoc compression,
high-rank delta and lack of universal DoRA advantage are prior art. New activity
diagnosis closes old L5 measurement gap without rewriting frozen claim CSV.

Scientific assessment: material for a focused endpoint empirical paper exists;
TMLR/Findings are meaningful goals after evidence/synthesis improvement, workshop
paper can be scoped to present evidence. Main-track ambition needs a stronger
discriminating/generalizable result. No promise of acceptance. Current strongest
observation: active D perturbation (~17.94% update norm) with close mean GSM8K
accuracy, despite changed answers. D-specific dispensability, training cause,
independent replication and general superiority remain unestablished.

Proposed bounded EXISTING-DATA next work, not executed: (1) paired direct
remove_D vs separately trained LoRA and Q-vs-K contrasts, explicit exploratory
family; (2) cross-intervention overlap of repaired/broken answers; (3) fresh
claim synthesis and robustness to scorer/reference/posthoc margin/multiple search.
Then paper outline. Technical implementation requires specs/delegation. Independent
pair and equally strong alternative perturbation are highest-value new-data
options, require a concrete next plan; no automatic Answer.AI batch/download.
New reports kept locally and mirrored on research server, no Git commit/push.

---

## Radial activity stage completed — 2026-10-11

User point1 completed on existing GSM8K weights. CPU6947checks/PASS;
CUDA+CPUjoin2381checks/PASS for144modules/313344rows. Actual CUDA quotient
is FP32, g==1 at4rows; medianabs(g-1)0.00233293,p990.01111308. CUDA-vsCPU
surrogate maxgerror1.073e-6,vs ideal3.684e-5. Weight-normalizer proxy
removeD/fullDelta17.93798%,reset17.97764%; ideal17.93785%/17.97717%.
This is18%norm, about3.22%squarednorm, not18%parameters or unique information.
DenseBF1646.713%elements changed. Earlier fullquality closeness therefore
coexists with measurable endpoint changes; no trainingcause/novelty claim.

CUDA4 full162.99s incl25.09sinitialSHA/IO; tensorwall10.47s includeshostgaps,
notpurecompute. Approxcontextresidency137.90s(~0.0383GPUh) throughmetadata,
not allpilot/failedattemptcost. Allocatorpeak253.22/278MiB,respectively;
samplednvidia480MiB notcontinuouspeak. GPU PIDs exited, separately verified;
noGPUholdingforCPUjoin17.24s. Finalpilot/full useidenticalfrozen codeSHA
ccfdfe72b1a5e6383c6501e834a8b76c8b60f909c3b8b0abf5f44ede769a2768 and
inputhashes. Earlierpilot archived afterjoinreportonlycodechange; original
sourcebytes notsaved, finalsamecodepilot rerun. Twoinitialcleanupvalidation
failureslogged; backendworkspace notmistakenforownedtensors afterfix.
CUDAmanifestSHA59469490348f65a84b84edd1b4290dbe3fbfa7f08b51dbbc1db04a0a0afecadb.
Independent CUDA acceptance:5outputhashes/code/3CPUdeps/rawCPUrowSHA match;
recomputed all/Q/K/V/O energies/counts/ratios zeroissues. Pilot/full n/gmaxerr0.
2381checks=11join+1745full+625pilot, allpass. No blocker for statednormscope.

FINDINGS.md and all compact CPU/CUDA tables in
docs/diagnostics/radial-activity-2026-10-11/ locally/server. Rawrows/logs/
archives in /path/to/user-user/lora-dora-profiling/radial-activity-2026-10-11/.
Source execution/radial-activity/. Frozenanalysis/bundle preserved. No new
models/fullquality/training/dependencies. New diagnostic costs separate from
historical130.997635GPUh accepted fullinference. Newstage notpublished.

Next scientific priority: independently reproduce active-radial-change with
meanquality preservation, preferably one Answer.AI pair afterloader/access
validation and a concrete budget; control equallystrong alternativeperturbation
to distinguish D-specific robustness. No automaticfull Answer.AIbatch/newtraining.
Norm-onlyCUDA verifies g/weightproxy, not activationbranch effectiveweights,
logits, qualityequivalence or causes ofoptimization. FINDINGS gives oldpaired
quality CI and posthocmargin/multiple-search limitations.

---

## CPU accepted before CUDA control — archived stage entry

Completed CPU measurement:144modules/313344rows/6947checks/PASS. First4module
pilot/full rows exactly match; independent read-only formula/aggregation/hash
review passed. Ideal removeD norm/full adaptation norm17.9379%, square-norm
ratio3.2177%; magnitude reset17.9772%. Relative to base only0.34414%, so the
reference matters. Dense BF16 removeD changed440839223/943718400 elements
(46.713%), only146fullyequalrows; perturbation/full BF16update norm21.5653%.
BF16(g)==1 for167261rows but167115ofthose still have changed denseweights;
this quotient cast is counterfactual, actual installed g is FP32. Typical
abs(g-1)median0.002333; no zero/nonfinite norms or m. CPU surrogate g exact1
at5rows versus ideal1row; this does not establish CUDA/fullfunction fidelity.

Wall146.58s/hash26.34s/measurement119.30s,peakRSS958.7MiB,2CPUthreads.
Python3.12.3/Torch2.5.1+cu121/NumPy1.26.4/PEFT0.17.1. First toy tolerance
2e-6 narrowly failed2.10e-6, corrected toy-only3e-6 with firstlog preserved.
CodeSHA d8e7ad824cdf458a1c0a328a4b79e4b11f152c911b677e2e08d8a6010bac9164;
manifestSHA81859bfb4b609a0c95b2a53aca6cf3b5fb3052b2e460e422fe316ffbdb32dd6d.
New findings and compact tables in docs/diagnostics/radial-activity-2026-10-11/.
Raw rows/logs /path/to/user-user/lora-dora-profiling/radial-activity-2026-10-11/.

CUDA_PROBE_SPEC.md adds one-GPU norm-only check using existing tensors, without
fullmodel/calibration/generation/training. User allows partiallyoccupiedGPU.
CUDA4chosen on current headroom/load;4module numerical pilotpassed, cleanup
assertion mistook retained cuBLAS workspace for tensors; failedprocess exited,
log preserved. Agent corrects cleanup reporting then runs144ifpilotpasses.
GPU must be released immediately; no GPUhold while waiting for CPU joins.

Scientific stage conclusion: interventions measurably change endpointweights
yet earlier mean GSM8Kquality remained close. This is not evidence of unchanged
function, radial uselessness, trainingcause, superiority or established novelty.
FINDINGS.md gives precise quantities and prior quality CI with posthoc caveats.
Next finish CUDA control, then plan independent targeted replication; no
automatic Answer.AI/fullquality run or newmodeltraining.

### Original authorization and design

User explicitly requested point1 of the stronger-result plan; mentor report is
already delivered. New specification, cached-input inventory and precision
review are in docs/diagnostics/radial-activity-2026-10-11/. Delegated streamed
CPU measurement of144 Qwen3-4B/GSM8K adapted modules, using existing pinned
weights and at most2threads. No training or full quality rerun. Technical work
uses gpt-6.1-sol, low/high/xhigh; no max/ultra. New artifacts separate from
frozen accepted analysis. Script: execution/radial-activity/analyze_radial_activity.py.

Precision review found actual PEFT ratio g is FP32 despite BF16 base/autocast;
rounding g to BF16 is a counterfactual, not runtime inactivity. Compare ideal
geometry, dense BF16 endpoints and CPU implementation surrogate separately.
Endpoint m-minus-base norms cannot identify learned movement: initializer,
norm precision and training base provenance remain unknown. Weight SHA values
come from configs/shadow_qwen3_4b_gsm8k.json; downloads manifest records paths
and revisions. Next: accept toy/pilot checks, measure full144modules, interpret
activity relative to whole adapter change and assess bounded CUDA control.
This paragraph records the original design; measured current state is above.

---

## Existing-data scientific analysis completed and integrated — 2026-10-11

Latest preferences are in MEMORY_CONTINUATION.md. Historical MEMORY.md/AGENTS.md
are included in immutable bundle43 and must keep their original bytes. Root
post-verification local mirror check detected a changed MEMORY hash after
syncing current preferences; original frozen MEMORY bytes restored from Git
with exactSHA b002858c97ffa058e6d6fb791f06f1314b133b40375c567064c15813452f8e9a.
No scientific result changed; new preferences preserved separately and here.

User-requested continuation completed Q/C/L/T synthesis and all L1–L9 claims.
Final read-only integration PASS:1258checks,238hashed files,zeroerrors,
complete=true,pending=[],immutable_sources_modified=false. Root independently
checked local report flags/check count and manifest SHA. Artifacts/code mirrored
on server and locally: docs/analysis/2026-10-11/results/{REPORT.md,limitations.md,
claim-evidence.csv,theory-review.md,analysis-manifest.json,integration-validation.json};
verifier execution/scientific-analysis/verify_analysis.py --final. ManifestSHA
bc9d188e8460a9f3b56c1319b0dda58d8a7c3387131007cccee11dbb3803c9ed;
verifierSHA77149d849f13b0e457672b47be83f0ce83217580c8caf05ec6d2d93d336d5735.
Q946/C1507/L1213package checks retained. Final integrator verifies hashes,
counts/schemas/references, paired deterministic estimands/transitions/Holm;
it does not rerun bootstrap or substitute for root scientific review.

Scientific conclusions: no established DoRA−LoRA quality advantage in three
task-specific Qwen3-4B pairs. Global radial interventions satisfy pointwise
0.5pp loss criterion but alter answers; removeD repairs38/breaks26 final cases.
This endpoint is in fixed-base additive LoRA-r family with DoRA-trained A/B;
not equivalent training or independent LoRA replication. Rank32/E95 satisfy
pointwise1ppcriterion vsoriginalDoRA; actualBF16delta rank unmeasured. Local
Q/K estimates descriptive,8joint CI include0,Holm8p1; additivity not proved.
Specific scalar V/O map fixed-baseDoRA-r admissible; FP32rho changes slightly,
no signflip; denseBF16short64error0 separate from deployedrho/PEFTfidelity.
No causal training mechanism, isolated entropy effect or unique novelty established.

T review accepted with corrections to hash provenance,identity vsnonidentity
matrix counts,endpoint vsinitialization/training and sourceclaims. Root corrected
literature Shortcuts partial-reversion wording: alternative/boundary case,
not separate verified sweep. Historical review SHA refers to prior version.
QhistoricalSPEC hash remains explicitly documented/unavailable; original
validation preserved and current Qdata checked independently.

CPU only,Python3.12.3/NumPy1.26.4,max2threads/task,no dependencies,weights/model
forward/SVD/training/GPUh added. User assistantmodelgpt-6.1-sol,L/Ihigh,Txhigh;
max/ultra not used. Confirmed acceptedfull inferencecost130.997635GPUh,
baseline25.172667/intervention105.824969; excludes historical overhead/attempts/
heldGPUtime, not totalcampaigncost. Mentor-facing plain-language summary was
updated outsideGit, then deleted at the user's explicit request. Scientific
REPORT and accepted artifacts preserved. Repeated final verification after
restoring frozenMEMORY passes1258checks/238files/noerrors; final manifestSHA above.

Next: discuss scope/novelty and whether a targeted Answer.AI check is warranted;
no automatic new model experiments, no Qwen3-8B/LLaVA. New analysis continuation
not published. Only earlier redacted GitHub snapshotd3e324a is public; private
history/operational context remain local. Currentstate CHECKPOINT.md overrides
archived stop notices; root will not edit hashed artifacts after final acceptance.

---

## Package L completed and accepted — 2026-10-11

Continuation finished L on server CPU with Python3.12.3/NumPy1.26.4, at most
two numerical threads. Missing matplotlib caused the previous plot-stage
failure; build_localizations.py now uses dependency-free SVG. No estimator,
seed, bootstrap, input or evaluator changes; no dependencies/model/GPU runs.
All1213checks pass, hashes verified:28effects,8paired interactions,84transition
rows, SVG28intervals, localization-findings.md and localization-validation.json
in docs/analysis/2026-10-11/results/, mirrored locally and on server. CodeSHA
d5e8d16d2568bc2b0a846748d16ec6d118e1f5f78f17dbe6f5c38753d8ecef9a.

No localization CI excludes0; none significant under globalHolm40. Qpositive/
Knegative estimates under both interventions remain descriptive; directQ−K
contrast not tested. All8interactionCI include0, Holm8p=1; this does not prove
additivity. Pointwise loss-exclusion counts at0.5/1/2pp are11/20/28 of28cells.
Global radial final+0.910pp; removeD repairs38/breaks26, baseMagnitude39/27.
Accuracy preservation is not preservation of answers/function. Next:T review,
L1–L9ledger/REPORT and integrated read-only acceptance. Old Lpartial entries
below are historical. Other research scope and privacy policy unchanged.

---

## Scientific analysis resumed — 2026-10-11

User explicitly resumed scientific analysis. Assistant model gpt-6.1-sol,
reasoning at most xhigh; never max/ultra. Latest execution plan:
docs/analysis/2026-10-11/RESUME_SPEC.md. Q/C retained accepted; completing L,
independent T review and read-only integrated verifier in parallel. No new
model runs, weights/SVD, GPU usage, training, dependencies or automatic
Answer.AI validation. Immutable bundle/evaluator/original predictions preserved.
Historical stop notices below no longer prohibit the user-requested analysis.

Publication correction: redacted 28-file scientific snapshot successfully
published to research/prepare-checkpoint-study as d3e324aa398da5af0a5698bdb583522ed16ad110,
under reports/redacted-scientific-snapshot-2026-10-11/. Original/private local
Git ancestry was not pushed. One script excluded by automatic review;
operational/access context remains local-only. Earlier blocked-publication
entries below describe the prior attempt, not the current branch state.

---

## User declined public operational disclosure — 2026-10-11

User explicitly declined publication of infrastructure/access context and requested a separate local-only file. Central private snapshot: workspace local-only/OPERATIONS_PRIVATE.md outside Git, permissions0600/directory0700. See docs/analysis/2026-10-11/PUBLICATION_POLICY.md. Do not push the current private history: deleting details in a later commit does not remove them from ancestors. Raw provenance, validations and existing bundles stay local/private. A separate redacted public-export is prepared outside Git; it is not published and is not byte-identical canonical provenance. Analysis remains stopped. This privacy task does not authorize new computations or research jobs.

---

## Stop checkpoint publication blocked — 2026-10-11


All work remains in the local Git history and server copies. Incremental Git bundle of the completed local history is saved outside Git as outer outputs/analysis-stop.bundle and P=/path/to/user-user/lora-dora-profiling/analysis-stop.bundle. Resume details and whole-pipeline summary: docs/analysis/2026-10-11/CHECKPOINT.md. Q/C accepted, T saved but integration pending, L partial/unaccepted. No analysis or model jobs are to resume automatically.

---

## Analysis stopped at user request — 2026-10-11 12:25 MSK

User requested immediate stop, preservation of intermediate results, whole-pipeline summary/plans, commit and push, then end work. No automatic continuation. Resume only after a new user instruction. Snapshot: docs/analysis/2026-10-11/CHECKPOINT.md. REPORT.md is explicitly an unfinished Q/C synthesis, not the final scientific report.

Q accepted: 946 checks, 29 accepted runs, 15 baseline contrasts, 4 dense rows; all DoRA-minus-LoRA CI include zero. C accepted: 1507 checks, all40 intervention/scorer rows, 4radial/8compression/2DID/6direct-original/576entropy rows. Global radial removals exclude >0.5pp loss pointwise; rank32/E95 pass 1pp loss criterion against original DoRA, E99 only2pp. These are fixed-checkpoint benchmark results, not training mechanisms/equivalence. Dense fidelity differs from PEFT; matched control is scalar attenuation on one prompt/54tokens; actual post-BF16 rank and D activity are unmeasured. Code/results retained under execution/scientific-analysis and docs/analysis/2026-10-11/results. No new model forward, weight SVD, training, dependencies or GPU usage during analysis; versions unchanged.

T audit saved, integration pending: specific positive scalar V/O transformation is algebraically admissible in fixed-base DoRA-r via magnitude scaling; additive LoRA-r does not inherit that guarantee. Short64 dense numerical checks maxerror0 do not establish training cause/full benchmark equivalence. L partial CSV/code saved, not accepted: localization-effects, joint-interactions, paired-outcome-transitions; final findings/SVG/validation absent. No scientific analysis scripts found running at stop. Helpers interrupted. Existing original bundle and frozen evaluator preserved.

Whole pipeline, exact paths, caveats and resume steps are in CHECKPOINT.md. Next only after user resumes: finish/check L, review T, complete L1–L9 evidence ledger and final REPORT, build integrated manifest/verifier. Answer.AI remains deferred, Qwen3-8B/LLaVA excluded. Assistant model gpt-6.1-sol; user now permits effort according to task, overriding historical low preference.

GPU instantaneous utilization/VRAM MiB at approximately12:25MSK: 0=0%/5056;1=87%/8987;2=99%/9957;3=91%/10424;4=46%/871;5=75%/8552;6=71%/8586; total each16376. No foreign processes touched. Publishing snapshot to requested GitHub research/prepare-checkpoint-study as fast-forward; local execution branch remains research/two-extra-series. Git commit/push outcome reported in chat.

---

## Научный анализ: этапы A–B / пакет Q — 2026-10-11

Пользователь явно разрешил начать научный анализ 11 октября и выбирать reasoning помощников gpt-6.1-sol по усмотрению основного агента; это заменяет историческое low-ограничение. Точное ТЗ: `docs/analysis/2026-10-11/EXECUTION_SPEC.md`, план `docs/analysis/2026-10-11/PLAN.md` (exploratory, после сбора данных).

Пакет Q готов: `execution/scientific-analysis/build_quality.py`; `docs/analysis/2026-10-11/results/{quality-overview.csv,numerical-controls.csv,quality-and-controls.svg,quality-findings.md,quality-validation.json}`. CPU gpu-host, существующая venv, максимум два потока. Версии/зависимости и frozen evaluator не менялись; новых forward, GPU, обучения или SVD нет. Read-only 946 checks прошли: 29 accepted runs, 15 baseline metric contrasts, 4 dense scorer rows, 219 overview rows; hashes 197 input paths, accepted paths, completeness, alignment, means, subjects, answerability strata и dense transitions воспроизведены. Старый bundle неизменён. Исторические p/CI сохранены буквально, новых baseline tests нет.

Все DoRA−LoRA baseline CI включают ноль: GSM8K оба scorer +1.0614 п.п. [−0.6065,+2.7293], MMLU +0.0570 [−0.4059,+0.5341], SQuADv2 exact −0.1348 [−0.4801,+0.2021], F1 −0.2655 [−0.5597,+0.0236]. Это не equivalence и не неопределённость обучения. GSM8K base 1.213% author vs63.836% final; token cap base544/1319, DoRA35, LoRA40 — адаптация−base author не чистая оценка reasoning gain.

Dense DoRA−original: author −0.5307 п.п. CI [−1.5940,+0.6065], final −0.6823 CI [−1.7437,+0.3810], 511 changed texts; исправлено24/22, сломано31/31. Dense LoRA author0 п.п. (25 исправлено/25 сломано), final−0.0758 (25/26), 526 changed texts. Numeric original→dense maxabs logits error DoRA1.34375, LoRA1.578125, argmax agreement.98148149 на одном calibration prompt/54 positions. Это conversion fidelity, не fidelity последующего rank intervention. Функциональная идентичность PEFT/dense не доказана. Gate к компрессии условно пройден: все downstream rank/energy contrasts только относительно proper dense DoRA, matched-LoRA относительно dense LoRA; перенос на original checkpoints ограничен conversion discrepancy. Следующий этап: приёмка пакета C основным агентом, затем L по ТЗ.

---

## Scientific analysis plan and novelty audit prepared — 2026-10-11T07:21:46.544358+00:00

Prepared [analysis plan](analysis/2026-10-11/PLAN.md) and [novelty/chronology audit](analysis/2026-10-11/NOVELTY_AUDIT.md). The plan is written after data collection and previous reports, not preregistration. Scientific interpretation under this plan has not been performed. Read-only technical acceptance passed local links, counts, references and Git chronology; source artifact roots are S=/path/to/user-user/lora-dora-series and P=/path/to/user-user/lora-dora-profiling, with exact paths taken from manifests.

Early commits 004983b (2026-10-09 08:56:19 UTC) and 20c4684 (11:21:22 UTC) already recorded SORA/conditioning/spectral entropy, DeLoRA, PoLAR, BiDoRA and limits of known algebra versus functional necessity. The literature review expanded and clarified prior knowledge; these sources must not all be presented as new discoveries. Nine directions are provisionally classified 5 direct prior-art overlaps / 2 partial overlaps / 2 candidates for additional contribution. This is an unweighted guide, not a percentage of lost novelty or wasted GPU-hours, and does not establish novelty.

No new model runs or training, no new dependencies. Prepared analysis bundle, MEMORY and frozen evaluator untouched. Next: stages A–C (corpus/numerical controls, baseline quality, component necessity), then D–F (localization, symmetry scope and evidence synthesis), following the plan and explicit execution assignments.

## Literature search on LoRA/DoRA mechanisms — 2026-10-11T06:53:54.183242+00:00

Completed a curated primary-source literature search and review: 13 sources (12 research papers plus one technical report), including LoRA-Squeeze and Shortcuts in the Tail. Review: [LoRA/DoRA mechanisms, alternative explanations and overlaps](literature/2026-10-11-lora-dora-mechanisms.md). Exact inspected versions, publication-status qualifications and source links are recorded in that review; SHA256 87288a0555bae37f2ec00582f29b86512ce87ac0787327fa6e8f4b74a76cbdcf.

Recorded overlaps include conditioning and spectral entropy; frozen magnitude during training versus our posthoc interventions; optimization and overfitting; negative cases; and posthoc compression controls. No novelty or universal causality is asserted. No CPU/GPU model runs, own-result analysis, new dependencies or changes to the frozen evaluator. Prepared-result bundle remains unchanged; the latest read-only offline verification passed 43 files with zero errors. Next: discuss analysis after the user reads the literature review; no new experiment plan is authorized by this search.

## Preparation of existing results for analysis — 2026-10-11T06:15:00.147044+00:00


Canonical bundle: /path/to/user-user/lora-dora-series/docs/analysis-preparation/2026-10-11/, mirrored in the local research checkout. Package01 covers 29 accepted full runs, 29 saved comparisons, three baseline triples, MMLU subjects, scorer agreement, baseline transitions and explicit SQuAD answerability strata. Package02 covers 20 interventions, 40 scorer comparisons, transitions/localization grids, 8 exploratory descriptive interaction rows and 60674 compact score rows (gzip, no texts). Package03 contains rank/module, matched-impact, numerical/symmetry and resource tables: 1728 module rows, 144 impact rows, resource records for all29 runs. Unmeasured quantities remain explicitly unavailable. Three saved Holm families 8/9/3 remain separate; derived descriptive interactions receive no inherited p/CI/Holm. Attempts tables have intentionally different scopes (A32/C35), not total campaign cost.

All packages passed their consistency and output hash checks; integrated acceptance passed locally and on server. Frozen evaluator: independently rehashed31 files against distributed-important/plan.json, zero mismatches. Entry point: python3 execution/analysis-preparation/verify_bundle.py from repository root; no raw data/network/NumPy/Torch needed. Source input hashes, schemas, extractor/output hashes and validation are in package manifests and validation; root bundle manifest covers43 compact files (~4.9 MB), excluding its own hash and volatile bundle validation. Extractors live in execution/analysis-preparation/, outside frozen scripts/configs/lora_dora_study. CPU scratch copies remain under /path/to/user-user/lora-dora-profiling/analysis-preparation/2026-10-11/. Original results unmodified; dependency versions unchanged.

MEMORY.md created with delegation preference, access host/login (no password was provided or stored), scope and resource rules; AGENTS.md points to it. Latest user decision: ongoing authorization for CPU and partially occupied GPU use on ShAD at agent discretion without repeated approval, preserve foreign processes and existing maximum6-GPU limit. This authorization does not expand the current research plan. Answer.AI remains deferred, Qwen3-8B/LLaVA excluded. Next: scientific interpretation of prepared data when explicitly requested; do not restart completed queues.

## Reconciled completed removeD-K/V statuses — 2026-10-11T05:53:56.602191+00:00

Both full outputs have complete summaries. Their matched-comparison.json files exactly match entries in localization-family-holm.json. Updated only stale job status fields from outputs_complete_analysis_pending to complete, with reconciliation timestamps; no inference or analysis rerun. Prior status copies and status-reconciliation-report.json preserved in /path/to/user-user/lora-dora-profiling/distributed-important/. All 20 intervention comparisons and three Holm families are available. Next: interpret results and select any targeted Answer.AI validation.

## Distributed intervention stage: gpu4 / complete_gpu_released

UTC 2026-10-11T05:17:27.841863+00:00

State: /path/to/user-user/lora-dora-profiling/distributed-important/gpu4-state.json. External controller: /path/to/user-user/lora-dora-profiling/distributed_shared_localizations.py. Frozen evaluator unchanged; versions Torch2.5.1+cu121 / Transformers4.57.1 / PEFT0.17.1 / Accelerate1.11.0.

```json
{
  "pid": 1368372,
  "lane": "gpu4",
  "gpu_uuid": "GPU_UUID",
  "status": "complete_gpu_released",
  "completed_jobs": [
    "gsm8k-remove_d-k",
    "gsm8k-remove_d-v",
    "gsm8k-remove_d-o",
    "gsm8k-remove_d-qk"
  ],
  "created_utc": "2026-10-10T18:27:50.953941+00:00",
  "updated_utc": "2026-10-11T05:17:21.579182+00:00",
  "job": "gsm8k-remove_d-qk",
  "phase": "full",
  "role": "dora",
  "worker_pid": null,
  "command": [
    "/path/to/user-user/.venvs/lora-dora-research/bin/python",
    "/path/to/user-user/lora-dora-profiling/shared_held_gpu_worker.py",
    "scripts/series_worker.py",
    "--job",
    "/path/to/user-user/lora-dora-series/results/first-series-greedy/jobs/gsm8k-remove_d-qk/job.json",
    "--gpu-uuid",
    "GPU_UUID",
    "--role",
    "dora",
    "--output-dir",
    "/path/to/user-user/lora-dora-series/results/first-series-greedy/jobs/gsm8k-remove_d-qk/full-dora-distributed-1"
  ],
  "compute_completed_utc": "2026-10-11T05:17:21.577051+00:00",
  "analysis_completed_utc": "2026-10-11T05:17:21.579167+00:00",
  "pending_comparisons": [],
  "released_utc": "2026-10-11T05:17:24.660389+00:00",
  "gpu_retained": false
}
```

Next: inspect failures immediately; otherwise follow lane plan.json sequentially, compare only completed matched outputs, retain assigned GPU after compute.

## Completed queue released GPU: gpu4

{
  "pid": 1368372,
  "lane": "gpu4",
  "gpu_uuid": "GPU_UUID",
  "status": "complete_gpu_released",
  "completed_jobs": [
    "gsm8k-remove_d-k",
    "gsm8k-remove_d-v",
    "gsm8k-remove_d-o",
    "gsm8k-remove_d-qk"
  ],
  "created_utc": "2026-10-10T18:27:50.953941+00:00",
  "updated_utc": "2026-10-11T05:17:21.579182+00:00",
  "job": "gsm8k-remove_d-qk",
  "phase": "full",
  "role": "dora",
  "worker_pid": null,
  "command": [
    "/path/to/user-user/.venvs/lora-dora-research/bin/python",
    "/path/to/user-user/lora-dora-profiling/shared_held_gpu_worker.py",
    "scripts/series_worker.py",
    "--job",
    "/path/to/user-user/lora-dora-series/results/first-series-greedy/jobs/gsm8k-remove_d-qk/job.json",
    "--gpu-uuid",
    "GPU_UUID",
    "--role",
    "dora",
    "--output-dir",
    "/path/to/user-user/lora-dora-series/results/first-series-greedy/jobs/gsm8k-remove_d-qk/full-dora-distributed-1"
  ],
  "compute_completed_utc": "2026-10-11T05:17:21.577051+00:00",
  "analysis_completed_utc": "2026-10-11T05:17:21.579167+00:00",
  "pending_comparisons": [],
  "released_utc": "2026-10-11T05:17:24.660389+00:00",
  "gpu_retained": false
}

All GPU workers finished; any pending comparisons continue in CPU-only process. Next: other users may use this GPU; night queues only admit truly idle cards after22Moscow.

## Distributed intervention stage: gpu6 / complete_gpu_released

UTC 2026-10-11T04:49:37.410409+00:00

State: /path/to/user-user/lora-dora-profiling/distributed-important/gpu6-state.json. External controller: /path/to/user-user/lora-dora-profiling/distributed_localizations_v2.py. Frozen evaluator unchanged; versions Torch2.5.1+cu121 / Transformers4.57.1 / PEFT0.17.1 / Accelerate1.11.0.

```json
{
  "pid": 402546,
  "lane": "gpu6",
  "gpu_uuid": "GPU_UUID",
  "status": "complete_gpu_released",
  "completed_jobs": [
    "short-vo",
    "gsm8k-e99",
    "gsm8k-remove_d-q",
    "gsm8k-base_magnitude-v",
    "gsm8k-base_magnitude-q",
    "gsm8k-base_magnitude-vo"
  ],
  "created_utc": "2026-10-10T03:46:56.152087+00:00",
  "worker_pid": null,
  "updated_utc": "2026-10-11T04:49:27.432519+00:00",
  "job": "gsm8k-base_magnitude-vo",
  "phase": "full",
  "role": "dora",
  "command": [
    "/path/to/user-user/.venvs/lora-dora-research/bin/python",
    "scripts/held_gpu_worker.py",
    "scripts/series_worker.py",
    "--job",
    "/path/to/user-user/lora-dora-series/results/first-series-greedy/jobs/gsm8k-base_magnitude-vo/job.json",
    "--gpu-uuid",
    "GPU_UUID",
    "--role",
    "dora",
    "--output-dir",
    "/path/to/user-user/lora-dora-series/results/first-series-greedy/jobs/gsm8k-base_magnitude-vo/full-dora-distributed-1"
  ],
  "compute_completed_utc": "2026-10-11T04:49:27.431601+00:00",
  "analysis_completed_utc": "2026-10-11T04:49:27.432506+00:00",
  "pending_comparisons": [],
  "released_utc": "2026-10-11T04:49:33.886662+00:00",
  "gpu_retained": false
}
```

Next: inspect failures immediately; otherwise follow lane plan.json sequentially, compare only completed matched outputs, retain assigned GPU after compute.

## Completed queue released GPU: gpu6

{
  "pid": 402546,
  "lane": "gpu6",
  "gpu_uuid": "GPU_UUID",
  "status": "complete_gpu_released",
  "completed_jobs": [
    "short-vo",
    "gsm8k-e99",
    "gsm8k-remove_d-q",
    "gsm8k-base_magnitude-v",
    "gsm8k-base_magnitude-q",
    "gsm8k-base_magnitude-vo"
  ],
  "created_utc": "2026-10-10T03:46:56.152087+00:00",
  "worker_pid": null,
  "updated_utc": "2026-10-11T04:49:27.432519+00:00",
  "job": "gsm8k-base_magnitude-vo",
  "phase": "full",
  "role": "dora",
  "command": [
    "/path/to/user-user/.venvs/lora-dora-research/bin/python",
    "scripts/held_gpu_worker.py",
    "scripts/series_worker.py",
    "--job",
    "/path/to/user-user/lora-dora-series/results/first-series-greedy/jobs/gsm8k-base_magnitude-vo/job.json",
    "--gpu-uuid",
    "GPU_UUID",
    "--role",
    "dora",
    "--output-dir",
    "/path/to/user-user/lora-dora-series/results/first-series-greedy/jobs/gsm8k-base_magnitude-vo/full-dora-distributed-1"
  ],
  "compute_completed_utc": "2026-10-11T04:49:27.431601+00:00",
  "analysis_completed_utc": "2026-10-11T04:49:27.432506+00:00",
  "pending_comparisons": [],
  "released_utc": "2026-10-11T04:49:33.886662+00:00",
  "gpu_retained": false
}

All GPU workers finished; any pending comparisons continue in CPU-only process. Next: other users may use this GPU; night queues only admit truly idle cards after22Moscow.

## Distributed intervention stage: gpu6 / running

UTC 2026-10-11T04:49:27.388279+00:00

State: /path/to/user-user/lora-dora-profiling/distributed-important/gpu6-state.json. External controller: /path/to/user-user/lora-dora-profiling/distributed_localizations_v2.py. Frozen evaluator unchanged; versions Torch2.5.1+cu121 / Transformers4.57.1 / PEFT0.17.1 / Accelerate1.11.0.

```json
{
  "pid": 402546,
  "lane": "gpu6",
  "gpu_uuid": "GPU_UUID",
  "status": "running",
  "completed_jobs": [
    "short-vo",
    "gsm8k-e99",
    "gsm8k-remove_d-q",
    "gsm8k-base_magnitude-v",
    "gsm8k-base_magnitude-q",
    "gsm8k-base_magnitude-vo"
  ],
  "created_utc": "2026-10-10T03:46:56.152087+00:00",
  "worker_pid": 3173555,
  "updated_utc": "2026-10-11T04:49:27.162117+00:00",
  "job": "gsm8k-base_magnitude-vo",
  "phase": "full",
  "role": "dora",
  "command": [
    "/path/to/user-user/.venvs/lora-dora-research/bin/python",
    "scripts/held_gpu_worker.py",
    "scripts/series_worker.py",
    "--job",
    "/path/to/user-user/lora-dora-series/results/first-series-greedy/jobs/gsm8k-base_magnitude-vo/job.json",
    "--gpu-uuid",
    "GPU_UUID",
    "--role",
    "dora",
    "--output-dir",
    "/path/to/user-user/lora-dora-series/results/first-series-greedy/jobs/gsm8k-base_magnitude-vo/full-dora-distributed-1"
  ]
}
```

Next: inspect failures immediately; otherwise follow lane plan.json sequentially, compare only completed matched outputs, retain assigned GPU after compute.

## Completed queue released GPU: night-k

{
  "pid": 1049531,
  "lane": "night-k",
  "gpu_uuid": "GPU_UUID",
  "status": "complete_gpu_released",
  "completed_jobs": [
    "gsm8k-base_magnitude-k",
    "gsm8k-base_magnitude-o"
  ],
  "created_utc": "2026-10-10T12:48:45.310163+00:00",
  "job": "gsm8k-base_magnitude-o",
  "phase": "full",
  "role": "dora",
  "worker_pid": null,
  "command": [
    "/path/to/user-user/.venvs/lora-dora-research/bin/python",
    "scripts/held_gpu_worker.py",
    "scripts/series_worker.py",
    "--job",
    "/path/to/user-user/lora-dora-series/results/first-series-greedy/jobs/gsm8k-base_magnitude-o/job.json",
    "--gpu-uuid",
    "GPU_UUID",
    "--role",
    "dora",
    "--output-dir",
    "/path/to/user-user/lora-dora-series/results/first-series-greedy/jobs/gsm8k-base_magnitude-o/full-dora-distributed-1"
  ],
  "updated_utc": "2026-10-11T04:14:33.683279+00:00",
  "compute_completed_utc": "2026-10-11T04:14:33.679770+00:00",
  "analysis_completed_utc": "2026-10-11T04:14:33.683245+00:00",
  "pending_comparisons": [],
  "released_utc": "2026-10-11T04:14:43.071798+00:00",
  "gpu_retained": false
}

All GPU workers finished; any pending comparisons continue in CPU-only process. Next: other users may use this GPU; night queues only admit truly idle cards after22Moscow.

## Completed queue released GPU: night-qk

{
  "pid": 3123836,
  "lane": "night-qk",
  "gpu_uuid": "GPU_UUID",
  "status": "complete_gpu_released",
  "completed_jobs": [
    "gsm8k-base_magnitude-qk"
  ],
  "created_utc": "2026-10-10T20:27:59.639417+00:00",
  "job": "gsm8k-base_magnitude-qk",
  "phase": "full",
  "role": "dora",
  "worker_pid": null,
  "command": [
    "/path/to/user-user/.venvs/lora-dora-research/bin/python",
    "/path/to/user-user/lora-dora-profiling/shared_held_gpu_worker.py",
    "scripts/series_worker.py",
    "--job",
    "/path/to/user-user/lora-dora-series/results/first-series-greedy/jobs/gsm8k-base_magnitude-qk/job.json",
    "--gpu-uuid",
    "GPU_UUID",
    "--role",
    "dora",
    "--output-dir",
    "/path/to/user-user/lora-dora-series/results/first-series-greedy/jobs/gsm8k-base_magnitude-qk/full-dora-distributed-1"
  ],
  "updated_utc": "2026-10-11T04:11:37.774718+00:00",
  "compute_completed_utc": "2026-10-11T04:11:37.773126+00:00",
  "analysis_completed_utc": "2026-10-11T04:11:37.774693+00:00",
  "pending_comparisons": [],
  "released_utc": "2026-10-11T04:11:42.633846+00:00",
  "gpu_retained": false
}

All GPU workers finished; any pending comparisons continue in CPU-only process. Next: other users may use this GPU; night queues only admit truly idle cards after22Moscow.

## Distributed intervention stage: gpu4 / running

UTC 2026-10-10T23:57:53.286330+00:00

State: /path/to/user-user/lora-dora-profiling/distributed-important/gpu4-state.json. External controller: /path/to/user-user/lora-dora-profiling/distributed_shared_localizations.py. Frozen evaluator unchanged; versions Torch2.5.1+cu121 / Transformers4.57.1 / PEFT0.17.1 / Accelerate1.11.0.

```json
{
  "pid": 1368372,
  "lane": "gpu4",
  "gpu_uuid": "GPU_UUID",
  "status": "running",
  "completed_jobs": [
    "gsm8k-remove_d-k",
    "gsm8k-remove_d-v",
    "gsm8k-remove_d-o"
  ],
  "created_utc": "2026-10-10T18:27:50.953941+00:00",
  "updated_utc": "2026-10-10T23:57:49.196962+00:00",
  "job": "gsm8k-remove_d-qk",
  "phase": "full",
  "role": "dora",
  "worker_pid": 3366147,
  "command": [
    "/path/to/user-user/.venvs/lora-dora-research/bin/python",
    "/path/to/user-user/lora-dora-profiling/shared_held_gpu_worker.py",
    "scripts/series_worker.py",
    "--job",
    "/path/to/user-user/lora-dora-series/results/first-series-greedy/jobs/gsm8k-remove_d-qk/job.json",
    "--gpu-uuid",
    "GPU_UUID",
    "--role",
    "dora",
    "--output-dir",
    "/path/to/user-user/lora-dora-series/results/first-series-greedy/jobs/gsm8k-remove_d-qk/full-dora-distributed-1"
  ]
}
```

Next: inspect failures immediately; otherwise follow lane plan.json sequentially, compare only completed matched outputs, retain assigned GPU after compute.

## Distributed intervention stage: gpu4 / running

UTC 2026-10-10T23:57:33.273370+00:00

State: /path/to/user-user/lora-dora-profiling/distributed-important/gpu4-state.json. External controller: /path/to/user-user/lora-dora-profiling/distributed_shared_localizations.py. Frozen evaluator unchanged; versions Torch2.5.1+cu121 / Transformers4.57.1 / PEFT0.17.1 / Accelerate1.11.0.

```json
{
  "pid": 1368372,
  "lane": "gpu4",
  "gpu_uuid": "GPU_UUID",
  "status": "running",
  "completed_jobs": [
    "gsm8k-remove_d-k",
    "gsm8k-remove_d-v",
    "gsm8k-remove_d-o"
  ],
  "created_utc": "2026-10-10T18:27:50.953941+00:00",
  "updated_utc": "2026-10-10T23:57:23.789241+00:00",
  "job": "gsm8k-remove_d-qk",
  "phase": "smoke",
  "role": "dora",
  "worker_pid": 3365532,
  "command": [
    "/path/to/user-user/.venvs/lora-dora-research/bin/python",
    "/path/to/user-user/lora-dora-profiling/shared_held_gpu_worker.py",
    "scripts/series_worker.py",
    "--job",
    "/path/to/user-user/lora-dora-series/results/first-series-greedy/jobs/gsm8k-remove_d-qk/job.json",
    "--gpu-uuid",
    "GPU_UUID",
    "--role",
    "dora",
    "--output-dir",
    "/path/to/user-user/lora-dora-series/results/first-series-greedy/jobs/gsm8k-remove_d-qk/smoke-dora-distributed-1",
    "--limit",
    "2"
  ]
}
```

Next: inspect failures immediately; otherwise follow lane plan.json sequentially, compare only completed matched outputs, retain assigned GPU after compute.

## Distributed intervention stage: gpu6 / running

UTC 2026-10-10T21:10:10.965589+00:00

State: /path/to/user-user/lora-dora-profiling/distributed-important/gpu6-state.json. External controller: /path/to/user-user/lora-dora-profiling/distributed_localizations_v2.py. Frozen evaluator unchanged; versions Torch2.5.1+cu121 / Transformers4.57.1 / PEFT0.17.1 / Accelerate1.11.0.

```json
{
  "pid": 402546,
  "lane": "gpu6",
  "gpu_uuid": "GPU_UUID",
  "status": "running",
  "completed_jobs": [
    "short-vo",
    "gsm8k-e99",
    "gsm8k-remove_d-q",
    "gsm8k-base_magnitude-v",
    "gsm8k-base_magnitude-q"
  ],
  "created_utc": "2026-10-10T03:46:56.152087+00:00",
  "worker_pid": 3173555,
  "updated_utc": "2026-10-10T21:10:09.313968+00:00",
  "job": "gsm8k-base_magnitude-vo",
  "phase": "full",
  "role": "dora",
  "command": [
    "/path/to/user-user/.venvs/lora-dora-research/bin/python",
    "scripts/held_gpu_worker.py",
    "scripts/series_worker.py",
    "--job",
    "/path/to/user-user/lora-dora-series/results/first-series-greedy/jobs/gsm8k-base_magnitude-vo/job.json",
    "--gpu-uuid",
    "GPU_UUID",
    "--role",
    "dora",
    "--output-dir",
    "/path/to/user-user/lora-dora-series/results/first-series-greedy/jobs/gsm8k-base_magnitude-vo/full-dora-distributed-1"
  ]
}
```

Next: inspect failures immediately; otherwise follow lane plan.json sequentially, compare only completed matched outputs, retain assigned GPU after compute.

## Distributed intervention stage: gpu6 / running

UTC 2026-10-10T21:09:30.891514+00:00

State: /path/to/user-user/lora-dora-profiling/distributed-important/gpu6-state.json. External controller: /path/to/user-user/lora-dora-profiling/distributed_localizations_v2.py. Frozen evaluator unchanged; versions Torch2.5.1+cu121 / Transformers4.57.1 / PEFT0.17.1 / Accelerate1.11.0.

```json
{
  "pid": 402546,
  "lane": "gpu6",
  "gpu_uuid": "GPU_UUID",
  "status": "running",
  "completed_jobs": [
    "short-vo",
    "gsm8k-e99",
    "gsm8k-remove_d-q",
    "gsm8k-base_magnitude-v",
    "gsm8k-base_magnitude-q"
  ],
  "created_utc": "2026-10-10T03:46:56.152087+00:00",
  "worker_pid": 3172669,
  "updated_utc": "2026-10-10T21:09:29.235765+00:00",
  "job": "gsm8k-base_magnitude-vo",
  "phase": "smoke",
  "role": "dora",
  "command": [
    "/path/to/user-user/.venvs/lora-dora-research/bin/python",
    "scripts/held_gpu_worker.py",
    "scripts/series_worker.py",
    "--job",
    "/path/to/user-user/lora-dora-series/results/first-series-greedy/jobs/gsm8k-base_magnitude-vo/job.json",
    "--gpu-uuid",
    "GPU_UUID",
    "--role",
    "dora",
    "--output-dir",
    "/path/to/user-user/lora-dora-series/results/first-series-greedy/jobs/gsm8k-base_magnitude-vo/smoke-dora-distributed-1",
    "--limit",
    "2"
  ]
}
```

Next: inspect failures immediately; otherwise follow lane plan.json sequentially, compare only completed matched outputs, retain assigned GPU after compute.

## Night QK admitted on explicitly authorized shared GPU5 — 2026-10-10 20:28 UTC

User explicitly requested occupying GPU5. Fresh snapshot: utilization 0%, used 688 MiB; only foreign CUDA PID2039512 with 678 MiB. Recorded PID start-time identity in shared-admission-policy.json. Scoped exception applies only to night-qk on this UUID: total initial VRAM <=1024 MiB, utilization <=10%, only the recorded foreign process with <=768 MiB; other lanes retain original thresholds. Two checks 10 seconds apart and cooperative GPU/slot leases retained. Waiting-only admission controller replaced; new controller3123836 admitted GPU5 and launched smoke worker3124449, then full baseMagnitude-QK. Foreign process untouched. Frozen evaluator unchanged; external worker uses shared admission wrapper. Estimated duration 7.9 hours, finish approximately 11 October 07:25 Moscow, subject to observed throughput. Release monitor recognizes unchanged admission controller name and frees GPU after compute; no GPU retained for pending CPU comparisons.

Scripts /path/to/user-user/lora-dora-profiling/night_localization_admission.py, night_localization_worker_shared.py, shared_held_gpu_worker.py; state and log /path/to/user-user/lora-dora-profiling/distributed-important/night-qk-state.json and night-qk-shared-launch.log. External syntax checks passed, controller admission and smoke launch verified. Next: verify full inference and release at completion. Other queues untouched.

## GPU4 recovery and GPU load — 2026-10-10 18:29 UTC (21:29 Moscow)

GPU4 full removeD-o attempt 1 was refused before model loading at 17:53 UTC: the admission probe observed residual 100% GPU utilization after our smoke. No full predictions were lost. External shared_held_gpu_worker.py now retries the actual admission predicate for up to 10 seconds with fresh snapshots, retaining all UUID, foreign PID/start-time, memory and utilization checks. Frozen evaluator and generation settings were not edited. Recovery controller 1368372 replaced only our failed keeper 408126, preserving GPU continuity; worker 1368487 is running full-dora-distributed-2 with accepted admission and GPU utilization 99%. Completed removeD-k/v are skipped. Existing foreign GPU4 PID321456 was untouched. Release monitor 1368373 recognizes recover_gpu4_shared.py and releases GPU after inference, with pending comparisons on CPU.

Artifacts: /path/to/user-user/lora-dora-profiling/distributed-important/gpu4-failure-before-recovery.json, gpu4-recovery.log, gpu4-state.json; evaluator output /path/to/user-user/lora-dora-series/results/first-series-greedy/jobs/gsm8k-remove_d-o/full-dora-distributed-2/. External recovery script /path/to/user-user/lora-dora-profiling/recover_gpu4_shared.py. Python syntax checks passed; accepted runtime admission and allocated model VRAM verified. Dependency versions unchanged.

Snapshot GPU0..6 utilization: 45,27,6,99,99,0,99%; memory MiB: 5697,7679,8579,8513,8616,12825,8527. Our inference occupies 3/4/6; other cards have foreign processes. QK still waits until 22:00 Moscow and then a genuinely free card. Next: monitor recovered removeD-o then removeD-qk, release completed cards; preliminary GPU4 finish shifts to approximately 11 October 08:40 Moscow (estimate, not measured completion).

## Distributed intervention stage: gpu4 / running

UTC 2026-10-10T18:27:58.346456+00:00

State: /path/to/user-user/lora-dora-profiling/distributed-important/gpu4-state.json. External controller: /path/to/user-user/lora-dora-profiling/distributed_shared_localizations.py. Frozen evaluator unchanged; versions Torch2.5.1+cu121 / Transformers4.57.1 / PEFT0.17.1 / Accelerate1.11.0.

```json
{
  "pid": 1368372,
  "lane": "gpu4",
  "gpu_uuid": "GPU_UUID",
  "status": "running",
  "completed_jobs": [
    "gsm8k-remove_d-k",
    "gsm8k-remove_d-v"
  ],
  "created_utc": "2026-10-10T18:27:50.953941+00:00",
  "updated_utc": "2026-10-10T18:27:50.984351+00:00",
  "job": "gsm8k-remove_d-o",
  "phase": "full",
  "role": "dora",
  "worker_pid": 1368487,
  "command": [
    "/path/to/user-user/.venvs/lora-dora-research/bin/python",
    "/path/to/user-user/lora-dora-profiling/shared_held_gpu_worker.py",
    "scripts/series_worker.py",
    "--job",
    "/path/to/user-user/lora-dora-series/results/first-series-greedy/jobs/gsm8k-remove_d-o/job.json",
    "--gpu-uuid",
    "GPU_UUID",
    "--role",
    "dora",
    "--output-dir",
    "/path/to/user-user/lora-dora-series/results/first-series-greedy/jobs/gsm8k-remove_d-o/full-dora-distributed-2"
  ]
}
```

Next: inspect failures immediately; otherwise follow lane plan.json sequentially, compare only completed matched outputs, retain assigned GPU after compute.

## Distributed intervention stage: gpu4 / failed_gpu_retained

UTC 2026-10-10T17:53:07.846517+00:00

State: /path/to/user-user/lora-dora-profiling/distributed-important/gpu4-state.json. External controller: /path/to/user-user/lora-dora-profiling/distributed_shared_localizations.py. Frozen evaluator unchanged; versions Torch2.5.1+cu121 / Transformers4.57.1 / PEFT0.17.1 / Accelerate1.11.0.

```json
{
  "pid": 408126,
  "lane": "gpu4",
  "gpu_uuid": "GPU_UUID",
  "status": "failed_gpu_retained",
  "completed_jobs": [
    "gsm8k-remove_d-k",
    "gsm8k-remove_d-v"
  ],
  "created_utc": "2026-10-10T03:52:08.620351+00:00",
  "job": "gsm8k-remove_d-o",
  "phase": "full",
  "role": "dora",
  "worker_pid": 808429,
  "command": [
    "/path/to/user-user/.venvs/lora-dora-research/bin/python",
    "/path/to/user-user/lora-dora-profiling/shared_held_gpu_worker.py",
    "scripts/series_worker.py",
    "--job",
    "/path/to/user-user/lora-dora-series/results/first-series-greedy/jobs/gsm8k-remove_d-o/job.json",
    "--gpu-uuid",
    "GPU_UUID",
    "--role",
    "dora",
    "--output-dir",
    "/path/to/user-user/lora-dora-series/results/first-series-greedy/jobs/gsm8k-remove_d-o/full-dora-distributed-1"
  ],
  "updated_utc": "2026-10-10T17:53:06.378147+00:00",
  "error": "Worker failed: gsm8k-remove_d-o/full",
  "traceback": "Traceback (most recent call last):\n  File \"/path/to/user-user/lora-dora-profiling/distributed_shared_localizations.py\", line 126, in main\n    if p.wait():raise RuntimeError('Worker failed: '+id+'/'+phase)\n                ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\nRuntimeError: Worker failed: gsm8k-remove_d-o/full\n"
}
```

Next: inspect failures immediately; otherwise follow lane plan.json sequentially, compare only completed matched outputs, retain assigned GPU after compute.

## Distributed intervention stage: gpu4 / running

UTC 2026-10-10T17:52:47.821651+00:00

State: /path/to/user-user/lora-dora-profiling/distributed-important/gpu4-state.json. External controller: /path/to/user-user/lora-dora-profiling/distributed_shared_localizations.py. Frozen evaluator unchanged; versions Torch2.5.1+cu121 / Transformers4.57.1 / PEFT0.17.1 / Accelerate1.11.0.

```json
{
  "pid": 408126,
  "lane": "gpu4",
  "gpu_uuid": "GPU_UUID",
  "status": "running",
  "completed_jobs": [
    "gsm8k-remove_d-k",
    "gsm8k-remove_d-v"
  ],
  "created_utc": "2026-10-10T03:52:08.620351+00:00",
  "job": "gsm8k-remove_d-o",
  "phase": "smoke",
  "role": "dora",
  "worker_pid": 808005,
  "command": [
    "/path/to/user-user/.venvs/lora-dora-research/bin/python",
    "/path/to/user-user/lora-dora-profiling/shared_held_gpu_worker.py",
    "scripts/series_worker.py",
    "--job",
    "/path/to/user-user/lora-dora-series/results/first-series-greedy/jobs/gsm8k-remove_d-o/job.json",
    "--gpu-uuid",
    "GPU_UUID",
    "--role",
    "dora",
    "--output-dir",
    "/path/to/user-user/lora-dora-series/results/first-series-greedy/jobs/gsm8k-remove_d-o/smoke-dora-distributed-1",
    "--limit",
    "2"
  ],
  "updated_utc": "2026-10-10T17:52:41.171804+00:00"
}
```

Next: inspect failures immediately; otherwise follow lane plan.json sequentially, compare only completed matched outputs, retain assigned GPU after compute.

## Distributed intervention stage: gpu6 / running

UTC 2026-10-10T13:29:14.484743+00:00

State: /path/to/user-user/lora-dora-profiling/distributed-important/gpu6-state.json. External controller: /path/to/user-user/lora-dora-profiling/distributed_localizations_v2.py. Frozen evaluator unchanged; versions Torch2.5.1+cu121 / Transformers4.57.1 / PEFT0.17.1 / Accelerate1.11.0.

```json
{
  "pid": 402546,
  "lane": "gpu6",
  "gpu_uuid": "GPU_UUID",
  "status": "running",
  "completed_jobs": [
    "short-vo",
    "gsm8k-e99",
    "gsm8k-remove_d-q",
    "gsm8k-base_magnitude-v"
  ],
  "created_utc": "2026-10-10T03:46:56.152087+00:00",
  "worker_pid": 2489005,
  "updated_utc": "2026-10-10T13:29:04.517655+00:00",
  "job": "gsm8k-base_magnitude-q",
  "phase": "full",
  "role": "dora",
  "command": [
    "/path/to/user-user/.venvs/lora-dora-research/bin/python",
    "scripts/held_gpu_worker.py",
    "scripts/series_worker.py",
    "--job",
    "/path/to/user-user/lora-dora-series/results/first-series-greedy/jobs/gsm8k-base_magnitude-q/job.json",
    "--gpu-uuid",
    "GPU_UUID",
    "--role",
    "dora",
    "--output-dir",
    "/path/to/user-user/lora-dora-series/results/first-series-greedy/jobs/gsm8k-base_magnitude-q/full-dora-distributed-1"
  ]
}
```

Next: inspect failures immediately; otherwise follow lane plan.json sequentially, compare only completed matched outputs, retain assigned GPU after compute.

## Distributed intervention stage: gpu6 / running

UTC 2026-10-10T13:28:14.409405+00:00

State: /path/to/user-user/lora-dora-profiling/distributed-important/gpu6-state.json. External controller: /path/to/user-user/lora-dora-profiling/distributed_localizations_v2.py. Frozen evaluator unchanged; versions Torch2.5.1+cu121 / Transformers4.57.1 / PEFT0.17.1 / Accelerate1.11.0.

```json
{
  "pid": 402546,
  "lane": "gpu6",
  "gpu_uuid": "GPU_UUID",
  "status": "running",
  "completed_jobs": [
    "short-vo",
    "gsm8k-e99",
    "gsm8k-remove_d-q",
    "gsm8k-base_magnitude-v"
  ],
  "created_utc": "2026-10-10T03:46:56.152087+00:00",
  "worker_pid": 2488150,
  "updated_utc": "2026-10-10T13:28:09.988059+00:00",
  "job": "gsm8k-base_magnitude-q",
  "phase": "smoke",
  "role": "dora",
  "command": [
    "/path/to/user-user/.venvs/lora-dora-research/bin/python",
    "scripts/held_gpu_worker.py",
    "scripts/series_worker.py",
    "--job",
    "/path/to/user-user/lora-dora-series/results/first-series-greedy/jobs/gsm8k-base_magnitude-q/job.json",
    "--gpu-uuid",
    "GPU_UUID",
    "--role",
    "dora",
    "--output-dir",
    "/path/to/user-user/lora-dora-series/results/first-series-greedy/jobs/gsm8k-base_magnitude-q/smoke-dora-distributed-1",
    "--limit",
    "2"
  ]
}
```

Next: inspect failures immediately; otherwise follow lane plan.json sequentially, compare only completed matched outputs, retain assigned GPU after compute.

## K/O night queues merged and started immediately on GPU3 — 2026-10-10T12:50:26.671415+00:00

User requests2nightqueues merged and run now onGPU3. K/O selected, sequential in historical lane night-k. Old waiting-only admission PIDs419770/419771 terminated; no worker interrupted. New admission/controller1049531 verifiedGPU3idle twice10s apart, acquired lease, launched frozen evaluator. night-o removed from active plan, archived admission marked merged. No duplicate jobs. night-qk419772 remains scheduled10October22Moscow, no CUDA reservation before then. Active plan /path/to/user-user/lora-dora-profiling/distributed-important/night-plan.json contains2lanes/3uniquejobs. Per-lane immediate deadline and requested_gpu_index3 forK/O; global22deadline forQK remains. Statistical nightfamily remains3independent contrasts; merging execution does not merge interventions.

Estimate15.7435GPUh; conditional finish 2026-10-11T07:33:22.026077+03:00. Report /path/to/user-user/lora-dora-profiling/distributed-important/merged-night-ko-report.json. Frozen source SHA256 unchanged, external syntax compiled, actualGPU3launch verified. Versions unchanged Python3.12.3 / Torch2.5.1+cu121 / Transformers4.57.1 / PEFT0.17.1 / Accelerate1.11.0. OtherGPU4/6queues unchanged. Automatic release monitor includesnight-k: freeGPUaftercompute, pending comparisons onCPU. Next: verifyKsmoke/full, continueO, releaseGPU3; keepQK22schedule. No unscheduled localizations remain.

## Distributed intervention stage: gpu1 / complete_gpu_released

UTC 2026-10-10T12:02:53.418810+00:00

State: /path/to/user-user/lora-dora-profiling/distributed-important/gpu1-state.json. External controller: /path/to/user-user/lora-dora-profiling/distributed_important.py. Frozen evaluator unchanged; versions Torch2.5.1+cu121 / Transformers4.57.1 / PEFT0.17.1 / Accelerate1.11.0.

```json
{
  "pid": 4170596,
  "lane": "gpu1",
  "gpu_uuid": "GPU_UUID",
  "status": "complete_gpu_released",
  "completed_jobs": [
    "gsm8k-dense-dora",
    "gsm8k-r32",
    "gsm8k-e95",
    "gsm8k-base_magnitude-all"
  ],
  "created_utc": "2026-10-09T21:24:47.331082+00:00",
  "job": "gsm8k-base_magnitude-all",
  "phase": "full",
  "role": "dora",
  "worker_pid": null,
  "command": [
    "/path/to/user-user/.venvs/lora-dora-research/bin/python",
    "scripts/held_gpu_worker.py",
    "scripts/series_worker.py",
    "--job",
    "/path/to/user-user/lora-dora-series/results/first-series-greedy/jobs/gsm8k-base_magnitude-all/job.json",
    "--gpu-uuid",
    "GPU_UUID",
    "--role",
    "dora",
    "--output-dir",
    "/path/to/user-user/lora-dora-series/results/first-series-greedy/jobs/gsm8k-base_magnitude-all/full-dora-distributed-1"
  ],
  "updated_utc": "2026-10-10T12:02:41.565417+00:00",
  "compute_completed_utc": "2026-10-10T12:02:41.563711+00:00",
  "analysis_completed_utc": "2026-10-10T12:02:41.565406+00:00",
  "pending_comparisons": [],
  "released_utc": "2026-10-10T12:02:48.603781+00:00",
  "gpu_retained": false
}
```

Next: inspect failures immediately; otherwise follow lane plan.json sequentially, compare only completed matched outputs, retain assigned GPU after compute.

## Completed queue released GPU: gpu1

{
  "pid": 4170596,
  "lane": "gpu1",
  "gpu_uuid": "GPU_UUID",
  "status": "complete_gpu_released",
  "completed_jobs": [
    "gsm8k-dense-dora",
    "gsm8k-r32",
    "gsm8k-e95",
    "gsm8k-base_magnitude-all"
  ],
  "created_utc": "2026-10-09T21:24:47.331082+00:00",
  "job": "gsm8k-base_magnitude-all",
  "phase": "full",
  "role": "dora",
  "worker_pid": null,
  "command": [
    "/path/to/user-user/.venvs/lora-dora-research/bin/python",
    "scripts/held_gpu_worker.py",
    "scripts/series_worker.py",
    "--job",
    "/path/to/user-user/lora-dora-series/results/first-series-greedy/jobs/gsm8k-base_magnitude-all/job.json",
    "--gpu-uuid",
    "GPU_UUID",
    "--role",
    "dora",
    "--output-dir",
    "/path/to/user-user/lora-dora-series/results/first-series-greedy/jobs/gsm8k-base_magnitude-all/full-dora-distributed-1"
  ],
  "updated_utc": "2026-10-10T12:02:41.565417+00:00",
  "compute_completed_utc": "2026-10-10T12:02:41.563711+00:00",
  "analysis_completed_utc": "2026-10-10T12:02:41.565406+00:00",
  "pending_comparisons": [],
  "released_utc": "2026-10-10T12:02:48.603781+00:00",
  "gpu_retained": false
}

All GPU workers finished; any pending comparisons continue in CPU-only process. Next: other users may use this GPU; night queues only admit truly idle cards after22Moscow.

## Distributed intervention stage: gpu1 / complete_gpu_retained

UTC 2026-10-10T12:02:43.385310+00:00

State: /path/to/user-user/lora-dora-profiling/distributed-important/gpu1-state.json. External controller: /path/to/user-user/lora-dora-profiling/distributed_important.py. Frozen evaluator unchanged; versions Torch2.5.1+cu121 / Transformers4.57.1 / PEFT0.17.1 / Accelerate1.11.0.

```json
{
  "pid": 4170596,
  "lane": "gpu1",
  "gpu_uuid": "GPU_UUID",
  "status": "complete_gpu_retained",
  "completed_jobs": [
    "gsm8k-dense-dora",
    "gsm8k-r32",
    "gsm8k-e95",
    "gsm8k-base_magnitude-all"
  ],
  "created_utc": "2026-10-09T21:24:47.331082+00:00",
  "job": "gsm8k-base_magnitude-all",
  "phase": "full",
  "role": "dora",
  "worker_pid": null,
  "command": [
    "/path/to/user-user/.venvs/lora-dora-research/bin/python",
    "scripts/held_gpu_worker.py",
    "scripts/series_worker.py",
    "--job",
    "/path/to/user-user/lora-dora-series/results/first-series-greedy/jobs/gsm8k-base_magnitude-all/job.json",
    "--gpu-uuid",
    "GPU_UUID",
    "--role",
    "dora",
    "--output-dir",
    "/path/to/user-user/lora-dora-series/results/first-series-greedy/jobs/gsm8k-base_magnitude-all/full-dora-distributed-1"
  ],
  "updated_utc": "2026-10-10T12:02:41.565417+00:00",
  "compute_completed_utc": "2026-10-10T12:02:41.563711+00:00",
  "analysis_completed_utc": "2026-10-10T12:02:41.565406+00:00",
  "pending_comparisons": []
}
```

Next: inspect failures immediately; otherwise follow lane plan.json sequentially, compare only completed matched outputs, retain assigned GPU after compute.

## Distributed intervention stage: gpu4 / running

UTC 2026-10-10T10:53:12.564986+00:00

State: /path/to/user-user/lora-dora-profiling/distributed-important/gpu4-state.json. External controller: /path/to/user-user/lora-dora-profiling/distributed_shared_localizations.py. Frozen evaluator unchanged; versions Torch2.5.1+cu121 / Transformers4.57.1 / PEFT0.17.1 / Accelerate1.11.0.

```json
{
  "pid": 408126,
  "lane": "gpu4",
  "gpu_uuid": "GPU_UUID",
  "status": "running",
  "completed_jobs": [
    "gsm8k-remove_d-k"
  ],
  "created_utc": "2026-10-10T03:52:08.620351+00:00",
  "job": "gsm8k-remove_d-v",
  "phase": "full",
  "role": "dora",
  "worker_pid": 1096393,
  "command": [
    "/path/to/user-user/.venvs/lora-dora-research/bin/python",
    "/path/to/user-user/lora-dora-profiling/shared_held_gpu_worker.py",
    "scripts/series_worker.py",
    "--job",
    "/path/to/user-user/lora-dora-series/results/first-series-greedy/jobs/gsm8k-remove_d-v/job.json",
    "--gpu-uuid",
    "GPU_UUID",
    "--role",
    "dora",
    "--output-dir",
    "/path/to/user-user/lora-dora-series/results/first-series-greedy/jobs/gsm8k-remove_d-v/full-dora-distributed-1"
  ],
  "updated_utc": "2026-10-10T10:53:03.666316+00:00"
}
```

Next: inspect failures immediately; otherwise follow lane plan.json sequentially, compare only completed matched outputs, retain assigned GPU after compute.

## Distributed intervention stage: gpu4 / running

UTC 2026-10-10T10:52:42.544015+00:00

State: /path/to/user-user/lora-dora-profiling/distributed-important/gpu4-state.json. External controller: /path/to/user-user/lora-dora-profiling/distributed_shared_localizations.py. Frozen evaluator unchanged; versions Torch2.5.1+cu121 / Transformers4.57.1 / PEFT0.17.1 / Accelerate1.11.0.

```json
{
  "pid": 408126,
  "lane": "gpu4",
  "gpu_uuid": "GPU_UUID",
  "status": "running",
  "completed_jobs": [
    "gsm8k-remove_d-k"
  ],
  "created_utc": "2026-10-10T03:52:08.620351+00:00",
  "job": "gsm8k-remove_d-v",
  "phase": "smoke",
  "role": "dora",
  "worker_pid": 1095671,
  "command": [
    "/path/to/user-user/.venvs/lora-dora-research/bin/python",
    "/path/to/user-user/lora-dora-profiling/shared_held_gpu_worker.py",
    "scripts/series_worker.py",
    "--job",
    "/path/to/user-user/lora-dora-series/results/first-series-greedy/jobs/gsm8k-remove_d-v/job.json",
    "--gpu-uuid",
    "GPU_UUID",
    "--role",
    "dora",
    "--output-dir",
    "/path/to/user-user/lora-dora-series/results/first-series-greedy/jobs/gsm8k-remove_d-v/smoke-dora-distributed-1",
    "--limit",
    "2"
  ],
  "updated_utc": "2026-10-10T10:52:36.305691+00:00"
}
```

Next: inspect failures immediately; otherwise follow lane plan.json sequentially, compare only completed matched outputs, retain assigned GPU after compute.

## Distributed intervention stage: gpu2 / complete_gpu_released

UTC 2026-10-10T10:33:42.314214+00:00

State: /path/to/user-user/lora-dora-profiling/distributed-important/gpu2-state.json. External controller: /path/to/user-user/lora-dora-profiling/distributed_important.py. Frozen evaluator unchanged; versions Torch2.5.1+cu121 / Transformers4.57.1 / PEFT0.17.1 / Accelerate1.11.0.

```json
{
  "pid": 4163884,
  "lane": "gpu2",
  "gpu_uuid": "GPU_UUID",
  "status": "complete_gpu_released",
  "completed_jobs": [
    "gsm8k-dense-lora",
    "gsm8k-remove_d-all",
    "gsm8k-lora-matched-impact"
  ],
  "created_utc": "2026-10-09T21:17:50.589932+00:00",
  "worker_pid": null,
  "updated_utc": "2026-10-10T10:33:33.320386+00:00",
  "retained_gpu_uuid": "GPU_UUID",
  "job": "gsm8k-lora-matched-impact",
  "phase": "full",
  "role": "lora",
  "command": [
    "/path/to/user-user/.venvs/lora-dora-research/bin/python",
    "scripts/held_gpu_worker.py",
    "scripts/series_worker.py",
    "--job",
    "/path/to/user-user/lora-dora-series/results/first-series-greedy/jobs/gsm8k-lora-matched-impact/job.json",
    "--gpu-uuid",
    "GPU_UUID",
    "--role",
    "lora",
    "--output-dir",
    "/path/to/user-user/lora-dora-series/results/first-series-greedy/jobs/gsm8k-lora-matched-impact/full-lora-distributed-1"
  ],
  "existing_pair_completed_utc": "2026-10-10T03:04:47.603425+00:00",
  "compute_completed_utc": "2026-10-10T10:33:33.318658+00:00",
  "analysis_completed_utc": "2026-10-10T10:33:33.320357+00:00",
  "pending_comparisons": [],
  "released_utc": "2026-10-10T10:33:37.617518+00:00",
  "gpu_retained": false
}
```

Next: inspect failures immediately; otherwise follow lane plan.json sequentially, compare only completed matched outputs, retain assigned GPU after compute.

## Completed queue released GPU: gpu2

{
  "pid": 4163884,
  "lane": "gpu2",
  "gpu_uuid": "GPU_UUID",
  "status": "complete_gpu_released",
  "completed_jobs": [
    "gsm8k-dense-lora",
    "gsm8k-remove_d-all",
    "gsm8k-lora-matched-impact"
  ],
  "created_utc": "2026-10-09T21:17:50.589932+00:00",
  "worker_pid": null,
  "updated_utc": "2026-10-10T10:33:33.320386+00:00",
  "retained_gpu_uuid": "GPU_UUID",
  "job": "gsm8k-lora-matched-impact",
  "phase": "full",
  "role": "lora",
  "command": [
    "/path/to/user-user/.venvs/lora-dora-research/bin/python",
    "scripts/held_gpu_worker.py",
    "scripts/series_worker.py",
    "--job",
    "/path/to/user-user/lora-dora-series/results/first-series-greedy/jobs/gsm8k-lora-matched-impact/job.json",
    "--gpu-uuid",
    "GPU_UUID",
    "--role",
    "lora",
    "--output-dir",
    "/path/to/user-user/lora-dora-series/results/first-series-greedy/jobs/gsm8k-lora-matched-impact/full-lora-distributed-1"
  ],
  "existing_pair_completed_utc": "2026-10-10T03:04:47.603425+00:00",
  "compute_completed_utc": "2026-10-10T10:33:33.318658+00:00",
  "analysis_completed_utc": "2026-10-10T10:33:33.320357+00:00",
  "pending_comparisons": [],
  "released_utc": "2026-10-10T10:33:37.617518+00:00",
  "gpu_retained": false
}

All GPU workers finished; any pending comparisons continue in CPU-only process. Next: other users may use this GPU; night queues only admit truly idle cards after22Moscow.

## Distributed intervention stage: gpu5 / complete_gpu_released

UTC 2026-10-10T10:10:42.022612+00:00

State: /path/to/user-user/lora-dora-profiling/distributed-important/gpu5-state.json. External controller: /path/to/user-user/lora-dora-profiling/distributed_important.py. Frozen evaluator unchanged; versions Torch2.5.1+cu121 / Transformers4.57.1 / PEFT0.17.1 / Accelerate1.11.0.

```json
{
  "pid": 4164561,
  "lane": "gpu5",
  "gpu_uuid": "GPU_UUID",
  "status": "complete_gpu_released",
  "completed_jobs": [],
  "created_utc": "2026-10-09T21:18:11.000660+00:00",
  "worker_pid": null,
  "updated_utc": "2026-10-10T10:10:34.442447+00:00",
  "retained_gpu_uuid": "GPU_UUID",
  "job": "gsm8k-quality-greedy",
  "phase": "full",
  "role": "dora",
  "command": [
    "/path/to/user-user/.venvs/lora-dora-research/bin/python",
    "scripts/held_gpu_worker.py",
    "scripts/series_worker.py",
    "--job",
    "/path/to/user-user/lora-dora-series/results/first-series-greedy/jobs/gsm8k-quality-greedy/job.json",
    "--gpu-uuid",
    "GPU_UUID",
    "--role",
    "dora",
    "--output-dir",
    "/path/to/user-user/lora-dora-series/results/first-series-greedy/jobs/gsm8k-quality-greedy/full-dora-attempt-1"
  ],
  "existing_pair_completed_utc": "2026-10-10T10:10:34.392095+00:00",
  "compute_completed_utc": "2026-10-10T10:10:34.440843+00:00",
  "analysis_completed_utc": "2026-10-10T10:10:34.442418+00:00",
  "pending_comparisons": [],
  "released_utc": "2026-10-10T10:10:36.990417+00:00",
  "gpu_retained": false
}
```

Next: inspect failures immediately; otherwise follow lane plan.json sequentially, compare only completed matched outputs, retain assigned GPU after compute.

## Distributed intervention stage: gpu0 / complete_gpu_released

UTC 2026-10-10T10:10:41.998199+00:00

State: /path/to/user-user/lora-dora-profiling/distributed-important/gpu0-state.json. External controller: /path/to/user-user/lora-dora-profiling/distributed_shared_localizations.py. Frozen evaluator unchanged; versions Torch2.5.1+cu121 / Transformers4.57.1 / PEFT0.17.1 / Accelerate1.11.0.

```json
{
  "pid": 3233813,
  "lane": "gpu0",
  "gpu_uuid": "GPU_UUID",
  "status": "complete_gpu_released",
  "completed_jobs": [
    "gsm8k-remove_d-vo"
  ],
  "created_utc": "2026-10-10T03:52:07.546968+00:00",
  "job": "gsm8k-remove_d-vo",
  "phase": "full",
  "role": "dora",
  "worker_pid": null,
  "command": [
    "/path/to/user-user/.venvs/lora-dora-research/bin/python",
    "/path/to/user-user/lora-dora-profiling/shared_held_gpu_worker.py",
    "scripts/series_worker.py",
    "--job",
    "/path/to/user-user/lora-dora-series/results/first-series-greedy/jobs/gsm8k-remove_d-vo/job.json",
    "--gpu-uuid",
    "GPU_UUID",
    "--role",
    "dora",
    "--output-dir",
    "/path/to/user-user/lora-dora-series/results/first-series-greedy/jobs/gsm8k-remove_d-vo/full-dora-distributed-1"
  ],
  "updated_utc": "2026-10-10T09:26:34.742169+00:00",
  "compute_completed_utc": "2026-10-10T08:45:48.388353+00:00",
  "pending_comparisons": [
    "gsm8k-remove_d-vo"
  ],
  "previous_gpu_keeper_pid": 408122,
  "released_utc": "2026-10-10T09:26:36.782684+00:00",
  "gpu_retained": false,
  "analysis_completed_utc": "2026-10-10T10:10:38.098831+00:00"
}
```

Next: inspect failures immediately; otherwise follow lane plan.json sequentially, compare only completed matched outputs, retain assigned GPU after compute.

## Completed queue released GPU: gpu5

{
  "pid": 4164561,
  "lane": "gpu5",
  "gpu_uuid": "GPU_UUID",
  "status": "complete_gpu_released",
  "completed_jobs": [],
  "created_utc": "2026-10-09T21:18:11.000660+00:00",
  "worker_pid": null,
  "updated_utc": "2026-10-10T10:10:34.442447+00:00",
  "retained_gpu_uuid": "GPU_UUID",
  "job": "gsm8k-quality-greedy",
  "phase": "full",
  "role": "dora",
  "command": [
    "/path/to/user-user/.venvs/lora-dora-research/bin/python",
    "scripts/held_gpu_worker.py",
    "scripts/series_worker.py",
    "--job",
    "/path/to/user-user/lora-dora-series/results/first-series-greedy/jobs/gsm8k-quality-greedy/job.json",
    "--gpu-uuid",
    "GPU_UUID",
    "--role",
    "dora",
    "--output-dir",
    "/path/to/user-user/lora-dora-series/results/first-series-greedy/jobs/gsm8k-quality-greedy/full-dora-attempt-1"
  ],
  "existing_pair_completed_utc": "2026-10-10T10:10:34.392095+00:00",
  "compute_completed_utc": "2026-10-10T10:10:34.440843+00:00",
  "analysis_completed_utc": "2026-10-10T10:10:34.442418+00:00",
  "pending_comparisons": [],
  "released_utc": "2026-10-10T10:10:36.990417+00:00",
  "gpu_retained": false
}

All GPU workers finished; any pending comparisons continue in CPU-only process. Next: other users may use this GPU; night queues only admit truly idle cards after22Moscow.

## Эксперимент завершён gsm8k-quality-greedy

UTC: 2026-10-10T10:10:34.389767+00:00

```json
{
  "id": "gsm8k-quality-greedy",
  "completed": [
    "smoke/base",
    "smoke/lora",
    "smoke/dora",
    "full/base",
    "full/lora",
    "full/dora"
  ],
  "status": "complete",
  "phase": "full",
  "role": "dora",
  "output_path": "/path/to/user-user/lora-dora-series/results/first-series-greedy/jobs/gsm8k-quality-greedy/full-dora-attempt-1",
  "outputs": {
    "smoke/base": "results/first-series-greedy/jobs/gsm8k-quality-greedy/smoke-base-attempt-1",
    "smoke/lora": "results/first-series-greedy/jobs/gsm8k-quality-greedy/smoke-lora-attempt-1",
    "smoke/dora": "results/first-series-greedy/jobs/gsm8k-quality-greedy/smoke-dora-attempt-1",
    "full/base": "/path/to/user-user/lora-dora-series/results/first-series-greedy/jobs/gsm8k-quality-greedy/full-base-attempt-1",
    "full/lora": "/path/to/user-user/lora-dora-series/results/first-series-greedy/jobs/gsm8k-quality-greedy/full-lora-attempt-1",
    "full/dora": "/path/to/user-user/lora-dora-series/results/first-series-greedy/jobs/gsm8k-quality-greedy/full-dora-attempt-1"
  },
  "measured_gpu_seconds": 52448.611659129034
}
```

## gsm8k-quality-greedy / full/dora

UTC: 2026-10-10T10:10:34.193653+00:00

```json
{
  "path": "/path/to/user-user/lora-dora-series/results/first-series-greedy/jobs/gsm8k-quality-greedy/full-dora-attempt-1",
  "metrics": {
    "author_em": 0.775587566338135,
    "final_em": 0.7778620166793025
  },
  "memory": {
    "peak_allocated_bytes": 8368658432,
    "peak_reserved_bytes": 8501854208,
    "max_process_rss_bytes": 4741292032,
    "available_host_ram_bytes": 762499702784
  },
  "inference_seconds": 27570.703917281004,
  "predictions_completed": 1319,
  "full_evaluation": true,
  "versions": {
    "torch": "2.5.1+cu121",
    "transformers": "4.57.1",
    "peft": "0.17.1",
    "safetensors": "0.6.2",
    "accelerate": "1.11.0"
  }
}
```

## GPU release after compute fixed for all day and night queues — 2026-10-10T09:29:41.265978+00:00

User points out GPU0 was holding14GiB while waiting for originalDoRA comparison and explicitly requires release after GPUcompute. Earlier completion-only release monitor waited for CPUanalysis; that policy is superseded. GPU0 full removeDvo completed; verified no active child and missing primaryDoRA reference (no comparison underway), prepared CPU-only continuation3233813, terminated only completed keeper408122, preserved result/pending comparison. Actual GPU snapshot confirms neither oldkeeper nor CPUcontinuation has CUDA; GPU0 used445MiB by other contexts.

Global monitor /path/to/user-user/lora-dora-profiling/release_finished_queue_gpus.py now handles both complete_gpu_retained and compute_complete_analysis_pending with worker_pidNone and no children. It verifies same-user known keeper, prepares CPU-only continuation /path/to/user-user/lora-dora-profiling/finish_comparisons_cpu.py, releases CUDA keeper/lease, and signals CPUcontinuation to finish saved-output comparisons when references exist. Active workers and dependency-waiting computequeues are not terminated. Same policy covers all6daytime and3night queues. Normal10s polling means release within roughly10s after terminal compute state. Comparisons remain enabled; they no longer require retaining a GPU.

Validation: external syntax checked, frozen SHA256 unchanged, actual GPU0noCUDA confirmed, all5other current worker PIDs still alive/running unchanged. New generic future-release branch awaits next finishedqueue runtime validation; GPU0 CPU-only transfer already verified. Snapshot/sourcehashes/monitorPID artifact: /path/to/user-user/lora-dora-profiling/distributed-important/release-after-compute-fix.json. Versions unchanged Python3.12.3 / Torch2.5.1+cu121 / Transformers4.57.1 / PEFT0.17.1 / Accelerate1.11.0.

Next: verify automatic release of next completed queue and deferred CPUcomparison completion; preserve22:00night trulyidle admission/no daytime reservations. No inference scope changes, no foreign process modification.

## Distributed intervention stage: gpu0 / compute_complete_gpu_released_analysis_pending

UTC 2026-10-10T09:26:41.409747+00:00

State: /path/to/user-user/lora-dora-profiling/distributed-important/gpu0-state.json. External controller: /path/to/user-user/lora-dora-profiling/distributed_shared_localizations.py. Frozen evaluator unchanged; versions Torch2.5.1+cu121 / Transformers4.57.1 / PEFT0.17.1 / Accelerate1.11.0.

```json
{
  "pid": 3233813,
  "lane": "gpu0",
  "gpu_uuid": "GPU_UUID",
  "status": "compute_complete_gpu_released_analysis_pending",
  "completed_jobs": [
    "gsm8k-remove_d-vo"
  ],
  "created_utc": "2026-10-10T03:52:07.546968+00:00",
  "job": "gsm8k-remove_d-vo",
  "phase": "full",
  "role": "dora",
  "worker_pid": null,
  "command": [
    "/path/to/user-user/.venvs/lora-dora-research/bin/python",
    "/path/to/user-user/lora-dora-profiling/shared_held_gpu_worker.py",
    "scripts/series_worker.py",
    "--job",
    "/path/to/user-user/lora-dora-series/results/first-series-greedy/jobs/gsm8k-remove_d-vo/job.json",
    "--gpu-uuid",
    "GPU_UUID",
    "--role",
    "dora",
    "--output-dir",
    "/path/to/user-user/lora-dora-series/results/first-series-greedy/jobs/gsm8k-remove_d-vo/full-dora-distributed-1"
  ],
  "updated_utc": "2026-10-10T09:26:34.742169+00:00",
  "compute_completed_utc": "2026-10-10T08:45:48.388353+00:00",
  "pending_comparisons": [
    "gsm8k-remove_d-vo"
  ],
  "previous_gpu_keeper_pid": 408122,
  "released_utc": "2026-10-10T09:26:36.782684+00:00",
  "gpu_retained": false
}
```

Next: inspect failures immediately; otherwise follow lane plan.json sequentially, compare only completed matched outputs, retain assigned GPU after compute.

## Distributed intervention stage: gpu0 / compute_complete_analysis_pending

UTC 2026-10-10T08:45:50.847926+00:00

State: /path/to/user-user/lora-dora-profiling/distributed-important/gpu0-state.json. External controller: /path/to/user-user/lora-dora-profiling/distributed_shared_localizations.py. Frozen evaluator unchanged; versions Torch2.5.1+cu121 / Transformers4.57.1 / PEFT0.17.1 / Accelerate1.11.0.

```json
{
  "pid": 408122,
  "lane": "gpu0",
  "gpu_uuid": "GPU_UUID",
  "status": "compute_complete_analysis_pending",
  "completed_jobs": [
    "gsm8k-remove_d-vo"
  ],
  "created_utc": "2026-10-10T03:52:07.546968+00:00",
  "job": "gsm8k-remove_d-vo",
  "phase": "full",
  "role": "dora",
  "worker_pid": null,
  "command": [
    "/path/to/user-user/.venvs/lora-dora-research/bin/python",
    "/path/to/user-user/lora-dora-profiling/shared_held_gpu_worker.py",
    "scripts/series_worker.py",
    "--job",
    "/path/to/user-user/lora-dora-series/results/first-series-greedy/jobs/gsm8k-remove_d-vo/job.json",
    "--gpu-uuid",
    "GPU_UUID",
    "--role",
    "dora",
    "--output-dir",
    "/path/to/user-user/lora-dora-series/results/first-series-greedy/jobs/gsm8k-remove_d-vo/full-dora-distributed-1"
  ],
  "updated_utc": "2026-10-10T08:45:48.390472+00:00",
  "compute_completed_utc": "2026-10-10T08:45:48.388353+00:00",
  "pending_comparisons": [
    "gsm8k-remove_d-vo"
  ]
}
```

Next: inspect failures immediately; otherwise follow lane plan.json sequentially, compare only completed matched outputs, retain assigned GPU after compute.

## User decision: hypothesis-driven Answer.AI validation after Qwen analysis — 2026-10-10T08:20:23.797893+00:00

Answer.AI is a follow-up validation stage, not an automatic evaluation of all four candidate pairs. First finish the scheduled Qwen measurements and analyze them to formulate a concrete supported observation/hypothesis. Then select specific Answer.AI checkpoint pair(s), interventions and matched controls to test whether the same observation holds outside Qwen. Selection remains pending the Qwen findings; no particular Answer.AI pair is committed by this decision.

Do not automatically enqueue all four Answer.AI pairs or consume a six-GPU night merely because hardware is available. Assess expected scientific value, loader/intervention compatibility and measured runtime before scheduling the selected validation. Obtaining approved Hugging Face access may proceed as preparation; access alone is not authorization to launch full Answer.AI evaluations. Current ready Qwen/daytime/night queues and their resource/release policies remain unchanged. No Answer.AI full run added now.

Preserve interpretive limits: an observed effect need not generalize; a changed architecture/project/quantization introduces multiple differences. Test the stated observation with appropriate controls, including null/opposite outcomes; do not assume a DoRA advantage or infer training-trajectory causes from final-checkpoint interventions.

Next: complete and analyze Qwen results, state the hypothesis and its evidential limits, then propose a focused Answer.AI validation with real pilot-based resource estimates. The earlier recommendation to begin with Llama2/100k is not an approved selection and must not override this later user decision.

## Distributed intervention stage: gpu2 / running

UTC 2026-10-10T08:09:10.394547+00:00

State: /path/to/user-user/lora-dora-profiling/distributed-important/gpu2-state.json. External controller: /path/to/user-user/lora-dora-profiling/distributed_important.py. Frozen evaluator unchanged; versions Torch2.5.1+cu121 / Transformers4.57.1 / PEFT0.17.1 / Accelerate1.11.0.

```json
{
  "pid": 4163884,
  "lane": "gpu2",
  "gpu_uuid": "GPU_UUID",
  "status": "running",
  "completed_jobs": [
    "gsm8k-dense-lora",
    "gsm8k-remove_d-all"
  ],
  "created_utc": "2026-10-09T21:17:50.589932+00:00",
  "worker_pid": 2566958,
  "updated_utc": "2026-10-10T08:09:01.726471+00:00",
  "retained_gpu_uuid": "GPU_UUID",
  "job": "gsm8k-lora-matched-impact",
  "phase": "full",
  "role": "lora",
  "command": [
    "/path/to/user-user/.venvs/lora-dora-research/bin/python",
    "scripts/held_gpu_worker.py",
    "scripts/series_worker.py",
    "--job",
    "/path/to/user-user/lora-dora-series/results/first-series-greedy/jobs/gsm8k-lora-matched-impact/job.json",
    "--gpu-uuid",
    "GPU_UUID",
    "--role",
    "lora",
    "--output-dir",
    "/path/to/user-user/lora-dora-series/results/first-series-greedy/jobs/gsm8k-lora-matched-impact/full-lora-distributed-1"
  ],
  "existing_pair_completed_utc": "2026-10-10T03:04:47.603425+00:00"
}
```

Next: inspect failures immediately; otherwise follow lane plan.json sequentially, compare only completed matched outputs, retain assigned GPU after compute.

## Distributed intervention stage: gpu2 / running

UTC 2026-10-10T08:04:20.296252+00:00

State: /path/to/user-user/lora-dora-profiling/distributed-important/gpu2-state.json. External controller: /path/to/user-user/lora-dora-profiling/distributed_important.py. Frozen evaluator unchanged; versions Torch2.5.1+cu121 / Transformers4.57.1 / PEFT0.17.1 / Accelerate1.11.0.

```json
{
  "pid": 4163884,
  "lane": "gpu2",
  "gpu_uuid": "GPU_UUID",
  "status": "running",
  "completed_jobs": [
    "gsm8k-dense-lora",
    "gsm8k-remove_d-all"
  ],
  "created_utc": "2026-10-09T21:17:50.589932+00:00",
  "worker_pid": 2561429,
  "updated_utc": "2026-10-10T08:04:14.215273+00:00",
  "retained_gpu_uuid": "GPU_UUID",
  "job": "gsm8k-lora-matched-impact",
  "phase": "smoke",
  "role": "lora",
  "command": [
    "/path/to/user-user/.venvs/lora-dora-research/bin/python",
    "scripts/held_gpu_worker.py",
    "scripts/series_worker.py",
    "--job",
    "/path/to/user-user/lora-dora-series/results/first-series-greedy/jobs/gsm8k-lora-matched-impact/job.json",
    "--gpu-uuid",
    "GPU_UUID",
    "--role",
    "lora",
    "--output-dir",
    "/path/to/user-user/lora-dora-series/results/first-series-greedy/jobs/gsm8k-lora-matched-impact/smoke-lora-distributed-1",
    "--limit",
    "2"
  ],
  "existing_pair_completed_utc": "2026-10-10T03:04:47.603425+00:00"
}
```

Next: inspect failures immediately; otherwise follow lane plan.json sequentially, compare only completed matched outputs, retain assigned GPU after compute.

## Distributed intervention stage: gpu6 / running

UTC 2026-10-10T05:47:38.317099+00:00

State: /path/to/user-user/lora-dora-profiling/distributed-important/gpu6-state.json. External controller: /path/to/user-user/lora-dora-profiling/distributed_localizations_v2.py. Frozen evaluator unchanged; versions Torch2.5.1+cu121 / Transformers4.57.1 / PEFT0.17.1 / Accelerate1.11.0.

```json
{
  "pid": 402546,
  "lane": "gpu6",
  "gpu_uuid": "GPU_UUID",
  "status": "running",
  "completed_jobs": [
    "short-vo",
    "gsm8k-e99",
    "gsm8k-remove_d-q"
  ],
  "created_utc": "2026-10-10T03:46:56.152087+00:00",
  "worker_pid": 501232,
  "updated_utc": "2026-10-10T05:47:34.108360+00:00",
  "job": "gsm8k-base_magnitude-v",
  "phase": "full",
  "role": "dora",
  "command": [
    "/path/to/user-user/.venvs/lora-dora-research/bin/python",
    "scripts/held_gpu_worker.py",
    "scripts/series_worker.py",
    "--job",
    "/path/to/user-user/lora-dora-series/results/first-series-greedy/jobs/gsm8k-base_magnitude-v/job.json",
    "--gpu-uuid",
    "GPU_UUID",
    "--role",
    "dora",
    "--output-dir",
    "/path/to/user-user/lora-dora-series/results/first-series-greedy/jobs/gsm8k-base_magnitude-v/full-dora-distributed-1"
  ]
}
```

Next: inspect failures immediately; otherwise follow lane plan.json sequentially, compare only completed matched outputs, retain assigned GPU after compute.

## Distributed intervention stage: gpu6 / running

UTC 2026-10-10T05:47:08.292195+00:00

State: /path/to/user-user/lora-dora-profiling/distributed-important/gpu6-state.json. External controller: /path/to/user-user/lora-dora-profiling/distributed_localizations_v2.py. Frozen evaluator unchanged; versions Torch2.5.1+cu121 / Transformers4.57.1 / PEFT0.17.1 / Accelerate1.11.0.

```json
{
  "pid": 402546,
  "lane": "gpu6",
  "gpu_uuid": "GPU_UUID",
  "status": "running",
  "completed_jobs": [
    "short-vo",
    "gsm8k-e99",
    "gsm8k-remove_d-q"
  ],
  "created_utc": "2026-10-10T03:46:56.152087+00:00",
  "worker_pid": 500381,
  "updated_utc": "2026-10-10T05:47:02.111213+00:00",
  "job": "gsm8k-base_magnitude-v",
  "phase": "smoke",
  "role": "dora",
  "command": [
    "/path/to/user-user/.venvs/lora-dora-research/bin/python",
    "scripts/held_gpu_worker.py",
    "scripts/series_worker.py",
    "--job",
    "/path/to/user-user/lora-dora-series/results/first-series-greedy/jobs/gsm8k-base_magnitude-v/job.json",
    "--gpu-uuid",
    "GPU_UUID",
    "--role",
    "dora",
    "--output-dir",
    "/path/to/user-user/lora-dora-series/results/first-series-greedy/jobs/gsm8k-base_magnitude-v/smoke-dora-distributed-1",
    "--limit",
    "2"
  ]
}
```

Next: inspect failures immediately; otherwise follow lane plan.json sequentially, compare only completed matched outputs, retain assigned GPU after compute.

## Distributed intervention stage: gpu2 / running

UTC 2026-10-10T05:14:57.870324+00:00

State: /path/to/user-user/lora-dora-profiling/distributed-important/gpu2-state.json. External controller: /path/to/user-user/lora-dora-profiling/distributed_important.py. Frozen evaluator unchanged; versions Torch2.5.1+cu121 / Transformers4.57.1 / PEFT0.17.1 / Accelerate1.11.0.

```json
{
  "pid": 4163884,
  "lane": "gpu2",
  "gpu_uuid": "GPU_UUID",
  "status": "running",
  "completed_jobs": [
    "gsm8k-dense-lora"
  ],
  "created_utc": "2026-10-09T21:17:50.589932+00:00",
  "worker_pid": 473181,
  "updated_utc": "2026-10-10T05:14:48.435277+00:00",
  "retained_gpu_uuid": "GPU_UUID",
  "job": "gsm8k-remove_d-all",
  "phase": "full",
  "role": "dora",
  "command": [
    "/path/to/user-user/.venvs/lora-dora-research/bin/python",
    "scripts/held_gpu_worker.py",
    "scripts/series_worker.py",
    "--job",
    "/path/to/user-user/lora-dora-series/results/first-series-greedy/jobs/gsm8k-remove_d-all/job.json",
    "--gpu-uuid",
    "GPU_UUID",
    "--role",
    "dora",
    "--output-dir",
    "/path/to/user-user/lora-dora-series/results/first-series-greedy/jobs/gsm8k-remove_d-all/full-dora-distributed-1"
  ],
  "existing_pair_completed_utc": "2026-10-10T03:04:47.603425+00:00"
}
```

Next: inspect failures immediately; otherwise follow lane plan.json sequentially, compare only completed matched outputs, retain assigned GPU after compute.

## Distributed intervention stage: gpu2 / running

UTC 2026-10-10T05:14:37.846943+00:00

State: /path/to/user-user/lora-dora-profiling/distributed-important/gpu2-state.json. External controller: /path/to/user-user/lora-dora-profiling/distributed_important.py. Frozen evaluator unchanged; versions Torch2.5.1+cu121 / Transformers4.57.1 / PEFT0.17.1 / Accelerate1.11.0.

```json
{
  "pid": 4163884,
  "lane": "gpu2",
  "gpu_uuid": "GPU_UUID",
  "status": "running",
  "completed_jobs": [
    "gsm8k-dense-lora"
  ],
  "created_utc": "2026-10-09T21:17:50.589932+00:00",
  "worker_pid": 472896,
  "updated_utc": "2026-10-10T05:14:30.549707+00:00",
  "retained_gpu_uuid": "GPU_UUID",
  "job": "gsm8k-remove_d-all",
  "phase": "smoke",
  "role": "dora",
  "command": [
    "/path/to/user-user/.venvs/lora-dora-research/bin/python",
    "scripts/held_gpu_worker.py",
    "scripts/series_worker.py",
    "--job",
    "/path/to/user-user/lora-dora-series/results/first-series-greedy/jobs/gsm8k-remove_d-all/job.json",
    "--gpu-uuid",
    "GPU_UUID",
    "--role",
    "dora",
    "--output-dir",
    "/path/to/user-user/lora-dora-series/results/first-series-greedy/jobs/gsm8k-remove_d-all/smoke-dora-distributed-1",
    "--limit",
    "2"
  ],
  "existing_pair_completed_utc": "2026-10-10T03:04:47.603425+00:00"
}
```

Next: inspect failures immediately; otherwise follow lane plan.json sequentially, compare only completed matched outputs, retain assigned GPU after compute.

## Distributed intervention stage: gpu1 / running

UTC 2026-10-10T04:16:57.072876+00:00

State: /path/to/user-user/lora-dora-profiling/distributed-important/gpu1-state.json. External controller: /path/to/user-user/lora-dora-profiling/distributed_important.py. Frozen evaluator unchanged; versions Torch2.5.1+cu121 / Transformers4.57.1 / PEFT0.17.1 / Accelerate1.11.0.

```json
{
  "pid": 4170596,
  "lane": "gpu1",
  "gpu_uuid": "GPU_UUID",
  "status": "running",
  "completed_jobs": [
    "gsm8k-dense-dora",
    "gsm8k-r32",
    "gsm8k-e95"
  ],
  "created_utc": "2026-10-09T21:24:47.331082+00:00",
  "job": "gsm8k-base_magnitude-all",
  "phase": "full",
  "role": "dora",
  "worker_pid": 429162,
  "command": [
    "/path/to/user-user/.venvs/lora-dora-research/bin/python",
    "scripts/held_gpu_worker.py",
    "scripts/series_worker.py",
    "--job",
    "/path/to/user-user/lora-dora-series/results/first-series-greedy/jobs/gsm8k-base_magnitude-all/job.json",
    "--gpu-uuid",
    "GPU_UUID",
    "--role",
    "dora",
    "--output-dir",
    "/path/to/user-user/lora-dora-series/results/first-series-greedy/jobs/gsm8k-base_magnitude-all/full-dora-distributed-1"
  ],
  "updated_utc": "2026-10-10T04:16:54.799079+00:00"
}
```

Next: inspect failures immediately; otherwise follow lane plan.json sequentially, compare only completed matched outputs, retain assigned GPU after compute.

## Distributed intervention stage: gpu1 / running

UTC 2026-10-10T04:16:27.046535+00:00

State: /path/to/user-user/lora-dora-profiling/distributed-important/gpu1-state.json. External controller: /path/to/user-user/lora-dora-profiling/distributed_important.py. Frozen evaluator unchanged; versions Torch2.5.1+cu121 / Transformers4.57.1 / PEFT0.17.1 / Accelerate1.11.0.

```json
{
  "pid": 4170596,
  "lane": "gpu1",
  "gpu_uuid": "GPU_UUID",
  "status": "running",
  "completed_jobs": [
    "gsm8k-dense-dora",
    "gsm8k-r32",
    "gsm8k-e95"
  ],
  "created_utc": "2026-10-09T21:24:47.331082+00:00",
  "job": "gsm8k-base_magnitude-all",
  "phase": "smoke",
  "role": "dora",
  "worker_pid": 428605,
  "command": [
    "/path/to/user-user/.venvs/lora-dora-research/bin/python",
    "scripts/held_gpu_worker.py",
    "scripts/series_worker.py",
    "--job",
    "/path/to/user-user/lora-dora-series/results/first-series-greedy/jobs/gsm8k-base_magnitude-all/job.json",
    "--gpu-uuid",
    "GPU_UUID",
    "--role",
    "dora",
    "--output-dir",
    "/path/to/user-user/lora-dora-series/results/first-series-greedy/jobs/gsm8k-base_magnitude-all/smoke-dora-distributed-1",
    "--limit",
    "2"
  ],
  "updated_utc": "2026-10-10T04:16:25.318659+00:00"
}
```

Next: inspect failures immediately; otherwise follow lane plan.json sequentially, compare only completed matched outputs, retain assigned GPU after compute.

## Three truly idle night queues scheduled; completed GPU retention disabled — 2026-10-10T04:06:10.353558+00:00

User schedules3remaining independent localizations not before10October22:00Moscow (19:00UTC), then requests release of current cards so other users can work. Night plan /path/to/user-user/lora-dora-profiling/distributed-important/night-plan.json contains baseMagnitude-k/o/qk, ~7.86/7.89/7.88h, total23.6245GPUh. CPU-only delayed admission processes419770/419771/419772 are sleeping until22, no CUDA/context/lease/reservation before then. After22 require2trulyidle snapshots10s apart; any foreign context excludes a card. Cooperative permit cap6. Night queues do not inherit or reserve daytime cards. Existing sharing permission on0/4 is NOT applied to these night admissions.

Release monitor419773 /path/to/user-user/lora-dora-profiling/release_finished_queue_gpus.py terminates only verified own keepers after statuscomplete_gpu_retained, worker_pidNone and no children. No SIGSTOP, no active worker/comparison interrupted. CUDA context/reservation and lease released once queue finishes; others can use cards before22. If a queue is waiting for CPU comparisons, those remain enabled and completion precedes release.

User briefly requested stop of comparisons, then explicitly reversed: do not stop. Attempt to SIGSTOP coordinators was rejected before execution by automatic review (risk of blocking queues/GPUrelease). No coordinators suspended and no comparison pause applied. Comparisons remain enabled. Additional forecast budget for CPU paired bootstrap/Holm=0GPUh; dense-reference GPUevaluations are separate experiments, not the CPU statistics.

Night worker /path/to/user-user/lora-dora-profiling/night_localization_worker.py uses frozen evaluator and separate3contrast Holm family. No frozen source changes; Python3.12.3 / Torch2.5.1+cu121 / Transformers4.57.1 / PEFT0.17.1 / Accelerate1.11.0 unchanged. External scripts compile; night plan frozen hash and3waiting state verified. Runtime admission/inference validation pending until22. Earliest finish~11October06:00 if admitted22; completion by09–10 requires admission by roughly01–02Moscow, not guaranteed if cards occupied or throughput slower.

All3previously unscheduled localizations are now scheduled, unallocated budget0GPUh. Current daytime plan historical deferred list retains those3for provenance; authoritative night assignment is night-plan.json. Next: preserve current comparison/inference behavior, release completed queues, admit night jobs only after22on actuallyidle GPUs, append real completions to HANDOFF.

## Shared GPU0/GPU4 smoke verified; full evaluations running — 2026-10-10T03:53:48.831852+00:00

Both real-weight two-example smoke evaluations completed successfully with adapter validation and explicit per-worker sharing audits. Both controllers advanced to full evaluation; no full quality completion claimed.

```json
[
  {
    "lane": "gpu0",
    "smoke_path": "/path/to/user-user/lora-dora-series/results/first-series-greedy/jobs/gsm8k-remove_d-vo/smoke-dora-distributed-1",
    "inference_seconds": 16.586888224934228,
    "full_worker_pid": 408922
  },
  {
    "lane": "gpu4",
    "smoke_path": "/path/to/user-user/lora-dora-series/results/first-series-greedy/jobs/gsm8k-remove_d-k/smoke-dora-distributed-1",
    "inference_seconds": 16.007325037033297,
    "full_worker_pid": 408920
  }
]
```

Next: continue full localization queues, compare only complete matched outputs and update timing from actual throughput.

## User-authorized shared launches on physical GPU0 and GPU4 — 2026-10-10T03:53:06.718363+00:00

User explicitly says launch over existing contexts if GPU0/4 load unchanged. Two snapshots10s apart confirmed GPU0=0%/279MiB and GPU4=0%/171MiB with same tiny foreign contexts. Waiting-only admission PIDs402742/402743 cancelled; new holders408122/408126 started on exact requested cards with slots4/5. Existing foreign PIDs1661711/321456 untouched. Six research cards now active including otherGPU2/3/5/6.

Explicit sharing policy: /path/to/user-user/lora-dora-profiling/distributed-important/shared-admission-policy.json records real original GPU/process snapshots and PIDstartticks. External wrapper /path/to/user-user/lora-dora-profiling/shared_held_gpu_worker.py permits only authorized known foreign contexts <=512MiB each, total used<=1024MiB and utilization<=10% at admission. Unknown/new contexts fail guard; preceding own-worker utilization may settle for10s. Same-user direct parent and inherited GPU/slot leases still verified by original wrapper. Per-worker shared-admission.json records real measurements, authorization and decision. This is a documented admission extension, not a claim that cards were empty. No foreign process killed or modified. No changes to frozen inference, model loading, seed, dataset, generation, scoring or source SHA256; provenance includes external wrapper hashes. Sharing may change resource timing.

GPU0 removeDvo ~4.80h, estimated finish 2026-10-10T11:40:09.976414+03:00; GPU4 removeDk/v/o/qk ~25.44h, estimated finish 2026-10-11T08:18:20.332432+03:00. Both currently statusrunning; initial smoke/startup validation proceeds, full quality not yet claimed. Future workers use same documented sharing policy. Other queues unchanged, GPU6 remains near08:15Oct11. Three unscheduled baseMagnitude k/o/qk unchanged23.6245GPUh. Versions unchanged Python3.12.3 / Torch2.5.1+cu121 / Transformers4.57.1 / PEFT0.17.1 / Accelerate1.11.0.

Report/load/runtime state/external source hashes: /path/to/user-user/lora-dora-profiling/distributed-important/shared-launch-report.json. Next: verify smoke success then full launches, monitor shared resource timing and queue errors, retain cards after compute. Do not add sharing permission to other GPUs or foreign processes beyond this recorded authorization.

## Distributed intervention stage: gpu4 / running

UTC 2026-10-10T03:52:45.645521+00:00

State: /path/to/user-user/lora-dora-profiling/distributed-important/gpu4-state.json. External controller: /path/to/user-user/lora-dora-profiling/distributed_localizations_v2.py. Frozen evaluator unchanged; versions Torch2.5.1+cu121 / Transformers4.57.1 / PEFT0.17.1 / Accelerate1.11.0.

```json
{
  "pid": 408126,
  "lane": "gpu4",
  "gpu_uuid": "GPU_UUID",
  "status": "running",
  "completed_jobs": [],
  "created_utc": "2026-10-10T03:52:08.620351+00:00",
  "job": "gsm8k-remove_d-k",
  "phase": "full",
  "role": "dora",
  "worker_pid": 408920,
  "command": [
    "/path/to/user-user/.venvs/lora-dora-research/bin/python",
    "/path/to/user-user/lora-dora-profiling/shared_held_gpu_worker.py",
    "scripts/series_worker.py",
    "--job",
    "/path/to/user-user/lora-dora-series/results/first-series-greedy/jobs/gsm8k-remove_d-k/job.json",
    "--gpu-uuid",
    "GPU_UUID",
    "--role",
    "dora",
    "--output-dir",
    "/path/to/user-user/lora-dora-series/results/first-series-greedy/jobs/gsm8k-remove_d-k/full-dora-distributed-1"
  ],
  "updated_utc": "2026-10-10T03:52:38.032275+00:00"
}
```

Next: inspect failures immediately; otherwise follow lane plan.json sequentially, compare only completed matched outputs, retain assigned GPU after compute.

## Distributed intervention stage: gpu0 / running

UTC 2026-10-10T03:52:45.623979+00:00

State: /path/to/user-user/lora-dora-profiling/distributed-important/gpu0-state.json. External controller: /path/to/user-user/lora-dora-profiling/distributed_localizations_v2.py. Frozen evaluator unchanged; versions Torch2.5.1+cu121 / Transformers4.57.1 / PEFT0.17.1 / Accelerate1.11.0.

```json
{
  "pid": 408122,
  "lane": "gpu0",
  "gpu_uuid": "GPU_UUID",
  "status": "running",
  "completed_jobs": [],
  "created_utc": "2026-10-10T03:52:07.546968+00:00",
  "job": "gsm8k-remove_d-vo",
  "phase": "full",
  "role": "dora",
  "worker_pid": 408922,
  "command": [
    "/path/to/user-user/.venvs/lora-dora-research/bin/python",
    "/path/to/user-user/lora-dora-profiling/shared_held_gpu_worker.py",
    "scripts/series_worker.py",
    "--job",
    "/path/to/user-user/lora-dora-series/results/first-series-greedy/jobs/gsm8k-remove_d-vo/job.json",
    "--gpu-uuid",
    "GPU_UUID",
    "--role",
    "dora",
    "--output-dir",
    "/path/to/user-user/lora-dora-series/results/first-series-greedy/jobs/gsm8k-remove_d-vo/full-dora-distributed-1"
  ],
  "updated_utc": "2026-10-10T03:52:38.086836+00:00"
}
```

Next: inspect failures immediately; otherwise follow lane plan.json sequentially, compare only completed matched outputs, retain assigned GPU after compute.

## Distributed intervention stage: gpu4 / running

UTC 2026-10-10T03:52:15.608261+00:00

State: /path/to/user-user/lora-dora-profiling/distributed-important/gpu4-state.json. External controller: /path/to/user-user/lora-dora-profiling/distributed_localizations_v2.py. Frozen evaluator unchanged; versions Torch2.5.1+cu121 / Transformers4.57.1 / PEFT0.17.1 / Accelerate1.11.0.

```json
{
  "pid": 408126,
  "lane": "gpu4",
  "gpu_uuid": "GPU_UUID",
  "status": "running",
  "completed_jobs": [],
  "created_utc": "2026-10-10T03:52:08.620351+00:00",
  "job": "gsm8k-remove_d-k",
  "phase": "smoke",
  "role": "dora",
  "worker_pid": 408360,
  "command": [
    "/path/to/user-user/.venvs/lora-dora-research/bin/python",
    "/path/to/user-user/lora-dora-profiling/shared_held_gpu_worker.py",
    "scripts/series_worker.py",
    "--job",
    "/path/to/user-user/lora-dora-series/results/first-series-greedy/jobs/gsm8k-remove_d-k/job.json",
    "--gpu-uuid",
    "GPU_UUID",
    "--role",
    "dora",
    "--output-dir",
    "/path/to/user-user/lora-dora-series/results/first-series-greedy/jobs/gsm8k-remove_d-k/smoke-dora-distributed-1",
    "--limit",
    "2"
  ],
  "updated_utc": "2026-10-10T03:52:08.652490+00:00"
}
```

Next: inspect failures immediately; otherwise follow lane plan.json sequentially, compare only completed matched outputs, retain assigned GPU after compute.

## Distributed intervention stage: gpu0 / running

UTC 2026-10-10T03:52:15.586965+00:00

State: /path/to/user-user/lora-dora-profiling/distributed-important/gpu0-state.json. External controller: /path/to/user-user/lora-dora-profiling/distributed_localizations_v2.py. Frozen evaluator unchanged; versions Torch2.5.1+cu121 / Transformers4.57.1 / PEFT0.17.1 / Accelerate1.11.0.

```json
{
  "pid": 408122,
  "lane": "gpu0",
  "gpu_uuid": "GPU_UUID",
  "status": "running",
  "completed_jobs": [],
  "created_utc": "2026-10-10T03:52:07.546968+00:00",
  "job": "gsm8k-remove_d-vo",
  "phase": "smoke",
  "role": "dora",
  "worker_pid": 408342,
  "command": [
    "/path/to/user-user/.venvs/lora-dora-research/bin/python",
    "/path/to/user-user/lora-dora-profiling/shared_held_gpu_worker.py",
    "scripts/series_worker.py",
    "--job",
    "/path/to/user-user/lora-dora-series/results/first-series-greedy/jobs/gsm8k-remove_d-vo/job.json",
    "--gpu-uuid",
    "GPU_UUID",
    "--role",
    "dora",
    "--output-dir",
    "/path/to/user-user/lora-dora-series/results/first-series-greedy/jobs/gsm8k-remove_d-vo/smoke-dora-distributed-1",
    "--limit",
    "2"
  ],
  "updated_utc": "2026-10-10T03:52:07.600382+00:00"
}
```

Next: inspect failures immediately; otherwise follow lane plan.json sequentially, compare only completed matched outputs, retain assigned GPU after compute.

## Distributed intervention stage: gpu4 / admitted_shared_by_user

UTC 2026-10-10T03:52:05.574732+00:00

State: /path/to/user-user/lora-dora-profiling/distributed-important/gpu4-admission.json. External controller: /path/to/user-user/lora-dora-profiling/distributed_localizations_v2.py. Frozen evaluator unchanged; versions Torch2.5.1+cu121 / Transformers4.57.1 / PEFT0.17.1 / Accelerate1.11.0.

```json
{
  "pid": 408126,
  "status": "admitted_shared_by_user",
  "gpu_uuid": "GPU_UUID",
  "policy": {
    "initial_gpu": {
      "index": 4,
      "uuid": "GPU_UUID",
      "name": "NVIDIA RTX A4000",
      "total_mib": 16376,
      "used_mib": 171,
      "utilization_percent": 0
    },
    "foreign_start_ticks": {
      "321456": "43186507"
    },
    "initial_processes": [
      {
        "gpu_uuid": "GPU_UUID",
        "pid": 321456,
        "memory_mib": "160"
      }
    ]
  },
  "slot": 5
}
```

Next: inspect failures immediately; otherwise follow lane plan.json sequentially, compare only completed matched outputs, retain assigned GPU after compute.

## Distributed intervention stage: gpu0 / admitted_shared_by_user

UTC 2026-10-10T03:52:05.553264+00:00

State: /path/to/user-user/lora-dora-profiling/distributed-important/gpu0-admission.json. External controller: /path/to/user-user/lora-dora-profiling/distributed_localizations_v2.py. Frozen evaluator unchanged; versions Torch2.5.1+cu121 / Transformers4.57.1 / PEFT0.17.1 / Accelerate1.11.0.

```json
{
  "pid": 408122,
  "status": "admitted_shared_by_user",
  "gpu_uuid": "GPU_UUID",
  "policy": {
    "initial_gpu": {
      "index": 0,
      "uuid": "GPU_UUID",
      "name": "NVIDIA RTX A4000",
      "total_mib": 16376,
      "used_mib": 279,
      "utilization_percent": 0
    },
    "foreign_start_ticks": {
      "1661711": "50869200"
    },
    "initial_processes": [
      {
        "gpu_uuid": "GPU_UUID",
        "pid": 1661711,
        "memory_mib": "270"
      }
    ]
  },
  "slot": 4
}
```

Next: inspect failures immediately; otherwise follow lane plan.json sequentially, compare only completed matched outputs, retain assigned GPU after compute.

## Rebalanced localizations across requested GPU0/GPU4/GPU6 — 2026-10-10T03:48:32.191365+00:00

User explicitly requests GPU0~4h, GPU4~25h, GPU6 finishing near08:00Oct11. This authorizes6cards in total once admitted, overriding prior5cap; no foreign processes touched. PhysicalGPU0/4 still have foreign CUDA processes, so new admission queues402742/402743 wait for2trulyidle checks10s apart. No CUDA initialized on occupied cards. External permit slots4/5 under new6card cap.

GPU0: removeD-vo,4.8007h (shortest whole remaining evaluation, cannot promise4h). GPU4: removeD-k/v/o/qk,25.4366h after admission. GPU6: preserve running removeD-q worker111155, then baseMagnitude-v/q/vo,23.5008future hours; estimated finish 2026-10-11T08:14:11.843947+03:00. Reassigned3notstartedremoveD jobs from6to4 and added baseMagnitude q/vo to6 to balance near requested time. No partial or duplicated full evaluations. New coordinator402546 verified CUDA context before stopping old4178348; runningworker preserved. Controller/manifest: /path/to/user-user/lora-dora-profiling/distributed_localizations_v2.py, /path/to/user-user/lora-dora-profiling/distributed-important/gpu6-rebalance-go.json.

Remaining unscheduled3localizations: baseMagnitude-k/o/qk,23.6245GPUh. Active plan /path/to/user-user/lora-dora-profiling/distributed-important/plan.json has9localized contrasts; localization Holm family expanded before any localized full results completed. Core8 family unchanged; no joint17correction claimed. Frozen evaluator SHA256 unchanged; external source compiled and unique job ownership/deferred disjointness validated. Versions unchanged Python3.12.3 / Torch2.5.1+cu121 / Transformers4.57.1 / PEFT0.17.1 / Accelerate1.11.0. New GPU0/4 pipelines pending idle admission/runtime validation.

Fresh load/status/forecast artifact: /path/to/user-user/lora-dora-profiling/distributed-important/six-gpu-localization-schedule.json. Important: GPU0/4 are queued, not occupied by us; absolute completion unknown until foreign contexts leave. Next: monitor idle admission, complete adopted removeDq, run revised lane jobs, append actual stage transitions, retain assigned cards after compute. OtherGPU2/3/5queues unchanged.

## Distributed intervention stage: gpu4 / waiting_for_idle_gpu

UTC 2026-10-10T03:47:35.490591+00:00

State: /path/to/user-user/lora-dora-profiling/distributed-important/gpu4-admission.json. External controller: /path/to/user-user/lora-dora-profiling/distributed_localizations_v2.py. Frozen evaluator unchanged; versions Torch2.5.1+cu121 / Transformers4.57.1 / PEFT0.17.1 / Accelerate1.11.0.

```json
{
  "pid": 402743,
  "gpu_uuid": "GPU_UUID",
  "gpu_index": 4,
  "status": "waiting_for_idle_gpu",
  "consecutive_idle_checks": 0,
  "slot": 5
}
```

Next: inspect failures immediately; otherwise follow lane plan.json sequentially, compare only completed matched outputs, retain assigned GPU after compute.

## Distributed intervention stage: gpu0 / waiting_for_idle_gpu

UTC 2026-10-10T03:47:35.482634+00:00

State: /path/to/user-user/lora-dora-profiling/distributed-important/gpu0-admission.json. External controller: /path/to/user-user/lora-dora-profiling/distributed_localizations_v2.py. Frozen evaluator unchanged; versions Torch2.5.1+cu121 / Transformers4.57.1 / PEFT0.17.1 / Accelerate1.11.0.

```json
{
  "pid": 402742,
  "gpu_uuid": "GPU_UUID",
  "gpu_index": 0,
  "status": "waiting_for_idle_gpu",
  "consecutive_idle_checks": 0,
  "slot": 4
}
```

Next: inspect failures immediately; otherwise follow lane plan.json sequentially, compare only completed matched outputs, retain assigned GPU after compute.

## Distributed intervention stage: gpu6 / adopting_existing_worker

UTC 2026-10-10T03:47:02.086302+00:00

State: /path/to/user-user/lora-dora-profiling/distributed-important/gpu6-state.json. External controller: /path/to/user-user/lora-dora-profiling/distributed_localizations.py. Frozen evaluator unchanged; versions Torch2.5.1+cu121 / Transformers4.57.1 / PEFT0.17.1 / Accelerate1.11.0.

```json
{
  "pid": 402546,
  "lane": "gpu6",
  "gpu_uuid": "GPU_UUID",
  "status": "adopting_existing_worker",
  "completed_jobs": [
    "short-vo",
    "gsm8k-e99"
  ],
  "created_utc": "2026-10-10T03:46:56.152087+00:00",
  "worker_pid": 111155,
  "updated_utc": "2026-10-10T03:46:57.154864+00:00"
}
```

Next: inspect failures immediately; otherwise follow lane plan.json sequentially, compare only completed matched outputs, retain assigned GPU after compute.

## Morning status and refreshed ETAs — 2026-10-10T03:38:20.397822+00:00

All4physicalGPU2/3/5/6queues currently running; no current queue errors or dependency waits. Frozen evaluator source map unchanged. Completed full MMLU and SQuADv2 triples; denseDoRA/rank32/Energy99 outputs verified complete, predictions SHA256 and ordered coverage validated. Rank32 artifact exists before matchedLoRA is reached, eliminating current dependency risk. Core baseline fullbase/fullLoRA complete; fullDoRA running, denseDoRA-vs-original comparison still pending.

Versions unchanged: Python3.12.3 / Torch2.5.1+cu121 / Transformers4.57.1 / PEFT0.17.1 / Accelerate1.11.0. Artifact with load, validated completed metrics and revised per-lane ETAs: /path/to/user-user/lora-dora-profiling/distributed-important/morning-status-20261010.json.

```json
{
  "gpu1": {
    "physical_gpu_index": 3,
    "status": "running",
    "current_job": "gsm8k-e95",
    "role": "dora",
    "completed_jobs": [
      "gsm8k-dense-dora",
      "gsm8k-r32"
    ],
    "predictions": 960,
    "total": 1319,
    "current_remaining_hours": 0.6096906851694406,
    "future_jobs": [
      "gsm8k-base_magnitude-all"
    ],
    "estimated_remaining_compute_hours": 8.372758954750454,
    "estimated_finish_utc_plus3": "2026-10-10T15:00:42.330059+03:00"
  },
  "gpu2": {
    "physical_gpu_index": 2,
    "status": "running",
    "current_job": "gsm8k-dense-lora",
    "role": "lora",
    "completed_jobs": [],
    "predictions": 339,
    "total": 1319,
    "current_remaining_hours": 1.5702055334174625,
    "future_jobs": [
      "gsm8k-remove_d-all",
      "gsm8k-lora-matched-impact"
    ],
    "estimated_remaining_compute_hours": 6.687679060771362,
    "estimated_finish_utc_plus3": "2026-10-10T13:19:36.042441+03:00"
  },
  "gpu5": {
    "physical_gpu_index": 5,
    "status": "running",
    "current_job": "gsm8k-quality-greedy",
    "role": "dora",
    "completed_jobs": [],
    "predictions": 201,
    "total": 1319,
    "current_remaining_hours": 6.196940218862303,
    "future_jobs": [],
    "estimated_remaining_compute_hours": 6.196940218862303,
    "estimated_finish_utc_plus3": "2026-10-10T12:50:09.382610+03:00"
  },
  "gpu6": {
    "physical_gpu_index": 6,
    "status": "running",
    "current_job": "gsm8k-remove_d-q",
    "role": "dora",
    "completed_jobs": [
      "short-vo",
      "gsm8k-e99"
    ],
    "predictions": 854,
    "total": 1319,
    "current_remaining_hours": 2.0980240914700548,
    "future_jobs": [
      "gsm8k-remove_d-k",
      "gsm8k-remove_d-v",
      "gsm8k-remove_d-o",
      "gsm8k-base_magnitude-v"
    ],
    "estimated_remaining_compute_hours": 29.88739940428637,
    "estimated_finish_utc_plus3": "2026-10-11T12:31:35.035677+03:00"
  }
}
```

Timing estimates use active mean per-example time plus existing short-probe future estimates, not guaranteed ETAs or CIs. GPU5 baseline now around13:00Oct10 rather than12:15; other queues broadly on previous schedule. Unscheduled7localizations unchanged,49.573GPUh. Next: finish active jobs, inspect complete baseline paired comparisons, continue scheduled interventions/localizations and retain cards; no added/cancelled runs.

## Distributed intervention stage: gpu2 / running

UTC 2026-10-10T03:05:21.633367+00:00

State: /path/to/user-user/lora-dora-profiling/distributed-important/gpu2-state.json. External controller: /path/to/user-user/lora-dora-profiling/distributed_important.py. Frozen evaluator unchanged; versions Torch2.5.1+cu121 / Transformers4.57.1 / PEFT0.17.1 / Accelerate1.11.0.

```json
{
  "pid": 4163884,
  "lane": "gpu2",
  "gpu_uuid": "GPU_UUID",
  "status": "running",
  "completed_jobs": [],
  "created_utc": "2026-10-09T21:17:50.589932+00:00",
  "worker_pid": 365925,
  "updated_utc": "2026-10-10T03:05:18.183242+00:00",
  "retained_gpu_uuid": "GPU_UUID",
  "job": "gsm8k-dense-lora",
  "phase": "full",
  "role": "lora",
  "command": [
    "/path/to/user-user/.venvs/lora-dora-research/bin/python",
    "scripts/held_gpu_worker.py",
    "scripts/series_worker.py",
    "--job",
    "/path/to/user-user/lora-dora-series/results/first-series-greedy/jobs/gsm8k-dense-lora/job.json",
    "--gpu-uuid",
    "GPU_UUID",
    "--role",
    "lora",
    "--output-dir",
    "/path/to/user-user/lora-dora-series/results/first-series-greedy/jobs/gsm8k-dense-lora/full-lora-distributed-1"
  ],
  "existing_pair_completed_utc": "2026-10-10T03:04:47.603425+00:00"
}
```

Next: inspect failures immediately; otherwise follow lane plan.json sequentially, compare only completed matched outputs, retain assigned GPU after compute.

## Distributed intervention stage: gpu2 / running

UTC 2026-10-10T03:04:51.609078+00:00

State: /path/to/user-user/lora-dora-profiling/distributed-important/gpu2-state.json. External controller: /path/to/user-user/lora-dora-profiling/distributed_important.py. Frozen evaluator unchanged; versions Torch2.5.1+cu121 / Transformers4.57.1 / PEFT0.17.1 / Accelerate1.11.0.

```json
{
  "pid": 4163884,
  "lane": "gpu2",
  "gpu_uuid": "GPU_UUID",
  "status": "running",
  "completed_jobs": [],
  "created_utc": "2026-10-09T21:17:50.589932+00:00",
  "worker_pid": 365309,
  "updated_utc": "2026-10-10T03:04:47.607353+00:00",
  "retained_gpu_uuid": "GPU_UUID",
  "job": "gsm8k-dense-lora",
  "phase": "smoke",
  "role": "lora",
  "command": [
    "/path/to/user-user/.venvs/lora-dora-research/bin/python",
    "scripts/held_gpu_worker.py",
    "scripts/series_worker.py",
    "--job",
    "/path/to/user-user/lora-dora-series/results/first-series-greedy/jobs/gsm8k-dense-lora/job.json",
    "--gpu-uuid",
    "GPU_UUID",
    "--role",
    "lora",
    "--output-dir",
    "/path/to/user-user/lora-dora-series/results/first-series-greedy/jobs/gsm8k-dense-lora/smoke-lora-distributed-1",
    "--limit",
    "2"
  ],
  "existing_pair_completed_utc": "2026-10-10T03:04:47.603425+00:00"
}
```

Next: inspect failures immediately; otherwise follow lane plan.json sequentially, compare only completed matched outputs, retain assigned GPU after compute.

## Эксперимент завершён shadow_4b_squadv2

UTC: 2026-10-10T03:04:47.600527+00:00

```json
{
  "id": "shadow_4b_squadv2",
  "completed": [
    "smoke/base",
    "smoke/lora",
    "smoke/dora",
    "full/base",
    "full/lora",
    "full/dora"
  ],
  "status": "complete",
  "phase": "full",
  "role": "dora",
  "output_path": "/path/to/user-user/lora-dora-series/results/extra-series-greedy/jobs/shadow_4b_squadv2/full-dora-attempt-1",
  "outputs": {
    "smoke/base": "results/extra-series-greedy/jobs/shadow_4b_squadv2/smoke-base-attempt-1",
    "smoke/lora": "results/extra-series-greedy/jobs/shadow_4b_squadv2/smoke-lora-attempt-1",
    "smoke/dora": "results/extra-series-greedy/jobs/shadow_4b_squadv2/smoke-dora-attempt-2",
    "full/base": "/path/to/user-user/lora-dora-series/results/extra-series-greedy/jobs/shadow_4b_squadv2/full-base-attempt-1",
    "full/lora": "/path/to/user-user/lora-dora-series/results/extra-series-greedy/jobs/shadow_4b_squadv2/full-lora-attempt-1",
    "full/dora": "/path/to/user-user/lora-dora-series/results/extra-series-greedy/jobs/shadow_4b_squadv2/full-dora-attempt-1"
  },
  "measured_gpu_seconds": 29502.654787596897
}
```

## shadow_4b_squadv2 / full/dora

UTC: 2026-10-10T03:04:45.106640+00:00

```json
{
  "path": "/path/to/user-user/lora-dora-series/results/extra-series-greedy/jobs/shadow_4b_squadv2/full-dora-attempt-1",
  "metrics": {
    "exact": 0.8593447317442938,
    "f1": 0.8904261912100635
  },
  "memory": {
    "peak_allocated_bytes": 8374661120,
    "peak_reserved_bytes": 8501854208,
    "max_process_rss_bytes": 4817498112,
    "available_host_ram_bytes": 779255386112
  },
  "inference_seconds": 12213.065478718025,
  "predictions_completed": 11873,
  "full_evaluation": true,
  "versions": {
    "torch": "2.5.1+cu121",
    "transformers": "4.57.1",
    "peft": "0.17.1",
    "safetensors": "0.6.2",
    "accelerate": "1.11.0"
  }
}
```

## Distributed intervention stage: gpu5 / running

UTC 2026-10-10T02:31:01.238422+00:00

State: /path/to/user-user/lora-dora-profiling/distributed-important/gpu5-state.json. External controller: /path/to/user-user/lora-dora-profiling/distributed_important.py. Frozen evaluator unchanged; versions Torch2.5.1+cu121 / Transformers4.57.1 / PEFT0.17.1 / Accelerate1.11.0.

```json
{
  "pid": 4164561,
  "lane": "gpu5",
  "gpu_uuid": "GPU_UUID",
  "status": "running",
  "completed_jobs": [],
  "created_utc": "2026-10-09T21:18:11.000660+00:00",
  "worker_pid": 322761,
  "updated_utc": "2026-10-09T23:49:14.282185+00:00",
  "retained_gpu_uuid": "GPU_UUID",
  "job": "gsm8k-quality-greedy",
  "phase": "full",
  "role": "dora",
  "command": [
    "/path/to/user-user/.venvs/lora-dora-research/bin/python",
    "scripts/held_gpu_worker.py",
    "scripts/series_worker.py",
    "--job",
    "/path/to/user-user/lora-dora-series/results/first-series-greedy/jobs/gsm8k-quality-greedy/job.json",
    "--gpu-uuid",
    "GPU_UUID",
    "--role",
    "dora",
    "--output-dir",
    "/path/to/user-user/lora-dora-series/results/first-series-greedy/jobs/gsm8k-quality-greedy/full-dora-attempt-1"
  ]
}
```

Next: inspect failures immediately; otherwise follow lane plan.json sequentially, compare only completed matched outputs, retain assigned GPU after compute.

## gsm8k-quality-greedy / full/lora

UTC: 2026-10-10T02:30:52.108063+00:00

```json
{
  "path": "/path/to/user-user/lora-dora-series/results/first-series-greedy/jobs/gsm8k-quality-greedy/full-lora-attempt-1",
  "metrics": {
    "author_em": 0.7649734647460197,
    "final_em": 0.7672479150871873
  },
  "memory": {
    "peak_allocated_bytes": 8233698816,
    "peak_reserved_bytes": 8302624768,
    "max_process_rss_bytes": 4741787648,
    "available_host_ram_bytes": 779130920960
  },
  "inference_seconds": 9686.970680898055,
  "predictions_completed": 1319,
  "full_evaluation": true,
  "versions": {
    "torch": "2.5.1+cu121",
    "transformers": "4.57.1",
    "peft": "0.17.1",
    "safetensors": "0.6.2",
    "accelerate": "1.11.0"
  }
}
```

## Distributed intervention stage: gpu1 / running

UTC 2026-10-10T01:58:40.877207+00:00

State: /path/to/user-user/lora-dora-profiling/distributed-important/gpu1-state.json. External controller: /path/to/user-user/lora-dora-profiling/distributed_important.py. Frozen evaluator unchanged; versions Torch2.5.1+cu121 / Transformers4.57.1 / PEFT0.17.1 / Accelerate1.11.0.

```json
{
  "pid": 4170596,
  "lane": "gpu1",
  "gpu_uuid": "GPU_UUID",
  "status": "running",
  "completed_jobs": [
    "gsm8k-dense-dora",
    "gsm8k-r32"
  ],
  "created_utc": "2026-10-09T21:24:47.331082+00:00",
  "job": "gsm8k-e95",
  "phase": "full",
  "role": "dora",
  "worker_pid": 279820,
  "command": [
    "/path/to/user-user/.venvs/lora-dora-research/bin/python",
    "scripts/held_gpu_worker.py",
    "scripts/series_worker.py",
    "--job",
    "/path/to/user-user/lora-dora-series/results/first-series-greedy/jobs/gsm8k-e95/job.json",
    "--gpu-uuid",
    "GPU_UUID",
    "--role",
    "dora",
    "--output-dir",
    "/path/to/user-user/lora-dora-series/results/first-series-greedy/jobs/gsm8k-e95/full-dora-distributed-1"
  ],
  "updated_utc": "2026-10-10T01:58:33.674038+00:00"
}
```

Next: inspect failures immediately; otherwise follow lane plan.json sequentially, compare only completed matched outputs, retain assigned GPU after compute.

## Distributed intervention stage: gpu1 / running

UTC 2026-10-10T01:56:40.836462+00:00

State: /path/to/user-user/lora-dora-profiling/distributed-important/gpu1-state.json. External controller: /path/to/user-user/lora-dora-profiling/distributed_important.py. Frozen evaluator unchanged; versions Torch2.5.1+cu121 / Transformers4.57.1 / PEFT0.17.1 / Accelerate1.11.0.

```json
{
  "pid": 4170596,
  "lane": "gpu1",
  "gpu_uuid": "GPU_UUID",
  "status": "running",
  "completed_jobs": [
    "gsm8k-dense-dora",
    "gsm8k-r32"
  ],
  "created_utc": "2026-10-09T21:24:47.331082+00:00",
  "job": "gsm8k-e95",
  "phase": "smoke",
  "role": "dora",
  "worker_pid": 277207,
  "command": [
    "/path/to/user-user/.venvs/lora-dora-research/bin/python",
    "scripts/held_gpu_worker.py",
    "scripts/series_worker.py",
    "--job",
    "/path/to/user-user/lora-dora-series/results/first-series-greedy/jobs/gsm8k-e95/job.json",
    "--gpu-uuid",
    "GPU_UUID",
    "--role",
    "dora",
    "--output-dir",
    "/path/to/user-user/lora-dora-series/results/first-series-greedy/jobs/gsm8k-e95/smoke-dora-distributed-1",
    "--limit",
    "2"
  ],
  "updated_utc": "2026-10-10T01:56:37.800790+00:00"
}
```

Next: inspect failures immediately; otherwise follow lane plan.json sequentially, compare only completed matched outputs, retain assigned GPU after compute.

## Distributed intervention stage: gpu5 / running

UTC 2026-10-09T23:49:19.474629+00:00

State: /path/to/user-user/lora-dora-profiling/distributed-important/gpu5-state.json. External controller: /path/to/user-user/lora-dora-profiling/distributed_important.py. Frozen evaluator unchanged; versions Torch2.5.1+cu121 / Transformers4.57.1 / PEFT0.17.1 / Accelerate1.11.0.

```json
{
  "pid": 4164561,
  "lane": "gpu5",
  "gpu_uuid": "GPU_UUID",
  "status": "running",
  "completed_jobs": [],
  "created_utc": "2026-10-09T21:18:11.000660+00:00",
  "worker_pid": 113899,
  "updated_utc": "2026-10-09T23:49:14.282185+00:00",
  "retained_gpu_uuid": "GPU_UUID",
  "job": "gsm8k-quality-greedy",
  "phase": "full",
  "role": "lora",
  "command": [
    "/path/to/user-user/.venvs/lora-dora-research/bin/python",
    "scripts/held_gpu_worker.py",
    "scripts/series_worker.py",
    "--job",
    "/path/to/user-user/lora-dora-series/results/first-series-greedy/jobs/gsm8k-quality-greedy/job.json",
    "--gpu-uuid",
    "GPU_UUID",
    "--role",
    "lora",
    "--output-dir",
    "/path/to/user-user/lora-dora-series/results/first-series-greedy/jobs/gsm8k-quality-greedy/full-lora-attempt-1"
  ]
}
```

Next: inspect failures immediately; otherwise follow lane plan.json sequentially, compare only completed matched outputs, retain assigned GPU after compute.

## Distributed intervention stage: gpu6 / running

UTC 2026-10-09T23:46:49.431035+00:00

State: /path/to/user-user/lora-dora-profiling/distributed-important/gpu6-state.json. External controller: /path/to/user-user/lora-dora-profiling/distributed_localizations.py. Frozen evaluator unchanged; versions Torch2.5.1+cu121 / Transformers4.57.1 / PEFT0.17.1 / Accelerate1.11.0.

```json
{
  "pid": 4178348,
  "lane": "gpu6",
  "gpu_uuid": "GPU_UUID",
  "status": "running",
  "completed_jobs": [
    "short-vo",
    "gsm8k-e99"
  ],
  "created_utc": "2026-10-09T21:36:59.351254+00:00",
  "worker_pid": 111155,
  "updated_utc": "2026-10-09T23:46:49.378519+00:00",
  "job": "gsm8k-remove_d-q",
  "phase": "full",
  "role": "dora",
  "command": [
    "/path/to/user-user/.venvs/lora-dora-research/bin/python",
    "scripts/held_gpu_worker.py",
    "scripts/series_worker.py",
    "--job",
    "/path/to/user-user/lora-dora-series/results/first-series-greedy/jobs/gsm8k-remove_d-q/job.json",
    "--gpu-uuid",
    "GPU_UUID",
    "--role",
    "dora",
    "--output-dir",
    "/path/to/user-user/lora-dora-series/results/first-series-greedy/jobs/gsm8k-remove_d-q/full-dora-distributed-1"
  ]
}
```

Next: inspect failures immediately; otherwise follow lane plan.json sequentially, compare only completed matched outputs, retain assigned GPU after compute.

## Distributed intervention stage: gpu6 / running

UTC 2026-10-09T23:46:29.407174+00:00

State: /path/to/user-user/lora-dora-profiling/distributed-important/gpu6-state.json. External controller: /path/to/user-user/lora-dora-profiling/distributed_localizations.py. Frozen evaluator unchanged; versions Torch2.5.1+cu121 / Transformers4.57.1 / PEFT0.17.1 / Accelerate1.11.0.

```json
{
  "pid": 4178348,
  "lane": "gpu6",
  "gpu_uuid": "GPU_UUID",
  "status": "running",
  "completed_jobs": [
    "short-vo",
    "gsm8k-e99"
  ],
  "created_utc": "2026-10-09T21:36:59.351254+00:00",
  "worker_pid": 110601,
  "updated_utc": "2026-10-09T23:46:23.319179+00:00",
  "job": "gsm8k-remove_d-q",
  "phase": "smoke",
  "role": "dora",
  "command": [
    "/path/to/user-user/.venvs/lora-dora-research/bin/python",
    "scripts/held_gpu_worker.py",
    "scripts/series_worker.py",
    "--job",
    "/path/to/user-user/lora-dora-series/results/first-series-greedy/jobs/gsm8k-remove_d-q/job.json",
    "--gpu-uuid",
    "GPU_UUID",
    "--role",
    "dora",
    "--output-dir",
    "/path/to/user-user/lora-dora-series/results/first-series-greedy/jobs/gsm8k-remove_d-q/smoke-dora-distributed-1",
    "--limit",
    "2"
  ]
}
```

Next: inspect failures immediately; otherwise follow lane plan.json sequentially, compare only completed matched outputs, retain assigned GPU after compute.

## Distributed intervention stage: gpu2 / running

UTC 2026-10-09T23:41:09.323405+00:00

State: /path/to/user-user/lora-dora-profiling/distributed-important/gpu2-state.json. External controller: /path/to/user-user/lora-dora-profiling/distributed_important.py. Frozen evaluator unchanged; versions Torch2.5.1+cu121 / Transformers4.57.1 / PEFT0.17.1 / Accelerate1.11.0.

```json
{
  "pid": 4163884,
  "lane": "gpu2",
  "gpu_uuid": "GPU_UUID",
  "status": "running",
  "completed_jobs": [],
  "created_utc": "2026-10-09T21:17:50.589932+00:00",
  "worker_pid": 104463,
  "updated_utc": "2026-10-09T22:22:03.697001+00:00",
  "retained_gpu_uuid": "GPU_UUID",
  "job": "shadow_4b_squadv2",
  "phase": "full",
  "role": "dora",
  "command": [
    "/path/to/user-user/.venvs/lora-dora-research/bin/python",
    "scripts/held_gpu_worker.py",
    "scripts/series_worker.py",
    "--job",
    "/path/to/user-user/lora-dora-series/results/extra-series-greedy/jobs/shadow_4b_squadv2/job.json",
    "--gpu-uuid",
    "GPU_UUID",
    "--role",
    "dora",
    "--output-dir",
    "/path/to/user-user/lora-dora-series/results/extra-series-greedy/jobs/shadow_4b_squadv2/full-dora-attempt-1"
  ]
}
```

Next: inspect failures immediately; otherwise follow lane plan.json sequentially, compare only completed matched outputs, retain assigned GPU after compute.

## shadow_4b_squadv2 / full/lora

UTC: 2026-10-09T23:41:00.393329+00:00

```json
{
  "path": "/path/to/user-user/lora-dora-series/results/extra-series-greedy/jobs/shadow_4b_squadv2/full-lora-attempt-1",
  "metrics": {
    "exact": 0.8606923271287796,
    "f1": 0.8930813387109182
  },
  "memory": {
    "peak_allocated_bytes": 8233698816,
    "peak_reserved_bytes": 8327790592,
    "max_process_rss_bytes": 4816605184,
    "available_host_ram_bytes": 771873017856
  },
  "inference_seconds": 4724.541134977946,
  "predictions_completed": 11873,
  "full_evaluation": true,
  "versions": {
    "torch": "2.5.1+cu121",
    "transformers": "4.57.1",
    "peft": "0.17.1",
    "safetensors": "0.6.2",
    "accelerate": "1.11.0"
  }
}
```

## Distributed intervention stage: gpu1 / running

UTC 2026-10-09T23:38:19.275872+00:00

State: /path/to/user-user/lora-dora-profiling/distributed-important/gpu1-state.json. External controller: /path/to/user-user/lora-dora-profiling/distributed_important.py. Frozen evaluator unchanged; versions Torch2.5.1+cu121 / Transformers4.57.1 / PEFT0.17.1 / Accelerate1.11.0.

```json
{
  "pid": 4170596,
  "lane": "gpu1",
  "gpu_uuid": "GPU_UUID",
  "status": "running",
  "completed_jobs": [
    "gsm8k-dense-dora"
  ],
  "created_utc": "2026-10-09T21:24:47.331082+00:00",
  "job": "gsm8k-r32",
  "phase": "full",
  "role": "dora",
  "worker_pid": 101167,
  "command": [
    "/path/to/user-user/.venvs/lora-dora-research/bin/python",
    "scripts/held_gpu_worker.py",
    "scripts/series_worker.py",
    "--job",
    "/path/to/user-user/lora-dora-series/results/first-series-greedy/jobs/gsm8k-r32/job.json",
    "--gpu-uuid",
    "GPU_UUID",
    "--role",
    "dora",
    "--output-dir",
    "/path/to/user-user/lora-dora-series/results/first-series-greedy/jobs/gsm8k-r32/full-dora-distributed-1"
  ],
  "updated_utc": "2026-10-09T23:38:15.792656+00:00"
}
```

Next: inspect failures immediately; otherwise follow lane plan.json sequentially, compare only completed matched outputs, retain assigned GPU after compute.

## Distributed intervention stage: gpu1 / running

UTC 2026-10-09T23:36:09.235156+00:00

State: /path/to/user-user/lora-dora-profiling/distributed-important/gpu1-state.json. External controller: /path/to/user-user/lora-dora-profiling/distributed_important.py. Frozen evaluator unchanged; versions Torch2.5.1+cu121 / Transformers4.57.1 / PEFT0.17.1 / Accelerate1.11.0.

```json
{
  "pid": 4170596,
  "lane": "gpu1",
  "gpu_uuid": "GPU_UUID",
  "status": "running",
  "completed_jobs": [
    "gsm8k-dense-dora"
  ],
  "created_utc": "2026-10-09T21:24:47.331082+00:00",
  "job": "gsm8k-r32",
  "phase": "smoke",
  "role": "dora",
  "worker_pid": 98672,
  "command": [
    "/path/to/user-user/.venvs/lora-dora-research/bin/python",
    "scripts/held_gpu_worker.py",
    "scripts/series_worker.py",
    "--job",
    "/path/to/user-user/lora-dora-series/results/first-series-greedy/jobs/gsm8k-r32/job.json",
    "--gpu-uuid",
    "GPU_UUID",
    "--role",
    "dora",
    "--output-dir",
    "/path/to/user-user/lora-dora-series/results/first-series-greedy/jobs/gsm8k-r32/smoke-dora-distributed-1",
    "--limit",
    "2"
  ],
  "updated_utc": "2026-10-09T23:36:08.192524+00:00"
}
```

Next: inspect failures immediately; otherwise follow lane plan.json sequentially, compare only completed matched outputs, retain assigned GPU after compute.

## Distributed intervention stage: gpu2 / running

UTC 2026-10-09T22:22:08.489647+00:00

State: /path/to/user-user/lora-dora-profiling/distributed-important/gpu2-state.json. External controller: /path/to/user-user/lora-dora-profiling/distributed_important.py. Frozen evaluator unchanged; versions Torch2.5.1+cu121 / Transformers4.57.1 / PEFT0.17.1 / Accelerate1.11.0.

```json
{
  "pid": 4163884,
  "lane": "gpu2",
  "gpu_uuid": "GPU_UUID",
  "status": "running",
  "completed_jobs": [],
  "created_utc": "2026-10-09T21:17:50.589932+00:00",
  "worker_pid": 14641,
  "updated_utc": "2026-10-09T22:22:03.697001+00:00",
  "retained_gpu_uuid": "GPU_UUID",
  "job": "shadow_4b_squadv2",
  "phase": "full",
  "role": "lora",
  "command": [
    "/path/to/user-user/.venvs/lora-dora-research/bin/python",
    "scripts/held_gpu_worker.py",
    "scripts/series_worker.py",
    "--job",
    "/path/to/user-user/lora-dora-series/results/extra-series-greedy/jobs/shadow_4b_squadv2/job.json",
    "--gpu-uuid",
    "GPU_UUID",
    "--role",
    "lora",
    "--output-dir",
    "/path/to/user-user/lora-dora-series/results/extra-series-greedy/jobs/shadow_4b_squadv2/full-lora-attempt-1"
  ]
}
```

Next: inspect failures immediately; otherwise follow lane plan.json sequentially, compare only completed matched outputs, retain assigned GPU after compute.

## Five localization jobs added after Energy99 on GPU6 — 2026-10-09T21:37:45.710810+00:00

User requests approximately34 additional GPUh of localizations onGPU6 and a remaining-work/load report. Applied plan /path/to/user-user/lora-dora-profiling/distributed-important/plan.json. Added full removeD q/k/v/o sweep, plus baseMagnitude V:33.9353GPUh including smoke/preparation. Seven localization jobs remain unscheduled:49.5732GPUh. None of these seven will run automatically. Other13 scheduled full interventions have unique owners; no duplication or frozen source changes.

Energy99 worker4173579 preserved without signals or reload. Old coordinator4163392 replaced only after verified CUDA context4178348 on sameGPU6. New coordinator /path/to/user-user/lora-dora-profiling/distributed_localizations.py waits for that worker, validates its complete output/source/prediction hash, registers the full result, then performs5localizations sequentially. Historical completed MMLU/V/O preserved; no rerun. Handover: /path/to/user-user/lora-dora-profiling/distributed-important/gpu6-localizations-go.json. Prior state and plan archived in distributed-important. GPU retention continues during and after queue.

Statistical family: existing8core contrasts unchanged; new5localizations use a separate prespecified Holm family over both scorers, output localization-family-holm.json. Do not claim joint13correction. Final-checkpoint ablations do not identify training causes. Versions unchanged: Python3.12.3, Torch2.5.1+cu121, Transformers4.57.1, PEFT0.17.1, Accelerate1.11.0.

Validation: external controller syntax compiled; frozen SHA256 map matches;13scheduled full jobs unique;7deferred distinct; active Energy99 summary still running with 74 predictions. Newly queued5fulllocalizations not yet runtime verified. Fresh report/load/timing: /path/to/user-user/lora-dora-profiling/distributed-important/localization-schedule-report.json. GPU6 estimated completion 2026-10-11T12:39:51.683429+03:00 (~36.03h remaining); timing extrapolation, not guaranteed ETA.

Next: complete Energy99 adoption and run selected localizations. Monitor appends actual transitions to HANDOFF; inspect failures with GPU retained. Leave remaining7unscheduled until user changes scope.

## Distributed intervention stage: gpu6 / adopting_existing_worker

UTC 2026-10-09T21:37:00.803956+00:00

State: /path/to/user-user/lora-dora-profiling/distributed-important/gpu6-state.json. External controller: /path/to/user-user/lora-dora-profiling/distributed_important.py. Frozen evaluator unchanged; versions Torch2.5.1+cu121 / Transformers4.57.1 / PEFT0.17.1 / Accelerate1.11.0.

```json
{
  "pid": 4178348,
  "lane": "gpu6",
  "gpu_uuid": "GPU_UUID",
  "status": "adopting_existing_worker",
  "completed_jobs": [
    "short-vo"
  ],
  "created_utc": "2026-10-09T21:36:59.351254+00:00",
  "worker_pid": 4173579,
  "updated_utc": "2026-10-09T21:37:00.555101+00:00"
}
```

Next: inspect failures immediately; otherwise follow lane plan.json sequentially, compare only completed matched outputs, retain assigned GPU after compute.

## Distributed intervention stage: gpu6 / running

UTC 2026-10-09T21:28:40.711261+00:00

State: /path/to/user-user/lora-dora-profiling/distributed-important/gpu6-state.json. External controller: /path/to/user-user/lora-dora-profiling/distributed_important.py. Frozen evaluator unchanged; versions Torch2.5.1+cu121 / Transformers4.57.1 / PEFT0.17.1 / Accelerate1.11.0.

```json
{
  "pid": 4163392,
  "lane": "gpu6",
  "gpu_uuid": "GPU_UUID",
  "status": "running",
  "completed_jobs": [
    "short-vo"
  ],
  "created_utc": "2026-10-09T21:17:32.240901+00:00",
  "worker_pid": 4173579,
  "updated_utc": "2026-10-09T21:28:33.427451+00:00",
  "retained_gpu_uuid": "GPU_UUID",
  "job": "gsm8k-e99",
  "existing_pair_completed_utc": "2026-10-09T21:25:49.636013+00:00",
  "phase": "full",
  "role": "dora",
  "command": [
    "/path/to/user-user/.venvs/lora-dora-research/bin/python",
    "scripts/held_gpu_worker.py",
    "scripts/series_worker.py",
    "--job",
    "/path/to/user-user/lora-dora-series/results/first-series-greedy/jobs/gsm8k-e99/job.json",
    "--gpu-uuid",
    "GPU_UUID",
    "--role",
    "dora",
    "--output-dir",
    "/path/to/user-user/lora-dora-series/results/first-series-greedy/jobs/gsm8k-e99/full-dora-distributed-1"
  ]
}
```

Next: inspect failures immediately; otherwise follow lane plan.json sequentially, compare only completed matched outputs, retain assigned GPU after compute.

## Distributed intervention stage: gpu6 / running

UTC 2026-10-09T21:26:40.676340+00:00

State: /path/to/user-user/lora-dora-profiling/distributed-important/gpu6-state.json. External controller: /path/to/user-user/lora-dora-profiling/distributed_important.py. Frozen evaluator unchanged; versions Torch2.5.1+cu121 / Transformers4.57.1 / PEFT0.17.1 / Accelerate1.11.0.

```json
{
  "pid": 4163392,
  "lane": "gpu6",
  "gpu_uuid": "GPU_UUID",
  "status": "running",
  "completed_jobs": [
    "short-vo"
  ],
  "created_utc": "2026-10-09T21:17:32.240901+00:00",
  "worker_pid": 4172378,
  "updated_utc": "2026-10-09T21:26:34.985894+00:00",
  "retained_gpu_uuid": "GPU_UUID",
  "job": "gsm8k-e99",
  "existing_pair_completed_utc": "2026-10-09T21:25:49.636013+00:00",
  "phase": "smoke",
  "role": "dora",
  "command": [
    "/path/to/user-user/.venvs/lora-dora-research/bin/python",
    "scripts/held_gpu_worker.py",
    "scripts/series_worker.py",
    "--job",
    "/path/to/user-user/lora-dora-series/results/first-series-greedy/jobs/gsm8k-e99/job.json",
    "--gpu-uuid",
    "GPU_UUID",
    "--role",
    "dora",
    "--output-dir",
    "/path/to/user-user/lora-dora-series/results/first-series-greedy/jobs/gsm8k-e99/smoke-dora-distributed-1",
    "--limit",
    "2"
  ]
}
```

Next: inspect failures immediately; otherwise follow lane plan.json sequentially, compare only completed matched outputs, retain assigned GPU after compute.

## GPU3 admission runtime verification — 2026-10-09T21:25:56.092716+00:00

DenseDoRA smoke completed with 2 examples, inference 7.218016679980792 seconds, real weights and adapter verification using frozen evaluator. Output: /path/to/user-user/lora-dora-series/results/first-series-greedy/jobs/gsm8k-dense-dora/smoke-dora-distributed-1. Full denseDoRA worker4171217 is now running on physicalGPU3; no full quality result yet. Controller4170596 retains GPU between jobs. Next: complete full denseDoRA then rank32, energy95, baseMagnitudeAll.

## Distributed intervention stage: gpu6 / short_symmetry_validation

UTC 2026-10-09T21:25:50.660280+00:00

State: /path/to/user-user/lora-dora-profiling/distributed-important/gpu6-state.json. External controller: /path/to/user-user/lora-dora-profiling/distributed_important.py. Frozen evaluator unchanged; versions Torch2.5.1+cu121 / Transformers4.57.1 / PEFT0.17.1 / Accelerate1.11.0.

```json
{
  "pid": 4163392,
  "lane": "gpu6",
  "gpu_uuid": "GPU_UUID",
  "status": "short_symmetry_validation",
  "completed_jobs": [],
  "created_utc": "2026-10-09T21:17:32.240901+00:00",
  "worker_pid": 4171902,
  "updated_utc": "2026-10-09T21:25:49.647224+00:00",
  "retained_gpu_uuid": "GPU_UUID",
  "job": "short-vo",
  "existing_pair_completed_utc": "2026-10-09T21:25:49.636013+00:00"
}
```

Next: inspect failures immediately; otherwise follow lane plan.json sequentially, compare only completed matched outputs, retain assigned GPU after compute.

## Эксперимент завершён shadow_4b_mmlu

UTC: 2026-10-09T21:25:49.632728+00:00

```json
{
  "id": "shadow_4b_mmlu",
  "completed": [
    "smoke/base",
    "smoke/lora",
    "smoke/dora",
    "full/base",
    "full/lora",
    "full/dora"
  ],
  "status": "complete",
  "phase": "full",
  "role": "dora",
  "output_path": "results/extra-series-greedy/jobs/shadow_4b_mmlu/full-dora-attempt-1",
  "outputs": {
    "smoke/base": "results/extra-series-greedy/jobs/shadow_4b_mmlu/smoke-base-attempt-1",
    "smoke/lora": "results/extra-series-greedy/jobs/shadow_4b_mmlu/smoke-lora-attempt-2",
    "smoke/dora": "results/extra-series-greedy/jobs/shadow_4b_mmlu/smoke-dora-attempt-1",
    "full/base": "results/extra-series-greedy/jobs/shadow_4b_mmlu/full-base-attempt-1",
    "full/lora": "results/extra-series-greedy/jobs/shadow_4b_mmlu/full-lora-attempt-1",
    "full/dora": "/path/to/user-user/lora-dora-series/results/extra-series-greedy/jobs/shadow_4b_mmlu/full-dora-attempt-1"
  },
  "measured_gpu_seconds": 8670.333915336058
}
```

## Important 15h lane admitted on physical GPU3 — 2026-10-09T21:25:25.676951+00:00

User explicitly authorizes GPU3 or another idle GPU instead of waiting for GPU1. Waiter4156388 was verified waiting-only and terminated, no model/worker stopped. New external admission controller4170596 verified GPU3 idle twice10s apart, acquired GPU UUID GPU_UUID plus slot3 and launched the existing important lane. Historical logical lane key gpu1 is retained for artifact/dependency identity; it now means physical GPU3. plan.json contains the new UUID/index. Current state: /path/to/user-user/lora-dora-profiling/distributed-important/gpu1-state.json. Initial smoke worker4170864 for denseDoRA launched; full quality not yet claimed. Full lane: denseDoRA/rank32/energy95/baseMagnitudeAll, ~14.78h from admission, estimated finish 2026-10-10T15:11:35.331082+03:00. Other lanes/processes unchanged. GPU1 unrelated process untouched. No training.

Frozen source fingerprint unchanged; Python3.12.3 / Torch2.5.1+cu121 / Transformers4.57.1 / PEFT0.17.1 / Accelerate1.11.0. New external admission code: /path/to/user-user/lora-dora-profiling/admit_important_free_gpu.py. Updated server-load and conditional forecast artifact: /path/to/user-user/lora-dora-profiling/distributed-important/schedule-report.json.

Next: validate smoke completes, then full denseDoRA; inspect MMLU adoption and short V/O stage. Controllers retain cards after compute. Estimates are extrapolations, not guaranteed completion times.

## Distributed intervention stage: gpu1 / running

UTC 2026-10-09T21:25:20.639407+00:00

State: /path/to/user-user/lora-dora-profiling/distributed-important/gpu1-state.json. External controller: /path/to/user-user/lora-dora-profiling/distributed_important.py. Frozen evaluator unchanged; versions Torch2.5.1+cu121 / Transformers4.57.1 / PEFT0.17.1 / Accelerate1.11.0.

```json
{
  "pid": 4170596,
  "lane": "gpu1",
  "gpu_uuid": "GPU_UUID",
  "status": "running",
  "completed_jobs": [],
  "created_utc": "2026-10-09T21:24:47.331082+00:00",
  "job": "gsm8k-dense-dora",
  "phase": "full",
  "role": "dora",
  "worker_pid": 4171217,
  "command": [
    "/path/to/user-user/.venvs/lora-dora-research/bin/python",
    "scripts/held_gpu_worker.py",
    "scripts/series_worker.py",
    "--job",
    "/path/to/user-user/lora-dora-series/results/first-series-greedy/jobs/gsm8k-dense-dora/job.json",
    "--gpu-uuid",
    "GPU_UUID",
    "--role",
    "dora",
    "--output-dir",
    "/path/to/user-user/lora-dora-series/results/first-series-greedy/jobs/gsm8k-dense-dora/full-dora-distributed-1"
  ],
  "updated_utc": "2026-10-09T21:25:20.137430+00:00"
}
```

Next: inspect failures immediately; otherwise follow lane plan.json sequentially, compare only completed matched outputs, retain assigned GPU after compute.

## Distributed intervention stage: gpu1 / running

UTC 2026-10-09T21:24:50.617368+00:00

State: /path/to/user-user/lora-dora-profiling/distributed-important/gpu1-state.json. External controller: /path/to/user-user/lora-dora-profiling/distributed_important.py. Frozen evaluator unchanged; versions Torch2.5.1+cu121 / Transformers4.57.1 / PEFT0.17.1 / Accelerate1.11.0.

```json
{
  "pid": 4170596,
  "lane": "gpu1",
  "gpu_uuid": "GPU_UUID",
  "status": "running",
  "completed_jobs": [],
  "created_utc": "2026-10-09T21:24:47.331082+00:00",
  "job": "gsm8k-dense-dora",
  "phase": "smoke",
  "role": "dora",
  "worker_pid": 4170864,
  "command": [
    "/path/to/user-user/.venvs/lora-dora-research/bin/python",
    "scripts/held_gpu_worker.py",
    "scripts/series_worker.py",
    "--job",
    "/path/to/user-user/lora-dora-series/results/first-series-greedy/jobs/gsm8k-dense-dora/job.json",
    "--gpu-uuid",
    "GPU_UUID",
    "--role",
    "dora",
    "--output-dir",
    "/path/to/user-user/lora-dora-series/results/first-series-greedy/jobs/gsm8k-dense-dora/smoke-dora-distributed-1",
    "--limit",
    "2"
  ],
  "updated_utc": "2026-10-09T21:24:47.367339+00:00"
}
```

Next: inspect failures immediately; otherwise follow lane plan.json sequentially, compare only completed matched outputs, retain assigned GPU after compute.

## Important interventions distributed; current workers preserved — 2026-10-09T21:20:19.027366+00:00

User authorizes ~15h GPU1 lane, remaining important interventions after SQuADv2/GPU2, short V/O and Energy99 after MMLU/GPU6. Applied external plan /path/to/user-user/lora-dora-profiling/distributed-important/plan.json. Eight full interventions allocated exactly once; 12 local ablations deferred, not measured/cancelled. Original baseline triple onGPU5 continues. Answer.AI candidates still blocked and unchanged. Qwen8B cancelled; LLaVA excluded; full no-op/full V/O remain cancelled.

GPU1: denseDoRA, rank32, energy95, baseMagnitudeAll (14.78h after admission). GPU2: complete SQuADv2 triple, then denseLoRA, removeDAll, matchedLoRA (7.45h after pair; matched control needs rank32 artifact). GPU6: complete MMLU triple, then short V/O forward-only numerical/correlation diagnostic (no generation benchmark), Energy99 (2.22h). GPU5: complete primary base/LoRA/DoRA, no deferred localization runs. Comparisons deferred until full references exist, same frozen source/generation/scorers; separate dense-control comparisons and Holm family8 full contrasts ×2 scorers.

Safe transfer: old coordinators3786742/3785635/3914873 terminated only after verified replacement CUDA contexts4163392/4163884/4164561; original workers3850626/3785966/3865529 preserved without signals/reloads. Lease descriptors remain in old workers until exit, then new coordinators acquire. GPU1 waiter4156388 detects foreign process and checks every10s; requires2idle checks. No foreign process modified. Slot3 extension uses external holder under user5-GPU authorization; original frozen lease code unchanged. Retention is cooperative, not scheduler exclusivity.

Validation: external scripts compile, 8 full job IDs unique, required pinned paths exist, frozen source SHA256 matches all active results. New full interventions and short V/O have NOT yet run; their runtime validation is pending. Versions Python3.12.3, Torch2.5.1+cu121, Transformers4.57.1, PEFT0.17.1, Accelerate1.11.0. Source hashes, live progress/load and conditional ETAs: /path/to/user-user/lora-dora-profiling/distributed-important/schedule-report.json. Controller/status/log/go manifests in /path/to/user-user/lora-dora-profiling/distributed-important. Monitor /path/to/user-user/lora-dora-profiling/watch_distributed_handoff.py appends actual stage transitions.

Forecasts

```json
{
  "gpu5": {
    "remaining_compute_hours": 11.899672791642164,
    "finish_utc_plus3": "2026-10-10T12:14:17.849416+03:00"
  },
  "gpu2": {
    "remaining_existing_pair_hours": 5.297634247523137,
    "new_interventions_hours": 7.45,
    "remaining_compute_hours_if_rank32_artifact_ready": 12.747634247523138,
    "finish_if_artifact_ready_utc_plus3": "2026-10-10T13:05:10.510657+03:00",
    "dependency": "Matched LoRA waits for GPU1 rank32 full output; can extend completion if GPU1 admission delayed"
  },
  "gpu6": {
    "remaining_mmlu_hours": 0.10090869898649131,
    "new_interventions_hours": 2.22,
    "short_vo_hours_budget": 0.1,
    "remaining_compute_hours": 2.420908698986491,
    "finish_utc_plus3": "2026-10-10T02:45:34.298682+03:00",
    "dependency": "Paired Energy99 analysis waits for GPU1 denseDoRA output"
  },
  "gpu1": {
    "status": "waiting_for_gpu1",
    "hours_after_admission": 14.78,
    "earliest_finish_if_admitted_now_utc_plus3": "2026-10-10T15:07:07.027366+03:00",
    "absolute_eta": null,
    "reason": "GPU1 currently occupied by unrelated process; admission wait unknown"
  }
}
```

Next: verify MMLU adoption/paired summary and first short V/O run; inspect failures while retaining assigned card, then continue selected full interventions. Do not restart cancelled or deferred tasks. GPU1 unknown admission delay prevents a reliable absolute overall completion time. Baseline quality does not establish training-trajectory cause.

## Очередь остановлена

UTC: 2026-10-09T21:20:00.404304+00:00

```json
{
  "series": 1,
  "pid": 4164064,
  "status": "failed_needs_inspection",
  "interval_seconds": 10,
  "required_consecutive_checks": 2,
  "plan_sha256": "29fc7a734e2d0de1c26b5459b88706850409becca9ae1f70659f4a1be7404639",
  "estimated_gpu_seconds": 169200,
  "waiting": {
    "answerai_llama2_100k": "waiting_for_quantized_custom_loader_and_base_access",
    "answerai_llama3_100k": "waiting_for_quantized_custom_loader_and_base_access",
    "llava_7b": "waiting_for_multimodal_loader_projector_images_and_evaluator"
  },
  "finished": [],
  "failed": [],
  "ready": [
    "shadow_4b_mmlu"
  ],
  "timestamp_utc": "2026-10-09T21:20:00.400873+00:00",
  "job": "shadow_4b_mmlu",
  "phase": "full",
  "role": "dora",
  "idle_uuids": [
    "GPU_UUID"
  ],
  "stable_idle_uuids": [
    "GPU_UUID"
  ],
  "error": "Three research GPU workers already active"
}
```

## Distributed intervention stage: gpu6 / adopting_existing_worker

UTC 2026-10-09T21:19:00.562822+00:00

State: /path/to/user-user/lora-dora-profiling/distributed-important/gpu6-state.json. External controller: /path/to/user-user/lora-dora-profiling/distributed_important.py. Frozen evaluator unchanged; versions Torch2.5.1+cu121 / Transformers4.57.1 / PEFT0.17.1 / Accelerate1.11.0.

```json
{
  "pid": 4163392,
  "lane": "gpu6",
  "gpu_uuid": "GPU_UUID",
  "status": "adopting_existing_worker",
  "completed_jobs": [],
  "created_utc": "2026-10-09T21:17:32.240901+00:00",
  "worker_pid": 3850626,
  "updated_utc": "2026-10-09T21:17:33.644874+00:00"
}
```

Next: inspect failures immediately; otherwise follow lane plan.json sequentially, compare only completed matched outputs, retain assigned GPU after compute.

## Distributed intervention stage: gpu5 / adopting_existing_worker

UTC 2026-10-09T21:19:00.557016+00:00

State: /path/to/user-user/lora-dora-profiling/distributed-important/gpu5-state.json. External controller: /path/to/user-user/lora-dora-profiling/distributed_important.py. Frozen evaluator unchanged; versions Torch2.5.1+cu121 / Transformers4.57.1 / PEFT0.17.1 / Accelerate1.11.0.

```json
{
  "pid": 4164561,
  "lane": "gpu5",
  "gpu_uuid": "GPU_UUID",
  "status": "adopting_existing_worker",
  "completed_jobs": [],
  "created_utc": "2026-10-09T21:18:11.000660+00:00",
  "worker_pid": 3865529,
  "updated_utc": "2026-10-09T21:18:11.602342+00:00"
}
```

Next: inspect failures immediately; otherwise follow lane plan.json sequentially, compare only completed matched outputs, retain assigned GPU after compute.

## Distributed intervention stage: gpu2 / adopting_existing_worker

UTC 2026-10-09T21:19:00.550035+00:00

State: /path/to/user-user/lora-dora-profiling/distributed-important/gpu2-state.json. External controller: /path/to/user-user/lora-dora-profiling/distributed_important.py. Frozen evaluator unchanged; versions Torch2.5.1+cu121 / Transformers4.57.1 / PEFT0.17.1 / Accelerate1.11.0.

```json
{
  "pid": 4163884,
  "lane": "gpu2",
  "gpu_uuid": "GPU_UUID",
  "status": "adopting_existing_worker",
  "completed_jobs": [],
  "created_utc": "2026-10-09T21:17:50.589932+00:00",
  "worker_pid": 3785966,
  "updated_utc": "2026-10-09T21:17:51.593257+00:00"
}
```

Next: inspect failures immediately; otherwise follow lane plan.json sequentially, compare only completed matched outputs, retain assigned GPU after compute.

## Очередь 1 запущена

UTC: 2026-10-09T21:17:52.209189+00:00

```json
{
  "series": 1,
  "pid": 4164064,
  "status": "starting",
  "interval_seconds": 10,
  "required_consecutive_checks": 2,
  "plan_sha256": "29fc7a734e2d0de1c26b5459b88706850409becca9ae1f70659f4a1be7404639",
  "estimated_gpu_seconds": 169200
}
```

## Removed full no-op and full V/O benchmark; current worker preserved — 2026-10-09T21:01:35.917397+00:00

User authorizes removal of full V/O symmetry if it only checks function preservation; redundant full no-op also removed after audit. Neither full job had started. Both job states explicitly cancelled, not marked as measured or completed. Existing short timing/statistic artifacts remain. Full mathematical/statistical symmetry analysis is retained as a short validation, not a1319-case generation benchmark.

Active continuation plan: /path/to/user-user/lora-dora-profiling/first-series-without-redundant-full.json. It contains the baseline triple and20 interventions. Dependencies previously on no-op now point to primary quality; implicit intervention references explicitly point to the original primary DoRA output. Other interventions unchanged. Correction family follows the filtered plan. Frozen study sources unchanged.

Old coordinator3830527 stopped after verified new CUDA context3914873 on sameGPU5. Existing base worker3865529 continued without signal, reload, lost predictions or GPU release; observed 443 saved predictions. New coordinator3914873 currently adopts that worker, then validates complete output/hash/source, registers actual full/base completion and continues original evaluator with the external filtered plan. This is waiting for our own running worker, not waiting for a free GPU. State/log: /path/to/user-user/lora-dora-profiling/filtered-first/{state.json,coordinator.log,handover-go.json}. On failure it retains CUDA context for inspection. MMLU/SQuAD queues unchanged.

Reason for original no-op: technical reproducibility control was mistakenly expanded into a full repeated dataset run despite same source/model/prompts/greedy settings. Full repeat adds no independent evidence. Audit also identifies function-preserving full V/O as reducible to numerical/statistical checks; dense controls remain because actual BF16 conversion produced logits discrepancies. Answer.AI forecasts counted base per pair, but future identical base/eval controls for10k/100k should be reused once per base; those loaders/jobs remain unimplemented, not running.

Next: continue baseline; confirm filtered continuation after adopted base worker finishes; expand short symmetry checks on representative inputs if needed. Seven-core-intervention proposal remains unapplied. User does not authorize other pair/intervention removals.

## Server load and first-queue research-priority analysis — 2026-10-09T20:40:25.822875+00:00

User latest instruction: leave all other pairs and interventions untouched; report server load and scientific priority of first queue. Seven RTX A4000: ourGPU2/5/6 at97–100%, ~8GiB each; GPU0/1 low utilization but other compute processes present; GPU3/4 occupied by other processes. CPU20.2% over5s on80logical CPUs, availableRAM714.9/754.5GiB. Snapshot20:38UTC /23:38Moscow in /path/to/user-user/lora-dora-profiling/server-load-and-scope.json.

Analysis saved as /path/to/user-user/lora-dora-profiling/first-queue-priority-analysis.md and matching JSON. Recommend7 full interventions (dense DoRA/LoRA, global removeD/baseMagnitude, rank32/energy95, matched LoRA) costing22.23GPUh vs22 current jobs118.04h. Twelve localization ablations cost83.51GPUh and are lower priority before global effects are known. Full no-op/symmetry could become short validations, energy99 reserve. Expanded dense fidelity/activation-control calibration needed before strong interpretation. Proposed3-GPU distribution7.02/7.45/7.76h after baseline gives20–25h to core results if implemented and validated; current serial plan unchanged. Deadline through12October inclusive.

No additional cancellation, schedule change, GPU admission, training or foreign process modification. Source fingerprint recheck unchanged. Qwen8B remains cancelled, LLaVA excluded. Next: user decision on7-job subset and parallel execution, while current three ready evaluations continue.

## User scope decisions, deadline and sample-dependence audit — 2026-10-09T20:36:43.840749+00:00

Deadline: end of12October2026 inclusive (session Moscow time). Qwen3-8B entire two-GPU queue cancelled by explicit user instruction, PID3750344 terminated while waiting_for_two_free_gpus, no full jobs started. Cancellation saved in /path/to/user-user/lora-dora-dual/results/qwen8b-two-gpu/state.json, old state retained as state-before-user-cancellation.json. Both shadow_8b_gsm8k and shadow_8b_squadv2 excluded. LLaVA excluded by earlier explicit user instruction; never started, unimplemented loader cannot run from existing frozen queue. All future continuation must apply exclusions in /path/to/user-user/lora-dora-profiling/research-scope-decisions.json and use external continuation plan /path/to/user-user/lora-dora-profiling/two-series-without-llava.json. Frozen historical configs remain unchanged to preserve exact source_sha256 across active matched runs; currently loaded queues can still display historical blocked LLaVA entry until continuation restarts with filtered plan. Do not interpret that historical readiness entry as authorization to implement or run LLaVA.

Two independent ready-pair queues confirmed already active, no duplicate jobs launched: MMLU keeper3786742/worker3850626 onGPU6 (full DoRA), SQuAD keeper3785635/worker3785966 onGPU2 (full base). Primary GSM8K keeper3830527/worker3865529 onGPU5 (full base). Three retained cards continue; no other pairs or interventions changed. No training, gradients or optimizer steps.

Inventory audit: original10 candidate pairs were conditions, not10 bases. After exclusions remaining7 conditions on3 bases: Qwen3-4B across3 task-adapter pairs, Llama2-7B 10k/100k and Llama3-8B 10k/100k. Answer.AI pairs remain blocked, unchanged. Shared bases/tasks, related train sizes and absent seed replications limit independence. Qwen8B was a size-robustness condition within Qwen3 family, not another independent architecture; make this distinction explicit. Other known gaps: unknown per-run training hyperparameters/base snapshot, ShadowPEFT LR tuning and conflicting GSM8K LoRA table values, Answer.AI quantization/custom loader, reserve PeRL/Mistral confounds. User asks to report these without changing other candidates.

Research explanation and proposed resource budget in /path/to/user-user/lora-dora-profiling/research-scope-and-data.md and deadline-study-proposal.json. Proposed7 core interventions cost22.23GPUh, ~34h with baseline sequential or ~20–25h with a validated three-GPU schedule after primary quality. Proposal NOT applied; existing22 remain queued pending user choice. Current experiments collect per-example predictions/metrics, paired differences and CI, resource/provenance metadata; intervention probes add spectra, activation errors, logits and magnitude/direction correlations. These are final-checkpoint analyses, not identification of training trajectory. Need dense fidelity and richer calibration validation before stronger interpretations.

Next: answer user questions about sample overlap and collected data; await their intervention-scope choice, continue existing ready runs. Do not restart cancelled8B, runLLaVA, exclude other pairs, edit frozen study sources or cancel any additional job without new user instruction.

## Completed direct timing of all 22 interventions; primary resumed — 2026-10-09T20:18:30.778610+00:00

All22 real-weight preparation and four stratified generation probes completed; failed=0. Forecast includes separate smoke and full preparations and smoke inference: 118.04 h for22 jobs, 130.47 h for the remaining first queue including the baseline triple. Four cases/job are a timing extrapolation, not quality evaluation or a statistical CI. No jobs excluded; all queue plans unchanged.

GPU5 retained through handover/profiling/resume. Coordinator PID3830527; resumed worker PID3865529; resume from199 preserved greedy predictions, verified 212 complete predictions after restart. Exact two-case GPU resume validation passed. Frozen SERIES source SHA256 map rechecked: no changes. GPU SERIES HEAD6cc5898 plus frozen dirty study source; original primary HEAD93cd828184c422628e867a1f4946fdeef4d5e917. External wrapper hash bd13a2459a3e572b0630137ac61f40d549d2f53fe2f15140492040ef393145d2, original worker hash8f902d0ff539cf11d2743f98648a07c4015dd20f484f110ee6fbe97e97f61f9a. Historical483 sampled answers remain archived and unused in corrected quality.

Versions: Python3.12.3, torch2.5.1+cu121, transformers4.57.1, peft0.17.1, accelerate1.11.0. Maximum measured profiler allocated VRAM9.5645GiB, cumulative lifetime RSS11.2754GiB. Retaining process held separate4GiB during probes, now reservation0 with CUDA context retained while primary runs. File locks are cooperative, not scheduler exclusivity.

Numerical scope: V/O symmetry calibration logits were identical to its dense reference (max error0, argmax1.0); conversion from initial DoRA to BF16 dense itself had max abs logits error1.34375 and argmax agreement0.98148. Do not label the whole conversion exact, or infer full quality/function preservation from the calibration check. Planned dense controls must be included in later interpretation.

Blocked-model planning only: historical Answer.AI evaluation uses500 examples, cache=True, max_new_tokens1024, default batch16. Approximate central scenario per three-role pair ~11h with batch16 vs53h Llama2/57h Llama3 at batch1; batch16 fit and blocked loader performance unverified, broad scenario ranges in report. Training10k/100k does not change the500 evaluation count. HF approval, downloads and loader engineering not included. LLaVA author seven-task suite has roughly150590 calls/role, including107394 VQAv2 test-dev questions independently counted from official archive; remaining exact annotation counts pending. Assumed2–10sec/call =>167–837h for LoRA+DoRA, not measured LLaVA speed. Model sharding is not data-parallel speedup. No gated weights or blocked full models launched for these calculations.

Artifacts: /path/to/user-user/lora-dora-profiling/interventions-direct/ (real preparation reports, timing JSONL, state, resume validation); intervention-timing-export.json; intervention-time-forecast.json; blocked-time-estimates.json; direct-intervention-and-blocked-forecast.md. Code archive profiling-22-interventions-code.tgz SHA256 fdbd0b5ef7a78199f349f9413a428a59c036c086412ea4347d37d40b705f5d6a. VM mirrored outputs in /path/to/user/Documents/Codex/2026-10-09/dora-lora-https-github-com-kkoottiiaarraa/outputs/. Author source copies/hashes in VM outputs/author-timing-sources/, NVlabs main checked7e2f10abbe8efe212c8fca1d983ae1d04ef13a18, AnswerDotAI pinned e454d3180ef575654279d6ac444a86cb0bb3ff33.

Next: discuss timing budget with user without changing scope in this session; running corrected queues continue, dual8B still waits for two idle cards under total cap5. Quality study not complete; blocked loaders and authorized HF access still pending. Do not reinstall, reconfigure access, touch foreign processes, or modify frozen study source while matched runs active.

## Primary greedy quality resumed from saved prefix onGPU5

UTC 2026-10-09T20:13:46.483645+00:00

```json
{
  "pid": 3830527,
  "worker_pid": 3865529,
  "saved_predictions": 199,
  "output": "/path/to/user-user/lora-dora-series/results/first-series-greedy/jobs/gsm8k-quality-greedy/full-base-attempt-1"
}
```

## Очередь 3 запущена

UTC: 2026-10-09T20:13:46.478528+00:00

```json
{
  "series": 3,
  "pid": 3830527,
  "status": "starting",
  "interval_seconds": 10,
  "required_consecutive_checks": 2,
  "plan_sha256": "083d6b2aa6ec4cdb245dae70fbafa805d8717dbde667975bb9782db476bc8923",
  "estimated_gpu_seconds": 403056.0,
  "retained_gpu_uuid": "GPU_UUID"
}
```

## Direct intervention timing stage finished; resuming primary

UTC 2026-10-09T20:13:46.384194+00:00

```json
{
  "status": "complete",
  "pid": 3831463,
  "gpu_uuid": "GPU_UUID",
  "jobs_total": 22,
  "completed": [
    "gsm8k-unmodified-dora",
    "gsm8k-dense-dora",
    "gsm8k-dense-lora",
    "gsm8k-r32",
    "gsm8k-e95",
    "gsm8k-e99",
    "gsm8k-vo-symmetry",
    "gsm8k-lora-matched-impact",
    "gsm8k-remove_d-all",
    "gsm8k-base_magnitude-k",
    "gsm8k-base_magnitude-q",
    "gsm8k-base_magnitude-v",
    "gsm8k-remove_d-k",
    "gsm8k-remove_d-o",
    "gsm8k-remove_d-qk",
    "gsm8k-remove_d-vo",
    "gsm8k-base_magnitude-all",
    "gsm8k-base_magnitude-o",
    "gsm8k-base_magnitude-qk",
    "gsm8k-base_magnitude-vo",
    "gsm8k-remove_d-q",
    "gsm8k-remove_d-v"
  ],
  "failed": [],
  "sample_indices": [
    828,
    56,
    1245,
    199
  ],
  "scope": "Full preparation on real checkpoint; four stratified timed cases, no full quality evaluation",
  "frozen_study_source_sha256": {
    "configs/first_series_interventions.json": "083d6b2aa6ec4cdb245dae70fbafa805d8717dbde667975bb9782db476bc8923",
    "configs/gsm8k_evaluation.json": "51f1dcbe57ef9d368fed55b08ecd57b588f6a0af52082c8ef9232d0e2bae7892",
    "configs/shadow_qwen3_4b_gsm8k.json": "2dbfd7dee4d72ebd1318f6e822200288a76b2fa867d5c6b4315b41d824727b60",
    "configs/two_series.json": "29fc7a734e2d0de1c26b5459b88706850409becca9ae1f70659f4a1be7404639",
    "lora_dora_study/__init__.py": "fbc3bb7eb7c83ca1fd29e19cd1209a04a919d46abcd99918ac6fa8f670df4f79",
    "lora_dora_study/adapters.py": "4f91f9d1e20873cb0354517646ef6e84bd8447db14989cec88d9219c7f558729",
    "lora_dora_study/algebra.py": "87ac9d6a6ecde4a7c24774307b98f7cae8d6d0ba4244eb53b7f9ea6780996b12",
    "lora_dora_study/benchmarks.py": "1abd84b8e6b5e1c145ff83ede420d8b283a54c5afd030a6aa868f65201f3ba2d",
    "lora_dora_study/evaluation.py": "800346b795e2ed9259bc906286d4cd3e7862b53ba46cac49872f85160f781118",
    "lora_dora_study/interventions.py": "68b7582f33ace776902ad98df1e6b3238b7bf047a42e29ecf757ac3ac24a4e54",
    "lora_dora_study/leases.py": "143790f69c08aaa957eac8318c8d69eecdba06ba5aee9c31a89093d1b45cb71a",
    "lora_dora_study/rank_symmetry.py": "d50047efc0bc82778a511300d89a2555d462a7be95794fa23dfbb601d9132079",
    "lora_dora_study/retention.py": "3c181da178ebd5df6cee159640c2ed3fce6c49702fae9cb4aa7ddd02d056ed51",
    "lora_dora_study/series_queue.py": "edb9fbcd2b1ad0edfe2863543285bc004dcb94986cc4269d9b9527dd110ccab4",
    "lora_dora_study/series_results.py": "41335508fb591ab457a54d2d1d72d78412259839d17e2fdc530a6538249a33ae",
    "lora_dora_study/server.py": "80ce9961664b2530faea6161ee59982a7861fc801b301475da3ea7409105e077",
    "scripts/compare_gsm8k.py": "ec8f2486e2c08a301514c0bb8e6acb7836e470dcce267f221b7ad8a5ae07ef4e",
    "scripts/continue_after_pilot.py": "e4a4f822ac4d9e6e67e8ddd2531cdd39441352737ad001f1171d39cbd7fbc11c",
    "scripts/download_pilot.py": "5ca9d83eab7a7b9fa6741e5753a9dcf7a37f4a1ac7c58a842670542dd29b8fe4",
    "scripts/evaluate_gsm8k.py": "f7bd78ee63ebb253a266635921f0e20ec4fca80d72a9106a2a2f7f54f5ba5c08",
    "scripts/held_gpu_worker.py": "2554c0cf91ae5d9d06b782ec0b783d403daad62ca8ac255037220acde135dc56",
    "scripts/pilot_worker.py": "3b5631ac216de9ef90ab5e1f56cc3f70d31a2ce64172025efdc5bce3848e0bd1",
    "scripts/prepare_gsm8k.py": "d063e1e691bfc4f279cf42af2a4f4311bc8d266b02ae9213adfbf2fc9ef047d1",
    "scripts/prepare_series_data.py": "19441551346080856e2d9e52b266d030180beed6251a1000dda9753770ba1673",
    "scripts/resume_primary_held.py": "34e42275412ba627f25c7a87ea410c96f5bce8665b05eb7f665817783e251ce9",
    "scripts/run_pilot.py": "3c4c1ae59042c691cc1a5fc55d5d36f84148d7af9deb2e569cfbfed5e41a3965",
    "scripts/run_series_queue.py": "3c874540c3a8fa3a817569e4d492376086001b252618c1b3b2a06cce795c9d1d",
    "scripts/series_worker.py": "8f902d0ff539cf11d2743f98648a07c4015dd20f484f110ee6fbe97e97f61f9a",
    "scripts/server_preflight.py": "186d4d97765e41190ba67da44a39d2720270ea5df47dcabdf84a383ff7a4f80e",
    "scripts/wait_for_pilot.py": "b1949fe299b3f6d37ea0c9b06fa7f5901e26509639b9a2c1e3a607888b678d03"
  },
  "profiler_sha256": "1bbb6f10a9ae54b2f2fbb815d573879772b98c1a0e8a88dc5b948cd6570b505b",
  "versions": {
    "torch": "2.5.1+cu121",
    "transformers": "4.57.1",
    "peft": "0.17.1",
    "accelerate": "1.11.0"
  },
  "job": "gsm8k-remove_d-v",
  "phase": "inference",
  "estimated_full_22_hours": 117.67229845578814,
  "measured_total_preparation_hours": 0.17078160979911142
}
```

## shadow_4b_mmlu / full/lora

UTC: 2026-10-09T20:00:28.408948+00:00

```json
{
  "path": "/path/to/user-user/lora-dora-series/results/extra-series-greedy/jobs/shadow_4b_mmlu/full-lora-attempt-1",
  "metrics": {
    "accuracy": 0.7031761857285287
  },
  "memory": {
    "peak_allocated_bytes": 8233698816,
    "peak_reserved_bytes": 8302624768,
    "max_process_rss_bytes": 4779855872,
    "available_host_ram_bytes": 766458744832
  },
  "inference_seconds": 2047.4974543780554,
  "predictions_completed": 14042,
  "full_evaluation": true,
  "versions": {
    "torch": "2.5.1+cu121",
    "transformers": "4.57.1",
    "peft": "0.17.1",
    "safetensors": "0.6.2",
    "accelerate": "1.11.0"
  }
}
```

## Greedy prefix resume GPU validation passed; profiling all22

UTC 2026-10-09T19:40:20.403370+00:00

```json
{
  "pid": 3830527,
  "path": "/path/to/user-user/lora-dora-profiling/interventions-direct",
  "saved_predictions": 199
}
```

## shadow_4b_mmlu / full/base

UTC: 2026-10-09T19:26:10.120252+00:00

```json
{
  "path": "/path/to/user-user/lora-dora-series/results/extra-series-greedy/jobs/shadow_4b_mmlu/full-base-attempt-1",
  "metrics": {
    "accuracy": 0.660518444666002
  },
  "memory": {
    "peak_allocated_bytes": 8096166912,
    "peak_reserved_bytes": 8120172544,
    "max_process_rss_bytes": 4780470272,
    "available_host_ram_bytes": 768511791104
  },
  "inference_seconds": 1516.4973321959842,
  "predictions_completed": 14042,
  "full_evaluation": true,
  "versions": {
    "torch": "2.5.1+cu121",
    "transformers": "4.57.1",
    "peft": "0.17.1",
    "safetensors": "0.6.2",
    "accelerate": "1.11.0"
  }
}
```

## Final timing handoff: actual queues and next action

All five corrected short profiles complete. Wall forecast:4B/GSM13.113h,4B/MMLU2.387h,4B/SQuAD7.477h,8B GSM+SQuAD31.862h on2 GPUs. First queue really resumed onGPU5,PID3794009,full/base; at19:19UTC base93 rows. Historical483 sampling answers preserved,not reused. Additional queues GPU6 MMLU andGPU2 SQuAD running,8B full waits2 free initial cards. Short8B probes released extension slots; temporary max5 remains authorized.

Report /path/to/user-user/lora-dora-profiling/timing-and-resume.md; forecast-with-progress.json; final-queue-snapshot.json; source archive greedy-research-source-final.tgz. Local source commits series8b5f262,dual88bfad1; GPU frozen HEAD6cc5898+source hashes in summaries (all3 current hashes rechecked equal). Original GPUHEAD93cd828 unchanged. CPU33 regression tests and standalone config/transfer/guard tests pass. gc.collect() added between profiling roles afterAccelerate cycle OOM; completed base timing reused with recorded sample/revision/version checks.

Next: user budget discussion; baseline matched quality still running.22 subsequent first-queue jobs have NOT been directly timed,4–7days is coarse budget only. Gated/custom remaining pairs have no validated completion ETA. No training/DoRA quality advantage/trajectory causality inferred.

## Completed corrected timing for four queues

UTC 2026-10-09T19:18:32.850893+00:00

```json
{
  "updated_utc": "2026-10-09T19:18:32.850893+00:00",
  "profiles": {
    "gsm8k-4b-greedy": {
      "status": "complete",
      "sample_count": 8,
      "roles": {
        "base": {
          "estimated_full_hours": 3.669427777794287,
          "load_seconds": 3.1262436909601092,
          "adapter_seconds": 0,
          "per_gpu": {
            "GPU_UUID": {
              "peak_allocated_bytes": 8082846208,
              "peak_reserved_bytes": 8099201024
            }
          },
          "max_process_rss_bytes": 4748328960,
          "sample_count": 8,
          "adapter_validation": null
        },
        "lora": {
          "estimated_full_hours": 2.584190353515005,
          "load_seconds": 2.8670551349641755,
          "adapter_seconds": 1.0832096959929913,
          "per_gpu": {
            "GPU_UUID": {
              "peak_allocated_bytes": 8242747904,
              "peak_reserved_bytes": 8296333312
            }
          },
          "max_process_rss_bytes": 5313572864,
          "sample_count": 8,
          "adapter_validation": {
            "status": "verified",
            "saved_tensor_count": 288,
            "exact_loaded_value_match": true,
            "adapted_module_count": 144,
            "magnitude_vector_count": 0,
            "modules": [
              {
                "name": "base_model.model.model.layers.0.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.0.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.0.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.0.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.1.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.1.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.1.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.1.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.2.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.2.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.2.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.2.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.3.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.3.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.3.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.3.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.4.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.4.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.4.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.4.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.5.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.5.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.5.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.5.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.6.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.6.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.6.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.6.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.7.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.7.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.7.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.7.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.8.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.8.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.8.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.8.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.9.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.9.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.9.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.9.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.10.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.10.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.10.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.10.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.11.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.11.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.11.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.11.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.12.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.12.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.12.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.12.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.13.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.13.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.13.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.13.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.14.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.14.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.14.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.14.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.15.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.15.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.15.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.15.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.16.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.16.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.16.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.16.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.17.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.17.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.17.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.17.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.18.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.18.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.18.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.18.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.19.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.19.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.19.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.19.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.20.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.20.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.20.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.20.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.21.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.21.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.21.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.21.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.22.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.22.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.22.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.22.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.23.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.23.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.23.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.23.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.24.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.24.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.24.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.24.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.25.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.25.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.25.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.25.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.26.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.26.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.26.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.26.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.27.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.27.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.27.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.27.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.28.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.28.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.28.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.28.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.29.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.29.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.29.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.29.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.30.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.30.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.30.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.30.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.31.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.31.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.31.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.31.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.32.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.32.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.32.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.32.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.33.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.33.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.33.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.33.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.34.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.34.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.34.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.34.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.35.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.35.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.35.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.35.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              }
            ]
          }
        },
        "dora": {
          "estimated_full_hours": 6.859547560833873,
          "load_seconds": 2.6972806020639837,
          "adapter_seconds": 0.5609898800030351,
          "per_gpu": {
            "GPU_UUID": {
              "peak_allocated_bytes": 8388653056,
              "peak_reserved_bytes": 8552185856
            }
          },
          "max_process_rss_bytes": 5347192832,
          "sample_count": 8,
          "adapter_validation": {
            "status": "verified",
            "saved_tensor_count": 432,
            "exact_loaded_value_match": true,
            "adapted_module_count": 144,
            "magnitude_vector_count": 144,
            "modules": [
              {
                "name": "base_model.model.model.layers.0.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.0.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.0.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.0.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.1.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.1.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.1.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.1.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.2.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.2.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.2.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.2.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.3.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.3.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.3.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.3.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.4.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.4.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.4.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.4.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.5.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.5.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.5.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.5.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.6.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.6.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.6.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.6.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.7.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.7.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.7.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.7.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.8.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.8.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.8.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.8.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.9.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.9.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.9.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.9.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.10.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.10.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.10.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.10.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.11.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.11.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.11.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.11.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.12.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.12.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.12.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.12.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.13.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.13.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.13.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.13.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.14.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.14.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.14.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.14.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.15.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.15.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.15.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.15.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.16.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.16.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.16.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.16.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.17.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.17.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.17.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.17.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.18.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.18.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.18.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.18.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.19.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.19.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.19.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.19.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.20.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.20.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.20.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.20.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.21.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.21.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.21.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.21.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.22.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.22.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.22.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.22.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.23.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.23.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.23.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.23.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.24.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.24.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.24.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.24.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.25.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.25.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.25.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.25.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.26.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.26.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.26.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.26.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.27.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.27.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.27.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.27.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.28.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.28.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.28.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.28.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.29.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.29.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.29.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.29.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.30.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.30.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.30.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.30.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.31.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.31.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.31.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.31.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.32.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.32.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.32.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.32.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.33.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.33.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.33.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.33.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.34.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.34.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.34.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.34.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.35.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.35.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.35.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.35.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              }
            ]
          }
        }
      },
      "full_three_roles_hours": 13.113165692143165,
      "sampling_only_95pct_hours": [
        11.720665969326785,
        14.554477870676912
      ],
      "load_hours": 0.002870771945551193,
      "caveat": "Stratified timing bootstrap only; excludes contention changes, GPU waiting, interventions and custom-loader work. Not quality evidence."
    },
    "mmlu-4b-greedy": {
      "status": "complete",
      "sample_count": 12,
      "roles": {
        "base": {
          "estimated_full_hours": 0.5271280837753416,
          "load_seconds": 3.0611152390483767,
          "adapter_seconds": 0,
          "per_gpu": {
            "GPU_UUID": {
              "peak_allocated_bytes": 8085445120,
              "peak_reserved_bytes": 8120172544
            }
          },
          "max_process_rss_bytes": 4828491776,
          "sample_count": 12,
          "adapter_validation": null
        },
        "lora": {
          "estimated_full_hours": 0.5427131683627548,
          "load_seconds": 2.9836747919907793,
          "adapter_seconds": 1.3677062329370528,
          "per_gpu": {
            "GPU_UUID": {
              "peak_allocated_bytes": 8242754560,
              "peak_reserved_bytes": 8296333312
            }
          },
          "max_process_rss_bytes": 5395881984,
          "sample_count": 12,
          "adapter_validation": {
            "status": "verified",
            "saved_tensor_count": 288,
            "exact_loaded_value_match": true,
            "adapted_module_count": 144,
            "magnitude_vector_count": 0,
            "modules": [
              {
                "name": "base_model.model.model.layers.0.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.0.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.0.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.0.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.1.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.1.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.1.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.1.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.2.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.2.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.2.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.2.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.3.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.3.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.3.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.3.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.4.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.4.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.4.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.4.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.5.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.5.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.5.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.5.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.6.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.6.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.6.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.6.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.7.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.7.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.7.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.7.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.8.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.8.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.8.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.8.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.9.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.9.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.9.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.9.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.10.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.10.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.10.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.10.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.11.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.11.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.11.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.11.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.12.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.12.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.12.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.12.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.13.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.13.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.13.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.13.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.14.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.14.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.14.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.14.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.15.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.15.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.15.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.15.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.16.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.16.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.16.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.16.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.17.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.17.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.17.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.17.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.18.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.18.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.18.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.18.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.19.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.19.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.19.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.19.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.20.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.20.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.20.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.20.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.21.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.21.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.21.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.21.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.22.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.22.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.22.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.22.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.23.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.23.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.23.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.23.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.24.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.24.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.24.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.24.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.25.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.25.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.25.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.25.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.26.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.26.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.26.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.26.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.27.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.27.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.27.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.27.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.28.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.28.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.28.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.28.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.29.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.29.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.29.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.29.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.30.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.30.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.30.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.30.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.31.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.31.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.31.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.31.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.32.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.32.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.32.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.32.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.33.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.33.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.33.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.33.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.34.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.34.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.34.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.34.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.35.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.35.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.35.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.35.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              }
            ]
          }
        },
        "dora": {
          "estimated_full_hours": 1.3168624226980694,
          "load_seconds": 3.0067536800634116,
          "adapter_seconds": 1.4809514589142054,
          "per_gpu": {
            "GPU_UUID": {
              "peak_allocated_bytes": 8390874624,
              "peak_reserved_bytes": 8552185856
            }
          },
          "max_process_rss_bytes": 5430312960,
          "sample_count": 12,
          "adapter_validation": {
            "status": "verified",
            "saved_tensor_count": 432,
            "exact_loaded_value_match": true,
            "adapted_module_count": 144,
            "magnitude_vector_count": 144,
            "modules": [
              {
                "name": "base_model.model.model.layers.0.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.0.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.0.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.0.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.1.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.1.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.1.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.1.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.2.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.2.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.2.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.2.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.3.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.3.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.3.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.3.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.4.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.4.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.4.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.4.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.5.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.5.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.5.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.5.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.6.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.6.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.6.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.6.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.7.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.7.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.7.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.7.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.8.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.8.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.8.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.8.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.9.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.9.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.9.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.9.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.10.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.10.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.10.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.10.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.11.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.11.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.11.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.11.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.12.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.12.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.12.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.12.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.13.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.13.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.13.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.13.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.14.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.14.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.14.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.14.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.15.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.15.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.15.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.15.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.16.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.16.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.16.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.16.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.17.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.17.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.17.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.17.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.18.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.18.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.18.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.18.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.19.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.19.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.19.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.19.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.20.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.20.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.20.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.20.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.21.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.21.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.21.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.21.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.22.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.22.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.22.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.22.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.23.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.23.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.23.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.23.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.24.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.24.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.24.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.24.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.25.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.25.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.25.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.25.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.26.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.26.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.26.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.26.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.27.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.27.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.27.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.27.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.28.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.28.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.28.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.28.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.29.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.29.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.29.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.29.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.30.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.30.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.30.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.30.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.31.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.31.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.31.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.31.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.32.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.32.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.32.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.32.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.33.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.33.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.33.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.33.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.34.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.34.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.34.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.34.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.35.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.35.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.35.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.35.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              }
            ]
          }
        }
      },
      "full_three_roles_hours": 2.386703674836166,
      "sampling_only_95pct_hours": [
        2.0631692368286787,
        2.5975099301761064
      ],
      "load_hours": 0.003305611500820507,
      "caveat": "Stratified timing bootstrap only; excludes contention changes, GPU waiting, interventions and custom-loader work. Not quality evidence."
    },
    "squadv2-4b-greedy": {
      "status": "complete",
      "sample_count": 16,
      "roles": {
        "base": {
          "estimated_full_hours": 3.3062083815131658,
          "load_seconds": 2.8242949940031394,
          "adapter_seconds": 0,
          "per_gpu": {
            "GPU_UUID": {
              "peak_allocated_bytes": 8078632960,
              "peak_reserved_bytes": 8097103872
            }
          },
          "max_process_rss_bytes": 4879478784,
          "sample_count": 16,
          "adapter_validation": null
        },
        "lora": {
          "estimated_full_hours": 1.129195752957894,
          "load_seconds": 2.8423385430360213,
          "adapter_seconds": 1.5710454980144277,
          "per_gpu": {
            "GPU_UUID": {
              "peak_allocated_bytes": 8242752000,
              "peak_reserved_bytes": 8296333312
            }
          },
          "max_process_rss_bytes": 5428670464,
          "sample_count": 16,
          "adapter_validation": {
            "status": "verified",
            "saved_tensor_count": 288,
            "exact_loaded_value_match": true,
            "adapted_module_count": 144,
            "magnitude_vector_count": 0,
            "modules": [
              {
                "name": "base_model.model.model.layers.0.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.0.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.0.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.0.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.1.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.1.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.1.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.1.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.2.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.2.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.2.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.2.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.3.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.3.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.3.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.3.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.4.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.4.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.4.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.4.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.5.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.5.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.5.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.5.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.6.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.6.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.6.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.6.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.7.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.7.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.7.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.7.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.8.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.8.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.8.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.8.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.9.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.9.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.9.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.9.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.10.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.10.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.10.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.10.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.11.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.11.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.11.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.11.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.12.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.12.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.12.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.12.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.13.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.13.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.13.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.13.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.14.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.14.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.14.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.14.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.15.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.15.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.15.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.15.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.16.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.16.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.16.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.16.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.17.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.17.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.17.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.17.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.18.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.18.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.18.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.18.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.19.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.19.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.19.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.19.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.20.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.20.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.20.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.20.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.21.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.21.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.21.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.21.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.22.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.22.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.22.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.22.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.23.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.23.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.23.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.23.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.24.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.24.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.24.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.24.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.25.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.25.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.25.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.25.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.26.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.26.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.26.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.26.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.27.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.27.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.27.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.27.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.28.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.28.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.28.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.28.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.29.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.29.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.29.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.29.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.30.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.30.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.30.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.30.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.31.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.31.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.31.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.31.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.32.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.32.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.32.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.32.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.33.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.33.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.33.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.33.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.34.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.34.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.34.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.34.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.35.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.35.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.35.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.35.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              }
            ]
          }
        },
        "dora": {
          "estimated_full_hours": 3.041935763255557,
          "load_seconds": 2.7972865239717066,
          "adapter_seconds": 0.9590585090918466,
          "per_gpu": {
            "GPU_UUID": {
              "peak_allocated_bytes": 8395991040,
              "peak_reserved_bytes": 8554283008
            }
          },
          "max_process_rss_bytes": 5461606400,
          "sample_count": 16,
          "adapter_validation": {
            "status": "verified",
            "saved_tensor_count": 432,
            "exact_loaded_value_match": true,
            "adapted_module_count": 144,
            "magnitude_vector_count": 144,
            "modules": [
              {
                "name": "base_model.model.model.layers.0.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.0.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.0.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.0.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.1.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.1.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.1.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.1.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.2.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.2.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.2.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.2.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.3.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.3.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.3.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.3.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.4.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.4.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.4.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.4.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.5.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.5.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.5.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.5.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.6.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.6.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.6.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.6.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.7.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.7.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.7.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.7.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.8.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.8.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.8.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.8.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.9.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.9.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.9.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.9.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.10.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.10.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.10.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.10.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.11.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.11.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.11.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.11.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.12.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.12.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.12.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.12.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.13.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.13.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.13.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.13.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.14.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.14.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.14.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.14.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.15.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.15.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.15.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.15.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.16.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.16.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.16.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.16.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.17.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.17.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.17.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.17.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.18.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.18.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.18.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.18.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.19.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.19.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.19.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.19.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.20.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.20.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.20.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.20.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.21.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.21.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.21.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.21.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.22.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.22.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.22.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.22.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.23.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.23.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.23.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.23.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.24.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.24.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.24.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.24.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.25.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.25.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.25.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.25.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.26.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.26.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.26.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.26.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.27.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.27.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.27.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.27.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.28.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.28.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.28.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.28.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.29.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.29.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.29.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.29.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.30.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.30.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.30.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.30.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.31.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.31.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.31.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.31.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.32.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.32.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.32.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.32.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.33.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.33.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.33.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.33.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.34.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.34.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.34.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.34.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.35.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.35.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.35.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.35.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              }
            ]
          }
        }
      },
      "full_three_roles_hours": 7.477339897726617,
      "sampling_only_95pct_hours": [
        6.602015165746335,
        8.329025942809368
      ],
      "load_hours": 0.003053895574476984,
      "caveat": "Stratified timing bootstrap only; excludes contention changes, GPU waiting, interventions and custom-loader work. Not quality evidence."
    },
    "gsm8k-8b-greedy-staged": {
      "status": "complete",
      "sample_count": 8,
      "roles": {
        "base": {
          "estimated_full_hours": 6.5964543218744645,
          "load_seconds": 6.355935138068162,
          "adapter_seconds": 0,
          "per_gpu": {
            "GPU_UUID": {
              "peak_allocated_bytes": 8255474688,
              "peak_reserved_bytes": 8300527616
            },
            "GPU_UUID": {
              "peak_allocated_bytes": 8235826176,
              "peak_reserved_bytes": 8260681728
            }
          },
          "max_process_rss_bytes": 4832751616,
          "sample_count": 8,
          "adapter_validation": null
        },
        "lora": {
          "estimated_full_hours": 3.8359682578769734,
          "load_seconds": 6.203005905030295,
          "adapter_seconds": 0.6593227540142834,
          "per_gpu": {
            "GPU_UUID": {
              "peak_allocated_bytes": 8374769664,
              "peak_reserved_bytes": 8474591232
            },
            "GPU_UUID": {
              "peak_allocated_bytes": 8286884864,
              "peak_reserved_bytes": 8302624768
            }
          },
          "max_process_rss_bytes": 4832329728,
          "sample_count": 8,
          "adapter_validation": {
            "status": "verified",
            "saved_tensor_count": 288,
            "exact_loaded_value_match": true,
            "adapted_module_count": 144,
            "magnitude_vector_count": 0,
            "modules": [
              {
                "name": "base_model.model.model.layers.0.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.0.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.0.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.0.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.1.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.1.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.1.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.1.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.2.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.2.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.2.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.2.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.3.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.3.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.3.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.3.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.4.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.4.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.4.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.4.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.5.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.5.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.5.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.5.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.6.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.6.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.6.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.6.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.7.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.7.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.7.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.7.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.8.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.8.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.8.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.8.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.9.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.9.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.9.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.9.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.10.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.10.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.10.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.10.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.11.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.11.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.11.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.11.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.12.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.12.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.12.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.12.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.13.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.13.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.13.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.13.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.14.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.14.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.14.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.14.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.15.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.15.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.15.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.15.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.16.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.16.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.16.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.16.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.17.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.17.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.17.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.17.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.18.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.18.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.18.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.18.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.19.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.19.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.19.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.19.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.20.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.20.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.20.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.20.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.21.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.21.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.21.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.21.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.22.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.22.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.22.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.22.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.23.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.23.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.23.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.23.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.24.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.24.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.24.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.24.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.25.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.25.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.25.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.25.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.26.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.26.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.26.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.26.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.27.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.27.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.27.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.27.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.28.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.28.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.28.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.28.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.29.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.29.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.29.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.29.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.30.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.30.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.30.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.30.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.31.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.31.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.31.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.31.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.32.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.32.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.32.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.32.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.33.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.33.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.33.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.33.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.34.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.34.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.34.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.34.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.35.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.35.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.35.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.35.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              }
            ]
          }
        },
        "dora": {
          "estimated_full_hours": 11.286698907714955,
          "load_seconds": 6.290846583084203,
          "adapter_seconds": 2.3824966839747503,
          "per_gpu": {
            "GPU_UUID": {
              "peak_allocated_bytes": 8620017664,
              "peak_reserved_bytes": 8812232704
            },
            "GPU_UUID": {
              "peak_allocated_bytes": 8601720832,
              "peak_reserved_bytes": 8730443776
            }
          },
          "max_process_rss_bytes": 5503205376,
          "sample_count": 8,
          "adapter_validation": {
            "status": "verified",
            "saved_tensor_count": 432,
            "exact_loaded_value_match": true,
            "adapted_module_count": 144,
            "magnitude_vector_count": 144,
            "modules": [
              {
                "name": "base_model.model.model.layers.0.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.0.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.0.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.0.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.1.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.1.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.1.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.1.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.2.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.2.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.2.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.2.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.3.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.3.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.3.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.3.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.4.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.4.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.4.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.4.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.5.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.5.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.5.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.5.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.6.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.6.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.6.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.6.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.7.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.7.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.7.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.7.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.8.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.8.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.8.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.8.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.9.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.9.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.9.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.9.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.10.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.10.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.10.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.10.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.11.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.11.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.11.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.11.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.12.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.12.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.12.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.12.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.13.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.13.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.13.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.13.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.14.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.14.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.14.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.14.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.15.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.15.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.15.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.15.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.16.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.16.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.16.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.16.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.17.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.17.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.17.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.17.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.18.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.18.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.18.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.18.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.19.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.19.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.19.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.19.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.20.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.20.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.20.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.20.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.21.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.21.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.21.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.21.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.22.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.22.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.22.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.22.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.23.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.23.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.23.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.23.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.24.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.24.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.24.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.24.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.25.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.25.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.25.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.25.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.26.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.26.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.26.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.26.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.27.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.27.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.27.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.27.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.28.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.28.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.28.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.28.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.29.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.29.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.29.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.29.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.30.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.30.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.30.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.30.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.31.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.31.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.31.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.31.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.32.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.32.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.32.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.32.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.33.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.33.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.33.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.33.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.34.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.34.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.34.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.34.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.35.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.35.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.35.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.35.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              }
            ]
          }
        }
      },
      "full_three_roles_hours": 21.719121487466392,
      "sampling_only_95pct_hours": [
        19.441184936277633,
        24.19592368878269
      ],
      "load_hours": 0.006081001962269915,
      "caveat": "Stratified timing bootstrap only; excludes contention changes, GPU waiting, interventions and custom-loader work. Not quality evidence."
    },
    "squadv2-8b-greedy-staged": {
      "status": "complete",
      "sample_count": 16,
      "roles": {
        "base": {
          "estimated_full_hours": 3.4534559769391326,
          "load_seconds": 5.998057118966244,
          "adapter_seconds": 0,
          "per_gpu": {
            "GPU_UUID": {
              "peak_allocated_bytes": 8285553664,
              "peak_reserved_bytes": 8296333312
            },
            "GPU_UUID": {
              "peak_allocated_bytes": 8256301056,
              "peak_reserved_bytes": 8292139008
            }
          },
          "max_process_rss_bytes": 4963020800,
          "sample_count": 16,
          "adapter_validation": null
        },
        "lora": {
          "estimated_full_hours": 1.815479463947413,
          "load_seconds": 5.731040434911847,
          "adapter_seconds": 0.6163099970435724,
          "per_gpu": {
            "GPU_UUID": {
              "peak_allocated_bytes": 8383298560,
              "peak_reserved_bytes": 8474591232
            },
            "GPU_UUID": {
              "peak_allocated_bytes": 8317642752,
              "peak_reserved_bytes": 8357150720
            }
          },
          "max_process_rss_bytes": 5585608704,
          "sample_count": 16,
          "adapter_validation": {
            "status": "verified",
            "saved_tensor_count": 288,
            "exact_loaded_value_match": true,
            "adapted_module_count": 144,
            "magnitude_vector_count": 0,
            "modules": [
              {
                "name": "base_model.model.model.layers.0.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.0.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.0.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.0.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.1.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.1.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.1.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.1.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.2.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.2.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.2.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.2.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.3.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.3.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.3.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.3.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.4.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.4.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.4.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.4.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.5.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.5.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.5.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.5.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.6.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.6.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.6.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.6.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.7.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.7.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.7.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.7.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.8.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.8.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.8.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.8.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.9.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.9.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.9.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.9.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.10.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.10.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.10.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.10.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.11.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.11.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.11.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.11.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.12.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.12.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.12.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.12.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.13.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.13.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.13.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.13.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.14.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.14.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.14.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.14.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.15.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.15.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.15.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.15.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.16.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.16.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.16.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.16.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.17.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.17.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.17.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.17.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.18.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.18.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.18.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.18.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.19.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.19.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.19.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.19.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.20.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.20.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.20.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.20.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.21.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.21.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.21.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.21.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.22.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.22.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.22.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.22.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.23.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.23.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.23.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.23.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.24.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.24.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.24.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.24.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.25.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.25.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.25.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.25.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.26.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.26.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.26.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.26.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.27.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.27.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.27.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.27.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.28.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.28.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.28.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.28.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.29.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.29.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.29.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.29.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.30.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.30.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.30.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.30.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.31.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.31.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.31.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.31.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.32.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.32.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.32.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.32.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.33.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.33.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.33.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.33.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.34.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.34.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.34.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.34.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.35.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.35.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.35.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              },
              {
                "name": "base_model.model.model.layers.35.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": false
              }
            ]
          }
        },
        "dora": {
          "estimated_full_hours": 4.873471395242846,
          "load_seconds": 6.645437050960027,
          "adapter_seconds": 1.4737860050518066,
          "per_gpu": {
            "GPU_UUID": {
              "peak_allocated_bytes": 8664162304,
              "peak_reserved_bytes": 8912896000
            },
            "GPU_UUID": {
              "peak_allocated_bytes": 8609778688,
              "peak_reserved_bytes": 8740929536
            }
          },
          "max_process_rss_bytes": 5626208256,
          "sample_count": 16,
          "adapter_validation": {
            "status": "verified",
            "saved_tensor_count": 432,
            "exact_loaded_value_match": true,
            "adapted_module_count": 144,
            "magnitude_vector_count": 144,
            "modules": [
              {
                "name": "base_model.model.model.layers.0.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.0.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.0.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.0.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.1.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.1.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.1.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.1.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.2.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.2.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.2.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.2.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.3.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.3.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.3.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.3.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.4.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.4.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.4.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.4.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.5.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.5.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.5.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.5.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.6.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.6.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.6.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.6.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.7.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.7.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.7.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.7.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.8.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.8.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.8.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.8.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.9.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.9.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.9.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.9.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.10.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.10.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.10.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.10.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.11.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.11.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.11.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.11.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.12.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.12.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.12.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.12.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.13.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.13.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.13.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.13.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.14.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.14.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.14.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.14.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.15.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.15.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.15.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.15.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.16.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.16.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.16.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.16.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.17.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.17.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.17.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.17.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.18.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.18.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.18.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.18.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.19.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.19.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.19.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.19.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.20.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.20.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.20.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.20.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.21.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.21.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.21.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.21.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.22.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.22.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.22.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.22.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.23.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.23.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.23.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.23.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.24.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.24.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.24.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.24.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.25.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.25.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.25.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.25.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.26.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.26.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.26.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.26.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.27.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.27.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.27.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.27.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.28.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.28.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.28.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.28.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.29.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.29.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.29.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.29.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.30.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.30.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.30.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.30.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.31.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.31.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.31.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.31.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.32.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.32.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.32.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.32.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.33.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.33.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.33.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.33.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.34.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.34.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.34.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.34.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.35.self_attn.q_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.35.self_attn.k_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.35.self_attn.v_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              },
              {
                "name": "base_model.model.model.layers.35.self_attn.o_proj",
                "r": 32,
                "alpha": 32,
                "scaling": 1.0,
                "use_dora": true
              }
            ]
          }
        }
      },
      "full_three_roles_hours": 10.14240683612939,
      "sampling_only_95pct_hours": [
        8.68847222461315,
        11.556347186716545
      ],
      "load_hours": 0.005684619613037082,
      "caveat": "Stratified timing bootstrap only; excludes contention changes, GPU waiting, interventions and custom-loader work. Not quality evidence."
    }
  },
  "historical_sampling_predictions_preserved": 483,
  "corrected_predictions_reused": 0,
  "generation_fix": "use_model_defaults=False, do_sample=False",
  "automatic_first_queue": "/path/to/user-user/lora-dora-series/results/first-series-greedy",
  "waiting_time": "Unknown, not included",
  "blocked_loaders": "Answer.AI bases gated; quantized custom and LLaVA loaders not yet timed",
  "four_queues_hours": {
    "first_baseline": 13.113165692143165,
    "mmlu_ready_pair": 2.386703674836166,
    "squad_ready_pair": 7.477339897726617,
    "qwen8b_two_gpus": 31.861528323595785
  },
  "first_interventions_budget": "22 additional jobs; no direct full-model intervention timing yet. Cannot call this a measured total."
}
```

## 2026-10-09: first queue has resumed; P2P diagnosis and corrected timing

First logical queue now actually RUNNING, PID 3794009, retained GPU5
GPU_UUID, job gsm8k-quality-greedy, phase full/base.
All three corrected smoke roles completed. Quality output root:
/path/to/user-user/lora-dora-series/results/first-series-greedy.
After matched base/LoRA/DoRA it automatically runs the prespecified 22 interventions
on the same retained GPU, with no wait for free cards between workers.
483 historical sampling predictions remain untouched; zero reused in greedy run.

Completed corrected stratified timing on GPU5, projected full wall inference:
GSM8K/4B 3.669h base +2.584h LoRA +6.860h DoRA =13.113h;
MMLU/4B .527h +.543h +1.317h =2.387h;
SQuADv2/4B 3.306h +1.129h +3.042h =7.477h.
Sampling-only 95pct bootstrap totals: GSM11.721–14.554h, MMLU2.063–2.598h,
SQuAD6.602–8.329h. Samples8/12/16 per role respectively. These are timing
extrapolations, not completed full quality runs; they exclude unknown GPU waiting,
intervention preprocessing and custom-loader work. No advantage in quality inferred.

Initial 8B two-GPU generation did not finish warmup; isolated test found exact
arange(1024) CUDA peer copy corruption even though nvidia-smi topo -p2p reports OK.
Observed on GPU0+1, also prior stalled GPU5+0. No GPU resets/driver changes and
no foreign processes stopped. Process-local host-staged Tensor.to/cuda transfer
fix passes exact peer copy, finite-logits check and two-token Qwen8B generation:
/path/to/user-user/lora-dora-profiling/8b-diagnostic-staged/state.json.
Weights remain on both GPUs, no weight CPU offload/quantization. Host RAM carries
only inter-GPU transfers. CPU signature/idempotence test passed.
Module /path/to/user-user/lora-dora-dual/lora_dora_study/host_staged_transfer.py.
Dual full worker records and verifies staged transfer before model execution.

Independent corrected 8B timing coordinator PID3798276 runs base/LoRA/DoRA for
GSM8K then SQuAD on partially occupied GPU0+1, both extension slots3/4, explicitly
authorized short probes only. First real 8B answers are normal text, finite logits
verified; measured one108-token answer8.132s. First GPU5 no longer held up by8B.
Forecast reporter PID3799174 updates
/path/to/user-user/lora-dora-profiling/corrected-time-forecast.json.
Full 8B queue PID3750344 still waits two genuinely free cards for2x10s initial
checks; max5 simultaneous during8B, max3 original slots, no new training.
SQuAD corrected full/base runs GPU2, PID3785635; MMLU PID3786742 waits initial GPU.
Sources series/dual dirty HEAD6cc5898, exact source hashes in worker summaries.
Do not edit/commit active matched evaluator roots during a three-role run.
Next: finish staged8B timing, publish all four updated forecasts, inspect
first-series full summaries and later no-op/dense fidelity before interpretation.


## gsm8k-quality-greedy / smoke/dora

UTC: 2026-10-09T19:01:56.670898+00:00

```json
{
  "path": "/path/to/user-user/lora-dora-series/results/first-series-greedy/jobs/gsm8k-quality-greedy/smoke-dora-attempt-1",
  "metrics": {
    "author_em": 1.0,
    "final_em": 1.0
  },
  "memory": {
    "peak_allocated_bytes": 8352038400,
    "peak_reserved_bytes": 8501854208,
    "max_process_rss_bytes": 4739604480,
    "available_host_ram_bytes": 769297768448
  },
  "inference_seconds": 17.891178044024855,
  "predictions_completed": 2,
  "full_evaluation": false,
  "versions": {
    "torch": "2.5.1+cu121",
    "transformers": "4.57.1",
    "peft": "0.17.1",
    "safetensors": "0.6.2",
    "accelerate": "1.11.0"
  }
}
```

## gsm8k-quality-greedy / smoke/lora

UTC: 2026-10-09T19:01:27.102922+00:00

```json
{
  "path": "/path/to/user-user/lora-dora-series/results/first-series-greedy/jobs/gsm8k-quality-greedy/smoke-lora-attempt-1",
  "metrics": {
    "author_em": 1.0,
    "final_em": 1.0
  },
  "memory": {
    "peak_allocated_bytes": 8233698816,
    "peak_reserved_bytes": 8260681728,
    "max_process_rss_bytes": 4740554752,
    "available_host_ram_bytes": 769148866560
  },
  "inference_seconds": 10.47257697104942,
  "predictions_completed": 2,
  "full_evaluation": false,
  "versions": {
    "torch": "2.5.1+cu121",
    "transformers": "4.57.1",
    "peft": "0.17.1",
    "safetensors": "0.6.2",
    "accelerate": "1.11.0"
  }
}
```

## gsm8k-quality-greedy / smoke/base

UTC: 2026-10-09T19:01:04.513540+00:00

```json
{
  "path": "/path/to/user-user/lora-dora-series/results/first-series-greedy/jobs/gsm8k-quality-greedy/smoke-base-attempt-1",
  "metrics": {
    "author_em": 0.0,
    "final_em": 1.0
  },
  "memory": {
    "peak_allocated_bytes": 8081647616,
    "peak_reserved_bytes": 8099201024,
    "max_process_rss_bytes": 4735160320,
    "available_host_ram_bytes": 764857745408
  },
  "inference_seconds": 20.407111790962517,
  "predictions_completed": 2,
  "full_evaluation": false,
  "versions": {
    "torch": "2.5.1+cu121",
    "transformers": "4.57.1",
    "peft": "0.17.1",
    "safetensors": "0.6.2",
    "accelerate": "1.11.0"
  }
}
```

## shadow_4b_mmlu / smoke/dora

UTC: 2026-10-09T19:00:44.092485+00:00

```json
{
  "path": "/path/to/user-user/lora-dora-series/results/extra-series-greedy/jobs/shadow_4b_mmlu/smoke-dora-attempt-1",
  "metrics": {
    "accuracy": 0.0
  },
  "memory": {
    "peak_allocated_bytes": 8349364224,
    "peak_reserved_bytes": 8501854208,
    "max_process_rss_bytes": 4781379584,
    "available_host_ram_bytes": 765273276416
  },
  "inference_seconds": 1.1452447150368243,
  "predictions_completed": 2,
  "full_evaluation": false,
  "versions": {
    "torch": "2.5.1+cu121",
    "transformers": "4.57.1",
    "peft": "0.17.1",
    "safetensors": "0.6.2",
    "accelerate": "1.11.0"
  }
}
```

## Очередь 3 запущена

UTC: 2026-10-09T19:00:34.096007+00:00

```json
{
  "series": 3,
  "pid": 3794009,
  "status": "starting",
  "interval_seconds": 10,
  "required_consecutive_checks": 2,
  "plan_sha256": "083d6b2aa6ec4cdb245dae70fbafa805d8717dbde667975bb9782db476bc8923",
  "estimated_gpu_seconds": 403056.0,
  "retained_gpu_uuid": "GPU_UUID"
}
```

## shadow_4b_mmlu / smoke/lora

UTC: 2026-10-09T19:00:31.798322+00:00

```json
{
  "path": "/path/to/user-user/lora-dora-series/results/extra-series-greedy/jobs/shadow_4b_mmlu/smoke-lora-attempt-2",
  "metrics": {
    "accuracy": 0.5
  },
  "memory": {
    "peak_allocated_bytes": 8233698816,
    "peak_reserved_bytes": 8260681728,
    "max_process_rss_bytes": 4779749376,
    "available_host_ram_bytes": 765971640320
  },
  "inference_seconds": 0.6894373269751668,
  "predictions_completed": 2,
  "full_evaluation": false,
  "versions": {
    "torch": "2.5.1+cu121",
    "transformers": "4.57.1",
    "peft": "0.17.1",
    "safetensors": "0.6.2",
    "accelerate": "1.11.0"
  }
}
```

## Очередь 1 запущена

UTC: 2026-10-09T18:53:07.763864+00:00

```json
{
  "series": 1,
  "pid": 3786742,
  "status": "starting",
  "interval_seconds": 10,
  "required_consecutive_checks": 2,
  "plan_sha256": "29fc7a734e2d0de1c26b5459b88706850409becca9ae1f70659f4a1be7404639",
  "estimated_gpu_seconds": 169200
}
```

## shadow_4b_squadv2 / smoke/dora

UTC: 2026-10-09T18:52:27.700542+00:00

```json
{
  "path": "/path/to/user-user/lora-dora-series/results/extra-series-greedy/jobs/shadow_4b_squadv2/smoke-dora-attempt-2",
  "metrics": {
    "exact": 1.0,
    "f1": 1.0
  },
  "memory": {
    "peak_allocated_bytes": 8357227520,
    "peak_reserved_bytes": 8501854208,
    "max_process_rss_bytes": 4813385728,
    "available_host_ram_bytes": 758539649024
  },
  "inference_seconds": 2.6531166289933026,
  "predictions_completed": 2,
  "full_evaluation": false,
  "versions": {
    "torch": "2.5.1+cu121",
    "transformers": "4.57.1",
    "peft": "0.17.1",
    "safetensors": "0.6.2",
    "accelerate": "1.11.0"
  }
}
```

## Очередь 2 запущена

UTC: 2026-10-09T18:52:12.808260+00:00

```json
{
  "series": 2,
  "pid": 3785635,
  "status": "starting",
  "interval_seconds": 10,
  "required_consecutive_checks": 2,
  "plan_sha256": "29fc7a734e2d0de1c26b5459b88706850409becca9ae1f70659f4a1be7404639",
  "estimated_gpu_seconds": 140400,
  "retained_gpu_uuid": "GPU_UUID"
}
```

## 2026-10-09: correction superseding resume-of-483 plan

During 8B timing a CUDA sampling assertion exposed a real generation bug:
Transformers4.57.1 _prepare_generation_config inherits Qwen checkpoint defaults
(transformers_version4.51.0), changing GenerationConfig(do_sample=False) to
true when use_model_defaults is omitted. Both 4B and8B base checkpoint configs
have do_sample=true. Previous reported requested configuration did not reflect
this effective sampling. Old partial quality and timing are preserved but are
NOT greedy matched evaluation or valid greedy runtime forecasts. The 483 base
answers cannot be appended to a corrected greedy evaluation. They are not erased.

Actual generation now explicitly passes use_model_defaults=False,do_sample=False
in series_worker.py and profile_short.py, including warmup. A tiny CPU Qwen3 test
reproduces old behavior, verifies effective corrected config and deterministic
outputs across seeds: /path/to/user-user/lora-dora-profiling/greedy-config-test.log.

GPU5 coordinator PID 3779128 /path/to/user-user/lora-dora-profiling/hold_profile_greedy.py
retains CUDA context, GPU lock, original slot, and VRAM. It repeats corrected
4B GSM8K/MMLU/SQuAD and 8B GSM8K/SQuAD stratified short timing, then automatically
executes first-series plan on SAME retained GPU: new three-role quality job
(gsm8k-quality-greedy), then previously planned interventions. New root:
/path/to/user-user/lora-dora-series/results/first-series-greedy.
No-op compares to this corrected DoRA baseline. Source original checkout remains
93cd828184c422628e867a1f4946fdeef4d5e917, all old files retained. Original base
resume wrapper is superseded for this correction and will NOT append old rows.

SQuAD old sampling worker3762861 stopped; replacement queue3779924 keeps GPU2.
New extra root /path/to/user-user/lora-dora-series/results/extra-series-greedy.
MMLU restarted at same new root, only initial idle two consecutive10s checks.
Initial cooperative lease conflict now retries initial admission, never a wait
inside an acquired queue. Other users' processes untouched. GPU5/GPU2 handovers
confirmed replacement CUDA contexts before terminating old holders; delayed
VRAM cleanup is handled before reservation allocation. Cooperative locks do not
reserve cards against unrelated users.

Source series/dual changes are dirty on HEAD6cc5898; source_sha256 captures exact
files. Do not commit/edit running source until all matched roles finish, because
code_revision/source hashes are part of the matching guard. Versions unchanged.
Next: inspect corrected profile states, verify no non-finite logits on8B, confirm
first-series-greedy starts automatically after profiles, publish new forecasts.


## Очередь остановлена

UTC: 2026-10-09T18:49:35.583274+00:00

```json
{
  "series": 1,
  "pid": 3781254,
  "status": "failed_needs_inspection",
  "interval_seconds": 10,
  "required_consecutive_checks": 2,
  "plan_sha256": "29fc7a734e2d0de1c26b5459b88706850409becca9ae1f70659f4a1be7404639",
  "estimated_gpu_seconds": 169200,
  "waiting": {
    "answerai_llama2_100k": "waiting_for_quantized_custom_loader_and_base_access",
    "answerai_llama3_100k": "waiting_for_quantized_custom_loader_and_base_access",
    "llava_7b": "waiting_for_multimodal_loader_projector_images_and_evaluator"
  },
  "finished": [],
  "failed": [],
  "ready": [
    "shadow_4b_mmlu"
  ],
  "timestamp_utc": "2026-10-09T18:49:22.819502+00:00",
  "job": "shadow_4b_mmlu",
  "phase": "smoke",
  "role": "lora",
  "idle_uuids": [
    "GPU_UUID"
  ],
  "stable_idle_uuids": [
    "GPU_UUID"
  ],
  "retained_gpu_uuid": "GPU_UUID",
  "gpu_uuid": "GPU_UUID",
  "command": [
    "/path/to/user-user/.venvs/lora-dora-research/bin/python",
    "scripts/held_gpu_worker.py",
    "scripts/series_worker.py",
    "--job",
    "results/extra-series-greedy/jobs/shadow_4b_mmlu/job.json",
    "--gpu-uuid",
    "GPU_UUID",
    "--role",
    "lora",
    "--output-dir",
    "results/extra-series-greedy/jobs/shadow_4b_mmlu/smoke-lora-attempt-1",
    "--limit",
    "2"
  ],
  "worker_pid": 3781715,
  "error": "Assigned GPU guard refused; inspect conflict instead of waiting or switching cards"
}
```

## shadow_4b_mmlu / smoke/base

UTC: 2026-10-09T18:49:35.129636+00:00

```json
{
  "path": "/path/to/user-user/lora-dora-series/results/extra-series-greedy/jobs/shadow_4b_mmlu/smoke-base-attempt-1",
  "metrics": {
    "accuracy": 0.0
  },
  "memory": {
    "peak_allocated_bytes": 8062791680,
    "peak_reserved_bytes": 8078229504,
    "max_process_rss_bytes": 4778274816,
    "available_host_ram_bytes": 761531944960
  },
  "inference_seconds": 1.19157540705055,
  "predictions_completed": 2,
  "full_evaluation": false,
  "versions": {
    "torch": "2.5.1+cu121",
    "transformers": "4.57.1",
    "peft": "0.17.1",
    "safetensors": "0.6.2",
    "accelerate": "1.11.0"
  }
}
```

## Очередь 1 запущена

UTC: 2026-10-09T18:49:11.434358+00:00

```json
{
  "series": 1,
  "pid": 3781254,
  "status": "starting",
  "interval_seconds": 10,
  "required_consecutive_checks": 2,
  "plan_sha256": "29fc7a734e2d0de1c26b5459b88706850409becca9ae1f70659f4a1be7404639",
  "estimated_gpu_seconds": 169200
}
```

## Очередь остановлена

UTC: 2026-10-09T18:49:06.151334+00:00

```json
{
  "series": 2,
  "pid": 3779924,
  "status": "failed_needs_inspection",
  "interval_seconds": 10,
  "required_consecutive_checks": 2,
  "plan_sha256": "29fc7a734e2d0de1c26b5459b88706850409becca9ae1f70659f4a1be7404639",
  "estimated_gpu_seconds": 140400,
  "retained_gpu_uuid": "GPU_UUID",
  "waiting": {
    "answerai_llama2_10k": "waiting_for_quantized_custom_loader_and_base_access",
    "answerai_llama3_10k": "waiting_for_quantized_custom_loader_and_base_access"
  },
  "finished": [],
  "failed": [],
  "ready": [
    "shadow_4b_squadv2"
  ],
  "timestamp_utc": "2026-10-09T18:48:40.062343+00:00",
  "job": "shadow_4b_squadv2",
  "phase": "smoke",
  "role": "dora",
  "gpu_uuid": "GPU_UUID",
  "command": [
    "/path/to/user-user/.venvs/lora-dora-research/bin/python",
    "scripts/held_gpu_worker.py",
    "scripts/series_worker.py",
    "--job",
    "results/extra-series-greedy/jobs/shadow_4b_squadv2/job.json",
    "--gpu-uuid",
    "GPU_UUID",
    "--role",
    "dora",
    "--output-dir",
    "results/extra-series-greedy/jobs/shadow_4b_squadv2/smoke-dora-attempt-1",
    "--limit",
    "2"
  ],
  "worker_pid": 3781149,
  "error": "Assigned GPU guard refused; inspect conflict instead of waiting or switching cards"
}
```

## shadow_4b_squadv2 / smoke/lora

UTC: 2026-10-09T18:49:05.600030+00:00

```json
{
  "path": "/path/to/user-user/lora-dora-series/results/extra-series-greedy/jobs/shadow_4b_squadv2/smoke-lora-attempt-1",
  "metrics": {
    "exact": 1.0,
    "f1": 1.0
  },
  "memory": {
    "peak_allocated_bytes": 8233698816,
    "peak_reserved_bytes": 8281653248,
    "max_process_rss_bytes": 4815138816,
    "available_host_ram_bytes": 761605197824
  },
  "inference_seconds": 1.6706256510224193,
  "predictions_completed": 2,
  "full_evaluation": false,
  "versions": {
    "torch": "2.5.1+cu121",
    "transformers": "4.57.1",
    "peft": "0.17.1",
    "safetensors": "0.6.2",
    "accelerate": "1.11.0"
  }
}
```

## shadow_4b_squadv2 / smoke/base

UTC: 2026-10-09T18:48:52.826139+00:00

```json
{
  "path": "/path/to/user-user/lora-dora-series/results/extra-series-greedy/jobs/shadow_4b_squadv2/smoke-base-attempt-1",
  "metrics": {
    "exact": 0.5,
    "f1": 0.6153846153846154
  },
  "memory": {
    "peak_allocated_bytes": 8075113472,
    "peak_reserved_bytes": 8095006720,
    "max_process_rss_bytes": 4816453632,
    "available_host_ram_bytes": 760862093312
  },
  "inference_seconds": 3.2608208210440353,
  "predictions_completed": 2,
  "full_evaluation": false,
  "versions": {
    "torch": "2.5.1+cu121",
    "transformers": "4.57.1",
    "peft": "0.17.1",
    "safetensors": "0.6.2",
    "accelerate": "1.11.0"
  }
}
```

## Очередь 2 запущена

UTC: 2026-10-09T18:48:40.038949+00:00

```json
{
  "series": 2,
  "pid": 3779924,
  "status": "starting",
  "interval_seconds": 10,
  "required_consecutive_checks": 2,
  "plan_sha256": "29fc7a734e2d0de1c26b5459b88706850409becca9ae1f70659f4a1be7404639",
  "estimated_gpu_seconds": 140400,
  "retained_gpu_uuid": "GPU_UUID"
}
```

## 2026-10-09: retained GPU timing and automatic primary resume

User explicitly requested resuming the first queue after timing probes. GPU 5
(GPU_UUID) is retained by coordinator PID 3773893,
/path/to/user-user/lora-dora-profiling/hold_and_profile.py. It holds the GPU lock,
one original global slot, a live CUDA context and 4 GiB VRAM while children run.
Between probes it reserves 14 GiB. These cooperative locks do not bind other users.
A previous holder handoff hit OOM due delayed release of old process VRAM; both
failed holders exited; card was recovered before any foreign process took it.

Completed retained-card stratified timing (24 examples per role): MMLU/4B
base 0.382887 h, LoRA 0.514099 h, DoRA 1.299856 h, total 2.196842 h projected
full inference. SQuADv2/4B base 4.352021 h, LoRA 1.786040 h, DoRA 4.607219 h,
total 10.745280 h. Small timing samples are not quality results.
Reports /path/to/user-user/lora-dora-profiling/{mmlu,squadv2}-4b-retained/state.json.
Two-GPU Qwen3-8B timing is running on GPU 5 + partially occupied GPU 0, explicitly
authorized only for short probes. No foreign process was stopped.

After both 8B timing tasks, coordinator validates exact resume on original two
base smoke examples, then resumes full base from 483 saved predictions, and
runs full LoRA/DoRA, matched comparison, and first-series interventions on GPU 5.
Resume wrapper changes only prefix IO/counters/time accumulation; AST of generation
and example scoring is unchanged. Four CPU tests passed; GPU validation pending.
Original checkout source/HEAD 93cd828184c422628e867a1f4946fdeef4d5e917 preserved.
Wrapper /path/to/user-user/lora-dora-profiling/resume_evaluator.py records its own
hash separately. Source weights/revisions and versions must match saved summary.
Versions: torch2.5.1+cu121, transformers4.57.1, peft0.17.1, accelerate1.11.0.
Next: finish real 8B timing, verify resume-validation.json, confirm base row484+,
and publish updated forecasts for all four queues. Keep first GPU across stages.

## Очередь 1 запущена

UTC: 2026-10-09T18:44:16.460673+00:00

```json
{
  "series": 1,
  "pid": 3775369,
  "status": "starting",
  "interval_seconds": 10,
  "required_consecutive_checks": 2,
  "plan_sha256": "29fc7a734e2d0de1c26b5459b88706850409becca9ae1f70659f4a1be7404639",
  "estimated_gpu_seconds": 169200
}
```

## shadow_4b_squadv2 / smoke/dora

UTC: 2026-10-09T18:30:34.563868+00:00

```json
{
  "path": "/path/to/user-user/lora-dora-series/results/extra-series/jobs/shadow_4b_squadv2/smoke-dora-attempt-1",
  "metrics": {
    "exact": 1.0,
    "f1": 1.0
  },
  "memory": {
    "peak_allocated_bytes": 8358443008,
    "peak_reserved_bytes": 8501854208,
    "max_process_rss_bytes": 4814106624,
    "available_host_ram_bytes": 756405637120
  },
  "inference_seconds": 2.6310003189137205,
  "predictions_completed": 2,
  "full_evaluation": false,
  "versions": {
    "torch": "2.5.1+cu121",
    "transformers": "4.57.1",
    "peft": "0.17.1",
    "safetensors": "0.6.2",
    "accelerate": "1.11.0"
  }
}
```

## shadow_4b_squadv2 / smoke/lora

UTC: 2026-10-09T18:30:19.228442+00:00

```json
{
  "path": "/path/to/user-user/lora-dora-series/results/extra-series/jobs/shadow_4b_squadv2/smoke-lora-attempt-1",
  "metrics": {
    "exact": 1.0,
    "f1": 1.0
  },
  "memory": {
    "peak_allocated_bytes": 8233698816,
    "peak_reserved_bytes": 8281653248,
    "max_process_rss_bytes": 4812468224,
    "available_host_ram_bytes": 755262197760
  },
  "inference_seconds": 1.7147809739690274,
  "predictions_completed": 2,
  "full_evaluation": false,
  "versions": {
    "torch": "2.5.1+cu121",
    "transformers": "4.57.1",
    "peft": "0.17.1",
    "safetensors": "0.6.2",
    "accelerate": "1.11.0"
  }
}
```

## shadow_4b_squadv2 / smoke/base

UTC: 2026-10-09T18:30:06.515507+00:00

```json
{
  "path": "/path/to/user-user/lora-dora-series/results/extra-series/jobs/shadow_4b_squadv2/smoke-base-attempt-1",
  "metrics": {
    "exact": 0.5,
    "f1": 0.6153846153846154
  },
  "memory": {
    "peak_allocated_bytes": 8076328960,
    "peak_reserved_bytes": 8097103872,
    "max_process_rss_bytes": 4812771328,
    "available_host_ram_bytes": 754206056448
  },
  "inference_seconds": 3.198776385979727,
  "predictions_completed": 2,
  "full_evaluation": false,
  "versions": {
    "torch": "2.5.1+cu121",
    "transformers": "4.57.1",
    "peft": "0.17.1",
    "safetensors": "0.6.2",
    "accelerate": "1.11.0"
  }
}
```

## Очередь остановлена

UTC: 2026-10-09T18:29:51.538499+00:00

```json
{
  "series": 1,
  "pid": 3750342,
  "status": "failed_needs_inspection",
  "interval_seconds": 10,
  "required_consecutive_checks": 2,
  "plan_sha256": "29fc7a734e2d0de1c26b5459b88706850409becca9ae1f70659f4a1be7404639",
  "estimated_gpu_seconds": 169200,
  "waiting": {
    "answerai_llama2_100k": "waiting_for_quantized_custom_loader_and_base_access",
    "answerai_llama3_100k": "waiting_for_quantized_custom_loader_and_base_access",
    "llava_7b": "waiting_for_multimodal_loader_projector_images_and_evaluator"
  },
  "finished": [],
  "failed": [],
  "ready": [
    "shadow_4b_mmlu"
  ],
  "timestamp_utc": "2026-10-09T18:29:51.531916+00:00",
  "job": "shadow_4b_mmlu",
  "phase": "smoke",
  "role": "base",
  "idle_uuids": [
    "GPU_UUID"
  ],
  "stable_idle_uuids": [
    "GPU_UUID"
  ],
  "error": "[Errno 11] Resource temporarily unavailable"
}
```

## Очередь 1 запущена

UTC: 2026-10-09T18:19:44.014431+00:00

```json
{
  "series": 1,
  "pid": 3750342,
  "status": "starting",
  "interval_seconds": 10,
  "required_consecutive_checks": 2,
  "plan_sha256": "29fc7a734e2d0de1c26b5459b88706850409becca9ae1f70659f4a1be7404639",
  "estimated_gpu_seconds": 169200
}
```

## Очередь 2 запущена

UTC: 2026-10-09T18:19:44.008010+00:00

```json
{
  "series": 2,
  "pid": 3750343,
  "status": "starting",
  "interval_seconds": 10,
  "required_consecutive_checks": 2,
  "plan_sha256": "29fc7a734e2d0de1c26b5459b88706850409becca9ae1f70659f4a1be7404639",
  "estimated_gpu_seconds": 140400
}
```

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


---

## Очередь 2 запущена

UTC: 2026-10-09T18:07:08.086583+00:00

```json
{
  "series": 2,
  "pid": 3736761,
  "status": "starting",
  "interval_seconds": 10,
  "required_consecutive_checks": 2,
  "plan_sha256": "29fc7a734e2d0de1c26b5459b88706850409becca9ae1f70659f4a1be7404639",
  "estimated_gpu_seconds": 140400
}
```

## Очередь 1 запущена

UTC: 2026-10-09T18:07:08.078600+00:00

```json
{
  "series": 1,
  "pid": 3736760,
  "status": "starting",
  "interval_seconds": 10,
  "required_consecutive_checks": 2,
  "plan_sha256": "29fc7a734e2d0de1c26b5459b88706850409becca9ae1f70659f4a1be7404639",
  "estimated_gpu_seconds": 169200
}
```

## Реализация сохранена

UTC: 2026-10-09T17:57:28.490595+00:00

```json
{
  "implementation_commit_gpu": "6cc5898",
  "implementation_commit_vm": "8fee53e",
  "primary_keeper_pid": 3724102,
  "unchanged_base_evaluator_pid": 3652567,
  "extra_queue_pids": [
    3724281,
    3724282
  ],
  "cpu_tests_passed": 28,
  "original_baseline_head": "93cd828",
  "next_step": "Baseline full -> no-op/dense controls -> rank/symmetry -> radial interventions on retained first GPU"
}
```

# Первая серия: вмешательства и удержание GPU (2026-10-09)

Исходная оценка base/LoRA/DoRA продолжается без изменений evaluator, весов,
версий, generation settings или исходного Git HEAD 93cd828. Управляющий процесс
3586457 заменён; актуальный keeper 3724102; работающий base evaluator
3652567 не останавливался. GPU UUID GPU_UUID
удерживается CUDA keeper (измерено 188 MiB) до конца первой серии.

Ожидание 10 s / две последовательные свободные проверки применяется только
при первоначальном получении карты дополнительной очередью. Затем карта
удерживается между всеми worker-процессами. Перед загрузкой остаётся проверка
чужих процессов; конфликт останавливает очередь для разбора, не переключает
карту и не запускает новый цикл ожидания. CUDA keeper исключается из guard
только при подтверждённом same-user direct-parent PID. Общие GPU/three-slot
locks удерживаются родителем очереди и наследуются workers через pass_fds;
максимум три карты, включая промежутки между заданиями. При принятии уже
работающего original evaluator слот до его завершения держит сам evaluator.
Keeper не является эксклюзивной бронью против действий других пользователей.

Все GSM8K-вмешательства удалены из двух дополнительных очередей. Их 22 задания
теперь в configs/first_series_interventions.json: no-op проверка нового evaluator;
два dense reference (LoRA/DoRA); rank-r=32; адаптивные ранги для 95% и 99%
энергии полного обновления; V/O симметрия; LoRA контроль с тем же относительным
воздействием на выход модуля; 14 magnitude/remove-D абляций по q/k/v/o и группам.
Новые rank/symmetry условия идут перед magnitude/remove-D, после обязательных
контрольных оценок. Первая серия не запускает параллельную четвёртую очередь:
resume_primary_held.py делает exec в serial очередь 3 на той же назначенной GPU.

Rank/SVD считают полное эффективное delta в FP32; DoRA delta включает
(D-I)W0 + DL. По слоям сохраняются спектр, выбранный ранг и доля энергии.
Измеряется ||X(delta-delta_k)^T||² / ||X delta^T||². LoRA контроль ослабляет
собственное rank-r обновление так, чтобы совпала эта относительная ошибка.
Это не единственно возможный контроль и не одинаковая глобальная функциональная
ошибка: входные активации собственного checkpoint различаются, эффекты слоёв
взаимодействуют. Первый калибровочный проход ограничен первыми 128 токенами
первого train-примера; это техническая калибровка, её обобщаемость не установлена.
Test ответы для подбора рангов/масштабов не используются.

Калибровка на GPU: datasets/gsm8k-train-calibration.jsonl, 7473 строки,
OpenAI GSM8K commit 3101c7d5072418e28b9008a6636bde82a006892c,
SHA256 17f347dc51477c50d4efb83959dbb7c56297aba886e5544ee2aaed3024813465.
Dense reference оценивается отдельно, поскольку FP32 сборка с BF16 округлением
не обязана совпасть с PEFT forward. Численная ошибка сборки/logits записывается.
Вмешательства сравниваются со своим полным dense reference, а magnitude/remove-D
с PEFT no-op. Все quality contrast имеют paired CI и joint Holm поправку.

Симметрия: V_l -> c_l V_l, O_l -> O_l/c_l с заранее заданными c=(1/2,1,2)
по номеру слоя. Q/K не меняются: учитываются Q/K RMSNorm, RoPE и GQA Qwen3.
Проверяются logits, argmax и полная quality. Статистика по V: mean absolute
row-norm change и mean(1-cos), Pearson по слоям (PyTorch [out,in], что
соответствует столбцам транспонированной записи). Статистика вычисляется
относительно фиксированной и совместно преобразованной базы. Совместная
смена координат сохраняет rank-r класс; относительно прежней фиксированной
базы это не гарантируется. Слои не являются независимыми обученными повторами.

CPU: 28 тестов на GPU-сервере с CUDA_VISIBLE_DEVICES пустым, включая реальные
PEFT LoRA/DoRA на tiny Qwen3, dense fidelity, V/O logits, rank compression,
matched LoRA impact и запрет повторного ожидания карты. Журнал:
results/cpu-rank-symmetry-tests.log. Численный tiny отчёт:
results/cpu-rank-symmetry-report.json. На synthetic tiny DoRA logits V/O
преобразования совпали точно; dense-vs-PEFT max error 1.155e-7;
корреляция 0.737056 -> 0.021388 (совместная база), -0.585899 (фиксированная).
Это проверка кода на синтетике, не результат на опубликованном checkpoint.
Версии: Python3.12.3, torch2.5.1+cu121, transformers4.57.1, peft0.17.1,
accelerate1.11.0, safetensors0.6.2. Новых зависимостей не устанавливалось.

Две дополнительные очереди начинают MMLU и SQuAD/4B на разных новых картах;
дальше только остальные основные пары. Прокси полной трудоёмкости backlog
69 h и 59 h GPU-time, это не измеренный ETA: семь дополнительных loaders
ещё не validated. Резервные Mistral/PeRL исключены пользователем.

Loader access: results/loader-access-memory.json. Обе Meta Llama базы вернули
401 GatedRepoError при чтении config. Для Answer.AI нужен авторизованный HF
доступ на сервере (никаких токенов в Git/чат), далее восстановление авторской
quantized реализации и проверка тензоров. LLaVA требует своей сборки vision
encoder/projector/non_lora_trainables и matched image evaluator — это задача
реализации, не требование дополнительной информации от пользователя.
Qwen3-8B revision b968826d9c46dd6066d109eabc6255188de91218: индекс содержит
16381470720 bytes тензоров, карта 17171480576 bytes. Остаётся 790009856 bytes
(~0.736 GiB) до CUDA, адаптера и временных tensors. Реальная GPU проба 8B ещё
не выполнена; две карты не объявлены необходимыми. Сначала безопасная проба
одной карты, затем при необходимости BF16 CPU offload либо отдельное решение
о sharding с соблюдением общего лимита трёх карт. Квантизация не меняется молча.

GPU paths: /path/to/user-user/lora-dora-series/results/primary-retention-leased.log;
results/extra-series/series-{1,2}.json; results/first-series-interventions/series-3.json
появится после полной оценки original. Артефакты каждого вмешательства:
results/first-series-interventions/jobs/<id>/{status.json,*/intervention.json,*/summary.json}.
Ошибки не маскировать как завершённые эксперименты. Никаких выводов о
преимуществе DoRA или причине обучения из CPU/корреляционных тестов не следует.

Следующий шаг: следить за полным GSM8K и первыми свободными дополнительными
картами; проверить GPU smoke rank/symmetry после quality baseline и no-op/dense
контролей; разбирать ошибки; реализовать остальные loaders и измерить 8B peak.
Исходный evaluator и окружение не менять до завершения трёх baseline ролей.


---

## Очередь 1 запущена

UTC: 2026-10-09T17:55:12.958650+00:00

```json
{
  "series": 1,
  "pid": 3724281,
  "status": "starting",
  "interval_seconds": 10,
  "required_consecutive_checks": 2,
  "plan_sha256": "399a22912e4b7f2f0f0554f8c376138df3a2c325f64367715773c3b5d7c44694",
  "estimated_gpu_seconds": 248400
}
```

## Очередь 2 запущена

UTC: 2026-10-09T17:55:12.955130+00:00

```json
{
  "series": 2,
  "pid": 3724282,
  "status": "starting",
  "interval_seconds": 10,
  "required_consecutive_checks": 2,
  "plan_sha256": "399a22912e4b7f2f0f0554f8c376138df3a2c325f64367715773c3b5d7c44694",
  "estimated_gpu_seconds": 212400
}
```

## Очередь 2 запущена

UTC: 2026-10-09T17:46:42.058483+00:00

```json
{
  "series": 2,
  "pid": 3714975,
  "status": "starting",
  "interval_seconds": 10,
  "required_consecutive_checks": 2,
  "plan_sha256": "399a22912e4b7f2f0f0554f8c376138df3a2c325f64367715773c3b5d7c44694",
  "estimated_gpu_seconds": 212400
}
```

## Очередь 1 запущена

UTC: 2026-10-09T17:46:42.057239+00:00

```json
{
  "series": 1,
  "pid": 3714974,
  "status": "starting",
  "interval_seconds": 10,
  "required_consecutive_checks": 2,
  "plan_sha256": "399a22912e4b7f2f0f0554f8c376138df3a2c325f64367715773c3b5d7c44694",
  "estimated_gpu_seconds": 248400
}
```

## Очередь 1 запущена

UTC: 2026-10-09T17:44:19.627631+00:00

```json
{
  "series": 1,
  "pid": 3712307,
  "status": "starting",
  "interval_seconds": 10,
  "required_consecutive_checks": 2,
  "plan_sha256": "b7c40f09c982609d66a76a82013e4d812ee4c72e7b3b62856464f03e17a67a5e",
  "estimated_gpu_seconds": 237600.0
}
```

## Очередь 2 запущена

UTC: 2026-10-09T17:44:19.627065+00:00

```json
{
  "series": 2,
  "pid": 3712308,
  "status": "starting",
  "interval_seconds": 10,
  "required_consecutive_checks": 2,
  "plan_sha256": "b7c40f09c982609d66a76a82013e4d812ee4c72e7b3b62856464f03e17a67a5e",
  "estimated_gpu_seconds": 223200.0
}
```

## Подтверждён запуск обеих дополнительных очередей

UTC: 2026-10-09T17:28:27.547060+00:00

```json
{
  "code_commit": "05b3673",
  "series": [
    {
      "series": 1,
      "pid": 3692772,
      "status": "waiting_for_gpu",
      "job": "shadow_4b_mmlu",
      "phase": "smoke",
      "role": "base"
    },
    {
      "series": 2,
      "pid": 3692773,
      "status": "waiting_for_gpu",
      "job": "shadow_4b_squadv2",
      "phase": "smoke",
      "role": "base"
    }
  ],
  "plan_path": "/path/to/user-user/lora-dora-series/configs/two_series.json",
  "next_step": "wait for GPUs; runtime smoke; then full matched evaluation; GSM8K interventions after primary and no-op gate"
}
```

## Очередь 1 запущена

UTC: 2026-10-09T17:27:24.632325+00:00

```json
{
  "series": 1,
  "pid": 3692772,
  "status": "starting",
  "interval_seconds": 10,
  "required_consecutive_checks": 2,
  "plan_sha256": "55b795f0e35404d336017959b2e0a5f744f58925b38081a634444745f5813b64",
  "estimated_gpu_seconds": 404892.0
}
```

## Очередь 2 запущена

UTC: 2026-10-09T17:27:24.615264+00:00

```json
{
  "series": 2,
  "pid": 3692773,
  "status": "starting",
  "interval_seconds": 10,
  "required_consecutive_checks": 2,
  "plan_sha256": "55b795f0e35404d336017959b2e0a5f744f58925b38081a634444745f5813b64",
  "estimated_gpu_seconds": 385848.0
}
```

# Две дополнительные серии: актуальное состояние

Scope: основные пары и вмешательства; Mistral/PeRL исключены пользователем.
Текущий GPU pipeline в `/path/to/user-user/lora-dora-research` не меняется.
Новый checkout `/path/to/user-user/lora-dora-series`, ветка
`research/two-extra-series`. Точный план `configs/two_series.json`.

Две очереди: каждая serial на одной новой свободной GPU, interval 10 s,
2 consecutive idle checks. Общие с primary GPU/three-slot locks. Для primary
между worker переходами приоритет. Максимум 3 GPU across all research.

17 исполняемых заданий (2 пары, DoRA no-op, 14 абляций), 10 в backlog с
явными loader/memory/implementation prerequisites. Не называть backlog
запущенными GPU-экспериментами. Дальнейшая активация требует проверенного кода.

Данные подготовлены только на GPU: MMLU 14042 test и SQuAD 11873 validation;
manifest paths `results/{mmlu,squadv2,gsm8k}-dataset.json`. Все HF revisions,
SHA и adapter tensor checks фиксируются. Исходный GSM8K файл переиспользуется.
Новая PYTHONPATH dependency pyarrow19.0.1 изолирована в отдельном target;
существующая venv не менялась. 22 CPU tests прошли, compileall/CLI прошли.
GPU runtime новых benchmark/intervention ещё не проверен; впереди smoke.

Результаты: `results/extra-series/series-{1,2}.json`,
`results/extra-series/jobs/<job-id>/`, `results/series-{1,2}.log`.
После каждого этапа этот HANDOFF автоматически обновляется с путями/версиями.
Ошибки и неподготовленные jobs требуют разбирательства, blind retry нет.

Подробности/пилотные реальные измерения/распределение —
`docs/reports/2026-10-09-two-extra-series.md`.

Следующий шаг: прочитать live queue states; дождаться новых свободных GPU,
исправлять runtime ошибки на smoke. Не трогать исходную работающую оценку.

---

## История до дополнительных очередей

# Продолжение 2026-10-09: preflight выполнен, пилот ожидает GPU

Этот раздел заменяет устаревшие сведения о готовности среды ниже.

- Исходный VM checkout `/path/to/user/lora-dora-research` и GPU checkout
  `/path/to/user-user/lora-dora-research` были чистыми; stash не требовался.
  Оба обновлены ff-only с `3eb0442` до `4020b26`.
  Рабочая копия этой сессии находится в `Documents/Codex/2026-10-09/dora-lora-https-github-com-kkoottiiaarraa/work/lora-dora-research`.
  `research-user@GPU_HOST`; никаких переустановок или изменений сети.
- Подтверждены 7 RTX A4000 по 16376 MiB, driver 610.57.04. При preflight
  **все 7 GPU имеют чужие compute-процессы**, свободных нет.
  `/path/to/user-user/lora-dora-research/results/preflight-20261009T1525Z.json`
  содержит фактический timestamp `2026-10-09T15:23:10Z`, RAM available
  666174943232 байта, disk free 89623554134016 байт. Scheduler-команды
  squeue/sinfo/qstat/bjobs не найдены; это не доказывает отсутствие правил.
- Существующая venv `/path/to/user-user/.venvs/lora-dora-research`:
  Python 3.12.3, torch 2.5.1+cu121, transformers 4.57.1, peft 0.17.1,
  accelerate 1.11.0, safetensors 0.6.2, HF hub 0.35.3, numpy 1.26.4.
  `pip check` и 10 исходных CPU tests прошли. Torch на VM не ставили.
- `results/download.json` сохранён: база download/cache 782.102 s,
  verification 22.859 s; LoRA 14.648/0.275 s; DoRA 15.304/0.272 s.
  Повторная проверка сохраняется отдельно в `results/reverify-20261009.json`.
- Пользователь явно разрешил отложенный запуск: проверять каждые 10 s,
  запускать после двух подряд свободных проверок одной и той же GPU.
  Реализован `scripts/wait_for_pilot.py`; base/LoRA/DoRA идут serial,
  BF16/batch=1, 2 smoke-примера, merge check. Worker повторяет guard перед
  Torch import; сверяет все загруженные adapter tensors с файлом.
  Чужие процессы не останавливать. Общий предел 3 сохранён.
- Подготавливается matched GSM8K evaluator: авторский revision
  `b667348c51e24d21f67c329c5f514f80e2c124d4`, одинаковый prompt для трёх ролей,
  max input 512 / new tokens 256 / thinking=false / greedy / use_cache=false.
  Авторский `run_eval.py` имеет особый boxed prompt/scorer для base; в нашем
  matched протоколе это различие устранено. Авторский scorer fallback берёт
  первое число, поэтому отдельно сохраняется sensitivity scorer последнего
  числа. Оба фиксируются заранее; преимущество не предполагается.
- Waiter активен: PID `3576396`, состояние
  `results/deferred-pilot-20261009T1530Z/waiter.json`, лог
  `results/deferred-pilot-20261009T1530Z.log`. На 61-й проверке (15:38:52 UTC / 18:38:52 Москва) свободных GPU нет.
- Реализованы `scripts/evaluate_gsm8k.py`, `scripts/compare_gsm8k.py` и
  `scripts/continue_after_pilot.py`. После успешного пилота цепочка проверяет
  evaluator на 2 задачах для каждой роли, затем делает 3 полных serial прогона
  (1319 задач каждый), проверяет идентичность входов/версий/параметров/кода,
  сохраняет paired bootstrap CI. Автоматически обновляет HANDOFF после этапов.
  При runtime ошибке прекращает цепочку и записывает диагностику.
  Каталог продолжения: `results/pipeline-20261009T1535Z`, лог одноимённый `.log`.
  PID continuation `3586457`, состояние `waiting_for_pilot`; оба процесса живы.
- Код сохранён коммитами `d3fd304` (pipeline) и `b5f5275` (авторский BF16
  autocast для quality). VM исходный checkout и GPU checkout обновлены до
  `b5f5275`. На GPU сохранён safety stash всех наших промежуточных изменений
  `preserve session changes before continuation b5f5275`; значения файлов
  перед stash побайтно сверены с commit. Stash не применять поверх идентичного
  кода. Git bundle резервной копии: `results/research-continuation.bundle`.
- 17 CPU tests прошли на GPU-host venv: включая настоящий PEFT roundtrip,
  tiny-Qwen3 merge, обнаружение изменённого tensor, отказ от partial/mismatched
  quality и сохранение отрицательной DoRA-LoRA разницы. Compileall и CLI help
  прошли; полный evaluator ещё не проходил GPU runtime.
- Полный test JSONL на GPU: `datasets/gsm8k-matched-v1/test.jsonl`,
  1319 строк, 749738 байт, SHA256
  `3730d312f6e3440559ace48831e51066acaca737f6eabec99bccb9e4b3c39d14`.
  Canonical OpenAI repo revision `3101c7d5072418e28b9008a6636bde82a006892c`.
  Все 8 pinned HF fixtures совпали; равенство полного HF parquet не проверялось.
  Загрузка 0.511 s, подробности в `datasets/gsm8k-matched-v1/manifest.json`.
- Повторная проверка весов успешна: `results/reverify-20261009.json`,
  base verification 42.490 s, adapters 0.319/0.265 s. Исходные timings сохранены.
- Отчёт с командами: `docs/reports/2026-10-09-preflight-and-queue.md`.
- Пилот/полная оценка/вмешательства ещё не выполнены. CPU checks не являются
  инференсом. Следующий шаг: проверить waiter, исследовать первые runtime
  результаты/ошибки; только после валидного пилота запускать качество.

---

## Предыдущее состояние (историческая запись)

# Актуальное состояние исследования

Обновлено 9 октября 2026 года. Основной файл передачи состояния между чатами.
Готовый промпт продолжения: [CONTINUE_RESEARCH.md](CONTINUE_RESEARCH.md).

## Среда и доступ

Пользователь сообщает, что новый чат/окружение Codex уже настроены.
общий GPU-сервер. Агент на GPU-сервере не устанавливается.
Не повторять установку CLI, настройку VPN или разработку инфраструктуры доступа.
проверялась. Amnezia VPN, её Caddy и Docker должны сохраниться.

32 GB NVMe, 500 Mbps. По переданным пользователем измерениям доступно 1.46 GiB
RAM и 25 GB диска, CPU занят на 3–5%; amnezia-awg2 использует около 36.62 MiB
RAM, amnezia-downloads (Caddy) — 12.66 MiB. Исторический максимум занятой памяти
VM оставлял 1.37 GiB доступной RAM. Это данные пользователя, не измерения агента.

с сохранением проверки ключа хоста. Сообщённые семь RTX A4000 по 16 GiB и
их загрузка агентом ещё не проверены. Если новый чат уже сохранил результаты,
прочитать их перед повторными запусками и не перезаписывать.

## Что готово и что ещё нет

Ветка: research/prepare-checkpoint-study.
Origin: https://github.com/kkoottiiaarraa/lora-dora-research.git.
Исходный облачный checkout: /workspace/lora-dora-research.
Получить свежую ветку на VM и GPU, сохранив любые локальные изменения.
Существующий другой репозиторий GPU-сервера не трогать; создать новый checkout.

Готово:
- Контекст, каталог десяти основных пар-кандидатов и резервных Mistral/PeRL.
  Наличие metadata/файлов не равно проверенной совместимости и воспроизведению.
- Проверяемые гипотезы и ограничения выводов в RESEARCH_PROTOCOL.md.
- Pinned manifest Qwen3-4B/GSM8K: revisions, размеры, SHA256 весов,
  около 8.25 GB загрузки; восемь фиксированных smoke-примеров.
- scripts/server_preflight.py, scripts/download_pilot.py, scripts/run_pilot.py
  и pilot_worker.py: диагностика, проверка загрузок, короткая генерация,
  измерение времени/памяти, проверка merge на одном входе/токене.
- NumPy algebra и GPU guards; ранее десять CPU tests прошли.

Ещё не сделано этим агентом:
- Проверка реальных GPU, CUDA/PyTorch, создание GPU-venv, загрузка весов,
  запуск технического пилота. GPU-код ещё может требовать runtime исправлений.
- Полный одинаковый evaluator base/LoRA/DoRA на GSM8K: его нужно реализовать.
  Восемь коротких примеров и 64 generated tokens не являются оценкой качества.
- Интеграция математических операций с реальными PEFT весами, контрольные
  вмешательства, активации и повторная оценка. Есть только математические helper
  functions и протокол, не готовый экспериментальный pipeline.
- Проверка закономерностей на нескольких парах. Новые модели не обучались;
  качество, преимущество DoRA и механизм нами ещё не установлены.

## Исследовательская цель

Понять, когда и за счёт чего конкретные опубликованные DoRA checkpoints
превосходят сопоставимые LoRA. Исследование опирается на готовые пары, не на
собственное первоначальное обучение. Сохранять положительные и отрицательные
сравнения, неизвестные training revisions/seeds и прочие confounds.

Математический аргумент о симметриях показывает неинвариантность корреляции
magnitude/direction; он не доказывает, что авторы неправильно её посчитали,
не опровергает преимущество DoRA и не исключает условную интерпретацию внутри
фиксированной параметризации. Финальные веса и posthoc абляции сами по себе
не идентифицируют причину обучающей траектории. См. исходный контекст и протокол.

## Следующий конкретный шаг

Проверить GPU-сервер, изолированный checkout и фактическое окружение.
Подготовить venv/cache, скачать pinned первый набор и выполнить base/LoRA/DoRA
serial pilot на одной свободной GPU. Исправить runtime ошибки и записать
реальные download/load/attach/inference timings, VRAM, RSS и merge fidelity.
Учитывать scheduler/allocation; не занимать чужие карты и не останавливать процессы.
Общий предел — три GPU одновременно, первым запуском использовать одну.

После пилота: реализовать и проверить полный matched evaluation; затем
вмешательства из протокола и повторение на нескольких сопоставимых парах.
Не выбирать объяснение под заранее желаемый положительный результат.

## Где хранить состояние

Git: код, manifests/revisions, fixtures, протокол, гипотезы, этот HANDOFF,
небольшие итоговые таблицы и отчёты (например docs/reports/).
VM: checkout кода и управление, без больших данных и Torch.
GPU: отдельный checkout, .venv/, cache/, results/ и большие активации/предсказания.
Эти большие файлы исключены из Git; в HANDOFF указывать их пути и идентификаторы.
После этапа фиксировать Git revision, команды, зависимости, результаты,
ограничения и следующий шаг. История чата не заменяет такое состояние.

## Сохранение Git и публикация

Код и состояние сохранены на VM и GPU в ветке research/prepare-checkpoint-study
(код d3fd304/b5f5275; запись состояния 24742b4). GitHub push обычным HTTPS
не выполнен: нет настроенной GitHub write-аутентификации (`could not read Username`).
Сеть/CLI/аутентификация не перенастраивались. Исследовательские фоновые задания
от этого не зависят. Полная резервная копия коммитов — Git bundle в outputs
этой сессии и `results/research-continuation.bundle` на GPU. Следующему чату
использовать существующие checkout и GPU HANDOFF, а не только свежий origin.

Последний подтверждённый snapshot: 15:39:55 UTC / 18:39:55 Москва, waiter
проверка 67, idle_uuids пусто. Continuation ждёт пилот. GPU load/inference,
полная accuracy, вмешательства и дополнительные пары пока не получены.


## Direct timing of 22 first-queue jobs — 2026-10-09T19:48:01.767277+00:00

First greedy GSM8K baseline paused after 199 complete saved predictions. GPU5 retained continuously by coordinator PID3830527 (4 GiB during probes plus CUDA context). Resume wrapper validated on the real GPU: exact text, inputs and metrics match the two-case greedy reference. Frozen series source unchanged; external profiler imports it read-only. Real all-module preparation and four stratified timed questions per job; this is not full quality evaluation and four cases do not yield a within-stratum confidence interval. Current completed jobs: ['gsm8k-unmodified-dora', 'gsm8k-dense-dora', 'gsm8k-dense-lora', 'gsm8k-r32', 'gsm8k-e95']. Current job: gsm8k-e99. Coordinator automatically resumes the primary baseline from its preserved prefix and then the unchanged queue. Sources and artifacts: /path/to/user-user/lora-dora-profiling/{profile_interventions.py,resume_series_worker.py,hold_interventions_resume.py,interventions-direct/}. Status: interventions-direct/{coordinator.json,state.json,resume-validation.json,paused-queue.json}. Next: complete all 22 timing probes, inspect failures, verify baseline resume, and record measured forecasts. No jobs excluded and no foreign processes touched.
