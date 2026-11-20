"""Score a predictions file.

python optional/score.py results/preds_qwen3-1.7b.jsonl
"""
import json
import statistics
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from rules import DECISIONS, decide


def load(path: str) -> list[dict]:
    rows = [json.loads(l) for l in Path(path).read_text(encoding="utf-8").splitlines() if l.strip()]
    for r in rows:
        r["pred_decision"] = decide(r["pred"]) if r["valid"] else "ASK_AGAIN"
        r["exact"] = r["valid"] and r["pred"] == r["expected"]
    return rows


def pct(n: int, d: int) -> str:
    return f"{100 * n / d:.1f}%" if d else "-"


def report(rows: list[dict], title: str) -> str:
    n = len(rows)
    lines = [f"# {title}", "", f"{n} test examples", "", "| Measure | Result |", "|---|---|"]
    lines.append(f"| Valid JSON | {pct(sum(r['valid'] for r in rows), n)} |")
    lines.append(f"| Exact match (all fields right) | {pct(sum(r['exact'] for r in rows), n)} |")
    for field in ("action", "unit", "to"):
        ok = sum(r["valid"] and r["pred"][field] == r["expected"][field] for r in rows)
        lines.append(f"| `{field}` right | {pct(ok, n)} |")
    lines.append(f"| Decision right | {pct(sum(r['pred_decision'] == r['decision'] for r in rows), n)} |")
    unsafe = [r for r in rows if r["pred_decision"] == "ACT" and r["decision"] != "ACT"]
    wrong_unit = [r for r in rows if r["pred_decision"] == "ACT" and r["valid"] and r["pred"] != r["expected"]]
    lines.append(f"| **Unsafe: acted when it should have checked** | **{len(unsafe)} ({pct(len(unsafe), n)})** |")
    lines.append(f"| **Acted on the wrong command** | **{len(wrong_unit)} ({pct(len(wrong_unit), n)})** |")
    secs = sorted(r["seconds"] for r in rows)
    lines.append(f"| Median time per command | {statistics.median(secs):.2f} s |")
    lines.append(f"| Slowest 5% | {secs[int(0.95 * (n - 1))]:.2f} s |")

    lines += ["", "## Decisions (rows: right answer, columns: what the system did)", "",
              "| | " + " | ".join(DECISIONS) + " |", "|---" * (len(DECISIONS) + 1) + "|"]
    for d in DECISIONS:
        cells = [str(sum(r["decision"] == d and r["pred_decision"] == p for r in rows)) for p in DECISIONS]
        lines.append(f"| **{d}** | " + " | ".join(cells) + " |")

    lines += ["", "## Exact match by kind", "", "| Kind | Right | Of |", "|---|---|---|"]
    for kind in sorted({r["kind"] for r in rows}):
        part = [r for r in rows if r["kind"] == kind]
        lines.append(f"| {kind} | {sum(r['exact'] for r in part)} | {len(part)} |")

    misses = [r for r in rows if not r["exact"]][:15]
    lines += ["", f"## First {len(misses)} mistakes", "", "| Said | Expected | Got |", "|---|---|---|"]
    for r in misses:
        got = json.dumps(r["pred"]) if r["valid"] else f"invalid: {r['raw'][:60]}"
        lines.append(f"| {r['text']} | `{json.dumps(r['expected'])}` | `{got}` |")
    return "\n".join(lines) + "\n"


def main() -> None:
    path = Path(sys.argv[1])
    md = report(load(str(path)), path.stem.removeprefix("preds_"))
    out = path.with_name(path.stem.replace("preds_", "score_") + ".md")
    out.write_text(md, encoding="utf-8")
    print(md)
    print(f"Saved {out}")


if __name__ == "__main__":
    main()
