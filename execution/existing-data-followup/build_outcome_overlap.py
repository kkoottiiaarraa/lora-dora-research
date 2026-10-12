#!/usr/bin/env python3
"""Package B: descriptive joint binary outcomes from immutable saved scores.

Run on the research server, with two numerical threads and no GPU/model imports.
All repairs/breaks use the original PEFT DoRA checkpoint as a common reference.
"""
import argparse
import csv
import gzip
import hashlib
import io
import itertools
import json
import os
import platform
import re
import resource
import time
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

THREAD_KEYS = ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
               "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS")
for key in THREAD_KEYS:
    os.environ[key] = "2"
os.environ["CUDA_VISIBLE_DEVICES"] = ""

import numpy as np

RUNS = (
    "gsm8k-quality-greedy/dora", "gsm8k-quality-greedy/lora",
    "gsm8k-dense-dora/dora", "gsm8k-remove_d-all/dora",
    "gsm8k-base_magnitude-all/dora", "gsm8k-r32/dora",
    "gsm8k-e95/dora", "gsm8k-e99/dora",
)
LABELS = ("original_DoRA", "trained_LoRA", "dense_DoRA", "remove_D_all",
          "base_magnitude_all", "r32", "e95", "e99")
METRICS = ("author_em", "final_em")
N = 1319
PREP = "docs/analysis-preparation/2026-10-11"
ACCEPTED = "docs/analysis/2026-10-11/results"
OUT = "docs/analysis-followup/2026-10-11/B-outcome-overlap"
CODE = "execution/existing-data-followup/build_outcome_overlap.py"


