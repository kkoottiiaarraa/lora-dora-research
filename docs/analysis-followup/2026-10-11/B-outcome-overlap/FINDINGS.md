# Совместные изменения правильности: описательный результат

Все repairs/breaks ниже определены относительно original PEFT DoRA на 1319 GSM8K examples. Показатели exploratory и описательные; отдельно обученная LoRA и dense DoRA включены в полный перебор пар.

| Условие | author score | author repairs/breaks | final score | final repairs/breaks |
|---|---:|---:|---:|---:|
| original_DoRA | 0.775588 | 0/0 | 0.777862 | 0/0 |
| trained_LoRA | 0.764973 | 55/69 | 0.767248 | 56/70 |
| dense_DoRA | 0.770281 | 24/31 | 0.771039 | 22/31 |
| remove_D_all | 0.785444 | 39/26 | 0.786960 | 38/26 |
| base_magnitude_all | 0.784685 | 39/27 | 0.786960 | 39/27 |
| r32 | 0.777104 | 30/28 | 0.779378 | 30/28 |
| e95 | 0.777862 | 31/28 | 0.780136 | 32/29 |
| e99 | 0.773313 | 27/30 | 0.774829 | 26/30 |

| Пара | scorer | repairs intersection/union | breaks intersection/union | changed intersection/union | changed Jaccard |
|---|---|---:|---:|---:|---:|
| remove_D_all / base_magnitude_all | author_em | 20/58 | 14/39 | 34/97 | 0.3505 |
| remove_D_all / base_magnitude_all | final_em | 20/57 | 14/39 | 34/96 | 0.3542 |
| remove_D_all / r32 | author_em | 19/50 | 15/39 | 34/89 | 0.3820 |
| remove_D_all / r32 | final_em | 18/50 | 15/39 | 33/89 | 0.3708 |
| base_magnitude_all / r32 | author_em | 15/54 | 16/39 | 31/93 | 0.3333 |
| base_magnitude_all / r32 | final_em | 15/54 | 16/39 | 31/93 | 0.3333 |
| remove_D_all / trained_LoRA | author_em | 23/71 | 15/80 | 38/151 | 0.2517 |
| remove_D_all / trained_LoRA | final_em | 22/72 | 15/81 | 37/153 | 0.2418 |
| remove_D_all / dense_DoRA | author_em | 15/48 | 17/40 | 32/88 | 0.3636 |
| remove_D_all / dense_DoRA | final_em | 15/45 | 17/40 | 32/85 | 0.3765 |
| r32 / e95 | author_em | 16/45 | 14/42 | 30/87 | 0.3448 |
| r32 / e95 | final_em | 16/46 | 14/43 | 30/89 | 0.3371 |
| r32 / e99 | author_em | 11/46 | 13/45 | 24/91 | 0.2637 |
| r32 / e99 | final_em | 11/45 | 13/45 | 24/90 | 0.2667 |


Полный результат: run-summary.csv (16 строк), pairwise-outcomes.csv (56),
overlap.csv (42) и case-patterns.csv.gz (2638; порядок bits в METHOD.md).
Таблица выше перечисляет фиксированные содержательно связанные пары, а не
результаты поиска подгрупп; все пары доступны в полном CSV.

Близкие aggregate scores совместимы с ненулевыми repairs и breaks. Неполные
пересечения показывают различия множеств изменившейся правильности на этих
сохранённых примерах. Это не сравнение текстов, функций или смысловых ошибок,
не доказательство общего или различного механизма и не вывод о роли D при
обучении. Dense сдвиг и отдельно обученная LoRA требуют отдельных интерпретаций;
SVD-vs-original counts нельзя подменять историческими SVD-vs-dense counts.
Нет новых оценок значимости, seed uncertainty или универсальных claims.
