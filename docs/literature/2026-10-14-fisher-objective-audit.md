# Gold-label Fisher и teacher KL: различие известно, нового метода пока нет

14 октября 2026. Primary-source/code проверка после SORA audit, до возможного
нового компрессора. Новых модельных вычислений этот этап не создаёт.

## Что считали мы и LEMS

Наш `execution/next-experiments/kfac_full_capture.py` делает backward по сумме
CE на 32 gold токенах. Hook собирает Gram выходных activation gradients по
2048 позициям, затем добавляет shrinkage .3. Это KFAC-style **empirical**
gradient metric. Он не является точным Hessian teacher KL.

У [LEMS pinned _interface.py, _run_backward_calib](https://github.com/lems-svd/lems/blob/9eaf26243562f07c6261da8abbc8787ae655146c/compression/factorization/_interface.py#L172)
LLM targets берутся из следующего токена входного текста. В просмотренном
пути нет sampling targets из teacher distribution. Наши clipping/ridge/token
choices отличаются: это не воспроизведение полного LEMS pipeline.

## Точный источник различия

При фиксированном контексте пусть teacher distribution равна p, student logits
отличаются на delta z. В исходной точке:

```
KL(p || softmax(z + delta z))
  = 1/2 delta zᵀ [diag(p) − p pᵀ] delta z + O(||delta z||³).
```

Gold-label outer product использует `(p−e_y)(p−e_y)ᵀ` вместо этой матрицы.
Ожидание по `y ~ p` восстанавливает нужный Fisher в logit space; один заданный
gold label в общем случае этого не делает. Для бинарного logit и gold y=1:
EF=(1−p)², teacher Fisher=p(1−p), EF/F=(1−p)/p.
При p=.99 EF меньше в99раз; при p=.01 больше в99раз.
Это аналитический пример известного различия, не новый эмпирический результат.

Для внутренних активаций применяется downstream Jacobian; causal token
coupling и KFAC factorization добавляют другие приближения. Отделять эти ошибки
от выбора распределения targets. Более точная curvature сама по себе не обещает
лучшей конечной compression quality, особенно при больших perturbations.

## Проверенный приоритет

- [Kunstner, Balles, Hennig, NeurIPS 2019](https://proceedings.neurips.cc/paper/2019/hash/46a558d97954d0692411c861cf78ef79-Abstract.html)
  прямо разбирают отличие empirical Fisher от Fisher/Hessian и ограниченность
  curvature interpretation. Общий контрпример давно известен.
- [Improved Empirical Fisher, NeurIPS 2024](https://proceedings.neurips.cc/paper_files/paper/2024/hash/f23098fa0cfcdef0e743b134d380eeb9-Abstract-Conference.html)
  уже предлагает исправление EF и оценивает его в том числе на LoRA. Это
  optimizer study, не готовый posthoc DoRA compressor; не присваивать её идею.
- [AIR v2, Appendix A.1](https://arxiv.org/html/2606.19993v2#A1.SS1)
  прямо предупреждает об условиях empirical-Fisher curvature interpretation.
  Его основной relevance signal — LRP, не точный teacher-KL Hessian; авторы
  отдельно признают, что дальнейшее уменьшение local objective может ухудшать PPL.
- [FACTS/CoRS, §4.1 и Appendix C](https://arxiv.org/html/2609.07155v1#S4.SS1)
  уже исследует Fisher approximation, token structure и отсутствие гарантии,
  что лучшее совпадение proxy даёт лучшую compression accuracy. Их наблюдение
  нельзя объявить нашим новым thesis, заменив ViT на DoRA в формулировке.

## Решение

Уточнить интерпретацию прежних результатов: joint affine candidate не прошёл
gate при конкретном empirical-KFAC surrogate; это не доказательство оптимальности
всех вариантов сжатия. Существующие отчёты и раньше ограничивали вывод этим
кандидатом, поэтому результаты не аннулируются и заново не пересчитываются.

Не начинать новую Fisher/magnitude grid лишь потому, что обнаружено это
известное различие. Сначала нужен конкретный практический failure сильного
baseline при ясном deployment budget и самостоятельная идея исправления.
В задаче **байтов хранения** предыдущий fixed-D INT8 baseline уже намного
сильнее сложных FP32 rank-reduction методов; смена surrogate не отменяет его.
Если ограничивать rank/операции вместо bytes, это отдельная постановка,
её нужно обосновать до вычислений и сравнивать методы при общей цене inference.

Этот аудит закрывает простую заявку «мы впервые исправили EF на teacher Fisher»
до реализации. Ни нового алгоритма, ни новой подтверждённой заявки на B пока нет.
