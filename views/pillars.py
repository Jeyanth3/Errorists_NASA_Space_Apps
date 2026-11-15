import pandas as pd
import plotly.express as px
import streamlit as st

from firewise import data, insights, ui

ui.header("Safety pillars", "Prevent. Detect.<br>Suppress.",
          lead="Key measured findings per pillar. Charts only compare like with like - droplet extinction is "
               "never plotted against solid flame spread.")
runs = ui.runs()
OUT = {"extinction": "#14c27a", "disruption": "#f2b632", "completion": ui.CORAL}


def intro(pillar, title, text, src):
    n = int((runs["pillar"] == pillar).sum())
    ui.html(f"""<div class="fw-card" style="display:flex;margin-top:1.2rem"><div class="in" style="flex:1">
    <div class="row">{ui.tile(ui.PILLAR_ICON[pillar], mint=True)}<div class="label">{pillar}</div></div>
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:2rem;margin-top:1.4rem"><h4>{title}</h4>
    <p style="margin:0">{text}<br><span class="fw-mono" style="color:#0f8a52">{n} runs · {src}</span></p></div></div>
    <div class="{ui.PILLAR_PATTERN[pillar]}" style="width:150px"></div></div>""")


t1, t2, t3, t4 = st.tabs(["Prevention", "Detection", "Suppression", "Combustion physics"])

with t1:
    intro("prevention", "Can it burn in orbit?", "Solid materials burned in microgravity: films, rods, spheres and "
          "spacecraft-scale fabric sheets.", "BASS · BASS-II · Saffire I-III")
    for f in insights.prevention():
        ui.fact_box(f)
    sol = runs[runs["pillar"] == "prevention"]
    c = st.columns(2)
    cnt = sol.groupby(["fuel", "investigation"]).size().reset_index(name="runs")
    c[0].plotly_chart(px.bar(cnt, x="runs", y="fuel", color="investigation", orientation="h", height=400,
                             title="WHICH MATERIALS WERE TESTED, AND WHERE"), width="stretch")
    sat = sol[sol["investigation"].str.startswith("Saffire")].copy()
    sat["burn_time_s"] = sat["burn_time_s"].fillna(0)
    c[1].plotly_chart(px.bar(sat, x="run_id", y="burn_time_s", color="fuel", pattern_shape="flow_dir", height=400,
                             title="SAFFIRE · BURN TIME PER SAMPLE (0 = NO SUSTAINED FLAME)",
                             labels={"burn_time_s": "burn time (s)"}), width="stretch")
    b2 = sol[(sol["investigation"] == "BASS-II") & sol["o2_fraction"].notna()]
    st.plotly_chart(px.strip(b2, x="o2_fraction", y="fuel", color="geometry", height=300,
                             title="BASS-II · OXYGEN LEVEL OF EACH BURN (ALL NEAR 1 ATM)",
                             labels={"o2_fraction": "O₂ mole fraction"}), width="stretch")

with t2:
    intro("detection", "Will we notice it early?", "Smoke from overheated - not yet flaming - spacecraft materials, "
          "aged and measured.", "SAME · SAME-R")
    particles = pd.read_csv(data.CURATED / "smoke_particles.csv", keep_default_na=False)
    sizes = particles[particles["variable"] == "Count mean diameter"]
    study = st.radio("Smoke experiment", sizes["investigation"].unique(), horizontal=True)
    selected = sizes[sizes["investigation"] == study]
    st.plotly_chart(px.bar(selected, x="material", y="value", color="condition", barmode="group",
                           text="value", title=f"{study} · Smoke particle size before and after aging",
                           labels={"material": "Material", "value": "Mean particle diameter (nm)",
                                   "condition": "Smoke age", "page": "PDF page", "location": "Table"},
                           hover_data=["page", "location"],
                           color_discrete_map={"Unaged": ui.TEAL, "Aged 12 min": ui.ORANGE}),
                    width="stretch")
    source_id = "PSI-102" if study == "SAME" else "PSI-101"
    pages = ", ".join(selected["page"].unique())
    st.caption(f"Each particle counts equally in the mean diameter. "
               f"[NASA {study} final report, Table 1, PDF pages {pages}]"
               f"(https://psi.nasa.gov/physci/repo/data/investigations/{source_id})")
    if study == "SAME":
        reading = particles[particles["variable"] == "Particle number concentration"].iloc[0]
        st.metric("Kapton run 14 · average P-Trak reading", f"{reading['value']:,} {reading['unit']}")
        st.caption(f"Instrument concentration in the sampled air. Source: {reading['report']}, "
                   f"cell {reading['location']}.")
    for f in insights.detection():
        ui.fact_box(f)
    sm = runs[(runs["investigation"] == "SAME-R") & runs["aging_s"].notna()]
    c = st.columns(2)
    c[0].plotly_chart(px.box(sm, x="fuel", y="aging_s", color="fuel", points="all", height=400,
                             title="SAME-R · SMOKE AGING BEFORE MEASUREMENT", labels={"aging_s": "aging time (s)"}),
                      width="stretch")
    c[1].plotly_chart(px.scatter(sm, x="heater_ratio", y="aging_s", color="fuel", height=400,
                                 title="HEATER SETTING (RT/R0) VS AGING",
                                 labels={"heater_ratio": "Rt/R0 (temperature proxy)", "aging_s": "aging time (s)"}),
                      width="stretch")

with t3:
    intro("suppression", "What puts it out?", "Fuel droplets burned in air, CO₂ and helium mixtures at several "
          "pressures and oxygen levels.", "FLEX")
    for f in insights.suppression():
        ui.fact_box(f)
    fx = runs[runs["investigation"] == "FLEX"].copy()
    c = st.columns(2)
    c[0].plotly_chart(px.scatter(fx, x="o2_fraction", y="pressure_kpa", color="outcome", symbol="diluent",
                                 facet_col="fuel", height=420, hover_data=["run_id", "diameter_mm"],
                                 color_discrete_map=OUT, title="FLEX · HOW EACH BURN ENDED",
                                 labels={"o2_fraction": "O₂ fraction", "pressure_kpa": "pressure (kPa)"}),
                      width="stretch")
    k = fx.dropna(subset=["burning_rate_k"])
    c[1].plotly_chart(px.scatter(k, x="o2_fraction", y="burning_rate_k", color="diluent", facet_col="fuel",
                                 height=420, title="BURNING-RATE CONSTANT K VS OXYGEN",
                                 labels={"burning_rate_k": "K (mm²/s)", "o2_fraction": "O₂ fraction"}),
                      width="stretch")
    share = (fx.groupby(["fuel", "diluent"])["outcome"].apply(lambda s: (s == "extinction").mean())
             .reset_index(name="extinction share"))
    st.plotly_chart(px.bar(share, x="diluent", y="extinction share", color="fuel", barmode="group", height=320,
                           title="SHARE OF FLEX BURNS ENDING IN EXTINCTION, BY DILUENT"), width="stretch")
    st.caption("Small samples for CO₂ (20 runs) and He (4 runs) - shares are indicative, not rates.")

with t4:
    intro("combustion physics", "Combustion experiments", "CFI records droplet test conditions. "
          "CFI-G measures burner flames across a range of oxygen mixtures.", "CFI · ACME CFI-G")
    for f in insights.physics():
        ui.fact_box(f)
    cf = runs[runs["investigation"] == "ACME CFI-G"]
    st.plotly_chart(px.histogram(cf, x="o2_fraction", color="outcome", facet_col="fuel", nbins=20, height=380,
                                 title="CFI-G · OUTCOME BY OXYGEN FRACTION"), width="stretch")
ui.footer()
