# Независимая приёмка existing-data followup

Статус: **PASS**. Проверены пакеты A, B, C; 659 отдельных записей проверок, ошибок 0. Полная приёмка A/B/C: True.


A: независимо пересчитаны все восемь means/переходов, exact McNemar, Holm8 и 50000 paired multinomial bootstrap draws с заданными seeds. B: пересчитаны 16 summary, 56 pairwise, 42 overlap строк и все 2638 correctness patterns; проверен общий original-DoRA reference и cross-package пары.

Frozen bundle и исторические analysis outputs/code сверены с собственными manifest. Mutable HANDOFF/MEMORY_CONTINUATION не подгонялись под историю. Новые package inputs/code/outputs сверены по hashes.

Научные границы: exploratory выбор после просмотра данных; uncertainty по оценочным примерам фиксированных checkpoints, не по обучению. Holm8 и семья46 имеют разные scope и не охватывают всю историю поиска. Correctness overlap не устанавливает совпадение текстов/функций/механизма; Q−K не идентифицирует причинную роль Q/K. Posthoc margins не являются preregistered noninferiority и не доказывают equivalence. Будущие эксперименты не запускались.


Независимо получено q95=0.017437452615617893 (1.743745п.п.); construction containment=0.95124. Final remove_D/reset имеют simultaneous lower≈−0.834п.п.: loss threshold1п.п. проходит,0.5п.п. не проходит. r32/E95 против original проходят только2п.п.; final E99 против original не проходит2п.п. Это ограничения силы вывода, не доказательство наблюдаемой потери.


