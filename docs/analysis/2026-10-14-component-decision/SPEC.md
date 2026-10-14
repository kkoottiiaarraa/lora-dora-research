# Совместная проверка: смысл радиального вмешательства и решение об удалении

14 октября2026. Задано до новых outputs. Без агентов/обучения/новых weights.

## Вопрос, который объединяет направления

Можно ли малый эффект удаления всего D использовать как основание вернуть
magnitude готового адаптера к исходным нормам? Это разные операции:
U=W0+sBA, a=||W0||, n=||U||, L=m/a, N=a/n, D=LN.
Source=diag(LN)U; removeD=U; resetMagnitude=diag(N)U;
removeNormalization=diag(L)U. Последние две операции могут взаимно компенсироваться.
Это проверка **конечной функции**, не причин обучения. Proxy removeD→resetMagnitude
задаётся здесь явно; не утверждать, что конкретная статья уже использует его.

Практический критерий — сохранить source distribution с mean teacher KL≤.001
nat/token на заданных gold prefixes. Это fidelity budget, не порог безопасности
для task accuracy. Native-vs-native/dense numerical controls отдельно.
«Удалить обученную magnitude» значит resetMagnitude, а не removeD.
При неизвестной training initialization a — явный reference, не доказанный m_init.
Дополнительный reference ar=roundBF16(a) проверяет зависимость от initialization
rounding; для PeRL он точно совпадает с сохранённым m на3steps.

## Известное и реальный пробел

Magnitude/direction split и gradient coupling уже описаны
[DoRA](https://arxiv.org/abs/2402.09353).
[DeLoRA ICLR2025, appendixC](https://openreview.net/forum?id=X1U74IwuxG)
уже сравнивает training with fixed magnitude; это не endpoint intervention.
[DoRAFactors](https://sockeye44.github.io/dorafactors-docs/how-it-works/)
обсуждает precision. [Causal abstraction](https://www.jmlr.org/papers/v26/23-0058.html)
и прежний наш V/O audit ограничивают смысл representation-dependent ablations.
Алгебра L*N и известная симметрия не новые открытия.

Новый bounded question: получается ли на реальных адаптерах неправильное
**разрешение конкретного resetMagnitude действия** по removeD proxy,
воспроизводимое на новых inputs и устойчивое к reference rounding?

## Дизайн и решение до результатов

Stage1: Qwen3-4B/GSM8K pinned как раньше, первые8OLDcalibration cases,
CPU8 FP32 SDPA,32gold targets. Условия6: native, removeD, resetMagnitudeFP32,
removeNormalizationFP32, resetMagnitudeRounded, removeNormalizationRounded.
Веса всех144 q/k/v/o; MLP неизменны. По2case native/dense и formula-vs-native
controls до основных comparisons; repeat/restorationbitwise; finite/exactadapter.

Development primary gate: mean removeD KL<.001, mean resetMagnitude KL>.001
для **обоих references**. Secondary cancellation screen: min(meanKLresetM,
meanKLremoveN)/meanKLremoveD≥10 и обе separate means>.001, обаreferences.
Numeric floor<1% smallest nonzero effects. Если обаgatesFAIL — остановка,
без нового c/layer/threshold grid. Old full1319 GSM accuracy для native,
removeD/resetM переиспользовать; не повторять generation и не объявлять её
новым подтверждением. Full accuracy≈same не заменяет fidelity вопрос.

При positive stage1: заранее замороженная validation64GSMtrain questions,
с исключением test, first232 и **всех обнаруженных прежних own cases collections**
по contenthash. Не отбирать по ответам/эффекту. Раздельный audit восстанавливает
input_ids/targets из pinned dataset/tokenizer. Матрицы/пороги/conditions неизменны.
Primary confirmation: simultaneous Bonferroni95 bounds по3means
(D, resetMFP32, resetMRounded) дают upperD<.001 и обаlowerReset>.001.
Question bootstrap10000, не tokens/seedreplication. Secondary cancellation
report descriptive, не заменить им primarygate послеvalidation.

Только если confirmationpositive: Mistralr16 как заранее заданный отрицательный
контроль m≈roundedinitial,16GSMprefixes, тежеformula/references ипороги;
не искать gauge reversal. PeRL existing16×3step results/math используются
как дополнительный контроль exactroundedm reset no-op, без повторныхforwards.
Если validationnegative — Mistralновыйforward не нужен, публикуетсяfailedgate.

Все global операций совместно включаютV/O, поэтомуинвариантны к прежней
scalarVOgauge: source и removeN сохраняютbranchproduct, resetM послеgauge
имеет теже weights. Это не всехвозможныхsymmetries/уникальнаяcausal decomposition.
Tiny algebra/GQA control до model,sourcegauge checks2cases, без повторного
full no-op прогона. Если новыйproxyошибкинет, не объявлять практическийвклад.

CPU protective cap20min/dev и30min/validation, threads8, RAM preflight≥64GiB.
GPU0, rawlogitsserver-only, operational manifestsprivate. ПоэтапныйHANDOFF.
