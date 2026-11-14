import pandas as pd
import plotly.express as px
import streamlit as st

from firewise import mace, ui

ui.header("Compare runs", "Fair fight<br>or not?",
          lead="Put two NASA runs side by side - within one investigation or across investigations - and see "
               "whether the comparison is physically fair.")

runs = ui.runs().set_index("run_id")
invs = sorted(runs["investigation"].unique())

c = st.columns(2, gap="large")
picked = []
for i, col in enumerate(c):
    with col:
        ui.html(f'<div class="fw-menu"><div class="i on">› Run {"A" if i == 0 else "B"}</div></div>')
        with st.container(border=True):
            inv = st.selectbox("Investigation", invs, index=invs.index("FLEX"), key=f"inv{i}")
            ids = runs[runs["investigation"] == inv].index.tolist()
            picked.append(st.selectbox("Run", ids, index=min(i * 3, len(ids) - 1), key=f"run{i}"))

a, b = runs.loc[picked[0]], runs.loc[picked[1]]
fields = [("investigation", "Investigation"), ("pillar", "Pillar"), ("fuel", "Fuel"), ("fuel_state", "Fuel state"),
          ("geometry", "Geometry"), ("thickness_mm", "Thickness mm"), ("diameter_mm", "Diameter mm"),
          ("o2_fraction", "O₂ fraction"), ("pressure_kpa", "Pressure kPa"), ("po2_kpa", "pO₂ kPa"),
          ("diluent", "Diluent"), ("flow_cm_s", "Flow cm/s"), ("flow_dir", "Flow direction"), ("outcome", "Outcome"),
          ("burn_time_s", "Burn time s"), ("spread_rate_mm_s", "Spread mm/s"), ("burning_rate_k", "K mm²/s"),
          ("extinction_diameter_mm", "Extinction diameter mm"), ("aging_s", "Smoke aging s")]


def same(x, y):
    if pd.isna(x) or pd.isna(y):
        return ("unknown", "—")
    if isinstance(x, (int, float)) and isinstance(y, (int, float)):
        ok = abs(x - y) <= 0.05 * max(abs(x), abs(y), 1e-9)
    else:
        ok = str(x) == str(y)
    return ("match", "SAME") if ok else ("mismatch", "DIFFERS")


def fmt(v):
    if pd.isna(v):
        return "—"
    return f"{v:.3g}" if isinstance(v, float) else str(v)


rows = [f'<div class="r h"><span></span><span>Field</span><span>{picked[0]}</span><span>{picked[1]}</span><span></span></div>']
for k, label in fields:
    x, y = a.get(k), b.get(k)
    if pd.isna(x) and pd.isna(y):
        continue
    st_, lab = same(x, y)
    col = ui.STATUS_STYLE[st_][0]
    rows.append(f'<div class="r"><span>{ui.icon("chevron", 16)}</span><b>{label}</b><span class="fw-mono">{fmt(x)}</span>'
                f'<span class="fw-mono">{fmt(y)}</span><span class="fw-badge" style="background:{col}">{lab}</span></div>')
ui.html(f'<div class="fw-acc" style="margin-top:1.4rem">{"".join(rows)}</div>')

q = mace.Query(goal=a["pillar"] if a["pillar"] in mace.PILLARS else "prevention",
               gravity_g=a["gravity_g"], pressure_kpa=a["pressure_kpa"] if pd.notna(a["pressure_kpa"]) else 101.3,
               o2_fraction=a["o2_fraction"] if pd.notna(a["o2_fraction"]) else 0.21,
               material=a["fuel"] if pd.notna(a["fuel"]) else None)
bad = [ch.name for ch in mace.compare(b.to_dict() | {"run_id": picked[1]}, q) if ch.status == "mismatch"]
if a["pillar"] != b["pillar"]:
    verdict, tone, text = "Not comparable", ui.CORAL, (f"These runs answer different safety questions ({a['pillar']} vs "
                                                       f"{b['pillar']}). Their outcomes measure different things.")
elif a.get("fuel_state") != b.get("fuel_state"):
    verdict, tone, text = "Not comparable", ui.CORAL, "Different fuel states (e.g. droplet vs solid). Outcome numbers mean different things."
elif bad:
    verdict, tone, text = "Compare with care", "#f2b632", "These conditions differ: " + ", ".join(bad) + "."
else:
    verdict, tone, text = "Fair comparison", ui.MINT, "Same question, same fuel state and closely matching atmosphere."
ui.html(f"""<div class="fw-dark" style="display:flex;gap:1.6rem;align-items:center">
<div class="fw-tile" style="background:{tone}">{ui.icon("scale", 28)}</div>
<div><div class="fw-eyebrow mint">Verdict</div><h2 class="fw-display sm">{verdict}</h2>
<p class="fw-lead" style="max-width:none;margin-top:.6rem">{text}</p></div></div>""")

ui.header("Trends", "Inside one investigation", size="sm")
inv = st.selectbox("Investigation", invs, index=invs.index("FLEX"), key="trend")
d = runs[runs["investigation"] == inv].reset_index()
num = [c for c in d.columns if pd.api.types.is_numeric_dtype(d[c]) and d[c].notna().sum() > 3
       and c not in ("gravity_g", "source_row")]
if len(num) >= 2:
    c1, c2 = st.columns(2)
    x = c1.selectbox("X axis", num, index=num.index("o2_fraction") if "o2_fraction" in num else 0)
    y = c2.selectbox("Y axis", num, index=num.index("burn_time_s") if "burn_time_s" in num else 1)
    color = "outcome" if d["outcome"].notna().any() else "fuel"
    st.plotly_chart(px.scatter(d, x=x, y=y, color=color, hover_data=["run_id", "fuel"], height=440,
                               title=f"{inv.upper()} · {y} VS {x}"), width="stretch")
else:
    st.info("Not enough numeric fields in this investigation's table for a trend plot.")
ui.footer()
