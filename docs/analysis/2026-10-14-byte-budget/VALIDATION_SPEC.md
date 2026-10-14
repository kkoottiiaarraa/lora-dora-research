# Фиксированное сравнение хранения на имеющихся 128 development вопросах

14 октября 2026; до новых outputs. Продолжение положительного восьмивопросного
screen. Перечитываем те же сохранённые два archive без изменения рангов,
D, scales, кодека и битности. Повторная подготовка не нужна.

128 вопросов — EXACT набор прежнего joint affine сравнения, cases SHA256
`ae5f38d64a2487018e9e6539f0fc14a87d1ce10343dc66bae86c03ab28f7c749`.
Он исключён из calibration8, но уже использовался в предыдущей разработке;
не называть его новой независимой тестовой выборкой. Новый способ не выбирает
параметры по этим ответам, его два ранга заданы стоимостью и зафиксированы
до screen. Source мог видеть train-вопросы у авторов обучения.

Повторяем только два новых условия, 2×128=256 forwards. Используем сохранённые
исходные logits и 128 KFAC-r8 per-case метрик; не повторять их целиком.
Проверить все 128 target/input hashes и SHA cached logits до новых outputs.
Native4 old calibration + первые4 validation cached logits должны перезагрузиться
побитно. Для четырёх validation inputs проверить factorized native-r32/D floor.
Максимум control RMS <1% minimum mean compression RMS; source restored bitwise.
Все 144 modules/480 source tensors загрузить и принять точно.

Archive header/payload/dtypes/shapes/scales/file sizes проверить заново.
KFAC reference rows должны соответствовать cached source NLL на всех128 inputs.
Сохранить 384 строки (128 reuse +256new), все два сравнения с KFAC и их
paired question bootstrap CI95, sign-flip p с Holm2 (10000 повторов).
Предварительный практический критерий — KL ниже минимум20% против KFAC при
обоих byte costs <=23,592,960. Не заменять full accuracy малым token argmax.

CPU16 FP32 SDPA, GPU нет, 30min защитный timeout. Это оценка storage/fidelity,
не запуск нового алгоритма и не основание объявлять B. При технической ошибке
чинить по факту; при отрицательном качестве не расширять сетку.
