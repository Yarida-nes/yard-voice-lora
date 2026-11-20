"""Make labelled yard commands from templates.

python src/generate_data.py            -> data/examples.jsonl, train.jsonl, test.jsonl, train_conversations.jsonl
python src/generate_data.py --n 400    -> more examples
"""
import argparse
import csv
import json
import random
from pathlib import Path

from prompt import build_prompt
from rules import YARD, decide, has_lookalike

ROOT = Path(__file__).parent.parent
DATA = ROOT / "data"

ONES = "zero one two three four five six seven eight nine".split()
TEENS = "ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen".split()
TENS = "_ _ twenty thirty forty fifty sixty seventy eighty ninety".split()


def two_digits(n: int) -> str:
    if n < 10:
        return f"oh {ONES[n]}"
    if n < 20:
        return TEENS[n - 10]
    return TENS[n // 10] + ("" if n % 10 == 0 else f"-{ONES[n % 10]}")


def say_unit(unit: str, rng: random.Random) -> str:
    style = rng.choice(["digits", "digits", "pairs", "single"])
    if style == "digits":
        return unit
    if style == "pairs":
        return f"{two_digits(int(unit[:2]))} {two_digits(int(unit[2:]))}"
    return " ".join(ONES[int(d)] for d in unit)


def say_place(place: str, rng: random.Random) -> str:
    if place.startswith("door_"):
        n = int(place[-2:])
        word = rng.choice([str(n), ONES[n]])
        return f"{rng.choice(['door', 'door', 'dock', 'dock door'])} {word}"
    if place == "staging":
        return rng.choice(["staging", "the staging lane", "staging lane"])
    return rng.choice(["parking", "the parking area", "the park-up area"])


PRE = ["", "", "", "uh, ", "okay, ", "yeah, ", "um, ", "right, "]
POST = ["", "", "", " please", " thanks", " when you can", " mate"]

MOVE = ["move {u} to {p}", "take {u} to {p}", "{u} to {p}", "can you put {u} on {p}",
        "shift {u} over to {p}", "bring {u} up to {p}", "{u}, {p}", "send {u} to {p}"]
MOVE_NO_PLACE = ["move {u}", "take {u} over", "can you shift {u}", "{u} needs moving"]
PARK = ["park {u}", "park up {u}", "put {u} in {p}", "{u} can go to parking", "drop {u} in parking"]
RELEASE = ["release {u}", "{u} is good to go out the gate", "let {u} out", "release {u} at the gate",
           "{u} can leave now"]
STATUS = ["where's {u}", "status on {u}", "where is {u} at", "what's the status of {u}",
          "has {u} been moved"]
UNCLEAR = ["uh, can you, the thing near the door", "move the, um, the blue one", "door, uh, sorry say again",
           "take it over there", "the one by the fence, can you", "hang on, wait", "move that trailer",
           "um, which one was it, door"]


def fill(template: str, unit: str | None, place: str | None, rng: random.Random) -> str:
    text = template.format(u=say_unit(unit, rng) if unit else "", p=say_place(place, rng) if place else "")
    return (rng.choice(PRE) + text + rng.choice(POST)).strip()


def example(rng: random.Random, kind: str) -> dict:
    trailers = YARD["trailers"]
    plain = [t for t in trailers if not has_lookalike(t, trailers)]
    lookalike = [t for t in trailers if has_lookalike(t, trailers)]
    free = [d for d, s in YARD["doors"].items() if s == "free"]
    busy = [d for d, s in YARD["doors"].items() if s == "busy"]
    unknown = str(rng.randint(1000, 9999))
    while unknown in trailers:
        unknown = str(rng.randint(1000, 9999))

    if kind == "move_ok":
        u, p = rng.choice(plain), rng.choice(free + ["staging"])
        cmd, text = {"action": "move", "unit": u, "to": p}, fill(rng.choice(MOVE), u, p, rng)
    elif kind == "move_lookalike":
        u, p = rng.choice(lookalike), rng.choice(free)
        cmd, text = {"action": "move", "unit": u, "to": p}, fill(rng.choice(MOVE), u, p, rng)
    elif kind == "move_busy":
        u, p = rng.choice(plain), rng.choice(busy)
        cmd, text = {"action": "move", "unit": u, "to": p}, fill(rng.choice(MOVE), u, p, rng)
    elif kind == "move_no_place":
        u = rng.choice(trailers)
        cmd, text = {"action": "move", "unit": u, "to": None}, fill(rng.choice(MOVE_NO_PLACE), u, None, rng)
    elif kind == "move_unknown":
        p = rng.choice(free)
        cmd, text = {"action": "move", "unit": unknown, "to": p}, fill(rng.choice(MOVE), unknown, p, rng)
    elif kind == "correction":
        wrong, right = rng.sample(lookalike, 2) if rng.random() < 0.5 else rng.sample(plain, 2)
        p = rng.choice(free)
        fix = rng.choice(["no wait", "sorry", "I mean", "no, scratch that"])
        text = f"{rng.choice(['take', 'move'])} {say_unit(wrong, rng)}, {fix}, {say_unit(right, rng)} to {say_place(p, rng)}"
        cmd = {"action": "move", "unit": right, "to": p}
    elif kind == "park":
        u = rng.choice(plain)
        cmd, text = {"action": "park", "unit": u, "to": "parking"}, fill(rng.choice(PARK), u, "parking", rng)
    elif kind == "release":
        u = rng.choice(trailers)
        cmd, text = {"action": "release", "unit": u, "to": None}, fill(rng.choice(RELEASE), u, None, rng)
    elif kind == "status":
        u = rng.choice(trailers)
        cmd, text = {"action": "status", "unit": u, "to": None}, fill(rng.choice(STATUS), u, None, rng)
    else:
        cmd, text = {"action": None, "unit": None, "to": None}, rng.choice(UNCLEAR)
    return {"text": text, "expected": cmd, "decision": decide(cmd), "kind": kind, "source": "generated"}


KINDS = {"move_ok": 4, "move_lookalike": 2, "move_busy": 1, "move_no_place": 1, "move_unknown": 1,
         "correction": 1, "park": 1, "release": 1, "status": 1, "unclear": 1}


def load_handwritten() -> list[dict]:
    path = DATA / "handwritten_tricky.csv"
    if not path.exists():
        return []
    rows = []
    with path.open(newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            cmd = {k: (r[k].strip() or None) for k in ("action", "unit", "to")}
            rows.append({"text": r["text"].strip(), "expected": cmd, "decision": decide(cmd),
                         "kind": "handwritten", "source": "handwritten"})
    return rows


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=300)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--test-share", type=float, default=0.3)
    args = ap.parse_args()

    rng = random.Random(args.seed)
    kinds = [k for k, w in KINDS.items() for _ in range(w)]
    rows, seen = [], set()
    while len(rows) < args.n:
        ex = example(rng, rng.choice(kinds))
        if ex["text"].lower() not in seen:
            seen.add(ex["text"].lower())
            rows.append(ex)

    rng.shuffle(rows)
    cut = int(len(rows) * (1 - args.test_share))
    train, test = rows[:cut], rows[cut:] + load_handwritten()
    for i, r in enumerate(train):
        r["id"] = f"train-{i:04d}"
    for i, r in enumerate(test):
        r["id"] = f"test-{i:04d}"

    write_jsonl(DATA / "examples.jsonl", train + test)
    write_jsonl(DATA / "train.jsonl", train)
    write_jsonl(DATA / "test.jsonl", test)
    write_jsonl(DATA / "train_conversations.jsonl", [
        {"conversations": [{"role": "user", "content": build_prompt(r["text"])},
                           {"role": "assistant", "content": json.dumps(r["expected"])}]}
        for r in train])

    for name, part in (("train", train), ("test", test)):
        counts = {d: sum(r["decision"] == d for r in part) for d in ("ACT", "READ_BACK", "ASK_AGAIN")}
        shares = ", ".join(f"{d} {c} ({100 * c / len(part):.0f}%)" for d, c in counts.items())
        print(f"{name}: {len(part)} examples. {shares}")


if __name__ == "__main__":
    main()
