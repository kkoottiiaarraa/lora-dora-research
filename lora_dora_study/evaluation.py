"""GSM8K formatting/scoring without Torch or dataset-library dependencies."""
import hashlib
from decimal import Decimal
import json
import random
import re


def sha256_file(path):
    digest = hashlib.sha256()
    with open(path, "rb") as stream:
        for block in iter(lambda: stream.read(8 * 1024**2), b""):
            digest.update(block)
    return digest.hexdigest()


def source_fingerprint(root):
    """Capture exact runtime source even when a checkout has uncommitted changes."""
    paths = sorted(p for folder in ("lora_dora_study", "scripts", "configs")
                   for p in (root / folder).glob("*") if p.suffix in (".py", ".json"))
    return {str(p.relative_to(root)): sha256_file(p) for p in paths}


def gold_answer(text):
    match = re.search(r"####\s*([^\n\r]+)", text)
    candidate = match.group(1).strip() if match else text.strip()
    number = re.search(r"[-+]?\d[\d,]*\.?\d*", candidate)
    return number.group(0).replace(",", "").strip() if number else candidate


def clean_generated(text):
    text = re.sub(r"<think>.*?</think>", " ", text, flags=re.I | re.S)
    text = re.sub(r"<\|im_(?:start|end)\|>", " ", text)
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def author_answer(text):
    """ShadowPEFT scorer, including first-number fallback; keep for reproduction."""
    return gold_answer(clean_generated(text)) if text else ""


def final_answer(text):
    """Sensitivity scorer: ####, boxed number, then LAST number, never gold-aware."""
    cleaned = clean_generated(text)
    marked = re.findall(r"####\s*([-+]?\d[\d,]*\.?\d*)", cleaned)
    boxed = re.findall(r"\\boxed\{\s*([-+]?\d[\d,]*\.?\d*)\s*\}", cleaned)
    numbers = marked or boxed or re.findall(r"[-+]?\d[\d,]*\.?\d*", cleaned)
    return format(Decimal(numbers[-1].replace(",", "")).normalize(), "f") if numbers else ""


def prompt_text(tokenizer, question):
    return tokenizer.apply_chat_template(
        [{"role": "user", "content": "Question: " + question + "\nAnswer:"}],
        tokenize=False, add_generation_prompt=True, enable_thinking=False)


def paired_bootstrap(left, right, samples=10000, seed=42):
    """CI for right - left. Inputs are paired correctness, not independent means."""
    if len(left) != len(right) or not left:
        raise ValueError("Nonempty matched predictions required")
    if samples < 100:
        raise ValueError("At least 100 bootstrap replicates required")
    differences = [int(b) - int(a) for a, b in zip(left, right)]
    rng = random.Random(seed)
    distribution = sorted(sum(rng.choices(differences, k=len(left))) / len(left)
                          for _ in range(samples))
    return dict(n=len(left), difference=sum(differences)/len(left),
                ci95=[distribution[int(.025*samples)], distribution[int(.975*samples)]],
                resamples=samples, seed=seed,
                scope="paired test examples, not independent training repetitions")


def read_predictions(path):
    rows = [json.loads(line) for line in path.read_text().splitlines()]
    if len({r["test_row_index"] for r in rows}) != len(rows):
        raise ValueError("Duplicate predictions")
    return rows
