import plotly.express as px
import streamlit as st

from firewise import insights, mace, search, ui

ui.setup("🚀 Mission Explorer")
st.caption("Pick where the crew will live and what you need to know. FireWise ranks every NASA run by "
           "relevance, physical applicability and data quality - separately - and explains each match.")

runs = ui.runs()
left, right = st.columns([1, 2.2], gap="large")

with left:
    m = ui.mission_picker("mx", default="lunar_habitat")
    goal = st.radio("Safety goal", ["prevention", "detection", "suppression"], horizontal=True,
                    format_func=lambda g: f"{ui.PILLAR_ICON[g]} {g.title()}")
    mats = sorted(runs.loc[runs["pillar"].isin([goal, "combustion physics"] if goal != "detection" else [goal]),
                           "fuel"].dropna().unique())
    material = st.selectbox("Material / fuel (optional)", ["Any"] + mats)
    material = None if material == "Any" else material
    words = st.text_input("Keywords (optional)", placeholder="e.g. flame spread thin fabric")

    pO2 = m["o2_fraction"] * m["pressure_kpa"]
    st.markdown(
        f'<div class="fw-card"><h4>{m["name"]}</h4><p>'
        f'Gravity <b>{m["gravity_g"]:g} g</b> · Pressure <b>{m["pressure_kpa"]:.1f} kPa</b> '
        f'({m["pressure_kpa"] / 6.894757:.1f} psi)<br>O₂ <b>{m["o2_fraction"]:.0%}</b> · '
        f'O₂ partial pressure <b>{pO2:.1f} kPa</b><br>'
        f'<span class="fw-muted">status: {m["status"]} - {m["note"]}</span></p></div>', unsafe_allow_html=True)
    if abs(pO2 - 21.2) < 2.5 and m["o2_fraction"] > 0.25:
        st.info("Same O₂ partial pressure as sea-level air, but a higher O₂ *fraction*. Less inert nitrogen "
                "to absorb heat usually makes materials **more** flammable - pO₂ alone is not enough.")

q = mace.Query(goal=goal, gravity_g=m["gravity_g"], pressure_kpa=m["pressure_kpa"],
               o2_fraction=m["o2_fraction"], material=material, mission_name=m["name"], text=words)
ts = search.investigation_scores(words) if words else {}
assessed = mace.assess(q, text_scores=ts)
ranked = mace.rank_investigations(assessed)

with right:
    if assessed.empty:
        st.warning("No NASA run in the index addresses this combination.")
        st.stop()
    lv = assessed["level"].value_counts()
    c = st.columns(3)
    for col, L in zip(c, ["DIRECT", "SUPPORTING", "EXTRAPOLATED"]):
        col.markdown(f"{ui.badge(L)}", unsafe_allow_html=True)
        col.metric(f"{L.title()} runs", int(lv.get(L, 0)), label_visibility="collapsed")
    if lv.get("DIRECT", 0) == 0:
        st.error("**No DIRECT evidence exists in PSI for this question.** Everything below needs a stated "
                 "assumption to be used for this mission. That is itself a key finding.")

    st.markdown("#### Ranked NASA investigations")
    inv = ui.investigations().set_index("psi_id")
    for _, r in ranked.iterrows():
        title = inv.loc[r["psi_id"], "title"] if r["psi_id"] in inv.index else ""
        with st.container(border=True):
            a, b = st.columns([3, 2])
            a.markdown(f"**{r['investigation']}** - {title}  \n"
                       f"{ui.badge(r['best_level'])} &nbsp; <span class='fw-muted'>{r['runs']} runs · "
                       f"[{r['psi_id']}]({ui.psi_link(r['psi_id'])})</span>", unsafe_allow_html=True)
            b.progress(float(r["relevance"]), text=f"Relevance {r['relevance']:.2f}")
            b.progress(float(r["applicability"]), text=f"Applicability {r['applicability']:.2f}")
            b.progress(float(r["quality"]), text=f"Data quality {r['quality']:.2f}")

st.divider()
st.markdown("#### Relevance vs. applicability - every run")
st.caption("Top-right is what you want. High relevance + low applicability = right topic, wrong conditions.")
fig = px.scatter(assessed, x="applicability", y="relevance", color="level", symbol="investigation",
                 color_discrete_map=ui.LEVEL_COLOR, hover_data=["run_id", "quality"], height=430)
fig.update_traces(marker=dict(size=10, opacity=.8))
fig.update_layout(xaxis_range=[0, 1.05], yaxis_range=[0, 1.05], legend_title="", margin=dict(t=10))
st.plotly_chart(fig, width="stretch")

st.markdown("#### Condition certificate")
st.caption("Pick a run to see exactly which conditions match the mission. Built from rules, not written by a model.")
pick = st.selectbox("Run", assessed["run_id"].head(300),
                    format_func=lambda rid: f"{rid}  ({assessed.set_index('run_id').loc[rid, 'level']})")
row = assessed.set_index("run_id").loc[pick]
st.markdown(f"{ui.badge(row['level'])} &nbsp; **{pick}** · {row['investigation']}", unsafe_allow_html=True)
st.dataframe(mace.certificate_table(row["checks"]), hide_index=True, width="stretch")
raw = runs.set_index("run_id").loc[pick]
with st.expander("Raw NASA record and provenance"):
    st.write(f"Source: `{raw['source_file']}` row {raw['source_row']} · [{raw['psi_id']} on PSI]({ui.psi_link(raw['psi_id'])})")
    if raw["data_flags"]:
        st.warning("Flags: " + raw["data_flags"])
    st.dataframe(raw.dropna().astype(str).to_frame("value"), width="stretch")

st.markdown("#### What the measured data says")
facts = (insights.prevention(material, m["pressure_kpa"], m["o2_fraction"]) if goal == "prevention" else
         insights.suppression(m["pressure_kpa"], m["o2_fraction"]) if goal == "suppression" else insights.detection())
for f in facts:
    ui.fact_box(f)
if m["gravity_g"] > 0.01:
    st.warning(
        f"**Gravity transfer warning.** PSI holds microgravity data; this mission is at {m['gravity_g']:g} g. "
        "Partial-gravity flames are not 'between' 0 g and 1 g: weak buoyant flow can make some materials "
        "*more* flammable than in either case. Use these results to choose what to test, not as answers.")
