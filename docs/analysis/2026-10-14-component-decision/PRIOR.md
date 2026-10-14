# Точная граница novelty перед новым factorial screen

14 октября2026. Источники проверены до получения новых contrast outputs.

- [DoRA ICML2024](https://arxiv.org/html/2402.09353v3): weight normalization,
  magnitude/direction decomposition, gradient coupling и training granularity
  ablations уже описаны. Возврат конечного m к reference не воспроизводит
  авторскую training ablation и не опровергает её.
- [DeLoRA ICLR2025 appendixC](https://arxiv.org/html/2503.18225v1#A3):
  fixed-magnitude DoRA уже сравнивается при **обучении**. В small image-generation
  setting качество близко, но фиксация m не устраняет learning-rate instability;
  авторы обсуждают counterbalance расходящегося тренда. Общее утверждение
  «m компенсирует direction changes» не наша новизна. Полный HTML appendix
  прочитан; OpenReviewchallenge обойдён доступным arXiv primary, не credentials.
- [DoRAFactors](https://sockeye44.github.io/dorafactors-docs/how-it-works/):
  FP32 magnitude/norm division и near-unity rounding уже известны.
- [Causal abstraction JMLR2025](https://www.jmlr.org/papers/v26/23-0058.html):
  общий вопрос соответствия вмешательств известен. Наша явная факторизация
  не объявляется единственно правильной causal decomposition.

Наши прежние source/fullremoveD preserving V/O gauge результаты показывают
изменение отдельных **rawV/O** вмешательств; их нельзя выдавать за полезное
исправление arbitrary component-pruning policy. В новом тесте все global V/O
операции совместны и gauge invariant в проверяемой scalar группе.

Новый практический вопрос ограничен явно заданным решением: fidelity budget
.001 и actual resetMagnitude действие; можно ли заменить его измерение на
removeD proxy? Положительный случай был бы конкретным эмпирическим ограничением
такой подмены. Не утверждать, что опубликованная статья эту подмену делает.
Отрицательный результат закрывает этот proposed practical witness при заданном
budget; не подбирать другой threshold/representation после просмотра outcomes.
