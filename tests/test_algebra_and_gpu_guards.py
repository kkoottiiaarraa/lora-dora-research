import unittest
import contextlib
import tempfile
import numpy as np
from lora_dora_study.algebra import (best_rank_approximation, dora_components,
                                     relative_output_error)
from lora_dora_study.server import idle_gpu, parse_gpus
from lora_dora_study.leases import gpu_lease


class AlgebraTests(unittest.TestCase):
    def test_rank_one_direction_can_give_full_rank_effective_update(self):
        base = np.eye(4)
        update = np.ones((4, 1)) @ np.ones((1, 4)) / 10
        adapted, radial, scaled = dora_components(base, update, np.arange(2, 6))
        np.testing.assert_allclose(adapted - base, radial + scaled)
        np.testing.assert_allclose(np.linalg.norm(adapted, axis=1), np.arange(2, 6))
        self.assertEqual(np.linalg.matrix_rank(scaled), 1)
        self.assertEqual(np.linalg.matrix_rank(adapted - base), 4)

    def test_attention_scaling_preserves_logits_algebraically(self):
        rng = np.random.default_rng(42)
        x, q, k = rng.normal(size=(3, 4)), rng.normal(size=(4, 4)), rng.normal(size=(4, 4))
        np.testing.assert_allclose((x @ q.T) @ (x @ k.T).T,
                                   (x @ (8 * q).T) @ (x @ (k / 8).T).T)

    def test_rank_projection_and_input_metric_are_different(self):
        update = np.diag([3., 2., 1.])
        approximate = best_rank_approximation(update, 1)
        self.assertAlmostEqual(relative_output_error(update, approximate, np.eye(3)), 5 / 14)
        self.assertEqual(relative_output_error(update, approximate, np.array([[1., 0., 0.]])), 0)

    def test_undefined_normalization_is_rejected(self):
        with self.assertRaises(ValueError):
            dora_components(np.eye(2), -np.eye(2), np.ones(2))


class GpuTests(unittest.TestCase):
    def test_fourth_worker_blocked_and_released_slot_reusable(self):
        with tempfile.TemporaryDirectory() as directory:
            with contextlib.ExitStack() as stack:
                for number in range(3):
                    stack.enter_context(gpu_lease('GPU-' + str(number), directory))
                with self.assertRaises(RuntimeError):
                    with gpu_lease('GPU-4', directory):
                        self.fail('A fourth worker was admitted')
                with self.assertRaises(BlockingIOError):
                    with gpu_lease('GPU-0', directory):
                        self.fail('Two workers acquired the same GPU')
            with gpu_lease('GPU-4', directory):
                pass

    def test_process_or_memory_or_utilization_blocks_gpu(self):
        gpu = parse_gpus("0, GPU-abc, NVIDIA RTX A4000, 16384, 40, 0\n")[0]
        self.assertTrue(idle_gpu(gpu, []))
        self.assertFalse(idle_gpu(gpu, [{"gpu_uuid": "GPU-abc", "pid": 123}]))
        self.assertFalse(idle_gpu(dict(gpu, used_mib=5000), []))
        self.assertFalse(idle_gpu(dict(gpu, utilization_percent=90), []))

    def test_unknown_utilization_fails_closed(self):
        with self.assertRaises(ValueError):
            parse_gpus("0, GPU-abc, NVIDIA RTX A4000, 16384, 40, N/A\n")


if __name__ == "__main__":
    unittest.main()
