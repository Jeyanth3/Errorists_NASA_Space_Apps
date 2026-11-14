import os
import re

import streamlit as st

from firewise import assistant, mace, ui

ui.header("Ask FireWise", "Ask in plain<br>English.",
          lead="Your question becomes a structured mission query. Answers use only numbers computed from NASA runs, "
               "each with its PSI source. If the data cannot answer, FireWise says so.")

examples = [
    "How flammable is PMMA in a lunar habitat at 30% oxygen and 10.2 psi?",
    "Does adding CO2 help extinguish fuel droplet fires on the ISS?",
    "What do we know about smoke from overheated Kapton wire insulation?",
    "Would a cotton-fiberglass fabric fire spread in a Mars base?",
]
if "q" not in st.session_state:
    st.session_state.q = examples[0]
ui.eyebrow("Try one")
cols = st.columns(len(examples))
for col, ex in zip(cols, examples):
    if col.button(ex, width="stretch"):
        st.session_state.q = ex

question = st.text_area("Your question", key="q", height=90)
if not question.strip():
    st.stop()
with st.spinner("Ranking NASA evidence..."):
    ans = assistant.answer(question)
p = ans["parsed"]

ui.html(f"""<div class="fw-card"><div class="band fw-pat-band"></div><div class="in">
<div class="row">{ui.tile("search", mint=True)}<div class="label" style="flex:1">How FireWise read it</div></div>
<div class="fw-stats" style="margin:1.2rem 0 0;grid-template-columns:repeat(6,1fr)">
<div class="fw-stat"><div class="v" style="font-size:1.4rem">{p['mission'].split(' (')[0]}</div><div class="l">mission</div></div>
<div class="fw-stat"><div class="v" style="font-size:1.4rem">{p['goal']}</div><div class="l">goal</div></div>
<div class="fw-stat"><div class="v" style="font-size:1.4rem">{p['material'] or 'any'}</div><div class="l">material</div></div>
<div class="fw-stat"><div class="v" style="font-size:1.4rem">{p['o2_fraction']:.0%}</div><div class="l">oxygen</div></div>
<div class="fw-stat"><div class="v" style="font-size:1.4rem">{p['pressure_kpa']:.0f} kPa</div><div class="l">pressure</div></div>
<div class="fw-stat"><div class="v" style="font-size:1.4rem">{p['gravity_g']:g} g</div><div class="l">gravity</div></div>
</div></div></div>""")

a, b = st.columns([1.5, 1], gap="large")
with a:
    ui.eyebrow("Answer")
    summary = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", ans["summary"])
    ui.html(f'<div class="fw-card"><div class="in"><p class="fw-lead" style="max-width:none">{summary}</p></div></div>')
    if ans.get("rephrased"):
        st.caption("Wording polished by a language model from the facts below; numbers come from NASA runs.")
    for cv in ans["caveats"]:
        ui.fact_box({"text": cv, "psi_ids": [], "kind": "gap"})
    for f in ans["facts"]:
        ui.fact_box(f)
with b:
    if ans["top_investigations"]:
        ui.eyebrow("Evidence ranking")
        rows = "".join(
            f'<div class="r" style="grid-template-columns:1fr auto"><span><b>{r["investigation"]}</b><br>'
            f'<span class="fw-mono" style="font-size:.7rem">{r["runs"]} runs · applicability {r["applicability"]:.2f} · '
            f'<a href="{ui.psi_link(r["psi_id"])}" target="_blank" style="color:#0f8a52">{r["psi_id"]} ↗</a></span></span>'
            f'{ui.badge(r["best_level"])}</div>' for r in ans["top_investigations"])
        ui.html(f'<div class="fw-acc">{rows}</div>')
    if ans["papers"]:
        ui.eyebrow("Related NASA publications")
        rows = "".join(f'<div class="r" style="grid-template-columns:1fr"><span>{h["title"]}<br>'
                       f'<span class="fw-mono" style="font-size:.7rem">{h["acronym"]} · '
                       f'<a href="{ui.psi_link(h["psi_id"])}" target="_blank" style="color:#0f8a52">{h["psi_id"]} ↗</a></span></span></div>'
                       for h in ans["papers"])
        ui.html(f'<div class="fw-acc">{rows}</div>')

with st.expander("Why trust this?"):
    st.markdown(
        "- Evidence levels (DIRECT / SUPPORTING / EXTRAPOLATED) come from explicit rules in `firewise/mace.py`, "
        "never from a language model.\n"
        "- Every number comes from `data/curated/runs.csv`, which keeps the source file and row of each NASA value.\n"
        "- Gravity and atmosphere mismatches are always shown, even when a run looks highly relevant.\n"
        f"- Thresholds: pO₂ match ±{mace.PO2_MATCH} kPa, O₂ fraction ±{mace.XO2_MATCH:.1%}, pressure ±{mace.P_MATCH:.0%}.")
    if not os.getenv("FIREWISE_LLM_KEY"):
        st.caption("Offline mode: no language model configured, answers are fully template-based.")
ui.footer()
