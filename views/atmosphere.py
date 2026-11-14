import numpy as np
import plotly.graph_objects as go
import streamlit as st

from firewise import data, insights, ui

ui.header("Atmosphere map", "Where NASA tested.<br>Where you live.",
          lead="Every NASA run plotted by the atmosphere it burned in. Mission atmospheres are stars; dotted lines "
               "join atmospheres with the same oxygen partial pressure.")

runs = ui.runs()
ms = data.missions()
d = runs.dropna(subset=["o2_fraction", "pressure_kpa"]).copy()
d = d[d["pressure_kpa"] < 250]

c1, c2 = st.columns([1, 2.8], gap="large")
with c1:
    ui.html('<div class="fw-menu"><div class="i on">› Filters</div></div>')
    with st.container(border=True):
        show = st.multiselect("Pillars", ["prevention", "detection", "suppression", "combustion physics"],
                              default=["prevention", "suppression", "combustion physics"])
        habitable = st.toggle("Hide burner-only mixtures (CFI-G)", value=False)
    rows = "".join(
        f'<div class="i" style="border-bottom:1px solid #0b6b66"><span>★ {m["short"]}</span>'
        f'<span style="font-size:.72rem;opacity:.8">{m["o2_fraction"]:.0%} · {m["pressure_kpa"]:.0f} kPa</span></div>'
        for m in ms.values())
    ui.html(f'<div class="fw-menu" style="margin-top:1rem">{rows}</div>')

d = d[d["pillar"].isin(show)]
if habitable:
    d = d[d["investigation"] != "ACME CFI-G"]

fig = go.Figure()
for ppo2 in (10, 15, 21.2, 30, 40):
    x = np.linspace(0.12, 0.9, 80)
    fig.add_trace(go.Scatter(x=x * 100, y=ppo2 / x, mode="lines", line=dict(dash="dot", width=1, color="#a8a395"),
                             hoverinfo="skip", showlegend=False))
    fig.add_annotation(x=ppo2 / 230 * 100 + 2, y=228, text=f"pO₂ {ppo2:g}", showarrow=False,
                       font=dict(size=10, color="#8c887e", family="IBM Plex Mono"))
for pillar, g in d.groupby("pillar"):
    fig.add_trace(go.Scatter(
        x=g["o2_fraction"] * 100, y=g["pressure_kpa"], mode="markers", name=f"{pillar} ({len(g)})",
        marker=dict(size=9, color=ui.PILLAR_COLOR[pillar], opacity=.75, line=dict(width=1, color="#fff")),
        text=g["run_id"] + " · " + g["investigation"] + " · " + g["fuel"].fillna(""),
        hovertemplate="%{text}<br>O₂ %{x:.1f}%<br>P %{y:.1f} kPa<extra></extra>"))
for m in ms.values():
    fig.add_trace(go.Scatter(x=[m["o2_fraction"] * 100], y=[m["pressure_kpa"]], mode="markers+text",
                             marker=dict(symbol="star", size=22, color=ui.INK, line=dict(color=ui.MINT, width=2)),
                             text=[m["short"]], textposition="top center", showlegend=False,
                             textfont=dict(family="IBM Plex Mono", size=11)))
fig.update_layout(height=620, xaxis_title="OXYGEN MOLE FRACTION (%)", yaxis_title="TOTAL PRESSURE (KPA)",
                  xaxis_range=[10, 90], yaxis_range=[20, 240], legend_title="NASA runs")
with c2:
    st.plotly_chart(fig, width="stretch")

ui.header("Coverage", "Tested vs untested", size="sm",
          lead="Runs per material and oxygen band. Empty cells were never tested in the indexed PSI data.")
pill = st.radio("Pillar", ["prevention", "suppression", "detection"], horizontal=True, format_func=str.title)
cov = insights.coverage(runs[runs["pillar"] == pill])
if cov.empty:
    st.info("No oxygen values recorded for this pillar (SAME/SAME-R did not log O₂).")
else:
    hm = go.Figure(go.Heatmap(z=cov.values, x=cov.columns.astype(str), y=cov.index, text=cov.values,
                              texttemplate="%{text}", colorscale=[[0, "#f4f1ea"], [0.001, "#c9f7df"], [1, "#0f8a52"]],
                              showscale=False, xgap=3, ygap=3,
                              hovertemplate="%{y} · %{x}: %{z} runs<extra></extra>"))
    hm.update_layout(height=140 + 40 * len(cov), xaxis_title="O₂ BAND")
    st.plotly_chart(hm, width="stretch")

hab = runs[(runs["o2_fraction"] >= 0.28) & (runs["pressure_kpa"] <= 80) & (runs["investigation"] != "ACME CFI-G")]
if hab.empty:
    msg = "None of the indexed PSI runs sit inside the lunar habitat atmosphere envelope."
else:
    msg = (f"All from {', '.join(sorted(hab['investigation'].unique()))}, all in microgravity, all liquid fuel droplets. "
           "This is the closest NASA evidence to a Moon-base atmosphere - and there is no solid-material run here at all.")
ui.html(f"""<div class="fw-dark"><div class="fw-eyebrow mint">Lunar habitat envelope · ≥28% O₂ · ≤80 kPa</div>
<h2 class="fw-display sm">{len(hab)} runs inside</h2>
<p class="fw-lead" style="max-width:52rem;margin-top:1rem">{msg}</p></div>""")
if not hab.empty:
    st.dataframe(hab[["run_id", "investigation", "fuel", "o2_fraction", "pressure_kpa", "outcome", "burn_time_s"]],
                 hide_index=True, width="stretch")
ui.footer()
