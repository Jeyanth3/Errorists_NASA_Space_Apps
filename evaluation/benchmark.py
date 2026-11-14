"""
FireWise-Eval: compare plain keyword retrieval (BM25) with MACE on hand-labelled questions.

  goal accuracy        did we read the safety question right?
  top-1 hit            is the best-ranked investigation one a domain reader would pick?
  unsafe claims        how often a system presents evidence as directly applicable
                       when the mission conditions make that impossible (lunar/Mars, other atmosphere)

BM25 has no notion of conditions, so every top hit is implicitly "applicable" - that is the point.
run:  python -m evaluation.benchmark
"""
import json
from pathlib import Path

from firewise import assistant, mace, search

GOLD = Path(__file__).with_name("gold_questions.jsonl")


def bm25_top(q):
    hits = [h for h in search.search(q, k=20) if h["kind"] == "investigation"] or search.search(q, k=1)
    return hits[0]["acronym"] if hits else None


def norm(name):
    return (name or "").upper().replace(" ", "")


def run():
    rows = [json.loads(line) for line in GOLD.read_text().splitlines() if line.strip()]
    res = {"bm25": {"top1": 0, "unsafe": 0}, "mace": {"top1": 0, "unsafe": 0, "goal": 0}}
    for g in rows:
        want = {norm(t) for t in g["top"]}
        b = bm25_top(g["q"])
        res["bm25"]["top1"] += norm(b) in want
        res["bm25"]["unsafe"] += (not g["direct_allowed"])  # BM25 always implies applicability

        q = assistant.parse(g["q"])
        res["mace"]["goal"] += q.goal == g["goal"]
        ranked = mace.rank_investigations(mace.assess(q, text_scores=search.investigation_scores(g["q"])))
        top = ranked.iloc[0] if len(ranked) else None
        res["mace"]["top1"] += top is not None and norm(top["investigation"]) in want
        res["mace"]["unsafe"] += top is not None and (not g["direct_allowed"]) and top["best_level"] == "DIRECT"
    n = len(rows)
    print(f"FireWise-Eval  n={n} questions\n")
    print(f"{'system':8} {'goal acc':>9} {'top-1 hit':>10} {'unsafe claims':>14}")
    print(f"{'BM25':8} {'-':>9} {res['bm25']['top1'] / n:>10.0%} {res['bm25']['unsafe'] / n:>14.0%}")
    print(f"{'MACE':8} {res['mace']['goal'] / n:>9.0%} {res['mace']['top1'] / n:>10.0%} {res['mace']['unsafe'] / n:>14.0%}")
    out = Path(__file__).with_name("results.json")
    out.write_text(json.dumps({"n": n, **res}, indent=2))
    return res


if __name__ == "__main__":
    run()
