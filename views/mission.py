import plotly.express as px
import streamlit as st

from firewise import insights, mace, search, ui

ui.header("Mission explorer", "Match the physics,<br>not the keywords.",
          lead="Pick where the crew will live and what you need to know. Every NASA run is scored for relevance, "
               "physical applicability and data quality - separately - and each match is explained.")

runs = ui.runs()
left, right = st.columns([1, 2.1], gap="large")

with left:
    ui.html('<div class="fw-menu"><div class="i on">› Your mission</div></div>')
    with st.container(border=True):
        m = ui.mission_picker("mx", default="lunar_habitat")
        goal = st.radio("Safety goal", ["prevention", "detection", "suppression"],
                        format_func=lambda g: g.title(), horizontal=True)
        pool = [goal, "combustion physics"] if goal != "detection" else [goal]
        mats = sorted(runs.loc[runs["pillar"].isin(pool), "fuel"].dropna().unique())
        material = st.selectbox("Material / fuel (optional)", ["Any"] + mats)
        material = None if material == "Any" else material
        words = st.text_input("Keywords (optional)", placeholder="e.g. flame spread thin fabric")

    pO2 = m["o2_fraction"] * m["pressure_kpa"]
    ui.html(f"""<div class="fw-card"><div class="band fw-pat-band"></div><div class="in">
    <div class="row">{ui.tile(ui.MISSION_ICON.get(m['key'], 'spark'), mint=True)}
    <div><div class="label" style="font-size:.78rem">{m['status']}</div><h4>{m['name']}</h4></div></div>
    <div class="fw-stats" style="margin:1.2rem 0 .6rem;grid-template-columns:1fr 1fr">
    <div class="fw-stat"><div class="v" style="font-size:2rem">{m['gravity_g']:g} g</div><div class="l">gravity</div></div>
    <div class="fw-stat"><div class="v" style="font-size:2rem">{m['pressure_kpa']:.1f}</div><div class="l">kPa · {m['pressure_kpa'] / 6.894757:.1f} psi</div></div>
    <div class="fw-stat" style="border-top:1px solid #e4dfd3"><div class="v" style="font-size:2rem">{m['o2_fraction']:.0%}</div><div class="l">oxygen fraction</div></div>
    <div class="fw-stat" style="border-top:1px solid #e4dfd3"><div class="v" style="font-size:2rem">{pO2:.1f}</div><div class="l">pO₂ kPa</div></div></div>
    <p class="fw-muted" style="margin:0">{m['note']}</p></div></div>""")
    if abs(pO2 - 21.2) < 2.5 and m["o2_fraction"] > 0.25:
        st.info("Same O₂ partial pressure as sea-level air, but a higher O₂ fraction: less nitrogen to soak up heat "
                "usually makes materials more flammable. pO₂ alone is not enough.")

q = mace.Query(goal=goal, gravity_g=m["gravity_g"], pressure_kpa=m["pressure_kpa"],
               o2_fraction=m["o2_fraction"], material=material, mission_name=m["name"], text=words)
assessed = mace.assess(q, text_scores=search.investigation_scores(words) if words else {})
ranked = mace.rank_investigations(assessed)

