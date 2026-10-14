# Один кандидат: radial residual projection после сжатия

Зафиксировано13октября2026 после full-adapter discovery, доcandidate scores.
Пользователь разрешил найти практическую ошибку, затем испытать обоснованное
исправление. Без агентов, обучения, Mistral и scale-grid расширения.

## Основание

При бюджетеordinary-LoRA rank8 (5,898,240elements) full-adapter W-SVD и
fixed-D structural baseline изменяют14/1024teacher argmax; meanKL≈.00192/.00212.
Приrank16 эффекты меньше. Для дальнейшей проверки фиксируем rank8budget
как practically relevant quarter-size target; этот выбор после discovery
явно exploratory. Все baselines/candidate оцениваются заново на новых cases.

Fixed-D baseline сохраняет радиальную часть, подходящую исходному rank32,
при удалении части направления. SourceD не обязана быть оптимальной после
truncation. Проверяем возможность компенсировать только ту часть residual,
которая проецируется на выход frozenbase, без изменения L/R и бюджета.

## Формула, без optimizer/labels

Для каждойпроекции Wteacher,W0,record(d0,L,R),covariance C=X'X/n+lambdaI:
min_d ||(Wteacher−diag(d)W0−LR) C^(1/2)||F².
Решение покомпонентно:
d_j = ((Wteacher−LR)_j C W0_j') / (W0_j C W0_j').
Эквивалентно d=d0+<residual,base>_C/||base||_C². Ridgeтотже.001mean(X²).
FP64calibration arithmetic, FP32deployed diagonal. Одиншаг, L/Rне меняются,
hyperparametersearch/новыхSVDнет. Проверитьmonotonic localobjective;
не считатьего доказательствомлучшейend-to-end функции. Нулевойbase/diagonal
илиnonfinite вызываютstop. Gauge-equivariance вreal arithmetic следует
излинейности поW/LR иcovariance scaling; FP32bitwise claimне делается.

Это closed-formcalibrationprocedure, не новоеобучение. Generic leastsquares/
errorcompensation известны. Новизна частногоDoRA compression применения
не установлена: [SigmaScale](https://arxiv.org/abs/2606.07098) ужеучит scaling
дляSVDcompression, [EoRA](https://arxiv.org/abs/2410.21271) даётlabel-free
eigenspace errorcompensation, [SVD-LLM](https://arxiv.org/abs/2403.07378)
имеетclosed-form recovery. Нашаформула не равноихполнойреализации и сама
посебене обеспечиваетB/A. Отсутствиеexactpriorне доказано.

## Данные и первичное сравнение

Прежниеcalibration64 только длякоэффициентов, безvalidationlabels.
Доcalibration заморозить64новыхtrainquestions:исключитьfirst232,testcontent,
calibration64,generic64,anchor64,budget16,fullscreen32. Старыйprompt/answerfilter.
Всеweights/Qwenrevision/software/CPUFP32SDPA прежние. Native referencefresh,
adapterexact144и4calbitwise checks. 32goldprefix targets наcase.
Сравнения:raw8,W-SVD8,fixed-D structural8, recalibrated8; размерстрогоодинаков.
Primary:recalibrated противfixed-D structural meanteacherKL, pairedwholecase
bootstrap95. Beneficialscreen:>=10%KLreduction иupperCI<0.
Другиеcomparisons иgoldNLL/argmax вторичные; невыдаватьKLзаtaskaccuracy.
Не выбиратьлучшийизнескольких recalibration вариантов:кандидат один.

## Проверки и stop

Unit:known diagonal recovery, closedform versuswhitenedsolution, scale-equivariance,
storage equality. Saved factors безизмененияL/R, identicaldiagonalcosts, finite.
Factorized/dense on2cases:floor<1%compressionRMS. Хранитьsources/cases/factors hashes.
CPU4prepare,CPU16evaluate; deadline3600s; GPU0. НаVMтолькометаданные/stdlibanalysis.
Еслиcandidate не проходитbenefit criterion —отрицательныйисход, безподбора
step sizes/iterations/новыхrankgrid поэтомуvalidation. Еслипроходит —отдельно
оценитьgoldNLL, абсолютнуювеличину, noveltygap и task-levelvalidation необходимость.
