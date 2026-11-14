import numpy as np
import plotly.graph_objects as go
import streamlit as st

from firewise import data, insights, ui

ui.setup("🗺️ Atmosphere Map")
st.caption("Every NASA run plotted by the atmosphere it burned in. Mission atmospheres are stars. "
           "Dashed lines join atmospheres with the same oxygen partial pressure.")

runs = ui.runs()
d = runs.dropna(subset=["o2_fraction", "pressure_kpa"]).copy()
d = d[d["pressure_kpa"] < 250]

c1, c2 = st.columns([1, 3])
with c1:
    show = st.multiselect("Show pillars", ["prevention", "detection", "suppression", "combustion physics"],
                          default=["prevention", "suppression", "combustion physics"])
    habitable = st.toggle("Hide burner-only mixtures (CFI-G)", value=False)
    st.markdown("**Mission atmospheres**")
    ms = data.missions()
    for _k, m in ms.items():
        st.markdown(f"⭐ {m['short']}: {m['o2_fraction']:.0%} O₂, {m['pressure_kpa']:.0f} kPa "
                    f"<span class='fw-muted'>({m['status']})</span>", unsafe_allow_html=True)

d = d[d["pillar"].isin(show)]
if habitable:
    d = d[d["investigation"] != "ACME CFI-G"]

fig = go.Figure()
for ppo2 in (10, 15, 21.2, 30, 40):
    x = np.linspace(0.12, 0.9, 80)
    fig.add_trace(go.Scatter(x=x * 100, y=ppo2 / x, mode="lines", line=dict(dash="dot", width=1, color="#56607a"),
                             name=f"pO₂ {ppo2:g} kPa", hoverinfo="skip", showlegend=False))
    fig.add_annotation(x=ppo2 / 105 * 100, y=105, text=f"pO₂ {ppo2:g}", showarrow=False,
                       font=dict(size=10, color="#8b95ad"))
for pillar, g in d.groupby("pillar"):
    fig.add_trace(go.Scatter(
        x=g["o2_fraction"] * 100, y=g["pressure_kpa"], mode="markers", name=f"{pillar} ({len(g)})",
        marker=dict(size=8, color=ui.PILLAR_COLOR[pillar], opacity=.65, line=dict(width=0)),
        text=g["run_id"] + " · " + g["investigation"] + " · " + g["fuel"].fillna(""),
        hovertemplate="%{text}<br>O₂ %{x:.1f}%<br>P %{y:.1f} kPa<extra></extra>"))
for _k, m in ms.items():
    fig.add_trace(go.Scatter(x=[m["o2_fraction"] * 100], y=[m["pressure_kpa"]], mode="markers+text",
                             marker=dict(symbol="star", size=20, color="white", line=dict(color="#ff7a45", width=2)),
                             text=[m["short"]], textposition="top center", name=m["short"], showlegend=False))
fig.update_layout(height=600, xaxis_title="Oxygen mole fraction (%)", yaxis_title="Total pressure (kPa)",
                  xaxis_range=[10, 90], yaxis_range=[20, 240], margin=dict(t=10), legend_title="NASA runs")
with c2:
    st.plotly_chart(fig, width="stretch")

st.subheader("Coverage gaps")
st.caption("How many runs exist for each material in each oxygen band. Empty cells are untested in the indexed PSI data.")
pill = st.radio("Pillar", ["prevention", "suppression", "detection"], horizontal=True)
sub = runs[runs["pillar"] == pill]
cov = insights.coverage(sub)
if cov.empty:
    st.info("No oxygen values recorded for this pillar (SAME/SAME-R did not log O₂).")
else:
    hm = go.Figure(go.Heatmap(z=cov.values, x=cov.columns.astype(str), y=cov.index, colorscale="Oranges",
                              text=cov.values, texttemplate="%{text}", hovertemplate="%{y} · %{x}: %{z} runs<extra></extra>"))
    hm.update_layout(height=120 + 38 * len(cov), xaxis_title="O₂ band", margin=dict(t=10))
    st.plotly_chart(hm, width="stretch")

hab = runs[(runs["o2_fraction"] >= 0.28) & (runs["pressure_kpa"] <= 80) & (runs["investigation"] != "ACME CFI-G")]
st.markdown("#### Runs inside the proposed lunar-habitat envelope (≥28% O₂, ≤80 kPa)")
if hab.empty:
    st.error("None. No PSI run in this index sits inside the lunar habitat atmosphere envelope.")
else:
    st.dataframe(hab[["run_id", "investigation", "fuel", "o2_fraction", "pressure_kpa", "outcome", "burn_time_s"]],
                 hide_index=True, width="stretch")
    st.caption(f"{len(hab)} runs - all {', '.join(sorted(hab['investigation'].unique()))}, all in microgravity. "
               "This is the closest NASA evidence to a Moon-base atmosphere.")
