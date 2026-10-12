# Проверка заявлений литературы и ближайших вмешательств

Дата: 11 октября 2026. Источники проверены по первичному тексту; это новый
аудит, исходные REPORT/claim-evidence.csv/literature не изменены. Статусы ниже
означают отношение наших данных к конкретному утверждению, а не оценку статьи
целиком. Поиск целевой, не систематический: отсутствие найденного совпадения
не доказывает приоритет.

## Опорные наши данные и новая поправка к реестру

Прочитаны [REPORT](../../analysis/2026-10-11/results/REPORT.md),
[реестр L1–L9](../../analysis/2026-10-11/results/claim-evidence.csv),
[литературный обзор](../../literature/2026-10-11-lora-dora-mechanisms.md),
[новая радиальная диагностика](../../diagnostics/radial-activity-2026-10-11/FINDINGS.md).
Последняя снимает старое ограничение строки L5 «численная активность D не
измерена». Замороженный CSV сохраняет исторический статус; актуальная оценка
ниже уже учитывает диагностику.

В ориентации W[out,in]: U=W0+sBA, D=diag(m/||U_rows||), W_DoRA=DU.
Следует различать три операции:

| Операция | Что остаётся | Какой вопрос проверяет |
|---|---|---|
| Наш posthoc remove_D | U с A/B, обученными внутри DoRA | Нужен ли итоговый коэффициент D для данного конечного качества? |
| Наш posthoc base_magnitude | diag(||W0_rows||/||U_rows||)U | Нужны ли сохранённые learned m, когда уже выбрано направление U? |
| Frozen m при обучении | Иная история A/B; нормирование U сохраняется | Нужно ли обучать m, чтобы найти хорошее решение? |

remove_D не означает просто frozen m: его эффективная норма равна ||U||,
а не норме базы. Оба наших вмешательства сохраняют историю оптимизации A/B.

На Qwen3-4B/GSM8K remove_D и base_magnitude дают по +0.910 п.п. final EM
относительно original PEFT DoRA; pointwise CI95 соответственно
[−0.227;+2.123] и [−0.303;+2.123]. Допуск потери 0.5 п.п. выбран после сбора.
Это фиксированный checkpoint, без seed uncertainty и без общей гарантии
семейства вмешательств. remove_D меняет 542 текста, исправляет 38 и портит 26
final ответов. Средняя точность и функция — разные объекты.

Удаление D составляет 17.9379% нормы полного обновления в идеальной FP32
реконструкции (3.2177% отношения квадратов норм); reset — 17.9772%.
В dense BF16 изменены 46.713% элементов; отношение норм 21.565%.
CUDA norm-only проверка подтверждает активный FP32 g: g==1 только у 4 строк
из 313344, proxy remove_D/fullDelta=17.93798%. Это не новый full-model quality
run и не точное измерение активационного возмущения PEFT. В частности,
гипотеза «весовое вмешательство буквально ничего не сделало» теперь исключена;
гипотеза «сеть терпит любое возмущение такой силы» не проверена.

## 1. DoRA: что действительно утверждалось

