"""
Evidence assistant.

1. parse a free-text question into a structured mission query (rules, no model needed)
2. rank evidence with MACE + BM25
3. assemble an answer only from computed facts, each with its PSI source
4. (optional) if an LLM endpoint is configured, ask it to *rephrase* those facts -
   it gets the facts and nothing else, and is told to refuse anything outside them.

The app works fully offline without step 4.
"""
import json
import os
import re
import urllib.request

from firewise import data, insights, mace, search, units

MISSION_WORDS = {
    "lunar_habitat": ["moon", "lunar", "artemis"],
    "exploration_atm": ["rover", "lander", "8.2", "suitport"],
    "mars_habitat": ["mars", "martian"],
    "iss": ["iss", "space station", "spacecraft", "orbit", "cabin", "microgravity"],
}
GOAL_WORDS = {
    "detection": ["smoke", "detect", "detector", "sensor", "aerosol", "particle", "alarm", "soot"],
    "suppression": ["extinguish", "suppress", "suppression", "extinction", "co2", "carbon dioxide", "helium",
                    "diluent", "put out", "inert", "droplet"],
    "prevention": ["flammab", "ignit", "spread", "burn", "material", "fabric", "catch fire", "flame"],
}


def parse(question):
    q = question.lower()
    mission = next((k for k, words in MISSION_WORDS.items() if any(w in q for w in words)), "iss")
    scores = {g: sum(q.count(w) for w in ws) for g, ws in GOAL_WORDS.items()}
    goal = max(scores, key=scores.get) if any(scores.values()) else "prevention"
    material = None
    fams = data.runs()["fuel"].dropna().unique()
    for fam in sorted(fams, key=len, reverse=True):
        key = fam.split(" ")[0].lower().strip("()")
        if key and re.search(rf"\b{re.escape(key)}", q):
            material = fam
            break
    query = mace.query_from_mission(mission, goal, material)
    m = re.search(r"(\d{2}(?:\.\d+)?)\s*%\s*(?:o2|oxygen)?", q)
    if m:
        query.o2_fraction = float(m.group(1)) / 100
    m = re.search(r"(\d+(?:\.\d+)?)\s*psi", q)
    if m:
        query.pressure_kpa = units.psi_to_kpa(float(m.group(1)))
    m = re.search(r"(\d+(?:\.\d+)?)\s*kpa", q)
    if m:
        query.pressure_kpa = float(m.group(1))
    query.text = question
    return query


def answer(question, use_llm=True):
    q = parse(question)
    text_scores = search.investigation_scores(question)
    assessed = mace.assess(q, text_scores=text_scores)
    ranked = mace.rank_investigations(assessed)

    if q.goal == "prevention":
        facts = insights.prevention(q.material, q.pressure_kpa, q.o2_fraction)
    elif q.goal == "suppression":
        facts = insights.suppression(q.pressure_kpa, q.o2_fraction)
    else:
        facts = insights.detection()

    levels = assessed["level"].value_counts().to_dict() if not assessed.empty else {}
    caveats = []
    if q.gravity_g > 0.01:
        caveats.append(
            f"All PSI runs here were in microgravity; your mission is at {q.gravity_g:g} g. "
            "PSI holds no partial-gravity combustion data, so nothing below is a measured lunar/Mars result.")
    if levels.get("DIRECT", 0) == 0:
        caveats.append("No run qualifies as DIRECT evidence for this exact question.")

    draft = {
        "question": question,
        "parsed": {"mission": q.mission_name, "goal": q.goal, "material": q.material,
                   "o2_fraction": round(q.o2_fraction, 3), "pressure_kpa": round(q.pressure_kpa, 1),
                   "po2_kpa": round(q.po2_kpa, 1), "gravity_g": q.gravity_g},
        "levels": levels,
        "top_investigations": ranked.head(5).to_dict("records") if not ranked.empty else [],
        "facts": facts,
        "caveats": caveats,
        "papers": search.search(question, k=5),
    }
    draft["summary"] = _template_summary(draft)
    if use_llm and os.getenv("FIREWISE_LLM_KEY"):
        try:
            draft["summary"] = _llm_rephrase(draft)
            draft["rephrased"] = True
        except Exception as e:  # never break the app because of the optional model
            draft["llm_error"] = str(e)
    return draft


def _template_summary(d):
    p = d["parsed"]
    top = d["top_investigations"]
    lead = (f"For a **{p['goal']}** question in a **{p['mission']}** setting "
            f"({p['o2_fraction']:.0%} O₂, {p['pressure_kpa']:.0f} kPa, pO₂ {p['po2_kpa']:.1f} kPa, {p['gravity_g']:g} g)")
    if p["material"]:
        lead += f" about **{p['material']}**"
    lead += ", "
    if top:
        best = top[0]
        lead += (f"the most applicable NASA investigation is **{best['investigation']}** ({best['psi_id']}), "
                 f"best evidence level **{best['best_level']}**.")
    else:
        lead += "no investigation in the index applies."
    return lead


def _llm_rephrase(d):
    """OpenAI-compatible chat endpoint. Configure FIREWISE_LLM_URL / _KEY / _MODEL in .env."""
    url = os.getenv("FIREWISE_LLM_URL", "https://api.openai.com/v1/chat/completions")
    model = os.getenv("FIREWISE_LLM_MODEL", "gpt-4o-mini")
    facts = "\n".join(f"- {f['text']} [{', '.join(f['psi_ids'])}]" for f in d["facts"])
    caveats = "\n".join(f"- {c}" for c in d["caveats"])
    prompt = (
        "You write for spacecraft fire-safety engineers. Using ONLY the facts and caveats below, "
        "write a 4-6 sentence answer to the question. Keep every number exactly as given, keep the "
        "[PSI-xx] tags, and state the caveats. If the facts do not answer the question, say so.\n\n"
        f"Question: {d['question']}\nParsed: {json.dumps(d['parsed'])}\nFacts:\n{facts}\nCaveats:\n{caveats}"
    )
    body = json.dumps({"model": model, "temperature": 0.1,
                       "messages": [{"role": "user", "content": prompt}]}).encode()
    req = urllib.request.Request(url, data=body, headers={
        "Content-Type": "application/json", "Authorization": f"Bearer {os.getenv('FIREWISE_LLM_KEY')}"})
    with urllib.request.urlopen(req, timeout=40) as r:
        out = json.loads(r.read())
    return out["choices"][0]["message"]["content"].strip()
