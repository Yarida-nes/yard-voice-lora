"""Option 1: Laya reads the action and the place, code reads the trailer number, rules decide.

The same job as Qwen in run_model.py (fill in the JSON, then src/rules.py decides), so the
results can be compared directly with score.py.

Run from the project folder with the Laya environment:
    laya-env/Scripts/python optional/run_laya_fields.py
"""
import json
import statistics
import sys
import time
from pathlib import Path

import laya
import torch

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "optional"))
from rules import decide  # noqa: E402
from read_unit import read_unit  # noqa: E402

DOORS = {f"door_0{i}": f"door {i}" for i in range(1, 9)}
QUESTIONS = {
    "action": {
        "type": "choice",
        "instructions": "A yard worker gave this spoken command. What do they want done with the trailer? "
                        "If they correct themselves, use the last thing they said.",
        "criteria": {
            "move": "move it to a door or the staging area",
            "park": "park it",
            "release": "let it leave the site",
            "status": "ask where it is",
            "none": "unclear, or the worker cancelled the command",
        },
    },
    "to": {
        "type": "choice",
        "instructions": "A yard worker gave this spoken command. Where should the trailer go? "
                        "If they correct themselves, use the last thing they said.",
        "criteria": {**DOORS, "staging": "the staging area", "parking": "parking",
                     "none": "no place was said, or it is not a move or park"},
    },
}


def load(name):
    return [json.loads(l) for l in (ROOT / "data" / name).read_text(encoding="utf-8").splitlines() if l.strip()]


def none_to_null(v):
    return None if v == "none" else v


def run(learner, rows):
    out = []
    for r in rows:
        if torch.cuda.is_available():
            torch.cuda.synchronize()
        t = time.perf_counter()
        ans = learner.decide(r["text"])["answers"]
        unit = read_unit(r["text"])
        if torch.cuda.is_available():
            torch.cuda.synchronize()
        secs = time.perf_counter() - t
        pred = {"action": none_to_null(ans["action"]["answer"]), "unit": unit,
                "to": none_to_null(ans["to"]["answer"])}
        out.append({"id": r["id"], "text": r["text"], "source": r["source"], "kind": r["kind"],
                    "expected": r["expected"], "decision": r["decision"],
                    "raw": json.dumps(pred), "pred": pred, "valid": True, "seconds": round(secs, 4),
                    "confidence": {q: round(ans[q]["confidence"], 4) for q in QUESTIONS}})
    return out


def report(name, preds):
    dec = [decide(p["pred"]) for p in preds]
    right = sum(d == p["decision"] for d, p in zip(dec, preds))
    unsafe = sum(d == "ACT" and p["decision"] != "ACT" for d, p in zip(dec, preds))
    exact = sum(p["pred"] == p["expected"] for p in preds)
    fields = {f: sum(p["pred"][f] == p["expected"][f] for p in preds) for f in ("action", "unit", "to")}
    hw = sum(d == p["decision"] for d, p in zip(dec, preds) if p["source"] == "handwritten")
    secs = [p["seconds"] for p in preds]
    print(f"{name}: exact {exact}/100 | fields {fields} | decision right {right}/100 | unsafe ACT {unsafe} | "
          f"hand-written {hw}/10 | median {statistics.median(secs):.3f} s | slowest {max(secs):.3f} s")
    return {"exact": exact, "fields": fields, "right": right, "unsafe": unsafe, "handwritten": hw,
            "median_s": round(statistics.median(secs), 4), "max_s": round(max(secs), 4)}


def main():
    train, test = load("train.jsonl"), load("test.jsonl")
    device = torch.cuda.get_device_name(0) if torch.cuda.is_available() else "CPU"
    print("device:", device)

    before = laya.Learner(QUESTIONS, examples=None, auto=False)
    run(before, test[:3])  # warm up
    p0 = run(before, test)
    r0 = report("BEFORE TRAINING", p0)

    examples = [(r["text"], {"action": r["expected"]["action"] or "none", "to": r["expected"]["to"] or "none"})
                for r in train]
    t = time.perf_counter()
    after = laya.Learner(QUESTIONS, examples=examples, auto=False, reader=before.reader)
    train_s = time.perf_counter() - t
    print(f"training: {train_s:.1f} s | {after.report}")
    p1 = run(after, test)
    r1 = report("AFTER TRAINING", p1)

    res = ROOT / "results"
    for name, preds in [("laya-fields-untrained", p0), ("laya-fields", p1)]:
        with (res / f"preds_{name}.jsonl").open("w", encoding="utf-8") as f:
            for p in preds:
                f.write(json.dumps(p) + "\n")
    (res / "laya_fields_summary.json").write_text(json.dumps(
        {"device": device, "training_seconds": round(train_s, 1), "fit_report": after.report,
         "before": r0, "after": r1}, indent=2, default=str), encoding="utf-8")
    print("saved results/preds_laya-fields.jsonl")


if __name__ == "__main__":
    main()
