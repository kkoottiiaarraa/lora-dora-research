"""Matched ShadowPEFT benchmark prompts and per-example metrics."""
import re
import string
from collections import Counter
from lora_dora_study.evaluation import clean_generated, author_answer, final_answer, gold_answer


def user_content(task, row):
    if task == "gsm8k":
        return "Question: " + row["question"] + "\nAnswer:"
    if task == "mmlu":
        return ("Question: " + row["question"] + "\n\nOptions:\n" +
                "".join(letter+": "+choice+"\n" for letter, choice in zip("ABCD", row["choices"])) +
                "\nInstructions: Answer with ONLY the letter (A, B, C, or D). "
                "Do not include any explanation, reasoning, or additional text. Answer:\n\n")
    if task == "squadv2":
        return ("Answer the question using the provided context.\n"
                "If the question is unanswerable from the context, respond with exactly: unanswerable\n\n"
                "Context:\n"+row["context"]+"\n\nQuestion:\n"+row["question"]+"\n\nAnswer:")
    raise ValueError("Unknown benchmark")


def normalize_span(text):
    text = "".join(c for c in text.lower() if c not in string.punctuation)
    return " ".join(re.sub(r"\b(a|an|the)\b", " ", text).split())


def span_score(prediction, gold):
    left, right = normalize_span(prediction), normalize_span(gold)
    exact = float(left == right)
    if not left or not right:
        return exact, exact
    shared = sum((Counter(left.split()) & Counter(right.split())).values())
    f1 = 2*shared/(len(left.split())+len(right.split()))
    return exact, f1


def score(task, text, row):
    if task == "gsm8k":
        gold = gold_answer(row["answer"])
        return dict(author_em=float(author_answer(text)==gold),
                    final_em=float(final_answer(text)==gold))
    if task == "mmlu":
        cleaned = clean_generated(text)
        match = re.search(r"\b([ABCD])\b", cleaned, re.I)
        if not match:
            match = re.search(r"(?:answer|option)\s*[:=-]?\s*([ABCD])", cleaned, re.I)
        answer = match.group(1).upper() if match else ""
        return dict(accuracy=float(answer == "ABCD"[row["answer"]]))
    if task == "squadv2":
        predicted = clean_generated(text)
        if predicted.lower() in {"unanswerable", "no answer", "n/a", "none", ""}:
            predicted = ""
        golds = [g for g in row["answers"]["text"] if normalize_span(g)] or [""]
        scores = [span_score(predicted, gold) for gold in golds]
        return dict(exact=max(s[0] for s in scores), f1=max(s[1] for s in scores))
    raise ValueError("Unknown benchmark")
