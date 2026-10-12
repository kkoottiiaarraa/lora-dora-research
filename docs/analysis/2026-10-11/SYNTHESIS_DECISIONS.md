# Решения для итогового научного синтеза

11 октября 2026. Авторские решения основного агента; это не новый протокол
сбора данных. Q/C приняты; L/T до завершения приёмки условны. Реализацию CSV
регистра поручить агенту; смысл тезисов и ограничения не изменять при экспорте.

## Схема claim-evidence.csv

Одна строка на L1–L9. Поля: claim_id, source_statement, source_url,
operational_test, evidence_files, effect_and_uncertainty, status,
what_is_not_identified, contribution_type. Источники только реально проверенные
версии из theory-audit/review. Пути evidence_files относительны results/;
числа в текстовых полях с единицами п.п. Никаких training-replication claims.

### L1

Тезис: DoRA разделяет норму и направление; forward и backward с detach следует
различать. Источник DoRA v6 §§4.1–4.3. Проверка: алгебра и сохранённый код
текущей реализации. Статус: структура поддержана; training backward наших
checkpoints не идентифицирован. Evidence theory-audit.md, theory-review.md.
Вклад: проверка известной конструкции, не самостоятельная новизна.

### L2

Тезис SORA: диагональное масштабирование допускает полный delta вне rank r.
Проверка: delta=(D−I)W0+DL и сохранённые spectra. Статус: структура поддержана
в FP32 реконструкции; actual BF16 delta rank не измерен. Evidence
theory-audit.md, spectral-entropy.csv, compression-quality.csv.
Эффект: median E99 rank303.5 против nominal directional rank32, не causal
quality result. Вклад: проверка известного, никакой новизны алгебры.

### L3

Тезис SORA: спектральная энтропия предлагается как объяснение gains; теорема
имеет специальные спектральные предпосылки. Наш тест: сохранить главные части
полного delta, проверить качество. Rank32 final +0.834п.п. против dense,
CI[-0.303,+1.971]; против original +0.152, CI[-0.986,+1.289]. Ideal median H
1.771→1.393nat. Статус: ограничено сильное operational следствие, что весь
исходный спектральный хвост необходим для данной accuracy; причинность
entropy и theorem не проверены/не опровергнуты. Evidence compression-quality.csv,
compression-original-reference.csv, spectral-entropy.csv, component-findings.md.
Усечение меняет несколько свойств сразу; нет активного entropy-only контроля.
Вклад: конкретное ограничение необходимости хвоста, кандидат на дополнение.

### L4

Тезис PoLAR: использование размерности/рост stable rank связан с качеством.
Проверка: только описательное сопоставление retained energy/rank и quality.
Статус: причинная связь неидентифицируема; три thresholds и144modules не
независимые training repeats; stable rank не заменять energy rank/entropy.
Evidence compression-quality.csv, spectral-entropy.csv, theory-audit.md.
E95 point estimate не хуже E99, но это не установленная inverse trend.
Вклад: ограничение переноса описателя на необходимость, не опровержение PoLAR.

### L5

Тезис DeLoRA: freezing magnitude во время обучения может дать близкое качество.
Наш тест иной: posthoc base_magnitude/remove_D-all. Final +0.910п.п. для обоих;
CI соответственно[-0.303,+2.123] и[-0.227,+2.123]. Статус: конечная необходимость
ограничена в нашем checkpoint по pointwise допуску0.5п.п.; авторский training
опыт не воспроизведён. Evidence component-necessity.csv, component-findings.md.
Сохраняется история обучения A/B; весовая численная активность D не измерена.
Вклад: конкретное posthoc наблюдение, не новый принцип freezing.

### L6

Тезисы BiDoRA/DoRAN/LoRA+: переобучение, стабильность и настройки оптимизации
могут объяснять различия методов. Проверка: аудит доступных training metadata.
Статус: неидентифицируемо данными готовых checkpoints; нет training trajectories,
seed repeats, matched tuning, причинного вмешательства в оптимизацию.
Evidence theory-audit.md, limitations.md. Вклад: явная граница выводов.

### L7

Тезис EVA: DoRA не имеет универсального выигрыша. Проверка: все3baseline triples.
GSM8K +1.061п.п.CI[-0.607,+2.729]; MMLU+0.057[-0.406,+0.534]; SQuAD exact
−0.135[-0.480,+0.202], F1−0.266[-0.560,+0.024]. Статус: убедительный выигрыш
DoRA не установлен в нашей выборке; equivalence/доказанный проигрыш также не
установлены. Evidence quality-overview.csv, quality-findings.md.
Вклад: проверка переносимости известного ограничения; не объяснение причин.

### L8

Тезис LoRA-Squeeze/Shortcuts in the Tail: posthoc compression и обучение сразу
на малом rank — разные процедуры. Проверка: действительный дизайн нашей
компрессии и matched LoRA. Статус: различие подтверждено аудитом; pure rank
mechanism неидентифицируем. DIDfinal−0.455п.п.CI[-2.123,+1.213], Holm2p=.895.
Evidence compression-difference-in-differences.csv, matched-control-limitations.json,
theory-audit.md. Matched LoRA — attenuation на1prompt/54tokens, не SVD/matched-rank
training; нет bottom/random-k и независимой partial-reversion серии.
Вклад: ограниченная posthoc проверка, известный метод с контролями.

### L9

DoRA использует magnitude/direction pattern по layers/training steps как
аргумент о большей learning capacity; усиление до инварианта функции отдельно
проверяем нами. Сохранённая
scalar V/O карта допустима algebraically в fixed-base DoRA-r через scaling m;
additive LoRA-r такой гарантии не имеет. Rho0.0972336→0.0913035 при той же базе;
joint-base0.1686408. Dense logits maxerror0 на64коротких входах. Статус:
ограничение функциональной инвариантности конкретной FP32 V-statistic;
training pattern/causality и full PEFT BF16 equivalence не проверены.
Evidence symmetry-scope.md, theory-review.md. FP32precast correlation не
выдавать за измеренную deployed BF16; знак в этом опыте не изменился.
Вклад: узкое mathematical уточнение, generic symmetry не новая идея.

## Локализации и главный рассказ

L принят:1213checks,28effects/8joint/84transitions; все8interactionCI содержат0,
Holm8p=1, ни один localizationCI не исключает0. В REPORT включены все14условий
с обоими scorers и8joint
contrasts с собственными CI/Holm8. Не использовать положительную точку Q и
отрицательную K как установленную специализацию. Если CIinteractions включает0,
итог — insufficient precision для неаддитивности, не доказанная аддитивность.

Главный результат — ограниченная необходимость radial компонентов/хвоста
для средней accuracy конкретного готового решения. Сохранение среднего не
сохранение функции: removeD-all final ломает26 и исправляет38ответов;
baseMagnitude-all ломает27 и исправляет39; тексты меняются542/539из1319.
Не обещать объяснение доказанной победы: убедительной DoRA−LoRA победы нет.

baseline25.172667/interventions105.824969. Это не общий учёт кампании;
пилоты/loads/preparation/cancellations/held time не суммированы. Новый анализ
