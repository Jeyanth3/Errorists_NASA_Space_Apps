import os

import streamlit as st

from firewise import assistant, mace, ui

ui.setup("💬 Ask FireWise")
st.caption("Ask a fire-safety question in plain English. FireWise turns it into a structured mission query, "
           "ranks NASA evidence, and answers only with numbers computed from NASA runs. If the data cannot "
           "answer, it says so.")

examples = [
    "How flammable is PMMA in a lunar habitat at 30% oxygen and 10.2 psi?",
    "Does adding CO2 help extinguish fuel droplet fires on the ISS?",
    "What do we know about smoke from overheated Kapton wire insulation?",
    "Would a cotton-fiberglass fabric fire spread in a Mars base?",
]
if "q" not in st.session_state:
    st.session_state.q = examples[0]
cols = st.columns(len(examples))
for col, ex in zip(cols, examples):
    if col.button(ex, width="stretch"):
        st.session_state.q = ex

question = st.text_area("Your question", key="q", height=80)
if not question.strip():
    st.stop()

with st.spinner("Ranking NASA evidence..."):
    ans = assistant.answer(question)

p = ans["parsed"]
st.markdown("##### How FireWise read your question")
c = st.columns(6)
c[0].metric("Mission", p["mission"].split(" (")[0].replace(" surface habitat", ""))
c[1].metric("Goal", p["goal"])
c[2].metric("Material", p["material"] or "any")
c[3].metric("O₂", f"{p['o2_fraction']:.0%}")
c[4].metric("Pressure", f"{p['pressure_kpa']:.0f} kPa")
c[5].metric("Gravity", f"{p['gravity_g']:g} g")

st.markdown("##### Answer")
st.markdown(ans["summary"])
if ans.get("rephrased"):
    st.caption("Wording polished by a language model from the facts below; numbers come from NASA runs.")
for cv in ans["caveats"]:
    st.warning(cv)
for f in ans["facts"]:
    ui.fact_box(f)

if ans["top_investigations"]:
    st.markdown("##### Evidence ranking")
    for r in ans["top_investigations"]:
        st.markdown(f"{ui.badge(r['best_level'])} **{r['investigation']}** · {r['runs']} runs · "
                    f"applicability {r['applicability']:.2f} · [{r['psi_id']}]({ui.psi_link(r['psi_id'])})",
                    unsafe_allow_html=True)

if ans["papers"]:
    st.markdown("##### Related NASA publications")
    for h in ans["papers"]:
        st.markdown(f"- {h['title']} - *{h['acronym']}* ([{h['psi_id']}]({ui.psi_link(h['psi_id'])}))")

with st.expander("Why trust this?"):
    st.markdown(
        "- The evidence level (DIRECT / SUPPORTING / EXTRAPOLATED) is decided by explicit rules in "
        "`firewise/mace.py`, never by a language model.\n"
        "- Every number comes from `data/curated/runs.csv`, which keeps the source file and row of each NASA value.\n"
        "- Gravity and atmosphere mismatches are always shown, even when a run looks highly relevant.\n"
        f"- Thresholds: pO₂ match ±{mace.PO2_MATCH} kPa, O₂ fraction ±{mace.XO2_MATCH:.1%}, pressure ±{mace.P_MATCH:.0%}.")
    if not os.getenv("FIREWISE_LLM_KEY"):
        st.caption("Running in offline mode (no language model configured). Answers are fully template-based.")
