import itertools
import unittest
from lora_dora_study.rank_budget import allocate


class RankBudgetTests(unittest.TestCase):
    def test_matches_exhaustive_optimum_with_unequal_costs(self):
        spectra = {'v': [9., 4., 1.], 'o': [8., 7., 2.], 'x': [5., 2., .5]}
        costs = {'v': 3, 'o': 5, 'x': 2}
        for budget in range(31):
            feasible = []
            names = sorted(spectra)
            for ranks in itertools.product(range(4), repeat=3):
                if sum(costs[n]*r for n, r in zip(names, ranks)) == budget:
                    gain = sum(sum(spectra[n][:r]) for n, r in zip(names, ranks))
                    feasible.append((gain, ranks))
            if not feasible:
                with self.assertRaises(ValueError): allocate(spectra, costs, budget)
            else:
                expected = min(feasible, key=lambda x: (-x[0], x[1]))
                ranks, gain = allocate(spectra, costs, budget)
                self.assertEqual((gain, tuple(ranks[n] for n in names)), expected)

    def test_infeasible_and_nonfinite(self):
        with self.assertRaises(ValueError): allocate({'v': [1.]}, {'v': 2}, 1)
        with self.assertRaises(ValueError): allocate({'v': [float('nan')]}, {'v': 2}, 2)


if __name__ == '__main__': unittest.main()
