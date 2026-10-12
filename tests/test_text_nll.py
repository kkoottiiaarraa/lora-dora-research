import math
from types import SimpleNamespace
import unittest

from lora_dora_study.text_nll import (
    build_wikitext2_segments, evaluate_text_nll, segment_token_stream)

try:
    import torch
except ImportError:
    torch = None


class CorpusTests(unittest.TestCase):
    def test_segmentation_is_nonoverlapping_prefix_and_drops_short_tail(self):
        self.assertEqual(segment_token_stream(range(11), segment_length=3, max_segments=2),
                         [[0, 1, 2], [3, 4, 5]])
        self.assertEqual(segment_token_stream(range(8), segment_length=3),
                         [[0, 1, 2], [3, 4, 5]])
        with self.assertRaises(ValueError):
            segment_token_stream([1, 2], segment_length=1)

    def test_corpus_fixed_text_tokenization_and_metadata(self):
        class Tokenizer:
            name_or_path = "fixture"
            init_kwargs = {"_commit_hash": "tokenizer-commit"}

            def __call__(self, text, **kwargs):
                self.text = text
                self.kwargs = kwargs
                return {"input_ids": list(range(len(text)))}

        tokenizer = Tokenizer()
        rows = [{"text": "abc"}, {"text": ""}, {"text": "defg"}]
        segments, metadata = build_wikitext2_segments(tokenizer, revision="fixture-commit",
            segment_length=3, max_segments=2, dataset=rows)
        self.assertEqual(tokenizer.text, "abc\n\n\n\ndefg")
        self.assertEqual(tokenizer.kwargs, dict(add_special_tokens=False, truncation=False))
        self.assertEqual(segments, [[0, 1, 2], [3, 4, 5]])
        self.assertEqual(metadata["scored_token_count"], 4)
        self.assertEqual(metadata["tokenizer_revision"], "tokenizer-commit")
        self.assertEqual(build_wikitext2_segments(tokenizer, revision="fixture-commit",
            segment_length=3, max_segments=2, dataset=rows)[1], metadata)
        with self.assertRaisesRegex(ValueError, "pinned"):
            build_wikitext2_segments(tokenizer, revision="main", dataset=rows)


@unittest.skipIf(torch is None, "Torch is available in the server test environment")
class NLLTests(unittest.TestCase):
    def model(self):
        class ToyModel(torch.nn.Module):
            def __init__(self):
                super().__init__()
                self.anchor = torch.nn.Parameter(torch.zeros(()))
                self.calls = 0

            def forward(self, input_ids, attention_mask, use_cache):
                self.calls += 1
                assert not self.training
                assert torch.is_inference_mode_enabled()
                assert not use_cache
                assert input_ids.shape[0] == 1
                # Token 0 -> p(next=0)=.8; token 1 -> p(next=0)=.3.
                table = torch.tensor([[.8, .2], [.3, .7]])
                return SimpleNamespace(logits=table[input_ids].log())
        return ToyModel()

    def test_gold_shifted_ce_and_token_weighted_aggregation(self):
        model = self.model()
        result = evaluate_text_nll(model, [[0, 0, 1, 1], [1, 0]])
        gold = -math.log(.8) - math.log(.2) - math.log(.7) - math.log(.3)
        self.assertAlmostEqual(result["summed_nll"], gold, places=6)
        self.assertEqual(result["token_count"], 4)
        self.assertAlmostEqual(result["mean_nll"], gold / 4, places=6)
        row_mean = sum(r["mean_nll"] for r in result["per_segment"]) / 2
        self.assertNotAlmostEqual(result["mean_nll"], row_mean, places=4)
        self.assertTrue(model.training)
        self.assertEqual(model.calls, 2)
        self.assertGreater(result["elapsed_seconds"], 0)

    def test_attention_and_label_mask_both_endpoints(self):
        result = evaluate_text_nll(self.model(), [dict(input_ids=[1, 0, 0, 1, 1],
            attention_mask=[0, 1, 1, 1, 1], labels=[-100, 0, 0, -100, 1])])
        self.assertEqual(result["token_count"], 2)
        self.assertAlmostEqual(result["summed_nll"], -math.log(.8)-math.log(.7), places=6)

    def test_warmup_is_explicit_excluded_and_iterator_replayed(self):
        model = self.model()
        model.eval()
        result = evaluate_text_nll(model, iter([[0, 1], [1, 0]]), warmup_segments=1)
        self.assertEqual(model.calls, 3)
        self.assertEqual(result["token_count"], 2)
        self.assertEqual(result["segment_count"], 2)
        self.assertEqual(result["warmup_segments"], 1)
        self.assertFalse(model.training)

    def test_invalid_inputs_and_mode_restored_on_error(self):
        for segment in ([1], [[0, 1], [1, 0]],
                        {"input_ids": [0, 1], "labels": [-100, -100]},
                        {"input_ids": [0, 1], "attention_mask": [1]}):
            model = self.model()
            with self.assertRaises(ValueError):
                evaluate_text_nll(model, [segment])
            self.assertTrue(model.training)
        with self.assertRaises(ValueError):
            evaluate_text_nll(self.model(), [])
        with self.assertRaises(ValueError):
            evaluate_text_nll(self.model(), [[0, 1]], warmup_segments=2)


class DatasetExportTests(unittest.TestCase):
    def test_revision_mismatch_is_rejected(self):
        from unittest.mock import MagicMock, patch
        from lora_dora_study.text_nll import _load_wikitext_rows
        response = MagicMock()
        response.__enter__.return_value.headers = {"x-revision": "b" * 40}
        with patch("urllib.request.urlopen", return_value=response) as request:
            with self.assertRaisesRegex(ValueError, "revision differs"):
                _load_wikitext_rows("a" * 40)
        self.assertEqual(request.call_count, 1)
        self.assertEqual(request.call_args.kwargs["timeout"], 20)


if __name__ == "__main__":
    unittest.main()
