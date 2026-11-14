import networkx as nx
import plotly.graph_objects as go
import streamlit as st

from firewise import audit, ui

ui.setup("🔎 Data Reliability")
st.caption("A dashboard is only as good as its data. Here is everything we assumed, inferred or found "
           "inconsistent in the NASA records - nothing was silently changed.")

runs = ui.runs()
c = st.columns(3)
c[0].metric("Runs without any flag", int((runs["data_flags"] == "").sum()))
c[1].metric("Runs with an assumption/inference", int((runs["data_flags"] != "").sum()))
c[2].metric("Metadata conflicts logged", len(audit.metadata_conflicts()))

st.subheader("Metadata conflicts")
st.dataframe(audit.metadata_conflicts(), hide_index=True, width="stretch")
st.caption("Also saved to data/audits/metadata_conflicts.csv. Original NASA values are kept in data/raw.")

st.subheader("Flags on individual runs")
st.dataframe(audit.flag_summary(), hide_index=True, width="stretch")

st.subheader("Field completeness per investigation")
st.caption("Share of runs where the field was reported (1.0 = always).")
comp = audit.completeness()
st.dataframe(comp.style.format("{:.0%}"), width="stretch")

st.subheader("Evidence graph")
st.caption("Investigations linked to shared hardware, safety pillar and materials. Shared hardware hints at "
           "comparable set-ups - but does not prove equal conditions.")
inv = ui.investigations()
G = nx.Graph()
core = inv[inv["psi_id"].isin(runs["psi_id"].unique())]
for _, r in core.iterrows():
    G.add_node(r["acronym"], kind="investigation")
    G.add_node(r["pillar"], kind="pillar")
    G.add_edge(r["acronym"], r["pillar"])
    hw = r["hardware"].lower()
    for key, name in (("glovebox", "Microgravity Science Glovebox"), ("msg", "Microgravity Science Glovebox"),
                      ("cir", "Combustion Integrated Rack"), ("cygnus", "Cygnus vehicle"),
                      ("soot diagnostic", "Comparative Soot Diagnostic hw"), ("mdca", "Droplet Apparatus (MDCA)")):
        if key in hw:
            G.add_node(name, kind="hardware")
            G.add_edge(r["acronym"], name)
for (acr, fuel), _ in runs.groupby(["investigation", "fuel"]):
    a = core.loc[core["psi_id"] == runs.loc[runs["investigation"] == acr, "psi_id"].iloc[0], "acronym"]
    if len(a):
        G.add_node(fuel, kind="material")
        G.add_edge(a.iloc[0], fuel)
pos = nx.spring_layout(G, seed=7, k=0.6)
colors = {"investigation": "#ff7a45", "pillar": "#4dabf7", "hardware": "#b197fc", "material": "#51cf66"}
ex, ey = [], []
for u, v in G.edges():
    ex += [pos[u][0], pos[v][0], None]
    ey += [pos[u][1], pos[v][1], None]
fig = go.Figure(go.Scatter(x=ex, y=ey, mode="lines", line=dict(color="#3a4361", width=1), hoverinfo="skip"))
for kind, col in colors.items():
    ns = [n for n, d in G.nodes(data=True) if d["kind"] == kind]
    fig.add_trace(go.Scatter(x=[pos[n][0] for n in ns], y=[pos[n][1] for n in ns], mode="markers+text", text=ns,
                             textposition="top center", name=kind,
                             marker=dict(size=18 if kind != "material" else 11, color=col)))
fig.update_layout(height=620, showlegend=True, xaxis=dict(visible=False), yaxis=dict(visible=False), margin=dict(t=10))
st.plotly_chart(fig, width="stretch")
