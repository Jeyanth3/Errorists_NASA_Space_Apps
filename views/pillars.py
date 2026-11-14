import plotly.express as px
import streamlit as st

from firewise import insights, ui

ui.setup("🧯 Prevent · Detect · Suppress")
st.caption("Key measured findings per safety pillar. Each chart compares only like with like - "
           "droplet extinction is never plotted against solid flame spread.")
runs = ui.runs()

t1, t2, t3, t4 = st.tabs(["🛡️ Prevention", "🚨 Detection", "🧯 Suppression", "⚛️ Combustion physics"])

with t1:
    st.markdown("**Can it burn?** Solid materials burned in microgravity: BASS, BASS-II, Saffire I-III.")
    for f in insights.prevention():
        ui.fact_box(f)
    sol = runs[runs["pillar"] == "prevention"]
    c = st.columns(2)
    cnt = sol.groupby(["fuel", "investigation"]).size().reset_index(name="runs")
    c[0].plotly_chart(px.bar(cnt, x="runs", y="fuel", color="investigation", orientation="h", height=380,
                             title="Which materials were tested, and where"), width="stretch")
    sat = sol[sol["investigation"].str.startswith("Saffire")].copy()
    sat["burn_time_s"] = sat["burn_time_s"].fillna(0)
    c[1].plotly_chart(px.bar(sat, x="run_id", y="burn_time_s", color="fuel", pattern_shape="flow_dir", height=380,
                             title="Saffire: burn time per sample (0 = no sustained flame)",
                             labels={"burn_time_s": "burn time (s)"}), width="stretch")
    b2 = sol[(sol["investigation"] == "BASS-II") & sol["o2_fraction"].notna()]
    st.plotly_chart(px.strip(b2, x="o2_fraction", y="fuel", color="geometry", height=300,
                             title="BASS-II: oxygen level of each burn (all near 1 atm)",
                             labels={"o2_fraction": "O₂ mole fraction"}), width="stretch")

with t2:
    st.markdown("**Will we notice it early?** Smoke from overheated (not yet flaming) materials: SAME, SAME-R.")
    for f in insights.detection():
        ui.fact_box(f)
    sm = runs[(runs["investigation"] == "SAME-R") & runs["aging_s"].notna()]
    c = st.columns(2)
    c[0].plotly_chart(px.box(sm, x="fuel", y="aging_s", color="fuel", points="all", height=380,
                             title="SAME-R: smoke aging time before measurement",
                             labels={"aging_s": "aging time (s)"}), width="stretch")
    c[1].plotly_chart(px.scatter(sm, x="heater_ratio", y="aging_s", color="fuel", size_max=10, height=380,
                                 title="Heater setting (Rt/R0, temperature proxy) vs. aging",
                                 labels={"heater_ratio": "Rt/R0", "aging_s": "aging time (s)"}),
                      width="stretch")
    st.info("Detection evidence covers six materials at ISS cabin pressure only. Particle size results live in "
            "the SAME reports on PSI (downloaded in data/raw/psi/PSI-101 and PSI-102).")

with t3:
    st.markdown("**How do we put it out?** Fuel droplets burned in different atmospheres: FLEX.")
    for f in insights.suppression():
        ui.fact_box(f)
    fx = runs[runs["investigation"] == "FLEX"].copy()
    c = st.columns(2)
    c[0].plotly_chart(px.scatter(fx, x="o2_fraction", y="pressure_kpa", color="outcome", symbol="diluent",
                                 facet_col="fuel", height=420, hover_data=["run_id", "diameter_mm"],
                                 color_discrete_map={"extinction": "#51cf66", "disruption": "#fcc419",
                                                     "completion": "#ff6b6b"},
                                 title="FLEX: how each burn ended, by atmosphere",
                                 labels={"o2_fraction": "O₂ fraction", "pressure_kpa": "pressure (kPa)"}),
                      width="stretch")
    k = fx.dropna(subset=["burning_rate_k"])
    c[1].plotly_chart(px.scatter(k, x="o2_fraction", y="burning_rate_k", color="diluent", facet_col="fuel",
                                 height=420, title="Burning-rate constant K vs. oxygen",
                                 labels={"burning_rate_k": "K (mm²/s)", "o2_fraction": "O₂ fraction"}),
                      width="stretch")
    share = (fx.groupby(["fuel", "diluent"])["outcome"].apply(lambda s: (s == "extinction").mean())
             .reset_index(name="extinction share"))
    st.plotly_chart(px.bar(share, x="diluent", y="extinction share", color="fuel", barmode="group", height=320,
                           title="Share of FLEX burns ending in extinction, by diluent"), width="stretch")
    st.caption("Small samples for CO₂ (20 runs) and He (4 runs) - treat shares as indicative, not rates.")

with t4:
    st.markdown("**Context only.** ACME CFI-G burner flames, including very high O₂ mixtures. These are "
                "combustion-physics conditions, not crew atmospheres.")
    for f in insights.physics():
        ui.fact_box(f)
    cf = runs[runs["investigation"] == "ACME CFI-G"]
    st.plotly_chart(px.histogram(cf, x="o2_fraction", color="outcome", facet_col="fuel", nbins=20, height=380,
                                 title="CFI-G outcome by oxygen fraction"), width="stretch")
