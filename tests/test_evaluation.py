import tempfile
import unittest
import json
from pathlib import Path
from lora_dora_study.evaluation import author_answer, final_answer, gold_answer, paired_bootstrap
from lora_dora_study.evaluation import sha256_file

class EvaluationTests(unittest.TestCase):

    def test_scorers_expose_first_number_fallback_difference(self):
        text = 'There are 12 boxes containing 5 items, so the answer is 60.'
        self.assertEqual(author_answer(text), '12')
        self.assertEqual(final_answer(text), '60')
        self.assertEqual(author_answer(text + '\n#### 60'), '60')
        self.assertEqual(gold_answer('work\n#### 1,200'), '1200')

    def test_cleaning_and_boxed_precedence(self):
        text = '<think>999</think> 4*5=20, \\boxed{20}'
        self.assertEqual(author_answer(text), '4')
        self.assertEqual(final_answer(text), '20')
        self.assertEqual(final_answer('No numeric answer'), '')

    def test_paired_ci_and_direction(self):
        self.assertEqual(paired_bootstrap([True] * 4, [False] * 4, 100)['ci95'], [-1, -1])
        self.assertEqual(paired_bootstrap([True, False], [True, False], 100)['ci95'], [0, 0])
        with self.assertRaises(ValueError):
            paired_bootstrap([True], [], 100)

class WaiterTests(unittest.TestCase):
    pass

class ComparisonTests(unittest.TestCase):

    def make_runs(self, root):
        directories = {}
        for role in ('base', 'lora', 'dora'):
            folder = root / role
            folder.mkdir()
            prediction = dict(test_row_index=0, question='test', gold='1', prompt_sha256='prompt', input_ids_sha256='ids', input_tokens=2, author_correct=role == 'lora', final_correct=role == 'lora')
            path = folder / 'predictions.jsonl'
            path.write_text(json.dumps(prediction) + '\n')
            report = dict(role=role, status='complete', full_evaluation=True, predictions_sha256=sha256_file(path), protocol=dict(expected_rows=1), protocol_sha256='config', generation_config={}, versions={}, artifacts={}, code_revision='revision', source_sha256={}, truncated_prompts=0, hit_token_limit=0)
            (folder / 'summary.json').write_text(json.dumps(report))
            directories[role] = folder
        return directories
if __name__ == '__main__':
    unittest.main()
