"""Before and after: two predictions files on the same test set.

python optional/compare.py results/preds_qwen3-1.7b.jsonl results/preds_yard-lora.jsonl
"""
import sys
from math import comb
from pathlib import Path

from score import load, pct


def mcnemar_p(b: int, c: int) -> float:
    """Exact two-sided McNemar test: is the change bigger than chance?"""
    n = b + c
    if n == 0:
        return 1.0
    tail = sum(comb(n, k) for k in range(0, min(b, c) + 1)) / 2 ** n
    return min(1.0, 2 * tail)


def main() -> None:
    a_path, b_path = sys.argv[1], sys.argv[2]
    a, b = load(a_path), load(b_path)
    by_id = {r["id"]: r for r in b}
    pairs = [(r, by_id[r["id"]]) for r in a if r["id"] in by_id]
    n = len(pairs)
    name_a, name_b = Path(a_path).stem[6:], Path(b_path).stem[6:]

    def row(label, fn):
        return f"| {label} | {pct(sum(fn(x) for x, _ in pairs), n)} | {pct(sum(fn(y) for _, y in pairs), n)} |"

    lines = [f"# {name_a} vs {name_b}", "", f"{n} test examples, the same for both", "",
             f"| Measure | {name_a} | {name_b} |", "|---|---|---|",
             row("Valid JSON", lambda r: r["valid"]),
             row("Exact match", lambda r: r["exact"]),
             row("Decision right", lambda r: r["pred_decision"] == r["decision"]),
             row("Unsafe: acted when it should have checked",
                 lambda r: r["pred_decision"] == "ACT" and r["decision"] != "ACT")]
    only_a = sum(x["exact"] and not y["exact"] for x, y in pairs)
    only_b = sum(y["exact"] and not x["exact"] for x, y in pairs)
    p = mcnemar_p(only_a, only_b)
    lines += ["", f"Right only for {name_a}: {only_a}. Right only for {name_b}: {only_b}.",
              f"McNemar test p = {p:.4f} ({'unlikely to be chance' if p < 0.05 else 'could be chance'})."]
    md = "\n".join(lines) + "\n"
    out = Path(a_path).parent / f"compare_{name_a}_vs_{name_b}.md"
    out.write_text(md, encoding="utf-8")
    print(md)
    print(f"Saved {out}")


if __name__ == "__main__":
    main()