with right:
    if assessed.empty:
        st.warning("No NASA run in the index addresses this combination.")
        st.stop()
    lv = assessed["level"].value_counts()
    ui.stats([(int(lv.get(L, 0)), f"{L.lower()} runs") for L in ("DIRECT", "SUPPORTING", "EXTRAPOLATED")])
    if lv.get("DIRECT", 0) == 0:
        ui.fact_box({"text": "<b>No DIRECT evidence exists in PSI for this question.</b> Everything below needs a stated "
                             "assumption before it can be used for this mission - that is itself a key finding.",
                     "psi_ids": [], "kind": "gap"})

    inv = ui.investigations().set_index("psi_id")
    for i, (_, r) in enumerate(ranked.iterrows()):
        title = inv.loc[r["psi_id"], "title"] if r["psi_id"] in inv.index else ""
        pillar = runs.loc[runs["psi_id"] == r["psi_id"], "pillar"].iloc[0]
        meters = ui.meter("Relevance", r["relevance"]) + ui.meter("Applicability", r["applicability"]) + \
            ui.meter("Data quality", r["quality"])
        ui.card(f"{i + 1:02d} · {r['investigation']}", ui.PILLAR_ICON[pillar], band=ui.PILLAR_PATTERN[pillar],
                mint_tile=(i == 0), right=ui.badge(r["best_level"]),
                body=f"""<div style="display:grid;grid-template-columns:1.1fr 1fr;gap:2rem;margin-top:1.2rem">
                <div><h4>{title}</h4><p class="fw-mono" style="margin-top:.8rem;font-size:.72rem">{r['runs']} runs ·
                {r['direct']} direct · {r['supporting']} supporting · {r['extrapolated']} extrapolated ·
                <a href="{ui.psi_link(r['psi_id'])}" target="_blank" style="color:#0f8a52">{r['psi_id']} ↗</a></p></div>
                <div>{meters}</div></div>""")

st.markdown("")
ui.header("Every run", "Relevance vs applicability", size="sm",
          lead="Top-right is what you want. High relevance with low applicability means right topic, wrong conditions.")
fig = px.scatter(assessed, x="applicability", y="relevance", color="level", symbol="investigation",
                 color_discrete_map=ui.LEVEL_COLOR, hover_data=["run_id", "quality"], height=440)
fig.update_traces(marker=dict(size=11, opacity=.85, line=dict(width=1, color="#fff")))
fig.update_layout(xaxis_range=[0, 1.05], yaxis_range=[0, 1.05], legend_title="")
st.plotly_chart(fig, width="stretch")

ui.header("Condition certificate", "Why this level?", size="sm",
          lead="Built from explicit rules, not written by a model. Pick any run.")
pick = st.selectbox("Run", assessed["run_id"].head(400),
                    format_func=lambda rid: f"{rid}  ·  {assessed.set_index('run_id').loc[rid, 'level']}")
row = assessed.set_index("run_id").loc[pick]
ui.html(f'<p>{ui.badge(row["level"])} &nbsp; <b>{pick}</b> · {row["investigation"]}</p>')
ui.certificate(row["checks"])
raw = runs.set_index("run_id").loc[pick]
with st.expander("Raw NASA record and provenance"):
    st.markdown(f"Source: `{raw['source_file']}` row {raw['source_row']} · [{raw['psi_id']} on PSI]({ui.psi_link(raw['psi_id'])})")
    if raw["data_flags"]:
        st.warning("Flags: " + raw["data_flags"])
    st.dataframe(raw.dropna().astype(str).to_frame("value"), width="stretch")
c1, c2 = st.columns(2)
c1.download_button("Download ranking (CSV)", ranked.to_csv(index=False), "firewise_ranking.csv", "text/csv")
c2.download_button("Download certificate (CSV)", mace.certificate_table(row["checks"]).to_csv(index=False),
                   f"certificate_{pick}.csv", "text/csv")

ui.header("Measured findings", "What the data says", size="sm")
facts = (insights.prevention(material, m["pressure_kpa"], m["o2_fraction"]) if goal == "prevention" else
         insights.suppression(m["pressure_kpa"], m["o2_fraction"]) if goal == "suppression" else insights.detection())
for f in facts:
    ui.fact_box(f)
if m["gravity_g"] > 0.01:
    ui.html(f"""<div class="fw-dark" style="display:flex;gap:1.6rem;align-items:flex-start">
    {ui.tile("warning", mint=True)}<div><div class="fw-eyebrow mint">Gravity transfer warning</div>
    <p class="fw-lead" style="max-width:none">PSI holds microgravity data; this mission is at {m['gravity_g']:g} g.
    Partial-gravity flames are not "between" 0 g and 1 g - weak buoyant flow can make some materials <b>more</b>
    flammable than in either case. Use these results to choose what to test, not as answers.</p></div></div>""")
ui.footer()
