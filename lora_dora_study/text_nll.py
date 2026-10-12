"""Fixed-text, batch-one causal NLL; no generation or corpus-wide logits.

Each segment resets context and scores its positions 1..length-1. Boundaries
between segments are deliberately unscored. Reuse the returned token segments
for every condition; do not tokenize separately for different models.
"""
import hashlib
import json
import math
import time


def _load_wikitext_rows(revision):
    """Read a bounded export; reject stale, partial, or malformed pages."""
    import re
    from urllib.parse import urlencode
    from urllib.request import urlopen
    if not re.fullmatch(r"[0-9a-f]{40}", revision):
        raise ValueError("Supply an immutable 40-character dataset commit SHA")
    endpoint = "https://datasets-server.huggingface.co/rows"
    rows, total = [], None
    for _ in range(50):
        url = endpoint + "?" + urlencode(dict(dataset="Salesforce/wikitext",
            config="wikitext-2-raw-v1", split="test", offset=len(rows), length=100))
        with urlopen(url, timeout=20) as response:
            if response.headers.get("x-revision") != revision:
                raise ValueError("Dataset export revision differs from requested commit")
            page = json.load(response)
        page_total = page.get("num_rows_total")
        if type(page_total) is not int or not 0 < page_total <= 5000:
            raise ValueError("Dataset export exceeds bounded row count")
        if total is not None and page_total != total:
            raise ValueError("Dataset export row count changed")
        total = page_total
        if page.get("partial") is not False:
            raise ValueError("Dataset export is partial")
        batch = page.get("rows")
        if not isinstance(batch, list) or len(batch) != min(100, total - len(rows)):
            raise ValueError("Dataset export page is incomplete")
        for entry in batch:
            if entry.get("row_idx") != len(rows) or entry.get("truncated_cells") != []:
                raise ValueError("Dataset export rows are noncontiguous or truncated")
            row = entry.get("row", {})
            if not isinstance(row.get("text"), str):
                raise ValueError("Dataset export text is missing")
            rows.append({"text": row["text"]})
        if len(rows) == total:
            return rows, endpoint
    raise ValueError("Dataset export exceeds 50-page limit")


