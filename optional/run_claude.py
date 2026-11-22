"""Run a Claude cloud model over a data file and save its answers.

Same prompt, same JSON schema and same output format as optional/run_model.py,
so optional/score.py and optional/compare.py work on the results unchanged.

Needs an Anthropic API key in the ANTHROPIC_API_KEY environment variable.
Each run of 100 sentences costs roughly US$0.50-1 on Claude Opus 5.5.

python optional/run_claude.py
python optional/run_claude.py --model claude-opus-5-5 --limit 5
"""
import argparse
import json
import sys
import time
from pathlib import Path

import anthropic
from pydantic import ValidationError

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from prompt import build_prompt
from schema import Command

ROOT = Path(__file__).parent.parent

# Structured outputs need every object to say additionalProperties: false.
SCHEMA = {**Command.model_json_schema(), "additionalProperties": False}


def ask(client: anthropic.Anthropic, model: str, effort: str, text: str):
    """Send one sentence. Returns (raw JSON text, usage)."""
    response = client.beta.messages.create(
        model=model,
        max_tokens=4000,
        # If Claude declines for safety reasons, retry on a fallback model in the same call.
        betas=["server-side-fallback-2026-07-01"],
        fallbacks="default",
        output_config={
            "effort": effort,
            "format": {"type": "json_schema", "schema": SCHEMA},
        },
        messages=[{"role": "user", "content": build_prompt(text)}],
    )
    if response.stop_reason == "refusal":
        return "", response.usage
    raw = next((b.text for b in response.content if b.type == "text"), "")
    return raw, response.usage


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="claude-opus-5-5")
    ap.add_argument("--effort", default="low", help="low | medium | high | xhigh | max")
    ap.add_argument("--data", default="data/test.jsonl")
    ap.add_argument("--name", help="results file name, default: the model name")
    ap.add_argument("--limit", type=int)
    args = ap.parse_args()

    rows = [json.loads(l) for l in (ROOT / args.data).read_text(encoding="utf-8").splitlines() if l.strip()]
    rows = rows[: args.limit] if args.limit else rows
    name = args.name or args.model
    out = ROOT / "results" / f"preds_{name}.jsonl"
    out.parent.mkdir(exist_ok=True)

    client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY
    tokens_in = tokens_out = 0
    with out.open("w", encoding="utf-8") as f:
        for i, r in enumerate(rows, 1):
            start = time.perf_counter()
            raw, usage = ask(client, args.model, args.effort, r["text"])
            seconds = time.perf_counter() - start
            tokens_in += usage.input_tokens
            tokens_out += usage.output_tokens
            try:
                pred, valid = Command.model_validate_json(raw).model_dump(), True
            except ValidationError:
                pred, valid = None, False
            f.write(json.dumps({**r, "raw": raw, "pred": pred, "valid": valid, "seconds": round(seconds, 3)}) + "\n")
            print(f"{i}/{len(rows)}  {seconds:.2f}s  {r['text'][:50]!r} -> {' '.join(raw.split())[:80]}")

    # Opus 5.5 list price: $4 per million input tokens, $20 per million output tokens.
    cost = tokens_in * 4 / 1e6 + tokens_out * 20 / 1e6
    print(f"Tokens: {tokens_in:,} in, {tokens_out:,} out. Approx cost at Opus 5.5 prices: US${cost:.2f}")
    print(f"Saved {out}")


if __name__ == "__main__":
    main()
