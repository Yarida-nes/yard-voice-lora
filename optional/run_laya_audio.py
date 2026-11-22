"""Train Laya (reads action + place) once, then run it on what Whisper heard.

Run with the Laya environment, from the project folder:
    laya-env/Scripts/python optional/run_laya_audio.py audio_clean.jsonl audio_noisy.jsonl
Each data file (in data/) gives results/preds_laya-fields-<file name without .jsonl, minus "audio_">.jsonl
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import json  # noqa: E402

import laya  # noqa: E402
from run_laya_fields import QUESTIONS, ROOT, load, report, run  # noqa: E402


def main():
    train = load("train.jsonl")
    reader = laya.Learner(QUESTIONS, examples=None, auto=False).reader
    examples = [(r["text"], {"action": r["expected"]["action"] or "none", "to": r["expected"]["to"] or "none"})
                for r in train]
    learner = laya.Learner(QUESTIONS, examples=examples, auto=False, reader=reader)
    for data in sys.argv[1:]:
        rows = load(data)
        preds = run(learner, rows)
        tag = data.removesuffix(".jsonl").replace("audio_", "audio-")
        report(tag, preds)
        with (ROOT / "results" / f"preds_laya-fields-{tag}.jsonl").open("w", encoding="utf-8") as f:
            for p in preds:
                f.write(json.dumps(p) + "\n")
        print(f"saved results/preds_laya-fields-{tag}.jsonl")


if __name__ == "__main__":
    main()
