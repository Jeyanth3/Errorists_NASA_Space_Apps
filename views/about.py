import streamlit as st

from firewise import data, ui

ui.setup("📚 Method & Sources")

st.subheader("How MACE ranks evidence")
st.markdown("""
**MACE** (Mission-Aware, Condition-constrained Evidence) scores every NASA run on three *separate* axes:

| Axis | Question | Built from |
|---|---|---|
| Relevance | Does this experiment study my safety question? | pillar match, material match, BM25 keyword score |
| Applicability | Were its physical conditions close to my mission? | gravity, O₂ partial pressure, O₂ fraction, total pressure, material, atmosphere type |
| Data quality | How much was measured rather than assumed? | completeness of outcome fields, inferred/assumed flags |

Then a rule assigns the evidence level:

- **DIRECT** - same pillar, same gravity regime, no condition differs
- **SUPPORTING** - right question, but something differs (or it is physics-only context)
- **EXTRAPOLATED** - gravity *and* atmosphere differ; usable only as a hypothesis

A single "92% relevant" score would hide exactly the information an engineer needs, so we never merge the three axes
into one number for display.
""")

st.subheader("Scientific limits we respect")
st.markdown("""
- PSI holds **no partial-gravity combustion data**. Lunar/Mars results are never interpolated between 0 g and 1 g.
- Same O₂ partial pressure ≠ same flammability: O₂ fraction, total pressure, flow and geometry all matter.
- CFI-G burner mixtures (up to 85% O₂) are combustion physics, **not** cabin atmospheres.
- Smoke (SAME) data comes from heated, non-flaming samples and is not compared with flame data.
- Droplet extinction (FLEX) is never plotted against solid flame spread.
- Rocket propulsion is outside this project's scope, as the challenge brief asks.
""")

st.subheader("From space to Earth")
for item in data.earth_links():
    st.markdown(f"**{item['title']}** - {item['text']}  \n<span class='fw-muted'>Source: "
                f"<a href='{item['url']}' target='_blank'>{item['source']}</a></span>", unsafe_allow_html=True)

st.subheader("NASA data used")
inv = ui.investigations()
show = inv[["psi_id", "acronym", "title", "pillar", "hardware", "doi", "license", "total_gb", "url"]]
st.dataframe(show, hide_index=True, width="stretch",
             column_config={"url": st.column_config.LinkColumn("PSI page"),
                            "total_gb": st.column_config.NumberColumn("data on PSI (GB)", format="%.1f")})
st.caption("NASA Physical Sciences Informatics (PSI) system, https://psi.nasa.gov - Combustion Science research "
           "area. Files are released under CC0 1.0. Publications are listed per investigation in "
           "data/curated/publications.csv.")

st.subheader("Team Errorists")
st.markdown("NASA Space Apps Challenge 2026 · Batticaloa, Sri Lanka · Challenge: *Flame in Freefall*.")