**Источник и статус:** Liu et al., *DoRA: Weight-Decomposed Low-Rank Adaptation*,
[ICML 2024, proceedings](https://proceedings.mlr.press/v235/liu24bn.html);
проверенный [текст v6](https://arxiv.org/html/2402.09353v6).

**Заявления и адреса.** §§3.2/4.1, Fig.2 связывают наблюдаемые patterns
magnitude/direction с большей learning capacity. Это мотивирующее объяснение,
не theorem о необходимом сохранении m в готовой модели. §4.2, Eq.6 содержит
касательную проекцию градиента; §4.3, Eq.11 и Appendix A.2/Table7 отсоединяют
норму при backward, убирая эту проекцию, с близкими результатами. §5.6/Table6
уже меняет trainability m/V по группам модулей: направление QKV и magnitude
остальных слоёв могут давать хорошие результаты. Это обучение разных
конфигураций. Abstract/§5 сообщают преимущества на исследованных LLaMA,
LLaVA и VL-BART, не гарантируют победу на любом будущем checkpoint.
[Все адреса — текст статьи](https://arxiv.org/html/2402.09353v6).

**Наш статус: конструкция поддержана, объяснение не идентифицировано.**
Активное posthoc удаление D с близкой accuracy ограничивает необходимость
его сохранения на данном endpoint. Оно не опровергает пользу параметризации
для поиска A/B или устойчивость обучения. Наше отсутствие установленного
выигрыша над LoRA не является отрицательной репликацией авторских задач.
Неинвариантность нашей финальной V-статистики — ограничение её функциональной
интерпретации; исходный pooled pattern по слоям/шагам не воспроизведён.
Backward исторического обучения checkpoints неизвестен.

**Пересечение:** разделение нормы/направления, исследование granularity и
абляция градиента нормирования уже сделаны. Новый вопрос может касаться
проверенной активности и posthoc необходимости именно D; нельзя называть
первым опытом с нормированием или magnitude.

## 2. SORA: сильная интерпретация есть, theorem о качестве нет

**Источник и статус:** Chang et al., *Calibrating and Rotating: A Unified
Framework for Weight Conditioning in PEFT*,
[AAAI 2026 proceedings](https://ojs.aaai.org/index.php/AAAI/article/view/40267),
[финальный PDF](https://ojs.aaai.org/index.php/AAAI/article/download/40267/44228).
Сопоставлен с [v1](https://arxiv.org/html/2511.00051v1).

**Заявления и адреса.** “Analysis and Insights”, Fig.1/2, Theorem1/Remark1,
“Unveiling DoRA” (PDF pp.2–3): entropy полного ΔW объясняет преимущества;
Remark1 называет её возможной основной движущей силой. Введение, метод и
заключение формулируют причинное объяснение увереннее. Theorem1 доказывает
только H_DoRA>H_LoRA для заданных двух-/трёхступенчатых спектров, s>r и
сохранённой энергии minor values. Он не связывает entropy с loss/accuracy и
не доказывает её необходимость. Формула диагонального conditioning и
возможность выхода ΔW за rank r уже опубликованы.
[Источник](https://ojs.aaai.org/index.php/AAAI/article/download/40267/44228).

**Наш статус: структура поддержана; сильное следствие ограничено.**
FP32 ΔW имеет median E99 rank 303.5 при directional r=32. При ideal rank32
median H падает 1.771→1.393 nat, final EM против dense +0.834 п.п.
[−0.303;+1.971]; против original +0.152 [−0.986;+1.289]. Второе сравнение
поддерживает лишь рабочий допуск 1 п.п., не 0.5. Реальный BF16 спектр не
измерен. Весь исходный ideal tail не оказался необходимым для этой средней
accuracy в указанном допуске. Это вызов универсальному переносу объяснения
на необходимость endpoint spectrum; авторы такого универсального theorem
не заявляли. Entropy, norm, directions и rounding изменяются вместе;
entropy-only причинный эффект и training explanation не идентифицированы.

**Отдельный логический пробел текста, не результат нашего quality опыта.**
В “Unveiling DoRA” (финальный PDF p.3) положительность хвоста обосновывается
верхней границей Weyl, σ_i(ΔW)≤σ_1(Wpre(D−I))+σ_i(BAD), i>r.
Верхняя граница не доказывает σ_i>0. Контрпример общему гарантированному
выводу: D=I ⇒ ΔW=sBA с нулевым хвостом выше r. Возможность высокого ранга
остаётся верной; это замечание не опровергает Theorem1 с его отдельными
предпосылками и не доказывает ошибочность измеренных авторами spectra.
[Проверяемое место](https://ojs.aaai.org/index.php/AAAI/article/download/40267/44228).

## 3. DeLoRA: близкое вмешательство уже было при обучении

**Источник и статус:** Bini, Girrbach, Akata, *Decoupling Angles and Strength in
Low-rank Adaptation*, [ICLR 2025 PDF](https://openreview.net/pdf/d26d7ddefe257b94c716d29250bd490d458d2492.pdf),
[текст v1](https://arxiv.org/html/2503.18225v1).

**Заявление и адрес:** Appendix C, Table10/Fig.5 — preliminary fixed-magnitude
DoRA training ablation в subject-driven image generation. DINO 0.681 против
0.683, CLIP-I 0.822 против 0.820: близко по этим метрикам, не однозначно хуже
на обеих. Fixed m не воспроизводит learning-rate robustness DeLoRA; при
высоких learning rates наблюдается дополнительная divergence.
[Appendix C](https://arxiv.org/html/2503.18225v1).

**Наш статус: совместимо, не репликация.** Наш reset готового m и remove_D
проверяют другие контрфактуалы. Нельзя писать «впервые обнаружили, что
обучаемая magnitude не нужна»; нельзя писать «подтвердили DeLoRA robustness».
Активность D усиливает именно наш endpoint вывод, но не превращает его в
training ablation. Ни подтверждения, ни опровержения robustness claim нет.

## 4. EVA: отсутствие универсального преимущества уже видно в таблицах

**Источник и статус:** Paischer et al., *Parameter Efficient Fine-tuning via
Explained Variance Adaptation*,
[NeurIPS 2025 main conference](https://proceedings.neurips.cc/paper_files/paper/2025/hash/41d33bd41fd44bd9dba0e092047cf213-Abstract-Conference.html),
[текст v5](https://arxiv.org/html/2410.07170v5).

**Заявление и адрес:** метод — activation-SVD initialization и rank
redistribution перед/при обучении. Appendix B, Table8 даёт Gemma-2-9B:
GSM8K LoRA 83.4±0.9, DoRA 82.5±0.6; MATH 40.7±0.2 и 39.7±0.4,
три random seeds. Это опубликованные контрпримеры к универсальному ожиданию
победы DoRA, а не отдельный theorem «DoRA не лучше».
[Table8](https://arxiv.org/html/2410.07170v5).

**Наш статус: согласуется с неоднородностью результатов.** У нас ни один
baseline CI DoRA−LoRA не исключает ноль. Это не подтверждённый проигрыш,
не equivalence и не seed-level повторение EVA. Ни теория EVA об ожидаемом
gradient signal, ни преимущество её метода нашими данными не тестируются.
EVA не является prior для нашего конкретного posthoc удаления D, но
предотвращает заявление новизны «DoRA не всегда лучше».

## 5. LoRA-Squeeze: общий compression принцип уже опубликован

**Источник:** Vulić et al., *LoRA-Squeeze: Simple and Effective Post-Tuning and
In-Tuning Compression of LoRA Modules*,
[проверенная v2](https://arxiv.org/html/2602.10993v2), 19 февраля 2026.
Accepted venue данным аудитом не установлен; обозначение — препринт.

**Заявление и адрес:** §1/§3/Algorithms1–2 отделяют высокий training rank от
низкого deployment rank через RSVD; §2 явно оставляет более сложные LoRA
architectures будущей работе. Это не прямой опубликованный DoRA-D ablation.
[Текст](https://arxiv.org/html/2602.10993v2).

**Наш статус: методологическое пересечение, не проверка их превосходства.**
Нельзя объявлять posthoc SVD или различие training/deployment rank новыми.
У нас сжимается полный DoRA ΔW; сжимать только BA означало бы иной объект.
Здесь нет обучения новой LoRA-r32 и доказательства, что она нашла бы такое
решение. Более того, compression evaluated как dense BF16; фактический ранг
BF16-разности и готовый маленький LoRA deployment artifact не проверены.
Поэтому нынешний результат — анализ endpoint, не завершённый эффективный
serving method. В remove_D отключён DoRA dispatcher и оценён обычный
additive LoRA-r32 forward с DoRA-trained A/B: качество этого пути измерено.
Не проверены отдельный сохранённый и повторно загруженный deployment artifact
и обучение LoRA с нуля для поиска того же решения.

## 6. Shortcuts in the Tail: уже есть posthoc полный ΔW с контролями

**Источник:** Sun, Troitskii, *Shortcuts in the Tail: Debiasing via Post-Hoc
Spectral Compression of Fine-Tuning Updates*,
[проверенная v2](https://arxiv.org/html/2606.07596v2), 3 сентября 2026;
[workshop-branded OpenReview PDF](https://openreview.net/pdf?id=4ZSmSVsUjI).
Рукопись указывает ICML 2026 Weight-Space Symmetries Workshop; решение об
acceptance независимо здесь не прочитано (OpenReview browser challenge).
Нельзя обозначать как ICML main conference.

**Заявление и адрес:** §§2–3/Fig.4–5 — posthoc top-k полного full-FT ΔW,
проверка group gap вместе с accuracy, bottom-k/random-k/matched-rank LoRA и
IMDB-marker boundary. Авторы интерпретируют tail как shortcut response
в исследованном поведенческом смысле; не как универсальную бесполезность
малых singular values. [Текст](https://arxiv.org/html/2606.07596v2).

**Наш статус: непосредственный prior общего дизайна, механизм не проверен.**
Наш benchmark EM не измеряет shortcuts, fairness gap или forgetting.
Отсутствуют bottom/random-k и независимый partial reversion control.
Наш matched LoRA — attenuation, подобранная на одном prompt/54 tokens,
а не их matched-rank training. Ни подтверждения их debiasing mechanism,
ни его опровержения нет. Эта работа снижает новизну общего утверждения
«можно отбросить tail полного ΔW и сохранить качество»; специфичность DoRA
остаётся вопросом, требующим дополнительного доказательства.

## 7. Ещё два близких accepted prior для логики компонентного удаления

Shuttleworth et al., *LoRA vs Full Fine-tuning: An Illusion of Equivalence*,
[NeurIPS 2025 main](https://papers.nips.cc/paper_files/paper/2025/hash/ff541950d1e885af90f523571564a401-Abstract-Conference.html),
[проверенная v3 §5/Fig.8/Appendix G](https://arxiv.org/html/2410.21228v3):
масштабируют вплоть до удаления top intruder component **merged weights**,
измеряют downstream accuracy и pretraining loss; контроль — соседний
non-intruder component с похожим singular value. Это уже причинный тест
конкретных весовых компонентов с проверкой специфичности. Наш D не
тождественен intruder; forgetting у нас не измерен. Поэтому generic
«компонент активен, но его можно изменить без падения task score» не новый
принцип, а отсутствие нашего контроля силы заметно на этом фоне.

Sharma, Ash, Misra, *The Truth is in There: Improving Reasoning in Language
Models with Layer-Selective Rank Reduction*,
[ICLR 2024 proceedings](https://proceedings.iclr.cc/paper_files/paper/2024/hash/4c2092ec0b1370cce3fb5965ab255fae-Abstract-Conference.html):
LASER заменяет выбранные готовые weight matrices низкоранговыми
приближениями. Объект — сами веса выбранных слоёв, не DoRA conditioning
и не ΔW; это дополнительный prior post-training spectral intervention,
а не прямая проверка наших утверждений.

## Результат аудита для основного синтеза

| Что можно сказать | Что нельзя приписывать источникам/нашим данным |
|---|---|
| Известная структура DoRA и возможность high-rank ΔW поддержаны | «Мы впервые вывели high rank/conditioning» |
| Удалено активное D, средняя accuracy сохранена в оговорённом допуске одного endpoint | «Magnitude бесполезна при обучении» или «DoRA опровергнута» |
| Снижение ideal entropy совместимо с близкой benchmark accuracy | «Опровергнута theorem SORA» или «entropy точно не помогает» |
| Наблюдение ограничивает сильный перенос spectral explanation на endpoint necessity | «Авторы доказали необходимость tail, и мы это опровергли» |
| DeLoRA — близкий frozen-m training prior, compression papers — близкий posthoc prior | «Никто не замораживал magnitude/не удалял обученные компоненты» |
| Доказанного выигрыша DoRA здесь нет | «Доказано, что LoRA лучше/эквивалентна вообще» |

**Моя оценка, отдельно от буквальных заявлений источников:** наиболее точный
кандидат на добавление — различие между активностью радиального conditioning
и его необходимостью для task score у готовой DoRA, при явно сохранённой
неопределённости о пользе training parameterization. Это узкое наблюдение,
а не установленный новый механизм. Его специфичность относительно generic
robustness, переносимость и приоритет ещё не установлены. Самые существенные
недостающие свидетельства — независимое воспроизведение и контроль
возмущения сопоставимой силы; описание ещё большего числа строк той же модели
не заменяет эти проверки. Этот аудит не авторизует их запуск.
