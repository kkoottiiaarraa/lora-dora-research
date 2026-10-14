# Existing diagnostic export (package C)

CPU-only, Python standard library. Accepted full runs are resolved exclusively from status.json outputs. Spectra and predictions stay on the GPU server; only compact aggregates are copied to the VM. Empty CSV fields mean unavailable, never zero. availability.csv supplies missing reasons for diagnostic categories. No quality interpretation or new uncertainty tests are produced.

Run on server (OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2):

```sh
python3 /path/to/user-user/lora-dora-profiling/analysis-preparation/2026-10-11/build_diagnostics.py --output /path/to/user-user/lora-dora-profiling/analysis-preparation/2026-10-11/03-diagnostics --check
```

resources contains accepted full runs; attempts contains other discovered summaries, error artifacts, cancellations, and the short numerical check. Coverage is the two specified job roots, not every historical campaign or controller log. Inference seconds /3600 are inference GPU-hours only. Bytes are bytes (GiB=2^30 bytes), times seconds, token rate generated tokens/inference seconds. Process maximum RSS and available_host_ram are separate measurements; neither is a campaign cost. Memory peaks are per run, never added. Wall time is missing without explicit start/end. Field names retain recorded memory/load_memory provenance.

rank_modules contains recorded module diagnostics and CPU-derived energy/ranks from saved singular values. Derived denominator is sum of squared saved spectrum per module; it is not model-global energy. rank_job_summary is unweighted min/median/max over available module values, with observed module counts. Activation error is squared output error divided by original update output energy on recorded calibration; it is not quality. matched_impact_checks joins the same module name with gsm8k-r32 and reports absolute difference and relative difference over target (undefined at zero).

numerical_fidelity preserves saved logit errors, argmax agreement and allclose flags. Short V/O cases use dense reference; dense-conversion errors use original adapter. Algebraic symmetry does not imply bitwise equivalence. symmetry_statistics exports only recorded correlations and rank flags; module_transform records retain saved scale parameters, layer_statistic records retain saved layer values; unmeasured fixed-base admissibility remains unknown. Recorded flags are not independent admissibility measurements.

Local verification without server sources: `python3 execution/analysis-preparation/build_diagnostics.py --output docs/analysis-preparation/2026-10-11/03-diagnostics --check --verify-local`.

All CSV column schemas are in manifests/schemas.json. Input hashes cover every read JSON and streamed predictions; output hashes cover tables, schemas, validation and this README. The manifest excludes its own hash. Validation checks complete/full flags, row counts, unique ordered test indices, prediction hash, accepted/planned counts, saved spectrum shape/order/nonnegativity, and energy reproduction. --check fails on any failed check.
