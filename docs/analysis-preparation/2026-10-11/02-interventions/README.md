# Intervention preparation

Deterministic CPU export of saved GSM8K scores. All differences are right-minus-left fractions; scores lie in [0,1]. All 1319 examples and both author_em/final_em are retained per run. No inference, weights, new p-values or confidence intervals. Existing CI/p/Holm are copied only from the exact saved pair, with independent families of 8/9/3 contrasts (16/18/6 scorer hypotheses). CI scope is test examples conditional on fixed checkpoints. Interactions are exploratory descriptive arithmetic on four aligned runs, without inference or inherited adjustment.

Empty CSV fields represent null; missing_reason explains unavailable statistics. Generated text changes compare SHA256 of exact decoded text, separately from correctness; texts and their hashes are not exported. The compact score table contains no question, gold, generated text or tokens. seconds is per-example inference time; token columns are counts.

Tables: intervention_metrics contains references, paths, targets, means, existing exact-pair statistics and family provenance; paired_transitions contains binary transition counts and separate generated-text change counts; localization_grid enumerates all 2×7×2 cells including availability; localization_interactions contains I_QK/I_VO and four-run provenance; numerical_control_contrasts contains dense-relative rank/matched-impact comparisons and dense-original differences; per_example_scores.csv.gz is a complete long run/example/scorer table. CSV headers define individual fields. validation/checks.json records run hash/completeness/means, pair and four-run fingerprint alignments, counts and family membership checks. manifests/export.json records all source and output SHA256, extractor hash and export UTC.

Reproduce on GPU host CPU (stdlib only, at most two threads):
```bash
OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 python3 /path/to/user-user/lora-dora-profiling/analysis-preparation/2026-10-11/build_interventions.py --output /path/to/user-user/lora-dora-profiling/analysis-preparation/2026-10-11/02-interventions
python3 /path/to/user-user/lora-dora-profiling/analysis-preparation/2026-10-11/build_interventions.py --output /path/to/user-user/lora-dora-profiling/analysis-preparation/2026-10-11/02-interventions --check
scp -r gpu-host:/path/to/user-user/lora-dora-profiling/analysis-preparation/2026-10-11/02-interventions docs/analysis-preparation/2026-10-11/
```

The source-root/distributed-root arguments support relocated source trees. Source artifacts remain unchanged. Integrity errors stop export explicitly. Local VM receives code and compact outputs only; all source scanning, row alignment, hashing and aggregation runs on host CPU.

Column schemas (empty fields are null):

- `intervention_metrics.csv`: `job_id`, `metric`, `actual_reference`, `left_path`, `right_path`, `targets`, `left_mean`, `right_mean`, `difference`, `difference_direction`, `existing_ci95_low`, `existing_ci95_high`, `existing_raw_p`, `existing_holm_p`, `family`, `family_size`, `family_metric_hypotheses`, `n`, `resamples`, `seed`, `ci_adjustment`, `scope`.
- `paired_transitions.csv`: `job_id`, `metric`, `n`, `correct_to_correct`, `correct_to_wrong`, `wrong_to_correct`, `wrong_to_wrong`, `generated_text_changes`, `difference`, `left_path`, `right_path`.
- `localization_grid.csv`: `method`, `target`, `metric`, `status`, `missing_reason`, `job_id`, `reference`, `difference`, `difference_direction`.
- `localization_interactions.csv`: `method`, `interaction`, `metric`, `value`, `n`, `status`, `formula`, `joint`, `single1`, `single2`, `reference`, `run_paths`, `source_families`, `existing_ci95_low`, `existing_ci95_high`, `existing_raw_p`, `existing_holm_p`, `missing_reason`.
- `numerical_control_contrasts.csv`: `job_id`, `metric`, `reference`, `left_path`, `right_path`, `n`, `left_mean`, `right_mean`, `difference`, `difference_direction`, `status`, `existing_ci95_low`, `existing_ci95_high`, `existing_raw_p`, `existing_holm_p`, `family`, `family_size`, `missing_reason`.
- `per_example_scores.csv.gz`: `run_id`, `test_row_index`, `source_id`, `metric`, `score`, `hit_token_limit`, `prompt_truncated`, `input_tokens`, `generated_tokens`, `seconds`, `prompt_sha256`, `input_ids_sha256`.

Units: `score`, means, differences, interaction value and CI endpoints are fractions (no percentage conversion); p-values lie in [0,1]; `n`, family sizes, transition/text-change counts and tokens are integer counts; `seconds` is elapsed seconds. Hash fields are SHA256 hex strings. `test_row_index` is zero-based source order. `source_id` is the retained source identifier. `run_id` is job/role. Flags are Boolean. Paths identify accepted server artifacts.
