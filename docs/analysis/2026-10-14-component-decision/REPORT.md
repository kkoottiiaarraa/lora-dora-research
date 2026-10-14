# Объединённое направление: сильной скрытой роли magnitude не найдено

14 октября2026. Выполнена ограниченная проверка роли magnitude/normalization
и связанного с ней решения об упрощении готового адаптера.
**Primary и secondary gates не пройдены.** Validation64/Mistral не запускались
согласно заранее заданной остановке. Ни training, ни новых models, ни GPU.

## Что именно проверено

Для U=W0+sBA: a=||W0||, n=||U||, L=m/a, N=a/n, D=L*N.
Удаление D даёт U; возврат magnitude к исходной norm даёт N*U;
удаление normalization даёт L*U. Есть также два таких же контраста относительно
ar=roundBF16(a). Это явные references; actual training initialization unknown.

Практический сценарий задан нами, не приписан опубликованной работе:
может ли малое KL после удаления D ошибочно разрешить **другую операцию** —
resetMagnitude — при fidelity budget .001 nat/token? Primary gate требует
meanKLremoveD<.001, а meanKLresetMagnitude>.001 в обоих references.
Secondary gate ищет сильную компенсацию: обе отдельные операции>.001 и
как минимум10кратный min separate/jointKL ratio. Пороги заданы до outputs.
Ни один не менялся после результатов. Accuracy — другой estimand.

Global операции охватывают все144q/k/v/o projection. V/O включены совместно:
контрасты инвариантны к нашей scalarVOgauge. Это позволяет сравнивать
одинаковый контрфактический вопрос, а не повторять rawV/O ranking ambiguity.
Уникальной decomposition и инвариантности ко всемсимметриям не заявляем.

## Новые измерения

Qwen3-4B/GSM8K, первые8прежнихcalibration cases,32gold-prefix targets/вопрос,
CPUFP32SDPA. Exploratory development; не новые64inputs и не benchmark generation.

| Операция | Mean teacher KL | Δgold NLL | Argmax changes/256 |
|---|---:|---:|---:|
| Удалить весь D | .000170577 | +.0011934 | 2 |
| Вернуть m к FP32norm(W0) | .000225755 | +.0013157 | 2 |
| Удалить normalization при FP32reference | .000023497 | −.0000351 | 1 |
| Вернуть m к roundedBF16norm(W0) | .000211340 | +.0014424 | 2 |
| Удалить normalization при roundedreference | .000049138 | −.0000832 | 0 |

Все пять вариантов ниже fidelity budget.001. Возврат magnitude имеет KL
в1.32раза выше removeD при FP32reference и1.24раза приroundedreference,
а не на порядок. Отдельный normalization effect меньше joint effect.
В данном screen не появилось ошибочного разрешения resetMagnitude действия
по removeD proxy и не обнаружена сильная скрытая взаимная компенсация.
Это отрицательный результат **этой постановки**, не эквивалентность всей
population и не доказательство, что proxy всегда надёжен.
Bootstrap интервалы в development/validation.json описательные:8cases —
не независимая validation, поэтому ими не заменялся prespecified gate.

## Почему maxima magnitude не помогли найти сильный механизм

В144modules/313344coordinates RMS log(L)=.003847 (~.385%),
RMS log(N)=.000691 (~.069%), RMS log(D)=.003819 (~.382%).
Это fixed-representation descriptions; не causal training attribution.
Log-factor cosine−.130, logDenergy/(logLenergy+logNenergy)=.955.
Identity residual5.30e−8. То есть малый D здесь не возник из почти полного
погашения двух больших opposing factors. Ранее найденные maxrelative deviations
m до9.2% не описывают типичный размер координатных изменений.
Эти weight summaries не заменяют новые функциональные measurements выше.

PeRL/Mistral observations о совпадении storedm с roundedinitial остаются
верными; их объяснение не переносится на Qwen. Само отличие Qwen m от
initialreference также не гарантирует большой endpoint functional effect.

## Проверка уже имеющейся task quality — повторных прогонов нет

Old full1319GSM8K results переиспользованы с проверкой одинаковых prompt/input
hashes. Native1026correct, removeD1038, resetMagnitude1038 поfinalEM.
ResetM против removeD:31вопрос correct только послеresetM и31только послеremoveD;
всего62correctnessdiscordances. Это **уже имевшиеся данные**, не новая находка
и не freshconfirmation. Они не показывают, что resetM сильнее портит качество.
Одинаковая суммарная accuracy не означает одинаковые predictions, эквивалентность
или одинаковую роль компонентов. Family-adjusted old test не подтверждает
преимущества; его не переинтерпретируем как universal safety.
Compact reuse: existing-quality.json и existing-direct-quality.json.

## Техническая приёмка и ресурсы

48rows=8×6conditions, exact432savedtensors/144modules. Два tiny tests factorization,
roundedinitial equivalence иGQA branchgauge пройдены до admission; после
уточнения nontrivialnorm fixture повторныйtinyrun такжеPASS.
17numericalcontrol rows: native/dense2, nativePEFT-vs-dense каждой из5формул
на2cases=10, sourcegauge2×2=4, final restoration1. MaxRMS1.63152e−5;
worst floor/effect0.0796%, ниже1%. Native repeat иrestoration bitwise.
Фактические localsourcehashes совпали с выполненным frozenmanifest.
48metricrows и17controlrows считаются отдельно.

Model wall252.67s (4.21мин), CPU8, peakRSS24.06GiB, GPUhours0.
Torch2.5.1+cu121, Transformers4.57.1, PEFT0.17.1,
Safetensors0.6.2, Accelerate1.11.0. BaseQwen3-4B revision
1cfa9a7208912126459214e8b04321603b3df60c;
DoRAshadow-llm/Qwen3-4B-GSM8k-DoRA revision
07f6a59c2ab6b36b1cecb5feb66187638202521d.
Workerterminal, PIDcheck подтверждает отсутствие работающего component worker;
RAMreleased, holders/waiters/GPUqueues нет. Rawlogits/cases/operationalmanifest
server-only; outerlocal-only/component-decision-20261014/locator-private.json.
Compact percase metrics/controls/modulefactors/source hashes доступны вdevelopment/.

## Научное решение и предел новизны

[PRIOR.md](PRIOR.md) проверяет близкие работы.
[DeLoRA appendixC](https://arxiv.org/html/2503.18225v1#A3) уже исследует
fixed-magnitude **training** и counterbalancing instability. Наш endpoint
screen не подтверждает/неопровергает этот training результат.
L*N algebra, precision risk и общая корректность matching intervention
не объявляются нашей новизной.

Этот cycle **не дал нового практически значимого witness**, способного
поднять материал доB. Объединённая программа в испытанной постановке не получила
основания для большого validation или нового GPUgeneration. Negative gate
не разрешает поиск другого threshold/слоя/кейса ради положительного результата.

Алгоритм сжатия не переоткрыт: конкретного failure сильного compression
comparator, под который строить исправление, этим тестом не установлено.
Следующее изменение research scope требует отдельного обоснованного вопроса;
ещё comparisons техже meanaccuracies или ещё одна кривая m не устранят noveltygap.
Ни статью, ни training/GPUqueue, ни письма, ниагентов в этом запросе не запускали.
