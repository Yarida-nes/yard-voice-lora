"""Test TypeSafe Jev (cloud decision model, through OpenRouter) on the 100 test sentences.

Jev cannot be trained on our data and never writes text, so it gets the same questions as Laya:
- "action" and "to" (choice): it reads the command; code reads the trailer number; src/rules.py decides.
- "decision" (choice): it picks ACT / READ_BACK / ASK_AGAIN on its own, like the first Laya test.
All three are asked in one request per sentence.

Needs OPENROUTER_API_KEY (saved with setx). Run from the project folder:
    python optional/run_jev.py            # all 100
    python optional/run_jev.py --one      # one sentence, to check the setup
    python optional/run_jev.py --data audio_clean.jsonl --name jev-audio-clean   # on what Whisper heard
"""
import json
import os
import statistics
import sys
import time
from pathlib import Path

import urllib.error
import urllib.request

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "optional"))
from rules import decide  # noqa: E402
from read_unit import read_unit  # noqa: E402

# The same questions as optional/run_laya_fields.py and optional/run_laya.py (copied, because
# importing those files needs the Laya environment).
FIELD_Q = {
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
        "criteria": {**{f"door_0{i}": f"door {i}" for i in range(1, 9)},
                     "staging": "the staging area", "parking": "parking",
                     "none": "no place was said, or it is not a move or park"},
    },
}
DECISION_Q = {
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

MODEL = "typesafe/jev-1.14"
URL = "https://openrouter.ai/api/alpha/decisions"
QUESTIONS = {**FIELD_Q, **DECISION_Q}


def api_key():
    key = os.environ.get("OPENROUTER_API_KEY")
    if not key and sys.platform == "win32":  # saved with setx but this shell started before that
        import winreg
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as k:
            key = winreg.QueryValueEx(k, "OPENROUTER_API_KEY")[0]
    return key


def load(name):
    return [json.loads(l) for l in (ROOT / "data" / name).read_text(encoding="utf-8").splitlines() if l.strip()]


def ask(headers, text):
    body = json.dumps({"model": MODEL, "state": {"spoken_command": text}, "questions": QUESTIONS}).encode()
    for attempt in range(3):
        t = time.perf_counter()
        try:
            req = urllib.request.Request(URL, data=body, headers=headers, method="POST")
            with urllib.request.urlopen(req, timeout=60) as r:
                data = json.loads(r.read())
            return data, time.perf_counter() - t
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503) and attempt < 2:
                time.sleep(2 * (attempt + 1))
                continue
            raise SystemExit(f"Jev request failed: HTTP {e.code}: {e.read()[:300]!r}")


def none_to_null(v):
    return None if v == "none" else v


def main():
    data = sys.argv[sys.argv.index("--data") + 1] if "--data" in sys.argv else "test.jsonl"
    name = sys.argv[sys.argv.index("--name") + 1] if "--name" in sys.argv else "jev"
    test = load(data)
    if "--one" in sys.argv:
        test = test[:1]
    headers = {"Authorization": f"Bearer {api_key()}", "Content-Type": "application/json"}

    preds, cost, model_seen = [], 0.0, None
    for i, r in enumerate(test, 1):
        res, secs = ask(headers, r["text"])
        a = res["answers"]
        model_seen = res.get("model", model_seen)
        cost += (res.get("usage") or {}).get("cost") or 0
        pred = {"action": none_to_null(a["action"]["choice"]), "unit": read_unit(r["text"]),
                "to": none_to_null(a["to"]["choice"])}
        preds.append({"id": r["id"], "text": r["text"], "source": r["source"], "kind": r["kind"],
                      "expected": r["expected"], "decision": r["decision"], "raw": json.dumps(pred),
                      "pred": pred, "valid": True, "seconds": round(secs, 4),
                      "confidence": {q: a[q].get("confidence") for q in QUESTIONS},
                      "jev_decision": a["decision"]["choice"]})
        if i % 10 == 0:
            print(f"{i}/{len(test)} done")

    if "--one" in sys.argv:
        print(json.dumps(preds[0], indent=2), "\nmodel:", model_seen, "| cost USD:", cost)
        return

    dec = [decide(p["pred"]) for p in preds]
    secs = [p["seconds"] for p in preds]
    fields = {f: sum(p["pred"][f] == p["expected"][f] for p in preds) for f in ("action", "unit", "to")}
    summary = {
        "model": model_seen, "cost_usd": round(cost, 6),
        "fields_route": {
            "exact": sum(p["pred"] == p["expected"] for p in preds), "fields": fields,
            "right": sum(d == p["decision"] for d, p in zip(dec, preds)),
            "unsafe": sum(d == "ACT" and p["decision"] != "ACT" for d, p in zip(dec, preds)),
            "handwritten": sum(d == p["decision"] for d, p in zip(dec, preds) if p["source"] == "handwritten")},
        "decision_only": {
            "right": sum(p["jev_decision"] == p["decision"] for p in preds),
            "unsafe": sum(p["jev_decision"] == "ACT" and p["decision"] != "ACT" for p in preds),
            "handwritten": sum(p["jev_decision"] == p["decision"] for p in preds if p["source"] == "handwritten")},
        "median_s": round(statistics.median(secs), 4), "max_s": round(max(secs), 4),
    }
    print(json.dumps(summary, indent=2))
    with (ROOT / "results" / f"preds_{name}.jsonl").open("w", encoding="utf-8") as f:
        for p in preds:
            f.write(json.dumps(p) + "\n")
    (ROOT / "results" / f"{name}_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"saved results/preds_{name}.jsonl")


if __name__ == "__main__":
    main()
