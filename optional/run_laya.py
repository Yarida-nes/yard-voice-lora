"""Train the Laya decision model on the training set and test it on the test set.

Laya answers one question straight from the sentence: ACT, READ_BACK or ASK_AGAIN.
It does not produce JSON and uses no yard rules, so it is compared on the decision only.

Needs its own environment (PyTorch + laya), e.g.:
    python -m venv laya-env
    laya-env/Scripts/python -m pip install torch --index-url https://download.pytorch.org/whl/cu124
    laya-env/Scripts/python -m pip install laya==0.5.1

Run from the project folder:
    laya-env/Scripts/python optional/run_laya.py
"""
import json
import statistics
import time
from pathlib import Path

import laya
import torch

ROOT = Path(__file__).parent.parent

QUESTIONS = {
    "decision": {
        "type": "choice",
        "instructions": "A yard worker gave this spoken command. Should the yard system act on it now, "
                        "read it back to confirm first, or ask the worker to say it again?",
        "criteria": {
            "ACT": "clear, complete and valid: act on it now",
            "READ_BACK": "valid but risky (a trailer number that looks like another one, or a release): confirm first",
            "ASK_AGAIN": "unclear, missing the trailer or the place, an unknown trailer, a busy or impossible door, "
                         "or cancelled: ask again",
        },
    }
}


def load(name):
    return [json.loads(l) for l in (ROOT / "data" / name).read_text(encoding="utf-8").splitlines() if l.strip()]


def run(learner, rows):
    """Decide every row, timing each decision on its own."""
    preds, secs = [], []
    for r in rows:
        if torch.cuda.is_available():
            torch.cuda.synchronize()
        t = time.perf_counter()
        preds.append(learner.decide(r["text"])["answers"]["decision"]["answer"])
        if torch.cuda.is_available():
            torch.cuda.synchronize()
        secs.append(time.perf_counter() - t)
    return preds, secs


def report(name, rows, preds, secs):
    pairs = list(zip(rows, preds))
    right = sum(p == r["decision"] for r, p in pairs)
    unsafe = sum(p == "ACT" and r["decision"] != "ACT" for r, p in pairs)
    gen = sum(p == r["decision"] for r, p in pairs if r["source"] == "generated")
    hw = sum(p == r["decision"] for r, p in pairs if r["source"] == "handwritten")
    print(f"{name}: decision right {right}/100 | unsafe ACT {unsafe} | generated {gen}/90 | "
          f"hand-written {hw}/10 | median {statistics.median(secs):.3f} s | slowest {max(secs):.3f} s")
    return {"right": right, "unsafe": unsafe, "generated": gen, "handwritten": hw,
            "median_s": round(statistics.median(secs), 4), "max_s": round(max(secs), 4)}


def main():
    train, test = load("train.jsonl"), load("test.jsonl")
    device = torch.cuda.get_device_name(0) if torch.cuda.is_available() else "CPU"
    print("device:", device)

    t = time.perf_counter()
    before = laya.Learner(QUESTIONS, examples=None, auto=False)
    print(f"reader loaded in {time.perf_counter() - t:.1f} s")
    run(before, test[:3])  # warm up
    p0, s0 = run(before, test)
    r0 = report("BEFORE TRAINING", test, p0, s0)

    t = time.perf_counter()
    examples = [(r["text"], {"decision": r["decision"]}) for r in train]
    after = laya.Learner(QUESTIONS, examples=examples, auto=False, reader=before.reader)
    train_s = time.perf_counter() - t
    print(f"training: {train_s:.1f} s | {after.report}")
    p1, s1 = run(after, test)
    r1 = report("AFTER TRAINING", test, p1, s1)

    out = ROOT / "results" / "preds_laya_laptop.jsonl"
    with out.open("w", encoding="utf-8") as f:
        for r, a, b, sa, sb in zip(test, p0, p1, s0, s1):
            f.write(json.dumps({"id": r["id"], "text": r["text"], "source": r["source"], "kind": r["kind"],
                                "decision": r["decision"], "laya_before": a, "laya_after": b,
                                "seconds_before": round(sa, 4), "seconds_after": round(sb, 4)}) + "\n")
    summary = {"device": device, "training_seconds": round(train_s, 1), "fit_report": after.report,
               "before": r0, "after": r1}
    (ROOT / "results" / "laya_laptop_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print("saved", out)


if __name__ == "__main__":
    main()
