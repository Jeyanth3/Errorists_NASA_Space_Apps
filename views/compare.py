import pandas as pd
import plotly.express as px
import streamlit as st

from firewise import mace, ui

ui.setup("⚖️ Compare Runs")
st.caption("Put two NASA runs side by side - within one investigation or across investigations. "
           "FireWise says whether the comparison is physically fair.")

runs = ui.runs().set_index("run_id")
invs = sorted(runs["investigation"].unique())

c = st.columns(2)
picked = []
for i, col in enumerate(c):
    with col:
        inv = st.selectbox(f"Investigation {i + 1}", invs, index=invs.index("FLEX") if i == 0 else invs.index("FLEX"),
                           key=f"inv{i}")
        ids = runs[runs["investigation"] == inv].index.tolist()
        rid = st.selectbox(f"Run {i + 1}", ids, index=min(i * 3, len(ids) - 1), key=f"run{i}")
        picked.append(rid)

a, b = runs.loc[picked[0]], runs.loc[picked[1]]
cols = ["investigation", "pillar", "fuel", "fuel_state", "geometry", "thickness_mm", "diameter_mm", "o2_fraction",
        "pressure_kpa", "po2_kpa", "diluent", "flow_cm_s", "flow_dir", "outcome", "burn_time_s", "spread_rate_mm_s",
        "burning_rate_k", "extinction_diameter_mm", "aging_s"]
tab = pd.DataFrame({"field": cols, picked[0]: [a.get(k) for k in cols], picked[1]: [b.get(k) for k in cols]})
tab = tab.dropna(subset=[picked[0], picked[1]], how="all")


def same(x, y):
    if pd.isna(x) or pd.isna(y):
        return "❔"
    if isinstance(x, (int, float)) and isinstance(y, (int, float)):
        return "✅" if abs(x - y) <= 0.05 * max(abs(x), abs(y), 1e-9) else "❌"
    return "✅" if str(x) == str(y) else "❌"


tab["same?"] = [same(x, y) for x, y in zip(tab[picked[0]], tab[picked[1]])]
st.dataframe(tab.astype(str), hide_index=True, width="stretch")

# fairness verdict, reusing MACE: treat run A's conditions as the "mission"
q = mace.Query(goal=a["pillar"] if a["pillar"] in mace.PILLARS else "prevention",
               gravity_g=a["gravity_g"], pressure_kpa=a["pressure_kpa"] if pd.notna(a["pressure_kpa"]) else 101.3,
               o2_fraction=a["o2_fraction"] if pd.notna(a["o2_fraction"]) else 0.21,
               material=a["fuel"] if pd.notna(a["fuel"]) else None)
checks = mace.compare(b.to_dict() | {"run_id": picked[1]}, q)
bad = [ch.name for ch in checks if ch.status == "mismatch"]
if a["pillar"] != b["pillar"]:
    st.error(f"Not comparable: these runs answer different safety questions ({a['pillar']} vs {b['pillar']}). "
             "Their outcomes measure different things.")
elif a.get("fuel_state") != b.get("fuel_state"):
    st.error("Not comparable: different fuel states (e.g. droplet vs solid). Outcome numbers mean different things.")
elif bad:
    st.warning("Comparable with care - these conditions differ: " + ", ".join(bad))
else:
    st.success("Fair comparison: same question, fuel state and closely matching atmosphere.")

st.markdown("#### Trend inside one investigation")
inv = st.selectbox("Investigation", invs, index=invs.index("FLEX"), key="trend")
d = runs[runs["investigation"] == inv].reset_index()
num = [c for c in d.columns if pd.api.types.is_numeric_dtype(d[c]) and d[c].notna().sum() > 3
       and c not in ("gravity_g", "source_row")]
if len(num) >= 2:
    x = st.selectbox("X", num, index=num.index("o2_fraction") if "o2_fraction" in num else 0)
    y = st.selectbox("Y", num, index=num.index("burn_time_s") if "burn_time_s" in num else 1)
    color = "outcome" if d["outcome"].notna().any() else "fuel"
    st.plotly_chart(px.scatter(d, x=x, y=y, color=color, hover_data=["run_id", "fuel"], height=420),
                    width="stretch")
else:
    st.info("Not enough numeric fields in this investigation's table for a trend plot.")
