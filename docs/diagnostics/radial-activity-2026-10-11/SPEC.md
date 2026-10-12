# Сила радиальных вмешательств: диагностика до новой оценки качества

11 октября 2026. Пользователь явно разрешил начать пункт1 и корректировать
план ради более сильного научного результата. Это новый измерительный этап
после завершённого анализа; его нельзя описывать как уже существовавший
контроль. Он проверяет содержательность вмешательства, а не обещает победу
DoRA или причину обучения. Исходные отчёты/manifest кампании не переписывать.

## Вопрос и разрешённая область

Основной вопрос: насколько отличаются итоговая DoRA, её additive endpoint
без D и endpoint с базовыми нормами; сохраняется ли отличие в BF16 и велико
ли оно относительно всего изменения модели? Сначала Qwen3-4B/GSM8K,
144проекции(36слоёв×Q/K/V/O), уже загруженные pinned веса. Ни новых моделей,
в execution/radial-activity/ и docs/diagnostics/radial-activity-2026-10-11/.
Старые frozenbundle/evaluator/AGENTS/MEMORY/analysismanifest не менять.

## Входы и происхождение

Точные pinned paths/ключи/формы — INVENTORY.md. Downloads manifest:
S/results/shadow_4b_gsm8k-downloads.json. Base revision1cfa9a7208912126459214e8b04321603b3df60c;
DoRA07f6a59c2ab6b36b1cecb5feb66187638202521d. Все432adapter tensors F32,
base BF16. Предыдущая acceptedvalidation: exact_loaded_value_match=true,
144modules/144magnitudes. Использовать сырой F32adapter, не округлять его
доBF16 при чтении. Module stem base_model.model.model.layers.L.self_attn.P;
base stem после удаления base_model.model., далее .weight. Проверять все
144A/B/msets, basekeymap, shapes, scaling32/32=1, отсутствиеpatterns/rslora/
bias/fan_in_fan_out. SHA256 всех используемых весовых файлов проверить на
пути/revisions и список проверенных файлов, но не содержит самих SHA.
Сверить согласованность config/manifest и сохранить hash обоих документов;
не заменять ссылку/имя файла проверкой его содержимого.

## Разделить три объекта

1. Ideal FP32: W0 = загруженная BF16база, переведённая вFP32; L=sB32A32;
   U=W0+L; n=rownorm(U); m=F32сохранённый вектор; g=m/n; WD=diag(g)U.
2. Dense BF16 proxy: округлить каждую ideal матрицу WD/U/Wreset в BF16 и
   сравнить. Это веса materializeddense, не точный PEFTforward.
   L_id=(B(A(I)))^T через дваLinear, как установленныйDoraLinearLayer.forward;
   weight W0.to(FP32), scaledL_id BF16, сумма/n вFP32, g=m/n FP32. Сверить
   BF16(g)==1 — только counterfactualscalarcast: реальныйgвPEFTздесьFP32.

становится существенным для вывода, следующий отдельно сформулированный
этап — короткий runtimeконтроль на реальных calibrationвходах. Настоящий
этап сам полныйmodelforward не запускает.

## Метрики на модуль и по всей области

Сохранить n/m/W0norm min/median/p90/p99/max; signedg−1 иabs(g−1) распределения,
число g==1, g<0, m==0, нулевых/неfiniteнорм. Denom0/неfinite — явнаяошибка,
не eps/скрытыйclamp. Сравнить m с FP32rownorm(W0), BF16округлённойFP32нормой
Эти показатели называть endpoint baseline residuals, а не learnedmovement:
истинный traininginitializer/library/base revision неизвестен.

Определить Wreset=diag(rownorm(W0)/n)U, R=WD−U, Rm=WD−Wreset,
Delta=WD−W0. Сохранить sumsquares W0,L,U,WD,Delta,R,Rm,Wreset−W0 иdot(R,L).
Отдельно R0=(g−1)W0 иGL=gL: sumsquares/crossdot должны восстановить
Delta²=R0²+GL²+2dot(R0,GL). Это full-rankconditioningterm, не то же самое
что весьremoveD effectR. Проверить rowidentity ||R_i||=|m_i−n_i| и
||Rm_i||=|m_i−rownorm(W0_i)| с FP32tolerances, не bitwise equality.
Относительные нормы R/Rm против W0, всегоDelta и L (приzero denom null).
У малости относительно базы не терять возможность большого вклада относительно
всегоадаптерногообновления. Доля||R||²/||Delta||² не обязана лежать[0,1].
Сохранять cancellation/statistics какописательные, без причинного объяснения.

Для dense BF16 WDvsU иWDvsWreset: total/equal/changed элементы, долястрок
полностьюequal, sumsquaresотличия вFP32 над округлёнными значениями, maxabs,
нормы отличия относительноBF16полногоDelta/L и базы. Литерал equality
здесь не означает равенства PEFTфункции. Для quotientcounterfactual: доли
surrogateg (absolute/relative). Сохранять все варианты и обеточкиотсчёта.

Глобальные значения считать из суммsquares/counts, отдельно all/Q/K/V/O;
не усреднять modulepercentages вместо весового итога. Медианы по модулям
можно дать отдельно, подписав unweighted. Рядовыеquantiles не восстанавливать
из modulequantiles: вычислять из сохранённых row-levelarrays или labelmissing.

## Выходы и приёмка

Код analyze_radial_activity.py в execution/radial-activity/. Компактные
outputsв docs/diagnostics/radial-activity-2026-10-11/: module-activity.csv(144),
group-activity.csv(5), validation.json, manifest.json, resource-use.json,
указывает путь/hash/schema. Root пишет FINDINGS.md после проверки чисел.
Не выбирать порог «почтиноль» по удобному результату; сначала непрерывные
величины/exactcounts и сравнение с precision и полнымDelta. Никакихpvalues
по модулям как по независимым обучениям, qualitycorrelations илиновизны.
Для BF16rounding использовать actualcast/nextafter; соседи1асимметричны
(.99609375 и1.0078125), один симметричныйepsthreshold некорректен.

заданное g2/0.5→предсказуемаяscale; perturbation ниже/вышеBF16rounding;
формулыglobalweightednorm иреальная dtypeтрасса; zeroденоминаторявноflag.
проверкаshape/dtype/header/finite иCSVschema. При успехе полный144module
NumPy/PEFT, actuallibrarysourcehash, code/spec/input/outputhash безциклов.
Всеошибки исправлять внеfrozenкода; новыхзависимостей неустанавливать.

После приёмки GSM8K root решает, нужны ли такие же лёгкие измерения двух
других уже имеющихся taskpairs либо runtimeконтроль. Это неавтоматический
Answer.AI/fullquality запуск. Модельагентовgpt-6.1-sol, effort<=xhigh.
