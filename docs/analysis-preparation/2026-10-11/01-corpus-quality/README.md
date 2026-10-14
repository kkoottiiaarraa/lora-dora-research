# Corpus and baseline quality export

CPU/stdlib extraction of all status-selected accepted full runs. No new CI, p values or inference. Scores are fractions in [0,1]; differences are right-minus-left. Existing CI/p/Holm are copied with each original comparison family. CI is conditional on fixed checkpoints and evaluation examples, not training seeds. CSV null is the literal `null`; unknown metadata has missing_reason.

Reproduce on GPU host (upload this extractor to the temporary directory first):

```bash
OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 python3 /path/to/user-user/lora-dora-profiling/analysis-preparation/2026-10-11/build_corpus_quality.py --out /path/to/user-user/lora-dora-profiling/analysis-preparation/2026-10-11/01-corpus-quality --check
```


Then copy only 01-corpus-quality back to docs/analysis-preparation/2026-10-11/. Raw predictions stay on the GPU host. --check writes validation and exits nonzero on any failed check. Source paths resolve relative to --source (default /path/to/user-user/lora-dora-series); plans come from --distributed.

Fields: IDs and paths preserve source provenance; *_sha256 are byte hashes, *_fingerprint is SHA256 of canonical sorted JSON. rows/n are example counts; expected/predictions_completed are saved counts. complete/full_evaluation are saved acceptance flags. status is recorded coverage or explicit comparability result. matched/mismatched_fields list required equality checks. original_score is copied from summary; means are deterministic saved-score aggregates. subject micro weights examples, macro weights subjects equally. author_em/final_em rows cover all four binary combinations; token limit counts are separate. resamples/seed/scope/adjustment describe existing statistics only. Family is exactly the original matched-comparison path. No training metadata inferred.

Transition columns correct_correct/correct_wrong/wrong_correct/wrong_wrong are counts of left-to-right binary correctness. Continuous metrics use increase/equal/decrease and have null binary columns. Answerability labels use explicit source answers.text; n is examples in each stratum. attempts.csv contains nonselected full and smoke directories separately; missing summary does not assert failure. dtype comes from the byte-matched saved evaluator source, tokenizer from pinned base snapshot; quantization remains null because not explicitly recorded.

Schemas:

- `attempts.csv` (32 rows): job, attempt_path, phase, accepted, status, reason, summary_path, missing_reason

- `baseline_pair_transitions.csv` (15 rows): job, contrast, metric, left_run, right_run, n, score_type, correct_correct, correct_wrong, wrong_correct, wrong_wrong, increase, equal, decrease, missing_reason

- `squadv2_answerability.csv` (12 rows): run_id, role, metric, answerability, n, mean, source_path, label_rule, missing_reason

- `run_inventory.csv` (29 rows): run_id, job, task, role, intervention, targets, summary_path, predictions_path, status_path, rows, expected_rows, predictions_completed, predictions_sha256, summary_sha256, status_sha256, dataset_revision, base_revision, adapter_revision, dtype, dtype_provenance, quantization, tokenizer, missing_reason, generation_fingerprint, source_fingerprint, versions_fingerprint, complete, full_evaluation

- `coverage.csv` (28 rows): job, planned, status, accepted_full_runs, source_decision, reason, smoke_as_replication

- `comparability.csv` (29 rows): job, contrast, left_run, right_run, matched_fields, mismatched_fields, matched_rows, status, refusal_reason

- `baseline_metrics.csv` (15 rows): run_id, task, role, metric, n, original_score, source_path

- `baseline_contrasts.csv` (15 rows): job, contrast, metric, left_run, right_run, difference_direction, difference, ci95_low, ci95_high, raw_p, holm_p, family, family_size, adjustment, ci_adjustment, n, resamples, seed, scope, source_path, missing_reason

- `mmlu_subject_metrics.csv` (177 rows): run_id, role, aggregation, subject, n, subject_count, metric, mean

- `gsm8k_scorer_agreement.csv` (12 rows): run_id, role, author_em, final_em, n

- `gsm8k_token_limits.csv` (3 rows): run_id, n, max_new_tokens, max_input_tokens, hit_token_limit, prompt_truncated
