# Независимая приёмка A/B/C

Read-only проверка новых outputs существующих scores. Не писать статью,
paper outline, новый протокол GPU-экспериментов, новые p-values вне указанного
ТЗ. Владелец ревьюера только execution/existing-data-followup/verify_followup.py
и docs/analysis-followup/2026-10-11/acceptance/. Основной SPEC неизменяемый input.
Вычисления CPU gpu-host <=2threads; VM только чтение/код/малыефайлы.

Не запускать execution/scientific-analysis/verify_analysis.py: он ПИШЕТ старые
analysis-manifest.json/integration-validation.json. Все frozen inputs/artifacts
и outputs A/B/C только читать. По найденным дефектам сообщать автору/root,
не чинить самостоятельно чужие файлы. NoGPU/weights/model-forward/install.

1. Сверить selected input hashes каждого нового пакета с текущими файлами
   и frozen bundle/accepted manifests. Проверить code/output hashes, версии,
   counts, наличие всех outputs, отсутствие пути rawdraws на VM. Проследить,
   что original AGENTS/MEMORY и accepted historical analysis не изменились
   относительно своих manifest. HANDOFF/MEMORY_CONTINUATION/SPEC новые input,
   не менять их ради совпадения старой истории.
2. Из frozen per-example scores независимо получить полные aligned vectors
   1319 по source_id, index, prompt/input hashes, обоим scorers. Без вызова
   функций build_A/B/C; verifier использует собственные простые формулы.
3. A: независимо все8 means/transition counts/z-distributions, exact binomial
   McNemar p и Holm8. Сверить hashes/code/seeds50000, воспроизвести pointwise
   bootstrap8 если нужно подтвердить численные интервалы. Null и direction
   toy checks, counts vs frozen accepted transitions. Проверить исключение
   seed-level/general method superiority в FINDINGS.
4. B: все16summary/56pairwise/42overlap строки пересчитать из aligned scores,
   включая original-DoRA reference, union/intersection/NaN empty convention,
   направленность mean difference. Проверить casepatterns и все margins.
   Не называть совпадение correctness совпадением текстов/функций.
5. C: полный exact inventory40+6, original/dense references, means/historical
   CI literal preservation. Из server raw50k×46 draws (SHA/shape/order в
   metadata) независимо проверить pointwise quantiles, max-abs95 critical,
   simultaneous bounds и все .5/1/2ppflags. Проверить общие resamples по
   documented construction/code/fixtures; можно воспроизвести initial chunk
   по seed и patterns. Не выдавать >=95% empirical inclusion of bootstrap
   draws за истинную frequentist coverage. Проверить scope семьи46 и её
   отличие от8A, отсутствие формальной equivalence/pre-registered NI claims.
6. Все9claims: совпадают original IDs/statements/status как historical;
   новые observations ссылаются на существующие outputs, L5 закрывает прежнее
   activity ограничение, но сохраняет training/independence/specificity gaps.
   Существенные выводы C/FINDINGS пересчитать и проверить прямые цитаты цифр.
7. Cross-package: одинаковые means/repairs/breaks там, где пары совпадают,
   совпадение source hashes/seeds/scorers. Дополнительные p/CI не наследуют
   чужой scope. Все новые выходы mirrored server/local точными bytes.

Выход acceptance/validation.json (отдельные проверки/errors, явный PASS/FAIL,
не inflated count prose), acceptance/REVIEW.md (scope/limitations/ошибки),
acceptance/manifest.json (hashes inputs/code/outputs, self-exclusions).
Root принимает научный синтез отдельно. Если автор ещё пишет пакет, сначала
проверять завершённые пакеты и дождаться финального SHA перед общей приёмкой.
Для завершения root пишет ANALYSIS_SUMMARY.md и обновляет HANDOFF; статья
и выбор/запуск следующего GPU-плана остаются за рамками этого этапа.
