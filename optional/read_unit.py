"""Read the trailer number out of a spoken yard command with plain code (no AI).

- Spoken numbers become digits: "forty four seventeen" -> 4417, "two two six nine" -> 2269,
  "eight four two oh" -> 8420.
- Numbers right after "door" or "dock" are door numbers, not trailers, so they are skipped.
- If the worker corrects themselves, the last trailer number wins ("4417, no wait, 4471" -> 4471).
- Returns None when no 4-digit number was said.

Check it on the data:  python optional/read_unit.py
"""
import re

DIGITS = {"zero": 0, "oh": 0, "o": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
          "six": 6, "seven": 7, "eight": 8, "nine": 9}
TEENS = {"ten": 10, "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14, "fifteen": 15,
         "sixteen": 16, "seventeen": 17, "eighteen": 18, "nineteen": 19}
TENS = {"twenty": 20, "thirty": 30, "forty": 40, "fifty": 50, "sixty": 60, "seventy": 70,
        "eighty": 80, "ninety": 90}
DOOR_WORDS = {"door", "dock"}


def _is_num(tok):
    return tok.isdigit() or tok in DIGITS or tok in TEENS or tok in TENS


def _run_to_digits(run):
    """['forty', 'four', 'seventeen'] -> '4417'."""
    out, i = "", 0
    while i < len(run):
        t = run[i]
        if t.isdigit():
            out += t
        elif t in TEENS:
            out += str(TEENS[t])
        elif t in TENS:
            if i + 1 < len(run) and run[i + 1] in DIGITS and DIGITS[run[i + 1]] > 0:
                out += str(TENS[t] + DIGITS[run[i + 1]])
                i += 1
            else:
                out += str(TENS[t])
        else:
            out += str(DIGITS[t])
        i += 1
    return out


def read_unit(text):
    toks = re.findall(r"[a-z]+|\d+|[,.;!?]", text.lower().replace("-", " "))
    found, run, after_door = [], [], False
    for tok in toks + ["."]:
        if _is_num(tok):
            run.append(tok)
            continue
        if run:
            if not after_door:
                found.append(_run_to_digits(run))
            run = []
        after_door = tok in DOOR_WORDS
    units = [f for f in found if len(f) == 4]
    return units[-1] if units else None


if __name__ == "__main__":
    import json
    from pathlib import Path

    root = Path(__file__).parent.parent
    for name in ["train.jsonl", "test.jsonl"]:
        rows = [json.loads(l) for l in (root / "data" / name).read_text(encoding="utf-8").splitlines() if l.strip()]
        wrong = [(r["text"], r["expected"]["unit"], read_unit(r["text"])) for r in rows
                 if read_unit(r["text"]) != r["expected"]["unit"]]
        print(f"{name}: trailer number right {len(rows) - len(wrong)}/{len(rows)}")
        for w in wrong:
            print("   ", w)
