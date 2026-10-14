"""CPU checks for sampling, pilot authorization limits, and SQuAD reporting."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('next_pilot', Path(__file__).with_name('pilot.py'))
pilot = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pilot)


class PilotTests(unittest.TestCase):
    def args(self, *extra):
        return ['--gpu-uuid', 'GPU-test', '--task', 'mmlu', '--mode', 'remove_d', '--output-dir', '/tmp/new-pilot-test', *extra]

    def test_quantiles_and_no_duplicates(self):
        selected = pilot.balanced_indices(list(range(99)), 6)
        self.assertEqual(len(set(selected)), 6)
        self.assertEqual([sum(i//33 == q for i in selected) for q in range(3)], [2, 2, 2])
        self.assertEqual(pilot.balanced_indices([1], 6), [0])

    def test_jsonl_unicode_separators_inside_strings(self):
        rows = [dict(question='alpha\u2028beta\u2029gamma'), dict(question='next')]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/'data.jsonl'
            path.write_text('\n'.join(json.dumps(row, ensure_ascii=False) for row in rows)+'\n')
            self.assertEqual(pilot.read_rows(path), rows)

    def test_response_quantile_balance(self):
        selected = pilot.balanced_indices(list(range(120)), 6, {i: i%40 for i in range(120)})
        self.assertEqual(len(set(selected)), 6)
        for q in range(3):
            self.assertEqual(sum(i//40 == q and i%40 < 20 for i in selected), 1)
            self.assertEqual(sum(i//40 == q and i%40 >= 20 for i in selected), 1)

    def test_default_is_bounded_pilot(self):
        a = pilot.arguments(self.args())
        self.assertEqual((a.stage, a.budget_seconds, a.timing_points, a.condition), ('pilot', 900, [], 'remove_d'))

    def test_full_requires_explicit_auth_and_budget(self):
        with self.assertRaises(SystemExit):
            pilot.arguments(self.args('--stage', 'evaluate'))
        a = pilot.arguments(self.args('--stage', 'evaluate', '--evaluation-authorized', '--budget-seconds', '3600'))
        self.assertEqual(a.budget_seconds, 3600)

    def test_pilot_cannot_expand(self):
        for options in [('--budget-seconds', '901'), ('--pilot-cases', '13'), ('--minimum-free-mib', '8000')]:
            with self.assertRaises(SystemExit):
                pilot.arguments(self.args(*options))

    def test_squad_answerability_and_empty_group(self):
        cases = [dict(answerable=True, metrics=dict(exact=1., f1=1.)), dict(answerable=False, metrics=dict(exact=0., f1=.25))]
        metrics = pilot.answerability_metrics(cases)
        self.assertEqual(metrics['answerable']['count'], 1)
        self.assertEqual(metrics['unanswerable']['f1'], .25)
        self.assertEqual(set(pilot.answerability_metrics(cases[:1])), {'answerable'})

    def test_forecast_cache_free_growth_and_actual_rows(self):
        case = dict(seconds=2., input_tokens=10, generated_tokens=2)
        result = pilot.forecast([case], [10, 100], {0: 2, 1: 2}, 10)
        self.assertEqual(result['full_dataset_cases'], 2)
        self.assertGreater(result['scenarios']['attention_quadratic']['median_seconds'], result['scenarios']['sequence_linear']['median_seconds'])


if __name__ == '__main__':
    unittest.main()
