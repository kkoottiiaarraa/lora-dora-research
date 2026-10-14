import tempfile
import unittest
import json
from pathlib import Path
from lora_dora_study.evaluation import author_answer, final_answer, gold_answer, paired_bootstrap
from lora_dora_study.evaluation import sha256_file


class EvaluationTests(unittest.TestCase):
    def test_scorers_expose_first_number_fallback_difference(self):
        text = "There are 12 boxes containing 5 items, so the answer is 60."
        self.assertEqual(author_answer(text), "12")
        self.assertEqual(final_answer(text), "60")
        self.assertEqual(author_answer(text + "\n#### 60"), "60")
        self.assertEqual(gold_answer("work\n#### 1,200"), "1200")

    def test_cleaning_and_boxed_precedence(self):
        text = "<think>999</think> 4*5=20, \\boxed{20}"
        self.assertEqual(author_answer(text), "4")
        self.assertEqual(final_answer(text), "20")
        self.assertEqual(final_answer("No numeric answer"), "")

    def test_paired_ci_and_direction(self):
        self.assertEqual(paired_bootstrap([True]*4, [False]*4, 100)["ci95"], [-1, -1])
        self.assertEqual(paired_bootstrap([True, False], [True, False], 100)["ci95"], [0, 0])
        with self.assertRaises(ValueError):
            paired_bootstrap([True], [], 100)


class WaiterTests(unittest.TestCase):
    def test_same_uuid_must_be_idle_twice_and_compute_process_blocks(self):
        from scripts.wait_for_pilot import stable_idle
        gpu = dict(uuid="GPU-a", used_mib=0, utilization_percent=0)
        current, stable = stable_idle(set(), dict(gpus=[gpu], compute_processes=[]))
        self.assertFalse(stable)
        self.assertEqual(stable_idle(current, dict(gpus=[gpu], compute_processes=[]))[1], {"GPU-a"})
        busy = dict(gpus=[gpu], compute_processes=[dict(gpu_uuid="GPU-a")])
        self.assertFalse(stable_idle(current, busy)[1])


class ComparisonTests(unittest.TestCase):
    def make_runs(self, root):
        directories = {}
        for role in ("base", "lora", "dora"):
            folder = root / role
            folder.mkdir()
            prediction = dict(test_row_index=0, question="test", gold="1",
                prompt_sha256="prompt", input_ids_sha256="ids", input_tokens=2,
                author_correct=role=="lora", final_correct=role=="lora")
            path = folder / "predictions.jsonl"
            path.write_text(json.dumps(prediction)+"\n")
            report = dict(role=role, status="complete", full_evaluation=True,
                predictions_sha256=sha256_file(path), protocol=dict(expected_rows=1),
                protocol_sha256="config", generation_config={}, versions={}, artifacts={},
                code_revision="revision", source_sha256={}, truncated_prompts=0, hit_token_limit=0)
            (folder / "summary.json").write_text(json.dumps(report))
            directories[role] = folder
        return directories

    def test_negative_dora_comparison_preserved_and_mismatched_input_rejected(self):
        from scripts.compare_gsm8k import compare
        with tempfile.TemporaryDirectory() as directory:
            paths = self.make_runs(Path(directory))
            result = compare(paths)
            self.assertEqual(result["contrasts"]["author"]["dora_minus_lora"]["difference"], -1)
            path = paths["dora"] / "predictions.jsonl"
            row = json.loads(path.read_text())
            row["input_ids_sha256"] = "different"
            path.write_text(json.dumps(row)+"\n")
            summary = paths["dora"] / "summary.json"
            report = json.loads(summary.read_text())
            report["predictions_sha256"] = sha256_file(path)
            summary.write_text(json.dumps(report))
            with self.assertRaisesRegex(ValueError, "Unmatched input"):
                compare(paths)

    def test_smoke_cannot_be_reported_as_full_quality(self):
        from scripts.compare_gsm8k import compare
        with tempfile.TemporaryDirectory() as directory:
            paths = self.make_runs(Path(directory))
            summary = paths["lora"] / "summary.json"
            report = json.loads(summary.read_text())
            report["full_evaluation"] = False
            summary.write_text(json.dumps(report))
            with self.assertRaisesRegex(ValueError, "Complete full evaluation"):
                compare(paths)


if __name__ == "__main__":
    unittest.main()
