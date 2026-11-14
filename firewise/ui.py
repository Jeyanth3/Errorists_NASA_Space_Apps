"""Shared bits for the Streamlit pages."""
import pandas as pd
import streamlit as st

from firewise import data

LEVEL_COLOR = {"DIRECT": "#2ecc71", "SUPPORTING": "#f1c40f", "EXTRAPOLATED": "#e74c3c"}
PILLAR_COLOR = {"prevention": "#ff7a45", "detection": "#4dabf7", "suppression": "#51cf66",
                "combustion physics": "#b197fc"}
PILLAR_ICON = {"prevention": "🛡️", "detection": "🚨", "suppression": "🧯", "combustion physics": "⚛️"}

CSS = """
<style>
.block-container {padding-top: 1.6rem; max-width: 1250px;}
.fw-hero {padding: 1.2rem 1.4rem; border-radius: 16px;
  background: linear-gradient(120deg, rgba(255,122,69,.18), rgba(77,171,247,.10)); border: 1px solid #2a3350;}
.fw-hero h1 {margin: 0 0 .3rem 0; font-size: 2.1rem;}
.fw-hero p {margin: 0; color: #c3cada; font-size: 1.05rem;}
.fw-card {padding: 1rem 1.1rem; border-radius: 14px; background: #141b2d; border: 1px solid #252e48; height: 100%;}
.fw-card h4 {margin: 0 0 .35rem 0;}
.fw-card p {margin: 0; color: #b8c0d4; font-size: .93rem;}
.fw-badge {display:inline-block; padding: 2px 10px; border-radius: 999px; font-weight: 600; font-size: .8rem; color:#0b1020;}
.fw-fact {padding: .55rem .8rem; border-left: 3px solid #ff7a45; background: #121828; margin-bottom: .4rem; border-radius: 6px;}
.fw-gap {border-left-color: #e74c3c;}
.fw-muted {color: #8b95ad; font-size: .85rem;}
</style>
"""


def setup(title):
    st.markdown(CSS, unsafe_allow_html=True)
    st.title(title)


def badge(level):
    c = LEVEL_COLOR.get(level, "#adb5bd")
    return f'<span class="fw-badge" style="background:{c}">{level}</span>'


def fact_box(f):
    cls = "fw-fact fw-gap" if f.get("kind") == "gap" else "fw-fact"
    src = " · ".join(f'<a href="https://psi.nasa.gov/physci/repo/data/{p}" target="_blank">{p}</a>' for p in f["psi_ids"])
    tag = "⚠️ evidence gap" if f.get("kind") == "gap" else "📊 computed from NASA runs"
    st.markdown(f'<div class="{cls}">{f["text"]}<br><span class="fw-muted">{tag} {("· " + src) if src else ""}</span></div>',
                unsafe_allow_html=True)


def psi_link(pid):
    return f"https://psi.nasa.gov/physci/repo/data/{pid}"


@st.cache_data
def runs():
    return data.runs().copy()


@st.cache_data
def investigations():
    return data.investigations().copy()


@st.cache_data
def publications():
    return data.publications().copy()


def mission_picker(key="mission", default="lunar_habitat", allow_custom=True):
    ms = data.missions()
    keys = list(ms.keys()) + (["custom"] if allow_custom else [])
    labels = {k: ms[k]["name"] for k in ms} | {"custom": "Custom environment"}
    k = st.selectbox("Mission environment", keys, index=keys.index(default), format_func=labels.get, key=key)
    if k == "custom":
        g = st.select_slider("Gravity", options=[0.0, 0.165, 0.38, 1.0], value=0.165,
                             format_func=lambda v: {0.0: "0 g (orbit)", 0.165: "Moon 0.165 g",
                                                    0.38: "Mars 0.38 g", 1.0: "Earth 1 g"}[v], key=key + "_g")
        p = st.slider("Total pressure (kPa)", 30.0, 110.0, 70.3, 0.5, key=key + "_p")
        x = st.slider("Oxygen fraction (%)", 15, 50, 30, key=key + "_x") / 100
        return {"key": "custom", "name": "Custom environment", "gravity_g": g, "pressure_kpa": p,
                "o2_fraction": x, "status": "user-defined", "note": "Values set by you."}
    return {"key": k, **ms[k]}


def fmt_pct(v):
    return "–" if pd.isna(v) else f"{v:.1%}"
