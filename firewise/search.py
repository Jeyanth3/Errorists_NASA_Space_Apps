"""Keyword search over investigation text and publication titles (BM25)."""
import re
from functools import lru_cache

from rank_bm25 import BM25Okapi

from firewise import data

STOP = set("""a an the of in on for to and or is are was were be by with from at as that this it its
which what how do does did can could should would about into than then their there these those we you
our your i me my""".split())


def tokens(text):
    return [t for t in re.findall(r"[a-z0-9]+", str(text).lower()) if t not in STOP and len(t) > 1]


@lru_cache(maxsize=1)
def _index():
    inv = data.investigations()
    pubs = data.publications()
    docs, meta = [], []
    for _, r in inv.iterrows():
        docs.append(tokens(f"{r['acronym']} {r['title']} {r['sub_area']} {r['hardware']} {r['text']}"))
        meta.append(("investigation", r["psi_id"], r["acronym"], r["title"]))
    for _, p in pubs.iterrows():
        docs.append(tokens(f"{p['acronym']} {p['title']}"))
        meta.append(("publication", p["psi_id"], p["acronym"], p["title"]))
    return BM25Okapi(docs), meta


def search(query, k=10):
    bm, meta = _index()
    q = tokens(query)
    if not q:
        return []
    scores = bm.get_scores(q)
    top = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:k]
    return [{"kind": meta[i][0], "psi_id": meta[i][1], "acronym": meta[i][2], "title": meta[i][3],
             "score": float(scores[i])} for i in top if scores[i] > 0]


def investigation_scores(query):
    """Normalised 0-1 text score per PSI id (best hit counts)."""
    hits = search(query, k=200)
    if not hits:
        return {}
    best = {}
    for h in hits:
        best[h["psi_id"]] = max(best.get(h["psi_id"], 0), h["score"])
    top = max(best.values())
    return {k: v / top for k, v in best.items()}
