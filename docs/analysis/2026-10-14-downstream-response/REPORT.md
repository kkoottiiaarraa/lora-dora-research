# Проверка downstream response: положительный gate не пройден

Все 96 измерений завершены; 16 вопросов × 3 блока × 2 вмешательства.
CPU8 FP32, 365.86s, peak RSS19.50GiB, GPU0; 144 DoRA modules загружены точно.
Два tiny CPU tests пройдены до модели. Repeat/restoration bitwise;
independent branch telescoping relative error максимум0.000202.

| Блок | Разница attenuation D−scalar | Bootstrap95 | Численный контроль |
|---|---:|---|---|
| 0 | −13.001 | [−17.769,−8.541] | FAIL: floor до31.2% frozen effect |
| 17 | −0.380 | [−2.771,2.070] | FAIL: floor до6.83% frozen effect |
| 35 | +0.160 | [+0.078,+0.252] | PASS: floor0.537% |

Dose ratios проходят заданные[.5,2] во всех случаях. В последнем блоке
радиальное вмешательство действительно сильнее ослабляется относительно
frozen-downstream reference, но разница ниже заранее заданного .25 и это
один из трёх блоков. Primary gate требует двух. **Gate FAIL.**
Ранние frozen effects настолько малы, что их отношения нельзя интерпретировать
как надёжное усиление/ослабление. Не выдавать их отрицательные attenuation
за открытие усиления downstream. Увеличение силы вмешательства задним числом
изменило бы вопрос; не назначено. Mistral confirmation не запускается.

Final RMSNorm denominator почти не меняет средний frozen KL последнего блока:
7.901e−7 dynamic против7.928e−7 source denominator. Здесь различие нельзя
объяснить одной последней нормировкой, но оно не устанавливает уникальный
нейронный механизм и не проверяет accuracy или причинность обучения.
Общий self-repair уже известен; новое общее утверждение не заявляется.

Артефакты: SPEC.md, validation.json, layers.csv, manifest.json.
Полные logits/rows/control records остаются на сервере; private locator вне Git.
Версии/source hashes сохранены в validation. Дальнейшее расширение этой сетки
не обосновано. Следующий неалгоритмический вопрос: роль D на опубликованных
промежуточных checkpoints одной настоящей RL trajectory, а не только endpoint.
