#!/usr/bin/env python3
"""Bounded exploratory 46-contrast joint paired bootstrap; existing scores only."""
import os

for _thread_variable in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "BLIS_NUM_THREADS"):
    os.environ[_thread_variable] = "2"
os.environ["CUDA_VISIBLE_DEVICES"] = ""

import argparse
import csv
import gzip
import hashlib
import itertools
import json
import math
from pathlib import Path
import platform
import re
import resource
import sys
import time
from collections import Counter, defaultdict
from datetime import datetime, timezone

import numpy as np

SEED = 2026101160
B = 50000
CHUNK = 256
N = 1319
PREP = Path("docs/analysis-preparation/2026-10-11")
PRIOR = Path("docs/analysis/2026-10-11/results")
ACTIVITY = Path("docs/diagnostics/radial-activity-2026-10-11")
DEST = Path("docs/analysis-followup/2026-10-11/C-robustness")
SPEC = Path("docs/analysis-followup/2026-10-11/SPEC.md")
METRICS = ("author_em", "final_em")
MARGINS = (("0_5pp", .005), ("1pp", .01), ("2pp", .02))
FAMILY = "46 exploratory signed GSM8K accuracy contrasts: 40 historical intervention scorer rows plus 6 compression-original scorer rows"
SCOPE = "paired test examples conditional on fixed checkpoints; not training uncertainty; not the whole adaptive search history; separate from 8 tests A"


