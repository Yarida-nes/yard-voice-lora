"""Run a local Ollama model over a data file and save its answers.

python optional/run_model.py --model qwen3:1.7b
python optional/run_model.py --model yard-lora --data data/audio_test.jsonl --name yard-lora-audio
"""
import argparse
import json
import time
from pathlib import Path

import ollama
from pydantic import ValidationError

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from prompt import build_prompt
from schema import Command

ROOT = Path(__file__).parent.parent


def ask(model: str, text: str) -> str:
    kwargs = dict(model=model, messages=[{"role": "user", "content": build_prompt(text)}],
                  format=Command.model_json_schema(), options={"temperature": 0})
    try:
        return ollama.chat(think=False, **kwargs).message.content
    except TypeError:
        return ollama.chat(**kwargs).message.content


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--data", default="data/test.jsonl")
    ap.add_argument("--name", help="results file name, default: the model name")
    ap.add_argument("--limit", type=int)
    args = ap.parse_args()

    rows = [json.loads(l) for l in (ROOT / args.data).read_text(encoding="utf-8").splitlines() if l.strip()]
    rows = rows[: args.limit] if args.limit else rows
    name = args.name or args.model.replace(":", "-").replace("/", "-")
    out = ROOT / "results" / f"preds_{name}.jsonl"
    out.parent.mkdir(exist_ok=True)

    ask(args.model, "warm up")
    with out.open("w", encoding="utf-8") as f:
        for i, r in enumerate(rows, 1):
            start = time.perf_counter()
            raw = ask(args.model, r["text"])
            seconds = time.perf_counter() - start
            try:
                pred, valid = Command.model_validate_json(raw).model_dump(), True
            except ValidationError:
                pred, valid = None, False
            f.write(json.dumps({**r, "raw": raw, "pred": pred, "valid": valid, "seconds": round(seconds, 3)}) + "\n")
            print(f"{i}/{len(rows)}  {seconds:.2f}s  {r['text'][:50]!r} -> {' '.join(raw.split())[:80]}")
    print(f"Saved {out}")


if __name__ == "__main__":
    main()
