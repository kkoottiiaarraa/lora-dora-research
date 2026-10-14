# LEMS/KFAC-SVD: код, цена переноса и проверка ориентации

14 октября 2026. Прочитаны10целевых файлов авторского репозитория
[lems-svd/lems](https://github.com/lems-svd/lems/tree/9eaf26243562f07c6261da8abbc8787ae655146c),
revision `9eaf26243562f07c6261da8abbc8787ae655146c`. Полный pipeline не запускался.
Ниже результаты чтения кода, а не независимая репликация ICML-результатов.

## Что реально делает pipeline

- [kfac_svd.py](https://github.com/lems-svd/lems/blob/9eaf26243562f07c6261da8abbc8787ae655146c/compression/factorization/kfac_svd.py)
  собирает input Gram и token-wise output-gradient Gram. Для языковых моделей
  градиенты обрезаются по первым/последним12.5%позиций, затем применяются clipping
  и shrinkage. Настройки row/column shrinkage0.3/0.1 не равны нашему ridge0.001.
- [_interface.py](https://github.com/lems-svd/lems/blob/9eaf26243562f07c6261da8abbc8787ae655146c/compression/factorization/_interface.py)
  выполняет backward по autoregressive CE. Это требует градиентных вычислений,
  но сбор статистик без optimizer step сам по себе не является обучением.
- [_sensitivity_base.py](https://github.com/lems-svd/lems/blob/9eaf26243562f07c6261da8abbc8787ae655146c/compression/search/_sensitivity_base.py)
  строит spectral tail curve и масштабирует её по single-layer KL measurement.
- [lems.py](https://github.com/lems-svd/lems/blob/9eaf26243562f07c6261da8abbc8787ae655146c/compression/search/lems.py)
  распределяет бюджет ILP и подбирает два depth coefficients через10Optuna trials
  с полными оценками compressed models. Авторский default использует Gurobi;
  альтернативный CBC не поддерживает все дополнительные ограничения.

Следствие: перенос всей процедуры существенно дороже одного SVD. Её результаты
нельзя приписывать чистой spectral allocation. Перенос к fixed-base DoRA требует
изменить объект сжатия, учёт D и стоимости каждого ранга. До этого наша программа
не является реализацией LEMS.

## Локальная проверка ориентации KFAC

Из кода: `whitening` возвращает нижний фактор `Lg` с `G=Lg Lg^T`, а
[safe_whitened_svd](https://github.com/lems-svd/lems/blob/9eaf26243562f07c6261da8abbc8787ae655146c/all_utils/compression_utils.py)
сжимает `Lg W Lc`, снимая масштабирование слева и справа.

Для стандартного критерия `tr(E^T G E C)`, где `C=Lc Lc^T`, правильное
преобразование — `Lg^T E Lc`. Авторский код вместо этого оптимизирует критерий
с row metric `Lg^T Lg`. Он также положительно определён, но в общем случае
отличается от собранного `G`. Это алгебраический вывод о конкретном коде и
данном соглашении, а не утверждение, что все опубликованные результаты неверны.

Выполнен CPU FP64 тест извлечённой функции автора на100случайных SPD парах,
матрицы4×3, rank1, seed20261014. Отношение ошибки к правильному минимуму по
`tr(E^T G E C)`: min1.000336, mean2.165479, max46.342678.
Первый пример:10.41286865против8.84434977; правильная ошибка совпала со
спектральным хвостом8.84434977. Тест не измеряет качество LLM. Значимость
несоответствия зависит от структуры настоящих ковариаций и shrinkage.

Следующая проверка, если эта ветка понадобится: на реальных covariance matrices
сравнить фактический критерий автора и стандартную KFAC форму, затем проверить
held-out функцию. Не выдавать перестановку transpose за новый алгоритм.

## Новые ближайшие предшественники

[FACTS/CoRS](https://arxiv.org/html/2609.07155v1), §3–4 и Appendix C,
уже рассматривает зависимость compression quality от способа аппроксимации
Fisher: более точный Fisher proxy не обязательно даёт лучшее качество ViT.
Учитывает token-local и activation-gradient coupling. Нельзя заявлять общий
принцип расхождения proxy и accuracy новым.

[Optimal Brain Decomposition](https://arxiv.org/html/2604.00821v1)
тоже использует input/output-gradient covariances и двустороннее взвешивание
SVD для LLM. Сам переход от input-only к двухстороннему критерию известен.
Его наличие не означает готового решения affine `DW0+LR` с fixed base.

Эти источники сужают возможную заявку: интерес представляет конкретная
ошибка/исправление при наших ограничениях, подтверждённая на реальных данных.
Синтетического witness или нового применения известной формулы для B недостаточно.