def sha(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def read_csv(path):
    with path.open(newline="") as stream:
        return list(csv.DictReader(stream))


def write_csv(path, rows, compressed=False):
    if compressed:
        with path.open("wb") as raw:
            with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as zipped:
                with io.TextIOWrapper(zipped, encoding="utf-8", newline="") as stream:
                    writer = csv.DictWriter(stream, list(rows[0]))
                    writer.writeheader()
                    writer.writerows(rows)
    else:
        with path.open("w", newline="") as stream:
            writer = csv.DictWriter(stream, list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)


def joint(left, right):
    return {
        "correct_to_correct": int(np.count_nonzero(left & right)),
        "correct_to_wrong": int(np.count_nonzero(left & ~right)),
        "wrong_to_correct": int(np.count_nonzero(~left & right)),
        "wrong_to_wrong": int(np.count_nonzero(~left & ~right)),
    }


def fraction(numerator, denominator):
    return numerator / denominator if denominator else "undefined"


def overlap(left, right):
    intersection = int(np.count_nonzero(left & right))
    union = int(np.count_nonzero(left | right))
    left_n, right_n = int(left.sum()), int(right.sum())
    return dict(left_count=left_n, right_count=right_n,
                intersection=intersection, union=union,
                jaccard=fraction(intersection, union),
                shared_fraction_of_left=fraction(intersection, left_n),
                shared_fraction_of_right=fraction(intersection, right_n))


def main():
    start = time.perf_counter()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    args = parser.parse_args()
    repo = args.repo.resolve()
    out = repo / OUT
    out.mkdir(parents=True, exist_ok=True)
    checks, inputs = [], {}

    def check(name, condition, **details):
        checks.append(dict(name=name, passed=bool(condition), **details))
        if not condition:
            raise ValueError(name + ": " + str(details))

    def record(relative):
        path = repo / relative
        item = dict(path=relative, sha256=sha(path), bytes=path.stat().st_size)
        inputs[relative] = item
        return item

    bundle_path = PREP + "/manifests/bundle.json"
    record(bundle_path)
    bundle = {r["path"]: r for r in json.loads((repo / bundle_path).read_text())["files"]}
    accepted_path = ACCEPTED + "/analysis-manifest.json"
    record(accepted_path)
    accepted = {r["path"]: r for r in json.loads((repo / accepted_path).read_text())["files"]}

    def frozen(relative):
        relative = PREP + "/" + relative
        item = record(relative)
        check("immutable SHA " + relative, item["sha256"] == bundle[relative]["sha256"])
        return repo / relative

    def accepted_csv(name):
        relative = ACCEPTED + "/" + name
        item = record(relative)
        expected = accepted.get(relative) or accepted.get("./artifacts" + relative)
        check("accepted manifest entry " + name, expected is not None)
        check("accepted SHA " + name, item["sha256"] == expected["sha256"])
        return read_csv(repo / relative)

    scores_path = frozen("02-interventions/tables/per_example_scores.csv.gz")
    metrics = read_csv(frozen("02-interventions/tables/intervention_metrics.csv"))
    transitions = read_csv(frozen("02-interventions/tables/paired_transitions.csv"))
    baseline_metrics = read_csv(frozen("01-corpus-quality/tables/baseline_metrics.csv"))
    baseline_pairs = read_csv(frozen("01-corpus-quality/tables/baseline_pair_transitions.csv"))
    accepted_pairs = accepted_csv("paired-outcome-transitions.csv")
    compression = accepted_csv("compression-original-reference.csv")
    record("docs/analysis-followup/2026-10-11/SPEC.md")
    grouped = defaultdict(dict)
    with gzip.open(scores_path, "rt", newline="") as stream:
        for row in csv.DictReader(stream):
            run, metric = row["run_id"], row["metric"]
            if run not in RUNS or metric not in METRICS:
                continue
            index = int(row["test_row_index"])
            if index in grouped[(run, metric)]:
                raise ValueError("duplicate aligned score: " + str((run, metric, index)))
            if float(row["score"]) not in (0.0, 1.0):
                raise ValueError("nonbinary score")
            grouped[(run, metric)][index] = row
    reference_ids = None
    vectors = {}
    for run, metric in itertools.product(RUNS, METRICS):
        rows = grouped[(run, metric)]
        check("full ordered index set " + run + " " + metric, sorted(rows) == list(range(N)))
        ids = [(r["source_id"], r["prompt_sha256"], r["input_ids_sha256"])
               for _, r in sorted(rows.items())]
        check("valid SHA256 identifiers " + run + " " + metric,
              all(re.fullmatch("[0-9a-f]{64}", value) for item in ids for value in item[1:]))
        check("unique source IDs " + run + " " + metric, len(set(item[0] for item in ids)) == N)
        if reference_ids is None:
            reference_ids = ids
        check("aligned IDs and hashes " + run + " " + metric, ids == reference_ids)
        vectors[(run, metric)] = np.array([float(rows[i]["score"]) for i in range(N)], dtype=bool)
    check("exact selected 8x2 groups", len(grouped) == 16)

    # Cross-check every applicable saved marginal and transition with actual references.
    frozen_pair_checks = accepted_pair_checks = compression_checks = baseline_pair_checks = 0
    for row in baseline_metrics:
        key = row["run_id"], row["metric"]
        if key in vectors:
            check("baseline marginal " + str(key), abs(vectors[key].mean() - float(row["original_score"])) <= 1e-12)
    for row in baseline_pairs:
        left, right, metric = row["left_run"], row["right_run"], row["metric"]
        if (left, metric) in vectors and (right, metric) in vectors:
            counts = joint(vectors[(left, metric)], vectors[(right, metric)])
            fields = ("correct_correct", "correct_wrong", "wrong_correct", "wrong_wrong")
            check("baseline pair " + str((left, right, metric)), list(counts.values()) == [int(row[f]) for f in fields])
            baseline_pair_checks += 1
    for row in metrics:
        right, left, metric = row["job_id"] + "/dora", row["actual_reference"], row["metric"]
        if (left, metric) in vectors and (right, metric) in vectors:
            check("intervention marginal " + str((left, right, metric)),
                  abs(float(vectors[(left, metric)].mean()) - float(row["left_mean"])) <= 1e-12
                  and abs(float(vectors[(right, metric)].mean()) - float(row["right_mean"])) <= 1e-12)
            tr = next(t for t in transitions if t["job_id"] == row["job_id"] and t["metric"] == metric)
            counts = joint(vectors[(left, metric)], vectors[(right, metric)])
            check("frozen transition actual reference " + str((left, right, metric)),
                  all(counts[k] == int(tr[k]) for k in counts))
            frozen_pair_checks += 1
    for row in accepted_pairs:
        left, right, metric = row["left_run_id"], row["right_run_id"], row["metric"]
        if (left, metric) in vectors and (right, metric) in vectors:
            counts = joint(vectors[(left, metric)], vectors[(right, metric)])
            check("accepted transition " + str((left, right, metric)), all(counts[k] == int(row[k]) for k in counts))
            accepted_pair_checks += 1
    for row in compression:
        right, metric = row["job_id"] + "/dora", row["metric"]
        left = row["actual_reference"]
        counts = joint(vectors[(left, metric)], vectors[(right, metric)])
        expected_z = json.loads(row["z_distribution"])
        check("compression original reference " + str((right, metric)), left == RUNS[0]
              and counts["correct_to_wrong"] == expected_z["-1"]
              and counts["wrong_to_correct"] == expected_z["1"]
              and counts["correct_to_correct"] + counts["wrong_to_wrong"] == expected_z["0"]
              and abs(float(vectors[(right, metric)].mean()) - float(row["changed_mean"])) <= 1e-12)
        compression_checks += 1
    check("expected cross-check coverage", (baseline_pair_checks, frozen_pair_checks, accepted_pair_checks, compression_checks) == (2, 12, 8, 6),
          actual=[baseline_pair_checks, frozen_pair_checks, accepted_pair_checks, compression_checks])

    summary, pairs, overlaps, patterns = [], [], [], []
    for metric in METRICS:
        original = vectors[(RUNS[0], metric)]
        original_correct = int(original.sum())
        events = {}
        for run, label in zip(RUNS, LABELS):
            vector = vectors[(run, metric)]
            counts = joint(original, vector)
            repair = ~original & vector
            broken = original & ~vector
            changed = original != vector
            events[run] = dict(repairs=repair, breaks=broken, changed_correctness=changed)
            check("disjoint repairs breaks partition " + run + " " + metric,
                  not np.any(repair & broken) and np.array_equal(repair | broken, changed))
            summary.append(dict(metric=metric, run_id=run, label=label, reference_run_id=RUNS[0], n=N,
                                correct_n=int(vector.sum()), score=float(vector.mean()),
                                repairs=counts["wrong_to_correct"], breaks=counts["correct_to_wrong"],
                                changed_correctness=int(changed.sum()),
                                original_correct_n=original_correct, original_wrong_n=N-original_correct,
                                repair_rate_given_original_wrong=fraction(int(repair.sum()), N-original_correct),
                                break_rate_given_original_correct=fraction(int(broken.sum()), original_correct),
                                difference_vs_original=float((vector.astype(int)-original.astype(int)).mean())))
        for left, right in itertools.combinations(RUNS, 2):
            a, b = vectors[(left, metric)], vectors[(right, metric)]
            counts = joint(a, b)
            check("pairwise total and marginals " + str((metric, left, right)), sum(counts.values()) == N
                  and counts["correct_to_correct"] + counts["correct_to_wrong"] == int(a.sum())
                  and counts["correct_to_correct"] + counts["wrong_to_correct"] == int(b.sum())
                  and counts["wrong_to_correct"] - counts["correct_to_wrong"] == int(b.sum()) - int(a.sum()))
            pairs.append(dict(metric=metric, left_run_id=left, right_run_id=right, n=N,
                              left_score=float(a.mean()), right_score=float(b.mean()), **counts,
                              changed_correctness=counts["correct_to_wrong"]+counts["wrong_to_correct"],
                              difference=float((b.astype(int)-a.astype(int)).mean()), difference_direction="right-minus-left"))
        for left, right in itertools.combinations(RUNS[1:], 2):
            row = dict(metric=metric, reference_run_id=RUNS[0], left_run_id=left, right_run_id=right, n=N)
            for event in ("repairs", "breaks", "changed_correctness"):
                values = overlap(events[left][event], events[right][event])
                row.update({event+"_"+key: value for key, value in values.items()})
                check("overlap set identities " + str((metric, left, right, event)),
                      values["union"] == values["left_count"] + values["right_count"] - values["intersection"]
                      and 0 <= values["intersection"] <= min(values["left_count"], values["right_count"])
                      and (values["jaccard"] == "undefined" if values["union"] == 0 else 0 <= values["jaccard"] <= 1))
            check("changed overlap partitions " + str((metric, left, right)),
                  row["changed_correctness_intersection"] == row["repairs_intersection"] + row["breaks_intersection"]
                  and row["changed_correctness_union"] == row["repairs_union"] + row["breaks_union"])
            overlaps.append(row)
        for index, ids in enumerate(reference_ids):
            vector_string = "".join(str(int(vectors[(run, metric)][index])) for run in RUNS)
            patterns.append(dict(metric=metric, test_row_index=index, source_id=ids[0], prompt_sha256=ids[1],
                                 input_ids_sha256=ids[2], correctness_vector=vector_string))
    check("exact output row counts", (len(summary), len(pairs), len(overlaps), len(patterns)) == (16,56,42,2638))
    check("empty union explicitly undefined", overlap(np.zeros(4,dtype=bool),np.zeros(4,dtype=bool))["jaccard"] == "undefined")
    # Reconstruct every correctness vector from the compact case output before writing.
    for metric in METRICS:
        cases = [r for r in patterns if r["metric"] == metric]
        for pos, run in enumerate(RUNS):
            recovered = np.array([int(r["correctness_vector"][pos]) for r in cases], dtype=bool)
            check("case-pattern vector roundtrip " + run + " " + metric, np.array_equal(recovered, vectors[(run,metric)]))
    write_csv(out / "run-summary.csv", summary)
    write_csv(out / "pairwise-outcomes.csv", pairs)
    write_csv(out / "overlap.csv", overlaps)
    write_csv(out / "case-patterns.csv.gz", patterns, compressed=True)
    with gzip.open(out / "case-patterns.csv.gz", "rt", newline="") as stream:
        check("compressed case-pattern roundtrip rows", len(list(csv.DictReader(stream))) == 2638)

    method = """# Метод пакета B: совместная правильность ответов

Этап exploratory: условия выбраны после просмотра прежних данных. Используется
одна фиксированная пара checkpoints GSM8K и сохранённые 1319 test examples;
каждая метрика анализируется отдельно. Новых forward, GPU-работы, загрузки
весов, обучения, установок, p-values, CI или subgroup search здесь нет.

Вход per_example_scores.csv.gz проверяется по SHA256 frozen bundle; выбранные
baseline/intervention таблицы также сверены с ним. Принятые paired-outcome и
compression-original таблицы сверены с analysis-manifest.json. Перед расчётом
проверены уникальность и полнота test_row_index 0..1318, binary scores и совпадение
source_id/prompt_sha256/input_ids_sha256 всех восьми run IDs и обоих scorers.
Хеши входных manifest сохраняются, но они не заменяют внешнюю доверенную подпись.

Единый reference repairs/breaks — gsm8k-quality-greedy/dora (original PEFT DoRA),
включая r32/e95/e99. Dense DoRA — явный численный контроль. Исторические SVD
переходы от dense проверяются отдельно, с их actual_reference, и не переносятся
в summary от original. LoRA — отдельно обученный опубликованный checkpoint,
не remove_D и не дополнительный seed. Здесь нет оценки training uncertainty.

repair_i = (original_i=0, run_i=1), break_i = (original_i=1, run_i=0);
changed-correctness = repair ∪ break. Summary даёт counts, score, разницу к
original и условные rates repair/original_wrong, break/original_correct.
Pairwise содержит четыре совместных исхода для всех 28 пар на scorer;
названия correct_to_wrong и wrong_to_correct читаются слева направо.
difference = right_score − left_score = (wrong_to_correct−correct_to_wrong)/1319.
Порядок пар фиксирован порядком run IDs ниже, а не величиной эффекта.

Overlap содержит все 21 пары non-original условий на scorer: для repairs,
breaks и changed-correctness показаны размеры обоих множеств, intersection,
union, Jaccard=intersection/union и intersection/размер каждого множества.
При нулевом знаменателе записывается literal undefined. Нулевой union не
подменяется единицей; условные доли также undefined при пустом множестве.
Все показатели описательные, без inferential тестов и поправок.

case-patterns.csv.gz содержит 2638 строк (1319×2): metric, aligned IDs/hashes
и 8-битный correctness_vector. Текстов ответов нет. Позиции битов:
"""
    method += "\n".join(f"{i+1}. {label}: `{run}`" for i, (run,label) in enumerate(zip(RUNS,LABELS)))
    method += """

Упаковка gzip детерминирована (mtime=0). Seeds не используются: расчёты
детерминированны, resampling отсутствует. Код запускается существующей venv
с CUDA_VISIBLE_DEVICES пустым и пятью thread env limits=2; Torch не импортируется.
Runtime, peak RSS, Python/NumPy/platform записаны в validation.json. Peak RSS —
high-water mark процесса по resource.getrusage, Linux KiB→MiB; wall включает
входные проверки, расчёты и запись таблиц/отчётов до финальной validation.

Проверки: hashes, alignment/binary/full N, saved marginals и transitions,
все pairwise маргинальные суммы, identities множеств, пустой union, обратное
восстановление vectors из case-patterns и чтение сжатой таблицы. Выбранные
неизменяемые входы повторно хешируются после записи результатов.

Ограничения: совпадение correctness не означает совпадение текстов, logits или
функции. Пересечение repairs/breaks не устанавливает общий механизм, смысловую
причину изменений, специфику D или необходимость компонента при обучении.
Нет сравнения норм вмешательств как причинного доказательства. Выводы ограничены
этими checkpoints, фиксированным evaluation и scorers; строки теста и матрицы
не являются независимыми обучениями. Текущий пакет не является текстом статьи.
"""
    (out / "METHOD.md").write_text(method)

    def get_overlap(left_label, right_label, metric):
        left = RUNS[LABELS.index(left_label)]
        right = RUNS[LABELS.index(right_label)]
        return next(r for r in overlaps if r["metric"] == metric and {r["left_run_id"], r["right_run_id"]} == {left,right})

    findings = "# Совместные изменения правильности: описательный результат\n\n"
    findings += "Все repairs/breaks ниже определены относительно original PEFT DoRA на 1319 GSM8K examples. Показатели exploratory и описательные; отдельно обученная LoRA и dense DoRA включены в полный перебор пар.\n\n"
    findings += "| Условие | author score | author repairs/breaks | final score | final repairs/breaks |\n|---|---:|---:|---:|---:|\n"
    for run,label in zip(RUNS,LABELS):
        rows = [next(r for r in summary if r["metric"] == metric and r["run_id"] == run) for metric in METRICS]
        findings += f"| {label} | {rows[0]['score']:.6f} | {rows[0]['repairs']}/{rows[0]['breaks']} | {rows[1]['score']:.6f} | {rows[1]['repairs']}/{rows[1]['breaks']} |\n"
    findings += "\n| Пара | scorer | repairs intersection/union | breaks intersection/union | changed intersection/union | changed Jaccard |\n|---|---|---:|---:|---:|---:|\n"
    key_pairs = (("remove_D_all", "base_magnitude_all"), ("remove_D_all", "r32"),
                 ("base_magnitude_all", "r32"), ("remove_D_all", "trained_LoRA"),
                 ("remove_D_all", "dense_DoRA"), ("r32", "e95"), ("r32", "e99"))
    for left,right in key_pairs:
        for metric in METRICS:
            row = get_overlap(left,right,metric)
            findings += f"| {left} / {right} | {metric} | {row['repairs_intersection']}/{row['repairs_union']} | {row['breaks_intersection']}/{row['breaks_union']} | {row['changed_correctness_intersection']}/{row['changed_correctness_union']} | {row['changed_correctness_jaccard']:.4f} |\n"
    findings += """

Полный результат: run-summary.csv (16 строк), pairwise-outcomes.csv (56),
overlap.csv (42) и case-patterns.csv.gz (2638; порядок bits в METHOD.md).
Таблица выше перечисляет фиксированные содержательно связанные пары, а не
результаты поиска подгрупп; все пары доступны в полном CSV.

Близкие aggregate scores совместимы с ненулевыми repairs и breaks. Неполные
пересечения показывают различия множеств изменившейся правильности на этих
сохранённых примерах. Это не сравнение текстов, функций или смысловых ошибок,
не доказательство общего или различного механизма и не вывод о роли D при
обучении. Dense сдвиг и отдельно обученная LoRA требуют отдельных интерпретаций;
SVD-vs-original counts нельзя подменять историческими SVD-vs-dense counts.
Нет новых оценок значимости, seed uncertainty или универсальных claims.
"""
    (out / "FINDINGS.md").write_text(findings)
    for relative, item in inputs.items():
        check("input unchanged after calculation " + relative, sha(repo / relative) == item["sha256"])
    validation = dict(schema_version=1, created_utc=datetime.now(timezone.utc).isoformat(),
                      passed=all(c["passed"] for c in checks), complete=True,
                      counts=dict(run_summary=len(summary), pairwise_outcomes=len(pairs), overlap=len(overlaps), case_patterns=len(patterns)),
                      checks=checks, check_count=len(checks), failed_checks=0,
                      resources=dict(wall_seconds=time.perf_counter()-start,
                                     peak_rss_mib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024,
                                     numerical_thread_limits={k:os.environ[k] for k in THREAD_KEYS},
                                     cuda_visible_devices=os.environ["CUDA_VISIBLE_DEVICES"], gpu_used=False),
                      versions=dict(python=platform.python_version(), numpy=np.__version__, platform=platform.platform()),
                      seeds=None, deterministic=True, uncertainty_scope="descriptive fixed-checkpoint saved-example outcomes only",
                      development_note="Initial pre-output run stopped on an incorrect expected accepted-pair count of 24; corrected to 8 eligible radial original/LoRA comparisons. Source data and computed counts were unchanged.")
    (out / "validation.json").write_text(json.dumps(validation,ensure_ascii=False,indent=2)+"\n")
    outputs = [dict(path=str(p.relative_to(repo)),sha256=sha(p),bytes=p.stat().st_size)
               for p in sorted(out.iterdir()) if p.is_file() and p.name != "manifest.json"]
    manifest = dict(schema_version=1, created_utc=datetime.now(timezone.utc).isoformat(), package="B-outcome-overlap",
                    complete=True, passed=validation["passed"], inputs=list(inputs.values()),
                    code=dict(path=CODE,sha256=sha(repo/CODE),bytes=(repo/CODE).stat().st_size), outputs=outputs,
                    exclusions=["manifest.json self hash"], reference_run_id=RUNS[0],
                    vector_order=[dict(position=i+1,run_id=r,label=l) for i,(r,l) in enumerate(zip(RUNS,LABELS))],
                    metrics=list(METRICS), runtime=validation["resources"], versions=validation["versions"])
    (out / "manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps(dict(passed=True,checks=len(checks),counts=validation["counts"],resources=validation["resources"]),ensure_ascii=False))


if __name__ == "__main__":
    main()