def segment_token_stream(token_ids, *, segment_length=256, max_segments=1024):
    """Take a deterministic prefix of complete, nonoverlapping segments."""
    if segment_length < 2 or max_segments < 1:
        raise ValueError("segment_length >= 2 and max_segments >= 1 required")
    tokens = list(token_ids)
    count = min(len(tokens) // segment_length, max_segments)
    return [tokens[i * segment_length:(i + 1) * segment_length]
            for i in range(count)]


def build_wikitext2_segments(tokenizer, *, revision, segment_length=256,
                            max_segments=1024, dataset=None):
    """Build WikiText-2 raw test segments once, retaining reproducibility metadata.

    ``revision`` must identify the preselected dataset revision. For production
    use an immutable Hub commit, not a moving branch. ``dataset`` is only an
    injection point for CPU fixtures or an already loaded pinned test split.
    The raw texts are joined with two newlines, including empty rows, and
    tokenized without special tokens. A short pilot uses the first 8-16 segments.
    """
    if not revision or revision in {"main", "master"}:
        raise ValueError("Supply a pinned dataset revision")
    source_api = None
    if dataset is None:
        dataset, source_api = _load_wikitext_rows(revision)
    dataset_fingerprint = getattr(dataset, "_fingerprint", None)
    dataset = list(dataset)
    exported_rows_sha256 = hashlib.sha256(json.dumps(dataset,
        ensure_ascii=False, separators=(",", ":")).encode()).hexdigest()
    text = "\n\n".join(row["text"] for row in dataset)
    encoded = tokenizer(text, add_special_tokens=False, truncation=False)
    segments = segment_token_stream(encoded["input_ids"],
        segment_length=segment_length, max_segments=max_segments)
    if not segments:
        raise ValueError("Corpus contains no complete segment")
    digest = hashlib.sha256(json.dumps(segments, separators=(",", ":")).encode()).hexdigest()
    metadata = dict(dataset="Salesforce/wikitext", config="wikitext-2-raw-v1",
        split="test", requested_revision=revision,
        source_api=source_api, exported_rows_sha256=exported_rows_sha256,
        dataset_fingerprint=dataset_fingerprint,
        tokenizer_name=getattr(tokenizer, "name_or_path", None),
        tokenizer_revision=getattr(tokenizer, "init_kwargs", {}).get("_commit_hash"),
        segment_length=segment_length, requested_max_segments=max_segments,
        segment_count=len(segments), input_token_count=sum(map(len, segments)),
        scored_token_count=sum(len(s) - 1 for s in segments),
        token_segments_sha256=digest,
        raw_text_sha256=hashlib.sha256(text.encode()).hexdigest(),
        join_separator="\n\n", add_special_tokens=False,
        context_policy="independent nonoverlapping segments; first token unscored",
        dropped_tail_tokens=len(encoded["input_ids"]) % segment_length,
        unused_complete_segments=max(0, len(encoded["input_ids"]) // segment_length - len(segments)))
    return segments, metadata


def evaluate_text_nll(model, segments, *, device=None, warmup_segments=0):
    """Return token-weighted NLL and per-segment measurements in nats.

    Accept sequences of token IDs, or mappings with input_ids and optional
    attention_mask/labels (labels=-100 masks a target). Inputs are one-dimensional
    or shape [1, length]. Both endpoints of a scored transition must be attended.
    Warmup explicitly repeats the first N segments and excludes them from timings
    and totals. Model training/eval mode is restored, and no optimizer is used.
    CUDA synchronization surrounds each measurement when inputs are on CUDA.
    """
    import torch
    import torch.nn.functional as F

    if warmup_segments < 0:
        raise ValueError("warmup_segments must be nonnegative")
    if device is None:
        device = next(model.parameters()).device
    device = torch.device(device)

    def sync():
        if device.type == "cuda":
            torch.cuda.synchronize(device)

    def tensor1(value, name):
        result = torch.as_tensor(value, dtype=torch.long, device=device)
        if result.ndim == 2 and result.shape[0] == 1:
            result = result[0]
        if result.ndim != 1:
            raise ValueError(name + " must be one segment (batch=1)")
        return result

    def score(segment):
        fields = segment if isinstance(segment, dict) else {"input_ids": segment}
        ids = tensor1(fields["input_ids"], "input_ids")
        if ids.numel() < 2:
            raise ValueError("Each segment needs at least two tokens")
        mask = tensor1(fields.get("attention_mask", torch.ones_like(ids)), "attention_mask")
        labels = tensor1(fields.get("labels", ids), "labels")
        if mask.shape != ids.shape or labels.shape != ids.shape:
            raise ValueError("Masks and labels must match input_ids")
        valid = (mask[:-1] != 0) & (mask[1:] != 0) & (labels[1:] != -100)
        count = int(valid.sum().item())
        if count == 0:
            raise ValueError("Segment has no scored next-token targets")
        output = model(input_ids=ids.unsqueeze(0), attention_mask=mask.unsqueeze(0),
                       use_cache=False)
        logits = output.logits
        if logits.ndim != 3 or logits.shape[:2] != (1, ids.numel()):
            raise ValueError("Model logits must have shape [1, segment_length, vocabulary]")
        # FP32 CE, float64 summation; no logits survive the function call.
        losses = F.cross_entropy(logits[0, :-1][valid].float(), labels[1:][valid],
                                 reduction="none")
        return float(losses.double().sum().item()), count

    iterator = iter(segments)
    prefix = []
    for _ in range(warmup_segments):
        try:
            prefix.append(next(iterator))
        except StopIteration:
            raise ValueError("warmup_segments exceeds available segments") from None
    training = model.training
    rows = []
    warmup_elapsed = 0.0
    try:
        model.eval()
        with torch.inference_mode():
            if prefix:
                sync()
                start = time.perf_counter()
                for segment in prefix:
                    score(segment)
                sync()
                warmup_elapsed = time.perf_counter() - start
            from itertools import chain
            sync()
            total_start = time.perf_counter()
            for index, segment in enumerate(chain(prefix, iterator)):
                sync()
                start = time.perf_counter()
                summed_nll, token_count = score(segment)
                sync()
                elapsed = time.perf_counter() - start
                rows.append(dict(index=index, summed_nll=summed_nll,
                    token_count=token_count, mean_nll=summed_nll / token_count,
                    elapsed_seconds=elapsed))
            sync()
            elapsed = time.perf_counter() - total_start
    finally:
        model.train(training)
    if not rows:
        raise ValueError("At least one segment is required")
    total = math.fsum(row["summed_nll"] for row in rows)
    count = sum(row["token_count"] for row in rows)
    return dict(summed_nll=total, token_count=count, mean_nll=total / count,
        elapsed_seconds=elapsed, tokens_per_second=count / elapsed if elapsed else None,
        segment_count=len(rows), per_segment=rows, warmup_segments=warmup_segments,
        warmup_elapsed_seconds=warmup_elapsed, batch_size=1, nll_unit="nats",
        aggregation="sum shifted token CE / count scored tokens")
