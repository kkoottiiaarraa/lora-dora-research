# Новизна corrective procedure: границы заявки

Проверено13октября2026, доитоговойоценкиvalidation. Отсутствие exact предшественника
не установлено; generic reparameterization/canonicalization не наша новизна.

- [Weight Equalization](https://arxiv.org/abs/1906.04721) использует scale-equivariance
  для cross-layer weight equalization при quantization. Принцип улучшения сжатия
  без изменения исходной функции известен минимум в этой форме.
- [SmoothQuant](https://arxiv.org/abs/2211.10438) переносит quantization difficulty
  между весами и активациями эквивалентным преобразованием. Нельзя заявить
  открытие связи между representation и compression quality.
- [AWQ](https://arxiv.org/abs/2306.00978) использует activation-aware equivalent
  channel scaling для уменьшения ошибки quantization. Поиск scaling поcalibration
  также не новый общий принцип.
- [SVD-LLM](https://arxiv.org/html/2403.07378v2) уже задаёт whitening objective.
  Наш W-SVD —адаптация известного objective кfull update, безавторскогоlayer-wise
  closed-form update. Сравнение не является полной репликациейSVD-LLM илиAIR.
- [PivGa](https://arxiv.org/html/2512.03062v1) использует gauge свободу факторовAB
  при неизменном произведении. Наше преобразование V/O относительноfixedW0
  отличается, но общий canonicalization/compression сюжет уже занят.

Ограниченныйкандидатвклада: показать ошибочность конкретного геометрического
вывода/ресурсного решения дляDoRA-r приfixedW0 и сохраняющей обаablation-endpoints
симметрии; показать процедурноеисправление, которое устойчиво и полезно на новых
вопросах приравномfactor budget. Формулаbase-anchor сама по себе не обеспечиваетB.
Положительныйmicro-KL результат не равно practically useful task accuracy.
NativeDoRA ужекомпактна, поэтомуогромной storage экономии против неё пока нет.

Данныхoriginaltraining trajectories/seeds нет, механизм преимуществаDoRA не
установлен. Статьяо causal training mechanism текущими результатами не поддержана.
Послеvalidation отдельно оценить: статистическаяопределённость, absolute magnitude,
практическийэффект, новизна, независимаярепликация. Не подменять одно другим.