def digest(path):
    h = hashlib.sha256()
    with open(path, "rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def load_csv(path):
    with open(path, newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def save_csv(path, rows):
    with open(path, "w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def readable_prose(text):
    text = re.sub(r"([А-Яа-яЁё])(?=[0-9])", r"\1 ", text)
    return re.sub(r"([0-9])(?=[А-Яа-яЁё])", r"\1 ", text)


def save_json(path, obj):
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2, allow_nan=False) + "\n")


class Validation:
    def __init__(self):
        self.checks = []

    def check(self, name, passed, details=None):
        self.checks.append({"name": name, "passed": bool(passed), "details": details})
        if not passed:
            raise ValueError(name + ": " + str(details))


def joint_bootstrap(z, resamples, seed, chunk=CHUNK):
    """All columns share each multinomial draw over their joint row patterns."""
    patterns, frequencies = np.unique(z, axis=0, return_counts=True)
    probabilities = frequencies / len(z)
    rng = np.random.default_rng(seed)
    values = np.empty((resamples, z.shape[1]), dtype=np.float64)
    float_patterns = patterns.astype(np.float64)
    for start in range(0, resamples, chunk):
        stop = min(resamples, start + chunk)
        weights = rng.multinomial(len(z), probabilities, size=stop - start)
        values[start:stop] = weights @ float_patterns / len(z)
    return values, patterns, frequencies


def intervals(draws, mu):
    pointwise = np.quantile(draws, [.025, .975], axis=0, method="linear")
    maximum = np.max(np.abs(draws - mu), axis=1)
    critical = float(np.quantile(maximum, .95, method="linear"))
    simultaneous = np.stack((np.maximum(-1., mu - critical), np.minimum(1., mu + critical)))
    return pointwise, simultaneous, critical, maximum


def toy_validation(v):
    z = np.array([[-1, -1, 0], [-1, -1, 0], [1, 1, 0]], dtype=np.int8)
    direct = Counter()
    for indices in itertools.product(range(3), repeat=3):
        direct[tuple(np.sum(z[list(indices)], axis=0).tolist())] += 1 / 27
    patterns, counts = np.unique(z, axis=0, return_counts=True)
    grouped = Counter()
    for k in range(4):
        count = np.array([k, 3 - k])
        probability = math.factorial(3) / (math.factorial(k) * math.factorial(3 - k))
        probability *= (counts[0] / 3) ** k * (counts[1] / 3) ** (3 - k)
        grouped[tuple((count @ patterns).tolist())] += probability
    v.check("toy exhaustive index resampling equals aggregated multinomial distribution", set(direct) == set(grouped) and max(abs(direct[k] - grouped[k]) for k in direct) < 1e-14, {"index_sequences": 27, "joint_patterns": len(patterns)})
    samples, _, _ = joint_bootstrap(z, 4000, 2026101161)
    point, simultaneous, q, _ = intervals(samples, z.mean(0))
    v.check("toy duplicated columns have identical bootstrap draws and both interval types", np.array_equal(samples[:, 0], samples[:, 1]) and np.array_equal(point[:, 0], point[:, 1]) and np.array_equal(simultaneous[:, 0], simultaneous[:, 1]))
    # A zero column in a nonzero family has the same common simultaneous radius;
    # the all-zero FAMILY is the zero-width check required by the specification.
    zeros = np.zeros((7, 4), dtype=np.int8)
    zero_draws, _, _ = joint_bootstrap(zeros, 200, 2026101162)
    zp, zs, zq, _ = intervals(zero_draws, zeros.mean(0))
    v.check("all-zero toy family has zero pointwise and simultaneous widths", zq == 0 and np.count_nonzero(zp) == 0 and np.count_nonzero(zs) == 0)
    v.check("toy common resampling preserves exact positive dependence", np.array_equal(samples[:, 0], samples[:, 1]) and q > 0)
    # Signs of an exact negative copy must stay opposed under common draws.
    opposite = np.column_stack((z[:, 0], -z[:, 0]))
    opp_samples, _, _ = joint_bootstrap(opposite, 1000, 2026101163)
    v.check("toy opposite columns share opposed draws", np.array_equal(opp_samples[:, 0], -opp_samples[:, 1]))
    return {"enumeration_tolerance": 1e-14, "toy_resamples": 4000, "toy_seed": 2026101161, "zero_seed": 2026101162, "opposite_seed": 2026101163}


def manifest_entries(data, root, base=None):
    entries = {}
    raw_entries = data.get("files", data.get("outputs", []))
    if isinstance(raw_entries, dict):
        raw_entries = [{"path": str(base / k), "sha256": h} for k, h in raw_entries.items()]
    for row in raw_entries:
        path = Path(row["path"])
        if path.is_absolute():
            try:
                path = path.relative_to(root)
            except ValueError:
                marker = "/lora-dora-series/"
                if marker not in str(path):
                    continue
                path = Path(str(path).split(marker, 1)[1])
        entries[str(path)] = row["sha256"]
    return entries


def claims_update(root, rows, cpu, cuda, v):
    claims = load_csv(root / PRIOR / "claim-evidence.csv")
    ids = [r["claim_id"] for r in claims]
    if ids != ["L" + str(i) for i in range(1, 10)]:
        return None, {"complete": False, "reason": "Unexpected original claim IDs", "observed_ids": ids}
    v.check("original claim IDs are exactly L1-L9 in source order", True, ids)
    selected = {(r["job_id"], r["metric"], r["left_run_id"]): r for r in rows}
    radial = selected[("gsm8k-remove_d-all", "final_em", "gsm8k-quality-greedy/dora")]
    reset = selected[("gsm8k-base_magnitude-all", "final_em", "gsm8k-quality-greedy/dora")]
    r32 = selected[("gsm8k-r32", "final_em", "gsm8k-quality-greedy/dora")]
    # Prior statements and dispositions are retained verbatim; new observations
    # below are bounded to this computation and the accepted activity outputs.
    qpp = 100 * float(radial["simultaneous_q95"])
    extra = {
        "L1": ("Новых forward/backward данных нет; новые интервалы касаются только correctness.", "Прежняя структурная проверка сохраняется; training backward не идентифицирован.", "Траектории и backward опубликованного обучения.", "METHOD.md;../../../analysis/2026-10-11/results/theory-audit.md"),
        "L2": ("Ранг и spectra заново не измерялись; семейство46 уточняет quality uncertainty, а не алгебру.", "FP32 структурный вывод сохраняется; actual BF16 delta rank и причинная роль ранга открыты.", "Actual BF16 rank; matched controls и независимые обучения.", "METHOD.md;../../../analysis/2026-10-11/results/spectral-entropy.csv"),
        "L3": (f"r32 final против original: эффект {100*float(r32['difference']):+.3f} п.п.; new pointwise [{100*float(r32['new_pointwise_ci95_low']):+.3f},{100*float(r32['new_pointwise_ci95_high']):+.3f}], simultaneous46 [{100*float(r32['simultaneous_ci95_low']):+.3f},{100*float(r32['simultaneous_ci95_high']):+.3f}] п.п. Reference sensitivity сохранена отдельно.", "Данные совместимы с малой средней потерей после усечения; сила loss-exclusion зависит от margin/reference и семьи. Теорема SORA и causal entropy не проверены и не опровергнуты.", "Entropy-only контроль; BF16 rank; whole-search correction; independent training pairs.", "robustness.csv;central-summary.csv;../../../analysis/2026-10-11/results/compression-original-reference.csv"),
        "L4": ("Все r32/e95/e99, оба scorer и dense/original reference сохранены в joint family46 без отбора.", "Причинное объяснение качеством stable rank не установлено; описательный порядок трёх порогов не независимые повторения.", "Причинное вмешательство с сопоставимыми свойствами; независимые пары.", "central-summary.csv;robustness.csv"),
        "L5": (f"Активность измерена: removeD/fullDelta ideal={100*float(cpu['R_norm_over_Delta']):.5f}% нормы, CUDA normalizer proxy={100*float(cuda['cuda_R_norm_over_Delta']):.5f}%; dense BF16 changed elements={100*float(cpu['remove_dense_changed_fraction']):.3f}%. Final removeD/reset эффекты {100*float(radial['difference']):+.3f}/{100*float(reset['difference']):+.3f} п.п.; общий simultaneous46 радиус {qpp:.3f} п.п. Строгий loss threshold 0.5 п.п. по simultaneous46 для обоих: {radial['simultaneous_lower_gt_minus_0_5pp']}/{reset['simultaneous_lower_gt_minus_0_5pp']}.", "Буквальная неактивность D исключена измерением нормировщика/весового proxy. Близкие mean scores после активного posthoc изменения сохраняются описательно; старый pointwise допуск0.5п.п. нельзя переносить на simultaneous46. Это не freezing during training и не D-specific dispensability.", "Неизвестны training initializer/trajectory; функциональная эквивалентность; контроль другой perturbation равной силы; независимая репликация. Остаток m к базе не движение при обучении.", "robustness.csv;central-summary.csv;../../../diagnostics/radial-activity-2026-10-11/FINDINGS.md;../../../diagnostics/radial-activity-2026-10-11/group-activity.csv;../../../diagnostics/radial-activity-2026-10-11/cuda-group-activity.csv"),
        "L6": ("Новые данные обучения/seed repeats/matched tuning не появились.", "Причины обучения по этим endpoint contrasts по-прежнему неидентифицируемы.", "Overfitting, stability, learning rates и совместная оптимизация.", "METHOD.md;../../../analysis/2026-10-11/results/limitations.md"),
        "L7": ("Joint46 — GSM8K intervention family; baseline DoRA-vs-LoRA triples не входят в неё и заново здесь не оценены.", "Прежний вывод об отсутствии установленного общего преимущества сохраняется в исходном scope; simultaneous46 не новая проверка superiority методов.", "Обобщение на методы/датасеты/seeds и причины различий.", "METHOD.md;../../../analysis/2026-10-11/results/quality-overview.csv"),
        "L8": ("SVD-vs-original и SVD-vs-dense интервалы приведены отдельно; actual weight-rank и matched-rank training здесь не измерены.", "Posthoc compression не переобучение на малом rank; pure rank mechanism остаётся неидентифицируемым.", "Bottom/random controls; matched-rank training; independent partial reversion.", "central-summary.csv;../../../analysis/2026-10-11/results/matched-control-limitations.json"),
        "L9": ("Симметрий/logits/correlation заново не вычисляли; correctness bootstrap не проверяет functional equivalence.", "Прежнее узкое symmetry уточнение сохраняется без расширения на training cause или deployed PEFT equivalence.", "Deployed BF16 statistic; full PEFT equivalence; исходный training pattern.", "METHOD.md;../../../analysis/2026-10-11/results/symmetry-scope.md"),
    }
    output = []
    for row in claims:
        observations, conclusion, unknown, links = extra[row["claim_id"]]
        output.append({"claim_id": row["claim_id"], "original_statement": row["source_statement"], "original_source_url": row["source_url"], "prior_disposition": row["status"], "prior_unknowns": row["what_is_not_identified"], "new_observations": readable_prose(observations), "new_source_links": links, "current_bounded_conclusion": readable_prose(conclusion), "what_remains_unknown": readable_prose(unknown), "scope": "updated registry; original frozen claim-evidence.csv unchanged; no new literature verification"})
    return output, {"complete": True, "rows": len(output)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--draws-dir", type=Path, default=Path("./artifacts"))
    args = parser.parse_args()
    root = args.root.resolve()
    out = root / DEST
    out.mkdir(parents=True, exist_ok=True)
    start = time.perf_counter()
    started_utc = datetime.now(timezone.utc).isoformat()
    cpu_start = time.process_time()
    v = Validation()
    bundle_path = PREP / "manifests/bundle.json"
    prior_manifest_path = PRIOR / "analysis-manifest.json"
    cpu_manifest_path = ACTIVITY / "manifest.json"
    cuda_manifest_path = ACTIVITY / "cuda-manifest.json"
    bundle = json.loads((root / bundle_path).read_text())
    prior_manifest = json.loads((root / prior_manifest_path).read_text())
    cpu_manifest = json.loads((root / cpu_manifest_path).read_text())
    cuda_manifest = json.loads((root / cuda_manifest_path).read_text())
    registries = [manifest_entries(bundle, root), manifest_entries(prior_manifest, root), manifest_entries(cpu_manifest, root), manifest_entries(cuda_manifest, root, ACTIVITY)]
    input_paths = [SPEC, bundle_path, prior_manifest_path, cpu_manifest_path, cuda_manifest_path,
                   Path("AGENTS.md"), Path("MEMORY.md"), PREP / "02-interventions/tables/per_example_scores.csv.gz",
                   PREP / "02-interventions/tables/intervention_metrics.csv", PREP / "02-interventions/tables/paired_transitions.csv", PREP / "02-interventions/tables/localization_grid.csv",
                   PRIOR / "all-intervention-evidence.csv", PRIOR / "compression-original-reference.csv", PRIOR / "claim-evidence.csv",
                   ACTIVITY / "FINDINGS.md", ACTIVITY / "group-activity.csv", ACTIVITY / "cuda-group-activity.csv", ACTIVITY / "validation.json", ACTIVITY / "cuda-validation.json"]
    hashes = {str(path): digest(root / path) for path in input_paths}
    for path in input_paths:
        registered = [registry[str(path)] for registry in registries if str(path) in registry]
        if registered:
            v.check("manifest input hash " + str(path), all(h == hashes[str(path)] for h in registered), {"actual": hashes[str(path)], "registered": registered})
        elif path not in [SPEC, bundle_path, prior_manifest_path, cpu_manifest_path, cuda_manifest_path, ACTIVITY / "FINDINGS.md"]:
            raise ValueError("Input has no accepted manifest entry: " + str(path))
    cpu_validation = json.loads((root / ACTIVITY / "validation.json").read_text())
    cuda_validation = json.loads((root / ACTIVITY / "cuda-validation.json").read_text())
    v.check("accepted CPU activity validation passed", cpu_validation.get("pass_") is True and cpu_validation.get("failed") == 0)
    v.check("accepted CUDA activity validation passed", cuda_validation.get("pass", cuda_validation.get("pass_", cuda_validation.get("passed"))) is True)
    historical = load_csv(root / PRIOR / "all-intervention-evidence.csv")
    original = load_csv(root / PRIOR / "compression-original-reference.csv")
    v.check("historical family has all 40 rows and 20 jobs", len(historical) == 40 and len({r["job_id"] for r in historical}) == 20)
    v.check("original-reference extension has exactly six rows", len(original) == 6 and Counter(r["job_id"] for r in original) == Counter({"gsm8k-r32": 2, "gsm8k-e95": 2, "gsm8k-e99": 2}))
    contrasts = []
    for source, rows in [("all-intervention-evidence.csv", historical), ("compression-original-reference.csv", original)]:
        for row in rows:
            if source == "all-intervention-evidence.csv":
                left, right = row["left_run_id"], row["right_run_id"]
                old_low, old_high = float(row["existing_ci95_low"]), float(row["existing_ci95_high"])
            else:
                right, left = json.loads(row["aligned_run_ids"])
                v.check("compression coefficients " + row["job_id"] + row["metric"], json.loads(row["coefficients"]) == [1, -1])
                old_low, old_high = float(row["ci95_low"]), float(row["ci95_high"])
            v.check("actual reference matches left " + source + row["job_id"] + row["metric"], row["actual_reference"] == left)
            contrasts.append({"source": source, "row": row, "left": left, "right": right, "old_low": old_low, "old_high": old_high})
    v.check("46 unique signed scorer contrasts", len(contrasts) == 46 and len({(r["left"], r["right"], r["row"]["metric"]) for r in contrasts}) == 46)
    v.check("each signed pair has both specified scorers", all(values == set(METRICS) for values in ({c["row"]["metric"] for c in contrasts if c["left"] == pair[0] and c["right"] == pair[1]} for pair in {(c["left"], c["right"]) for c in contrasts})))
    scores = defaultdict(dict)
    with gzip.open(root / PREP / "02-interventions/tables/per_example_scores.csv.gz", "rt", newline="") as stream:
        for row in csv.DictReader(stream):
            key = (row["run_id"], row["metric"])
            index = int(row["test_row_index"])
            if index in scores[key]:
                raise ValueError("Duplicate run/scorer/test_row_index")
            value = float(row["score"])
            if value not in (0., 1.):
                raise ValueError("Nonbinary score")
            identity = (index, row["source_id"], row["prompt_sha256"], row["input_ids_sha256"])
            scores[key][index] = (identity, int(value))
    reference = scores[("gsm8k-quality-greedy/dora", "author_em")]
    v.check("reference covers exact test indices 0..1318", set(reference) == set(range(N)))
    aligned = {}
    for key, values in sorted(scores.items()):
        v.check("full aligned run/scorer " + str(key), set(values) == set(range(N)) and all(values[i][0] == reference[i][0] for i in range(N)))
        v.check("source IDs unique and hashes nonempty " + str(key), len({values[i][0][1] for i in range(N)}) == N and all(len(values[i][0][2]) == 64 and len(values[i][0][3]) == 64 for i in range(N)))
        aligned[key] = np.array([values[i][1] for i in range(N)], dtype=np.int8)
    v.check("scores have exactly specified metrics", {key[1] for key in aligned} == set(METRICS))
    metric_rows = load_csv(root / PREP / "02-interventions/tables/intervention_metrics.csv")
    transition_rows = load_csv(root / PREP / "02-interventions/tables/paired_transitions.csv")
    accepted_metrics = {(row["job_id"], row["metric"]): row for row in metric_rows}
    accepted_transitions = {(row["job_id"], row["metric"]): row for row in transition_rows}
    v.check("accepted frozen metric and transition tables each cover40 rows", len(accepted_metrics) == 40 and len(accepted_transitions) == 40)
    # Accepted historical rows contain four marginals with an explicit reference;
    # verify each against the aligned scores, rather than guessing table schemas.
    z_columns = []
    means = []
    counts_by_contrast = []
    for index, contrast in enumerate(contrasts):
        row, left, right = contrast["row"], contrast["left"], contrast["right"]
        metric = row["metric"]
        x, y = aligned[(left, metric)], aligned[(right, metric)]
        z = y - x
        z_columns.append(z)
        left_mean, right_mean, effect = float(x.mean()), float(y.mean()), float(z.mean())
        expected = (float(row.get("left_mean", row.get("reference_mean"))), float(row.get("right_mean", row.get("changed_mean"))), float(row["difference"]))
        v.check("means agree <=1e-12 contrast " + str(index), max(abs(a - b) for a, b in zip((left_mean, right_mean, effect), expected)) <= 1e-12, {"actual": [left_mean, right_mean, effect], "accepted": expected})
        counts = {"correct_to_correct": int(np.sum((x == 1) & (y == 1))), "correct_to_wrong": int(np.sum((x == 1) & (y == 0))), "wrong_to_correct": int(np.sum((x == 0) & (y == 1))), "wrong_to_wrong": int(np.sum((x == 0) & (y == 0)))}
        v.check("transition marginals contrast " + str(index), sum(counts.values()) == N and counts["correct_to_correct"] + counts["correct_to_wrong"] == int(x.sum()) and counts["correct_to_correct"] + counts["wrong_to_correct"] == int(y.sum()) and counts["wrong_to_correct"] - counts["correct_to_wrong"] == int(z.sum()))
        if contrast["source"] == "all-intervention-evidence.csv":
            v.check("accepted transitions contrast " + str(index), all(counts[k] == int(row[k]) for k in counts))
            accepted_metric = accepted_metrics[(row["job_id"], metric)]
            accepted_transition = accepted_transitions[(row["job_id"], metric)]
            v.check("frozen metrics and paths match contrast " + str(index), accepted_metric["actual_reference"] == left and all(abs(float(accepted_metric[k]) - a) <= 1e-12 for k, a in zip(["left_mean", "right_mean", "difference"], [left_mean, right_mean, effect])) and accepted_metric["left_path"] == row["left_path"] and accepted_metric["right_path"] == row["right_path"])
            v.check("frozen transitions and paths match contrast " + str(index), all(counts[k] == int(accepted_transition[k]) for k in counts) and accepted_transition["left_path"] == row["left_path"] and accepted_transition["right_path"] == row["right_path"])
        else:
            expected_counts = json.loads(row["z_distribution"])
            v.check("accepted z distribution contrast " + str(index), {str(k): int(np.sum(z == k)) for k in [-1, 0, 1]} == expected_counts)
        means.append((left_mean, right_mean, effect))
        counts_by_contrast.append(counts)
    z = np.column_stack(z_columns)
    toy = toy_validation(v)
    bootstrap_start = time.perf_counter()
    draws, patterns, frequencies = joint_bootstrap(z, B, SEED)
    bootstrap_seconds = time.perf_counter() - bootstrap_start
    mu = z.mean(axis=0)
    pointwise, simultaneous, q95, maximum = intervals(draws, mu)
    args.draws_dir.mkdir(parents=True, exist_ok=True)
    draws_path = args.draws_dir / "bootstrap-means.npy"
    np.save(draws_path, draws, allow_pickle=False)
    draws_artifact = {"path": str(draws_path), "sha256": digest(draws_path), "bytes": draws_path.stat().st_size, "shape": list(draws.shape), "dtype": str(draws.dtype), "resamples": B, "seed": SEED, "column_order": [{"contrast_index": index, "job_id": c["row"]["job_id"], "metric": c["row"]["metric"], "left_run_id": c["left"], "right_run_id": c["right"]} for index, c in enumerate(contrasts)], "scope": "server-only outside Git; do not download draws to VM"}
    v.check("persisted bootstrap matrix roundtrip", np.array_equal(np.load(draws_path, allow_pickle=False, mmap_mode="r"), draws))
    v.check("joint pattern counts preserve exact sample count", int(frequencies.sum()) == N and len(patterns) <= N)
    v.check("joint pattern weighted means equal original means", np.max(np.abs((frequencies @ patterns.astype(np.float64)) / N - mu)) < 1e-15)
    v.check("bootstrap draws finite and bounded", np.all(np.isfinite(draws)) and np.max(np.abs(draws)) <= 1)
    v.check("both interval types finite ordered and bounded", all(np.all(np.isfinite(bands)) and np.all(bands[0] <= bands[1]) and np.min(bands) >= -1 and np.max(bands) <= 1 for bands in [pointwise, simultaneous]))
    v.check("simultaneous family has one shared unstudentized radius", np.allclose(simultaneous[0], mu - q95, atol=1e-15, rtol=0) and np.allclose(simultaneous[1], mu + q95, atol=1e-15, rtol=0), {"q95": q95, "quantile_method": "linear", "clipping_active": False})
    theory_variance = np.mean((z.astype(np.float64) - mu) ** 2, axis=0) / N
    mean_errors = np.abs(draws.mean(axis=0) - mu)
    mean_tolerance = 6 * np.sqrt(theory_variance / B) + 1e-12
    v.check("common bootstrap mean consistency <=6 Monte Carlo standard errors", np.all(mean_errors <= mean_tolerance), {"max_absolute_mean_error": float(mean_errors.max()), "max_standard_errors": float(np.max(mean_errors / np.maximum(np.sqrt(theory_variance / B), 1e-30)))})
    variance_errors = np.abs(draws.var(axis=0, ddof=1) - theory_variance)
    v.check("bootstrap marginal variances agree with iid empirical target within5pct", np.all(variance_errors <= .05 * theory_variance + 1e-15), {"max_relative_error": float(np.max(variance_errors / np.maximum(theory_variance, 1e-30)))})
    duplicate_pairs = []
    identical_scorer_pairs = []
    for j in range(46):
        for k in range(j):
            if np.array_equal(z[:, j], z[:, k]):
                duplicate_pairs.append([k, j])
                v.check("identical columns yield identical draws/intervals " + str((k, j)), np.array_equal(draws[:, j], draws[:, k]) and np.array_equal(pointwise[:, j], pointwise[:, k]) and np.array_equal(simultaneous[:, j], simultaneous[:, k]))
                if contrasts[j]["left"] == contrasts[k]["left"] and contrasts[j]["right"] == contrasts[k]["right"]:
                    identical_scorer_pairs.append([k, j])
    contained = np.all((draws >= simultaneous[0] - 1e-15) & (draws <= simultaneous[1] + 1e-15), axis=1)
    construction_fraction = float(contained.mean())
    v.check("bootstrap construction: >=95pct draws inside all46 bands", construction_fraction >= .95, {"fraction": construction_fraction, "draws_contained": int(contained.sum()), "resamples": B, "discrete_quantile_tolerance": 1e-15, "scope": "construction diagnostic, not verification of true frequentist coverage"})
    v.check("max-deviation and all-band containment diagnostics agree", np.array_equal(contained, maximum <= q95 + 1e-15))
    output = []
    for j, contrast in enumerate(contrasts):
        row = contrast["row"]
        left_mean, right_mean, effect = means[j]
        entry = {"contrast_index": j, "job_id": row["job_id"], "metric": row["metric"], "left_run_id": contrast["left"], "right_run_id": contrast["right"], "actual_reference": row["actual_reference"], "difference_direction": "right-minus-left", "left_mean": left_mean, "right_mean": right_mean, "difference": effect, "difference_pp": 100 * effect, "n": N, **counts_by_contrast[j], "old_pointwise_ci95_low": contrast["old_low"], "old_pointwise_ci95_high": contrast["old_high"], "old_ci_source": str(PRIOR / contrast["source"]), "old_ci_scope": "historical pointwise paired test-example CI; not simultaneous or training uncertainty", "old_resamples": row["resamples"], "old_seed": row["seed"], "new_pointwise_ci95_low": float(pointwise[0, j]), "new_pointwise_ci95_high": float(pointwise[1, j]), "new_pointwise_ci_scope": "percentile95 pointwise from common family46 draws; not simultaneous", "simultaneous_ci95_low": float(simultaneous[0, j]), "simultaneous_ci95_high": float(simultaneous[1, j]), "simultaneous_q95": q95, "simultaneous_method": "unstudentized maximum absolute centered bootstrap deviation; not max-t", "family": FAMILY, "family_size": 46, "resamples": B, "seed": SEED, "uncertainty_scope": SCOPE, "selection_scope": "exploratory family fixed after earlier data inspection; posthoc margins; not preregistered"}
        for prefix, low in [("old_pointwise", contrast["old_low"]), ("new_pointwise", pointwise[0, j]), ("simultaneous", simultaneous[0, j])]:
            for label, delta in MARGINS:
                entry[prefix + "_lower_gt_minus_" + label] = bool(low > -delta)
        output.append(entry)
    save_csv(out / "robustness.csv", output)
    selected_jobs = {"gsm8k-remove_d-all", "gsm8k-base_magnitude-all", "gsm8k-r32", "gsm8k-e95", "gsm8k-e99"}
    summary = [row for row in output if row["job_id"] in selected_jobs]
    v.check("central summary has16 exact scorer/reference rows", len(summary) == 16)
    save_csv(out / "central-summary.csv", summary)
    cpu_group = next(row for row in load_csv(root / ACTIVITY / "group-activity.csv") if row["group"] == "all")
    cuda_group = next(row for row in load_csv(root / ACTIVITY / "cuda-group-activity.csv") if row["group"] == "all")
    v.check("activity measurements cover144 modules and313344 rows", all(int(row["modules"]) == 144 and int(row["rows"]) == 313344 for row in [cpu_group, cuda_group]))
    claim_rows, ledger_status = claims_update(root, output, cpu_group, cuda_group, v)
    if claim_rows is not None:
        save_csv(out / "claim-update.csv", claim_rows)
    # Verify every input again after all computation. No prior file is rewritten.
    for path, prior_hash in hashes.items():
        v.check("input bytes unchanged after computation " + path, digest(root / path) == prior_hash)
    resources = {"started_utc": started_utc, "wall_seconds": time.perf_counter() - start, "cpu_seconds": time.process_time() - cpu_start, "bootstrap_seconds": bootstrap_seconds, "peak_rss_mib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024, "python": sys.version, "numpy": np.__version__, "platform": platform.platform(), "thread_environment": {key: os.environ[key] for key in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "BLIS_NUM_THREADS")}, "cuda_visible_devices": os.environ["CUDA_VISIBLE_DEVICES"], "gpu_used": False, "resamples": B, "seed": SEED, "chunk_max": CHUNK, "joint_patterns": len(patterns), "draws_matrix_shape": list(draws.shape), "draws_matrix_bytes": draws.nbytes, "draws_stored_on_disk": True, "draws_artifact_path": str(draws_path), "scope": "existing aligned score CSV and compact accepted activity reports only; no weights/forward/download/install"}
    save_json(out / "resource-use.json", resources)
    v.check("all numerical thread limits <=2", all(int(value) <= 2 for value in resources["thread_environment"].values()))
    validation = {"passed": True, "complete": ledger_status["complete"], "checks_count": len(v.checks), "failed": 0, "n": N, "family_size": 46, "resamples": B, "seed": SEED, "joint_patterns": len(patterns), "q95": q95, "construction_fraction": construction_fraction, "construction_scope": "bootstrap band construction diagnostic; not true coverage verification", "identical_difference_columns": duplicate_pairs, "identical_scorer_difference_columns": identical_scorer_pairs, "toy": toy, "ledger": ledger_status, "checks": v.checks}
    save_json(out / "validation.json", validation)
    write_method(out, resources, q95, construction_fraction, ledger_status, draws_artifact)
    write_findings(out, summary, output, q95, construction_fraction)
    source = Path(__file__).resolve()
    output_paths = sorted(path for path in out.iterdir() if path.is_file() and path.name != "manifest.json")
    manifest = {"schema_version": 1, "created_utc": datetime.now(timezone.utc).isoformat(), "passed": True, "complete": ledger_status["complete"], "family": FAMILY, "code": {"path": str(source.relative_to(root)), "sha256": digest(source), "bytes": source.stat().st_size}, "inputs": [{"path": path, "sha256": value, "bytes": (root / path).stat().st_size, "verification": "matched accepted manifest and unchanged postrun" if any(path in registry for registry in registries) else "snapshot SHA and unchanged postrun; manifest/spec/prose dependency"} for path, value in hashes.items()], "outputs": [{"path": str(path.relative_to(root)), "sha256": digest(path), "bytes": path.stat().st_size} for path in output_paths], "external_artifacts": [draws_artifact], "exclusions": ["manifest.json self hash", "bootstrap matrix mirrored only on server, outside Git"], "versions": {"python": platform.python_version(), "numpy": np.__version__}, "resource_use": "resource-use.json", "immutable_sources_modified": False}
    save_json(out / "manifest.json", manifest)
    print(json.dumps({"passed": True, "complete": ledger_status["complete"], "checks": len(v.checks), "q95": q95, "q95_pp": 100*q95, "joint_patterns": len(patterns), "construction_fraction": construction_fraction, "wall_seconds": resources["wall_seconds"], "peak_rss_mib": resources["peak_rss_mib"], "manifest_sha256": digest(out / "manifest.json")}, ensure_ascii=False))


def write_method(out, resources, q95, fraction, ledger, draws_artifact):
    text = f"""# Метод: устойчивость существующих accuracy contrasts

Семья заранее фиксирована в SPEC данного продолжения: все40 строк принятого
all-intervention-evidence.csv плюс все6 строк compression-original-reference.csv.
Это46 signed contrasts (23пары ×2scorers), без отбора по выгодному результату.
Каждая строка сохраняет exact left/right run IDs и свой reference; эффект
всегда right-minus-left. Выбор этой семьи после просмотра прежних результатов
делает анализ exploratory, а фиксация сейчас не является пререгистрацией.
Семья46 не охватывает всю историю адаптивного поиска и не объединяет автоматически
8 тестов пакета A. CI условны на фиксированные checkpoints, не на training seeds.

## Выравнивание и provenance

Бинарные scores всех run/scorer сверены по source_id, test_row_index,
prompt_sha256, input_ids_sha256; в каждом1319 примеров, индексы0..1318.
Means/effects каждой строки сверены с принятыми таблицами до1e−12,
четыре перехода и их маргинальные суммы — с scores и прежними counts.
Выбранные frozen inputs проверены по bundle/analysis manifest; activity CSV и
validation — по принятым CPU/CUDA manifests. Все входные bytes повторно
проверены после расчётов. manifest.json содержит точные SHA и размеры.
Неизменяемые evaluator/predictions/bundle/старые CI/claim CSV не переписаны.

## Joint paired bootstrap

Пусть Z_ij=Y_right,ij−Y_left,ij, i=1..1319,j=1..46. Обе метрики
входят в одну матрицу Z. Один paired bootstrap использует общие индексы i
для всех46 столбцов. B={B}, seed={SEED}, NumPy default_rng/PCG64,
multinomial chunk≤{CHUNK}. Квантили np.quantile(method='linear').

Для экономии памяти объединены идентичные полные46-компонентные строки Z.
Получено{resources['joint_patterns']} совместных patterns. Если pattern k встречается
c_k раз, при iid resampling1319 индексов число выбранных строк этого pattern
имеет Multinomial(1319,c_k/1319). Поэтому один общий вектор counts, умноженный
на pattern matrix, даёт ровно то же совместное распределение всех46 bootstrap
means, что и resampling индексов. Нельзя resample каждый столбец отдельно:
это разрушило бы сохранённую зависимость вмешательств/scorers. Toy enumeration
всех27 index sequences для3примеров подтверждает совпадение распределений.
Матрица draws B×46 занимает{resources['draws_matrix_bytes']}bytes в памяти.
Для независимой приёмки сохранена только на сервере внеGit:
{draws_artifact['path']}. SHA256={draws_artifact['sha256']};
shape={draws_artifact['shape']},dtype={draws_artifact['dtype']}.
Порядок столбцов: contrast_index0..45 в robustness.csv и полный column_order
в manifest.json/external_artifacts. НаVM матрица не копируется.

Новые pointwise интервалы: квантили .025/.975 каждого столбца из этих же draws.
Для simultaneous bands вычислено M_b=max_j |mu*_bj−mu_hat_j|,
q95=quantile_.95(M_b)={q95:.17g} accuracy units ({100*q95:.6f}п.п.).
Для всех46 применяется один общий интервал mu_hat_j±q95; clipping[-1,1]
разрешён, здесь не активен. Это приближённые двусторонние simultaneous95%
bootstrap bands на общей accuracy шкале: maximum ABSOLUTE UNSTUDENTIZED
deviation, **не max-t**. Студентизация или отдельные критические q не применялись.

Исторические pointwise CI сохранены отдельными колонками вместе с source,
старым seed/B и scope. Их отличие от новых pointwise связано с другим seed/B;
добавление simultaneous scope не переписывает исторические результаты.

## Margins и проверки

Для old/new pointwise/simultaneous отдельно вычислено строгое lower>−delta
при delta=.005/.01/.02 (0.5/1/2п.п.). Эти допуски posthoc; это описательная
проверка совместимой потери, без noninferiority p-value и без утверждения
functional equivalence. CI, включающий ноль, не доказательство equivalence.

Проверены all-zero toy family с нулевой шириной; одинаковые/противоположные
столбцы; совпадающие scorers; exact pattern-weighted means; Monte Carlo means
в пределах6MCSE; marginal bootstrap variances в пределах5% эмпирической iid
цели; конечность, bounds, transition margins и неизменность input SHA.
Доля bootstrap draws, попавших во все46 bands одновременно, {fraction:.6f}.
Порог≥95% проверен с допуском1e−15 для floating/discrete quantiles. Это
**проверка конструкции bootstrap**, не проверка истинной частотной coverage
неизвестного распределения. Никаких independent datasets/seeds здесь не создано.

## Реестр и ресурсы

claim-update.csv сохраняет9 исходных statements/dispositions и добавляет
bounded conclusions. L5 обновлён по принятой activity диагностике: измеренная
активность нормировщика и weight proxy, отдельно от функции/обучения.
Статус ledger: {ledger}. Frozen claim-evidence.csv остаётся исходным.
Литературу заново не проверяли; ссылки унаследованы от принятого реестра.

Python{platform.python_version()}, NumPy{np.__version__}; CPU исследовательского
сервера, численные thread limits2, CUDA_VISIBLE_DEVICES пуст.
Bootstrap {resources['bootstrap_seconds']:.3f}с; анализ до записи документации
{resources['wall_seconds']:.3f}с; peakRSS{resources['peak_rss_mib']:.2f}MiB.
Точные flags/версии/ресурсы — resource-use.json; проверки — validation.json.
Новые weights/forward/SVD/download/install/GPU jobs не выполнялись.
"""
    (out / "METHOD.md").write_text(readable_prose(text), encoding="utf-8")


def write_findings(out, summary, rows, q95, fraction):
    lines = ["# Устойчивость выводов на существующих данных", "", f"Совместный bootstrap всех46 signed contrasts дал общий радиус **{100*q95:.3f}п.п.** для приближённых simultaneous95% bands. Это шире pointwise CI; family46 exploratory и не исправляет всю историю адаптивного поиска.", "", "Ниже интервалы/эффекты в п.п. Флаги перечисляют posthoc margins, для которых строго lower>−margin; «—» означает отсутствие таких допусков из0.5/1/2п.п. Полные46строк и старые seeds/B/scopes сохранены в robustness.csv; центральные16строк в central-summary.csv.", "", "| Вмешательство | Scorer | Reference | Эффект | Старый pointwise95 | Новый pointwise95 | Simultaneous46 | Margins old / new / simultaneous |", "|---|---|---|---:|---|---|---|---|"]
    for row in summary:
        flag_texts = []
        for prefix in ["old_pointwise", "new_pointwise", "simultaneous"]:
            flag_texts.append(",".join(label.replace("0_5pp", "0.5").replace("pp", "") for label, _ in MARGINS if row[prefix + "_lower_gt_minus_" + label]) or "—")
        intervals_text = [f"[{100*row[prefix+'_ci95_low']:+.3f};{100*row[prefix+'_ci95_high']:+.3f}]" for prefix in ["old_pointwise", "new_pointwise", "simultaneous"]]
        ref = "original DoRA" if row["left_run_id"] == "gsm8k-quality-greedy/dora" else "dense DoRA"
        lines.append(f"| {row['job_id'].replace('gsm8k-', '')} | {row['metric']} | {ref} | {row['difference_pp']:+.3f} | {' | '.join(intervals_text)} | {' / '.join(flag_texts)} |")
    counts = {}
    for prefix in ["old_pointwise", "new_pointwise", "simultaneous"]:
        counts[prefix] = {label: sum(row[prefix + "_lower_gt_minus_" + label] for row in rows) for label, _ in MARGINS}
    lines += ["", "По всей семье46 число строк, исключающих потери более0.5/1/2п.п. по строгому lower threshold:", "", f"- Исторические pointwise: {list(counts['old_pointwise'].values())}.", f"- Новые pointwise из common draws: {list(counts['new_pointwise'].values())}.", f"- Simultaneous46: {list(counts['simultaneous'].values())}.", "", "Средние accuracy, направления эффектов и correctness transitions сохранены: новая процедура уточняет неопределённость и scope. В частности, активное удаление D/возврат базовых норм по-прежнему даёт близкие средние в этом checkpoint; старое pointwise исключение потери0.5п.п. нужно оценивать отдельно от более широких simultaneous46 bands. Порог2п.п. сильнее допускает потери и потому слабее как практическое требование.", "", "Для compression reference существенен: r32/e95/e99 против dense и против original — разные estimands. Положительные средние относительно dense нельзя переносить без поправки на original. Новый реестр claim-update.csv уточняет L3/L5/L8 и сохраняет ограничения остальных claims.", "", "L5: ранее неизвестная численная активность D теперь измерена в принятой диагностике (~17.94% нормы адаптерного обновления; dense BF16 изменяет46.713% элементов). CUDA подтверждает активный FP32 нормировщик и близкий weight proxy. Это устраняет объяснение буквально неизменными весами, но не устанавливает функциональную эквивалентность, бесполезность D, freezing during training или механизм поиска A/B. Сопоставление качества и активности — наблюдение одного endpoint; контроль другого возмущения сопоставимой силы и независимая репликация остаются открытыми.", "", f"validation.json: bootstrap construction containment={fraction:.6f}; это проверка построения bands, не истинной coverage. METHOD.md задаёт точные scope/формулы; manifest.json — hashes кода, входов и выходов. Все расчёты CPU≤2threads на существующих scores/малых таблицах; GPU/weights/forward/training/download/install отсутствуют. Статья и paper outline здесь не создавались."]
    lines += ["", "Конкретно ослабли следующие практические выводы:", "", "- remove_D-all и base_magnitude-all: оба scorer сохраняют исключение потери более 1 п.п. в simultaneous46, но уже не более 0.5 п.п. Значит центральное наблюдение близких средних сохраняется, а более сильная формулировка про 0.5 п.п. остаётся только pointwise.", "- r32/e95 против original: оба scorer проходят только допуск 2 п.п.; прежний pointwise допуск 1 п.п. после joint46 не проходит. Против dense у r32 final и e95 обоих scorer остаётся 1 п.п., у r32 author — только 2 п.п.", "- e99 против original: author проходит 2 п.п. с lower −1.971 п.п.; final имеет lower −2.047 п.п. и уже не проходит 2 п.п. Против dense оба scorer проходят 2 п.п., но не 1 п.п.", "", "Меняется и один пограничный исторический pointwise флаг: remove_D-QK author при 0.5 п.п. (old lower −0.531, new lower −0.455 п.п.). Это изменение seed/B percentile bootstrap, а не новая поправка на множественный поиск. Одновременный допуск 0.5 п.п. в семье46 проходит только matched-impact LoRA control; он не является доказательством специфичности D."]
    (out / "FINDINGS.md").write_text(readable_prose("\n".join(lines) + "\n"), encoding="utf-8")


if __name__ == "__main__":
    main()
