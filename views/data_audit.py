import networkx as nx
import plotly.graph_objects as go
import streamlit as st

from firewise import audit, ui

ui.header("Data reliability", "Nothing hidden.<br>Nothing invented.",
          lead="A dashboard is only as good as its data. Every assumption, inference and NASA metadata conflict we "
               "found - and nothing silently changed.")

runs = ui.runs()
conf = audit.metadata_conflicts()
ui.stats([(int((runs["data_flags"] == "").sum()), "runs without any flag"),
          (int((runs["data_flags"] != "").sum()), "runs with an assumption"),
          (len(conf), "metadata conflicts logged"),
          (runs["source_file"].nunique(), "NASA source tables")])

ui.header("Conflicts", "Metadata conflicts", size="sm")
rows = ['<div class="r h" style="grid-template-columns:28px 120px 1fr 1.4fr 170px"><span></span><span>PSI</span>'
        '<span>Field · NASA value</span><span>Conflicting evidence</span><span>Status</span></div>']
for _, c in conf.iterrows():
    rows.append(f'<div class="r" style="grid-template-columns:28px 120px 1fr 1.4fr 170px"><span>{ui.icon("warning", 16)}</span>'
                f'<span class="fw-mono">{c["psi_id"]}</span><span><b>{c["field"]}</b><br>'
                f'<span class="fw-muted">{c["nasa_value"]}</span></span><span>{c["conflicting_evidence"]}<br>'
                f'<span class="fw-muted">Proposed: {c["proposed"]}</span></span>'
                f'<span class="fw-badge" style="background:#f2b632">{c["status"]}</span></div>')
ui.html(f'<div class="fw-acc">{"".join(rows)}</div>')
st.caption("Saved to data/audits/metadata_conflicts.csv. Original NASA values are kept unchanged in data/raw.")

c1, c2 = st.columns(2, gap="large")
with c1:
    ui.eyebrow("Flags on runs")
    st.dataframe(audit.flag_summary(), hide_index=True, width="stretch", height=420)
with c2:
    ui.eyebrow("Field completeness")
    st.dataframe(audit.completeness().style.format("{:.0%}"), width="stretch", height=420)

ui.header("Connections", "Evidence graph", size="sm",
          lead="Investigations linked to hardware, safety pillar and materials. Shared hardware hints at comparable "
               "set-ups - it does not prove equal conditions.")
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
colors = {"investigation": ui.TEAL_2, "pillar": ui.MINT, "hardware": ui.PINK, "material": ui.ORANGE}
ex, ey = [], []
for u, v in G.edges():
    ex += [pos[u][0], pos[v][0], None]
    ey += [pos[u][1], pos[v][1], None]
fig = go.Figure(go.Scatter(x=ex, y=ey, mode="lines", line=dict(color="#cfc9bb", width=1), hoverinfo="skip",
                           showlegend=False))
for kind, col in colors.items():
    ns = [n for n, d in G.nodes(data=True) if d["kind"] == kind]
    fig.add_trace(go.Scatter(x=[pos[n][0] for n in ns], y=[pos[n][1] for n in ns], mode="markers+text", text=ns,
                             textposition="top center", name=kind, textfont=dict(family="IBM Plex Mono", size=10),
                             marker=dict(size=20 if kind != "material" else 12, color=col, symbol="square",
                                         line=dict(width=1, color=ui.INK))))
fig.update_layout(height=640, xaxis=dict(visible=False), yaxis=dict(visible=False), plot_bgcolor="#fff")
st.plotly_chart(fig, width="stretch")
ui.footer()
