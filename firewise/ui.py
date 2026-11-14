"""
FireWise look & feel.

Design language: deep teal + mint, warm cream paper, heavy condensed display type, mono uppercase labels,
square edges, barcode stripe bands and plank / waveform patterns. Everything visual lives here so pages stay small.
"""
import base64
import functools
import math
import textwrap

import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
import streamlit as st

from firewise import data

# ---------------------------------------------------------------- palette
TEAL = "#014a52"
TEAL_2 = "#03605c"
MINT = "#2bf09a"
GREEN = "#0f8a52"
INK = "#1f1f1f"
CREAM = "#f4f1ea"
PAPER = "#faf9f6"
LINE = "#e4dfd3"
ORANGE = "#ff8a3d"
CYAN = "#49d6ff"
PINK = "#ff5fb4"
YELLOW = "#f3e85a"
CORAL = "#ff6b4a"

LEVEL_COLOR = {"DIRECT": "#14c27a", "SUPPORTING": "#f2b632", "EXTRAPOLATED": CORAL}
PILLAR_COLOR = {"prevention": ORANGE, "detection": "#3cb4ff", "suppression": "#14c27a", "combustion physics": PINK}
PILLAR_ICON = {"prevention": "shield", "detection": "bell", "suppression": "drop", "combustion physics": "spark"}
PILLAR_PATTERN = {"prevention": "fw-pat-stripes", "detection": "fw-pat-wave", "suppression": "fw-pat-band",
                  "combustion physics": "fw-pat-planks"}

# ---------------------------------------------------------------- icons (24px stroke paths)
ICONS = {
    "arrow": "M5 12h14M13 6l6 6-6 6",
    "chevron": "M9 6l6 6-6 6",
    "check": "M5 12.5l4.5 4.5L19 7.5",
    "plus": "M12 5v14M5 12h14",
    "shield": "M12 3l7 3v6c0 4.5-3 7.5-7 9-4-1.5-7-4.5-7-9V6z",
    "bell": "M6 16v-5a6 6 0 0 1 12 0v5l1.5 2h-15zM10 20.5a2 2 0 0 0 4 0",
    "drop": "M12 3s6 6.5 6 11a6 6 0 0 1-12 0c0-4.5 6-11 6-11z",
    "spark": "M12 2v5M12 17v5M2 12h5M17 12h5M5 5l3.5 3.5M15.5 15.5L19 19M5 19l3.5-3.5M15.5 8.5L19 5",
    "flame": "M12 3c.8 3 4.5 4.5 4.5 9a4.5 4.5 0 0 1-9 0c0-2.2 1.1-3.4 1.9-4.5.4 1.5 1.1 2.2 1.9 2.2-.8-2.2 0-4.5.7-6.7z",
    "rocket": "M9 15l-3-3c1.5-4 5-8 12-9-1 7-5 10.5-9 12zM5 15c-1 1-1.5 3.5-1.5 5.5 2 0 4.5-.5 5.5-1.5M14.5 9.5h.01",
    "map": "M3 6l6-3 6 3 6-3v15l-6 3-6-3-6 3zM9 3v15M15 6v15",
    "scale": "M12 3v18M6 21h12M5 7h14M5 7l-3 7a3 3 0 0 0 6 0zM19 7l-3 7a3 3 0 0 0 6 0z",
    "chat": "M4 5h16v11H9l-5 4z",
    "search": "M10.5 10.5m-6.5 0a6.5 6.5 0 1 0 13 0a6.5 6.5 0 1 0-13 0M20 20l-4.8-4.8",
    "book": "M4 4h6a3 3 0 0 1 3 3v13a2 2 0 0 0-2-2H4zM20 4h-6a3 3 0 0 0-3 3v13a2 2 0 0 1 2-2h7z",
    "box": "M12 3l8 4.5v9L12 21l-8-4.5v-9zM4 7.5l8 4.5 8-4.5M12 12v9",
    "moon": "M20 14.5A8 8 0 1 1 9.5 4a6.5 6.5 0 0 0 10.5 10.5z",
    "planet": "M12 12m-5 0a5 5 0 1 0 10 0a5 5 0 1 0-10 0M3 16c1.5 2 17-4.5 18-8.5",
    "station": "M2 12h5M17 12h5M9 9h6v6H9zM12 3v6M12 15v6",
    "rover": "M3 7h11v8H3zM14 10h4l3 3v2h-7M6.5 18.5m-1.5 0a1.5 1.5 0 1 0 3 0a1.5 1.5 0 1 0-3 0M17.5 18.5m-1.5 0a1.5 1.5 0 1 0 3 0a1.5 1.5 0 1 0-3 0",
    "database": "M4 6c0-1.7 3.6-3 8-3s8 1.3 8 3-3.6 3-8 3-8-1.3-8-3zM4 6v12c0 1.7 3.6 3 8 3s8-1.3 8-3V6M4 12c0 1.7 3.6 3 8 3s8-1.3 8-3",
    "graph": "M6 6m-2 0a2 2 0 1 0 4 0a2 2 0 1 0-4 0M18 6m-2 0a2 2 0 1 0 4 0a2 2 0 1 0-4 0M12 18m-2 0a2 2 0 1 0 4 0a2 2 0 1 0-4 0M7 8l4 8M17 8l-4 8",
    "warning": "M12 3l10 18H2zM12 10v5M12 18h.01",
    "list": "M9 6h11M9 12h11M9 18h11M4.5 6h.01M4.5 12h.01M4.5 18h.01",
    "info": "M12 12m-9 0a9 9 0 1 0 18 0a9 9 0 1 0-18 0M12 11v6M12 7.5h.01",
}
MISSION_ICON = {"iss": "station", "lunar_habitat": "moon", "exploration_atm": "rover", "mars_habitat": "planet",
                "custom": "spark"}


def _b64(svg):
    return "data:image/svg+xml;base64," + base64.b64encode(svg.encode()).decode()


def icon_svg(name, color=INK, width=1.6):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{color}" '
            f'stroke-width="{width}" stroke-linecap="round" stroke-linejoin="round"><path d="{ICONS[name]}"/></svg>')


def icon(name, size=24, color=INK, width=1.6):
    return f'<img src="{_b64(icon_svg(name, color, width))}" width="{size}" height="{size}" alt="" style="display:block">'


# ---------------------------------------------------------------- patterns
def _band_svg(bg=MINT, line=GREEN):
    xs, x, gap = [], 3.0, 5.0
    while x < 1600:
        xs.append(x)
        x += gap
        gap = gap + 2.2 if gap < 70 else 6.0
    lines = "".join(f'<rect x="{v:.1f}" y="0" width="1.6" height="40" fill="{line}"/>' for v in xs)
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="40"><rect width="1600" height="40" fill="{bg}"/>{lines}</svg>'


def _planks_svg(bg=PINK, line="#c8006f", angle=-32):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="600" height="600"><defs>'
            f'<pattern id="p" width="130" height="96" patternUnits="userSpaceOnUse" patternTransform="rotate({angle})">'
            f'<rect width="130" height="96" fill="{bg}"/><path d="M0 0H130M0 48H130M40 0V48M105 48V96" '
            f'stroke="{line}" stroke-width="2.2"/></pattern></defs><rect width="600" height="600" fill="url(#p)"/></svg>')


def _wave_svg(bg=CYAN, line="#3c74ff"):
    out = []
    for i in range(48):
        x = 10 + i * 25
        h = 160 + 130 * math.sin(i / 4.2) + 40 * math.sin(i / 1.7)
        out.append(f'<rect x="{x}" y="{450 - h:.0f}" width="2" height="{h:.0f}" fill="{line}"/>')
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="450"><rect width="1200" height="450" fill="{bg}"/>{"".join(out)}</svg>'


def _stripes_svg(bg=ORANGE, line=YELLOW):
    out, x = [], 6
    widths = [3, 6, 2, 10, 4, 3, 14, 2, 7, 3, 18, 4, 2, 9, 3, 22, 5, 3]
    for i, w in enumerate(widths * 3):
        x += w + 8
        out.append(f'<rect x="{x}" y="0" width="{2 if i % 2 else 3}" height="600" fill="{line}"/>')
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="600" height="600"><rect width="600" height="600" fill="{bg}"/>{"".join(out)}</svg>'


def _rings_svg():
    cx, cy = 800, 520
    rings = "".join(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="#1d8a78" stroke-opacity="{o}" stroke-width="1.4"/>'
                    for r, o in ((250, .55), (340, .45), (440, .6), (560, .35), (700, .25)))
    nodes = []
    names = ["box", "rover", "flame", "drop", "shield", "bell", "spark", "graph", "moon", "planet", "station", "map"]
    k = 0
    for r, n, off in ((440, 12, 0.13), (560, 14, 0.0), (340, 8, 0.4)):
        for j in range(n):
            a = off + 2 * math.pi * j / n
            x, y = cx + r * math.cos(a), cy + r * math.sin(a)
            nm = names[k % len(names)]
            k += 1
            size = 46 if r != 340 else 38
            nodes.append(
                f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{size}" fill="#03605c" stroke="{MINT}" stroke-opacity=".55" stroke-width="1.5"/>'
                f'<g transform="translate({x - size * .5:.0f},{y - size * .5:.0f}) scale({size / 24:.2f})" fill="none" '
                f'stroke="#bff7dd" stroke-opacity=".85" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round">'
                f'<path d="{ICONS[nm]}"/></g>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="1040"><rect width="1600" height="1040" fill="{TEAL}"/>'
            f'{rings}{"".join(nodes)}</svg>')


# ---------------------------------------------------------------- CSS
FONTS = ("https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@62..125,400..900"
         "&family=IBM+Plex+Mono:wght@400;500;600&family=Instrument+Sans:wght@400;500;600;700&display=swap")


@functools.lru_cache(maxsize=1)
def _css():
    return f"""
<style>
@import url('{FONTS}');
:root {{ --teal:{TEAL}; --mint:{MINT}; --green:{GREEN}; --ink:{INK}; --cream:{CREAM}; --line:{LINE}; }}
html, body, .stApp, .stMarkdown, p, li, label, input, textarea, button, [data-testid="stMarkdownContainer"] {{
  font-family: 'Instrument Sans', system-ui, sans-serif; }}
.stApp {{ background: {CREAM}; }}
[data-testid="stHeader"] {{ background: transparent; }}
.block-container {{ max-width: 1320px; padding-top: 1.2rem; padding-bottom: 0; }}
h1, h2, h3 {{ font-family: 'Archivo', sans-serif !important; font-stretch: 68%; font-weight: 900 !important;
  text-transform: uppercase; letter-spacing: -.005em; line-height: .92; color: {INK}; }}

/* ---------- sidebar = menu panel */
[data-testid="stSidebar"] {{ background: #fff; border-right: 1px solid {LINE}; }}
[data-testid="stSidebarHeader"] {{ padding: 0 !important; border-bottom: 1px solid {LINE}; }}
[data-testid="stSidebarNav"] {{ padding-top: 0; }}
[data-testid="stNavSectionHeader"] {{ font-family: 'Archivo', sans-serif; font-stretch: 125%; font-weight: 800;
  letter-spacing: .32em; font-size: .68rem; color: {GREEN}; padding: 1.1rem 1.2rem .4rem; text-transform: uppercase; }}
[data-testid="stSidebarNavLink"] {{ border-radius: 0 !important; border-bottom: 1px solid {LINE}; padding: .95rem 1.2rem !important;
  margin: 0 !important; }}
[data-testid="stSidebarNavLink"] span[label] p {{ font-family: 'IBM Plex Mono', monospace !important;
  text-transform: uppercase; letter-spacing: .1em; font-size: .8rem; color: {INK}; }}
[data-testid="stSidebarNavLink"] [data-testid="stIconMaterial"] {{ color: {INK}; font-size: 1.15rem; }}
[data-testid="stSidebarNavLink"]:hover {{ background: {CREAM}; }}
[data-testid="stSidebarNavLink"][aria-current="page"] {{ background: {CREAM}; box-shadow: inset 4px 0 0 {MINT}; }}
[data-testid="stLogo"] {{ height: 3.4rem !important; max-width: 15rem; }}

/* ---------- buttons & links: pills */
.stButton > button, [data-testid="stPageLink"] a, .stDownloadButton > button {{
  border-radius: 999px !important; font-family: 'IBM Plex Mono', monospace; text-transform: uppercase;
  letter-spacing: .12em; font-weight: 600; font-size: .78rem; padding: .55rem 1.2rem; transition: all .15s; }}
.stButton > button[kind="primary"], .stDownloadButton > button {{ background: {MINT}; color: {INK}; border: 0; }}
.stButton > button[kind="primary"]:hover, .stDownloadButton > button:hover {{ background: {INK}; color: {MINT}; }}
.stButton > button[kind="secondary"] {{ background: transparent; border: 2px solid #14c27a; color: {INK}; }}
.stButton > button[kind="secondary"]:hover {{ background: {MINT}; border-color: {MINT}; color: {INK}; }}
.stButton > button p {{ font-family: 'IBM Plex Mono', monospace; }}
[data-testid="stPageLink"] a {{ background: {MINT}; justify-content: center; }}
[data-testid="stPageLink"] a span {{ font-family: 'IBM Plex Mono', monospace; color: {INK} !important; font-weight: 600; }}
[data-testid="stPageLink"] a:hover {{ background: {INK}; }}
[data-testid="stPageLink"] a:hover span {{ color: {MINT} !important; }}

/* ---------- inputs */
[data-baseweb="select"] > div, [data-baseweb="input"], .stTextArea textarea, [data-baseweb="base-input"] {{
  border-radius: 0 !important; background: #fff !important; border-color: {LINE} !important; }}
[data-testid="stWidgetLabel"] p {{ font-family: 'IBM Plex Mono', monospace; text-transform: uppercase; letter-spacing: .1em;
  font-size: .72rem !important; color: #55524a; }}
[data-testid="stRadio"] label p {{ font-family: 'IBM Plex Mono', monospace; text-transform: uppercase; letter-spacing: .06em; font-size: .8rem; }}

/* ---------- tabs = tab strip */
[role="tablist"] {{ gap: 6px; background: transparent; border: 0 !important; box-shadow: none !important; flex-wrap: wrap; }}
[data-testid="stTab"] {{ background: {PAPER}; border: 1px solid {LINE}; border-radius: 0; padding: 1.15rem 1.6rem !important;
  flex: 1; justify-content: center; min-width: 140px; }}
[data-testid="stTab"] p {{ font-family: 'IBM Plex Mono', monospace; text-transform: uppercase; letter-spacing: .12em; font-size: .82rem !important; }}
[data-testid="stTab"][data-selected="true"] {{ background: linear-gradient(90deg, {MINT} 0 45%, #fff 45%); border-color: {MINT}; }}
[data-testid="stTab"]:hover {{ background: #fff; }}
.react-aria-SelectionIndicator, [data-baseweb="tab-highlight"], [data-baseweb="tab-border"] {{ display: none !important; }}

/* ---------- metrics, containers, alerts, tables */
[data-testid="stMetricValue"] {{ font-family: 'Archivo', sans-serif; font-stretch: 68%; font-weight: 900; font-size: 2.7rem; }}
[data-testid="stMetricLabel"] p {{ font-family: 'IBM Plex Mono', monospace; text-transform: uppercase; letter-spacing: .1em; font-size: .72rem; }}
[data-testid="stVerticalBlockBorderWrapper"] {{ border-radius: 0 !important; }}
div[data-testid="stExpander"] details {{ border-radius: 0; border-color: {LINE}; background: #fff; }}
div[data-testid="stExpander"] summary p {{ font-family: 'IBM Plex Mono', monospace; text-transform: uppercase; letter-spacing: .1em; font-size: .8rem; }}
[data-testid="stAlert"] {{ border-radius: 0; }}
[data-testid="stDataFrame"] {{ border: 1px solid {LINE}; background: #fff; }}
.stPlotlyChart {{ background: #fff; border: 1px solid {LINE}; padding: .4rem; }}

/* ---------- FireWise components */
.fw-eyebrow {{ font-family: 'Archivo', sans-serif; font-stretch: 125%; font-weight: 800; letter-spacing: .34em;
  font-size: .8rem; color: {GREEN}; text-transform: uppercase; display: flex; align-items: center; gap: 1.1rem; margin: 0 0 1rem; }}
.fw-eyebrow::before {{ content: ""; width: 38px; height: 2px; background: {GREEN}; display: inline-block; }}
.fw-eyebrow.mint {{ color: {MINT}; }} .fw-eyebrow.mint::before {{ background: {MINT}; }}
.fw-eyebrow.plain::before {{ display: none; }}
.fw-display {{ font-family: 'Archivo', sans-serif; font-stretch: 66%; font-weight: 900; text-transform: uppercase;
  line-height: .9; letter-spacing: -.005em; font-size: clamp(2.6rem, 6vw, 5.4rem); color: {INK}; margin: 0; }}
.fw-display.sm {{ font-size: clamp(2rem, 4vw, 3.4rem); }}
.fw-display.xs {{ font-size: 1.9rem; line-height: 1; }}
.fw-head {{ display: flex; justify-content: space-between; align-items: flex-end; gap: 2rem; margin: .4rem 0 2.2rem; flex-wrap: wrap; }}
.fw-lead {{ font-size: 1.12rem; line-height: 1.6; color: #3d3b36; max-width: 36rem; margin: 0; }}
.fw-mono {{ font-family: 'IBM Plex Mono', monospace; text-transform: uppercase; letter-spacing: .1em; font-size: .78rem; }}
.fw-muted {{ color: #77736a; font-size: .86rem; }}
.fw-pill {{ display: inline-flex; align-items: center; gap: .8rem; padding: .55rem .6rem .55rem 1.4rem; border-radius: 999px;
  background: {MINT}; color: {INK} !important; text-decoration: none !important; font-family: 'IBM Plex Mono', monospace;
  font-weight: 600; letter-spacing: .14em; text-transform: uppercase; font-size: .82rem; }}
.fw-pill .dot {{ width: 34px; height: 34px; border-radius: 50%; background: {INK}; display: grid; place-items: center; }}
.fw-pill.outline {{ background: transparent; border: 2px solid #14c27a; padding: .7rem 1.5rem; }}
.fw-badge {{ display: inline-block; padding: 3px 12px; border-radius: 999px; font-family: 'IBM Plex Mono', monospace;
  font-weight: 600; font-size: .7rem; letter-spacing: .1em; color: {INK}; }}
.fw-tile {{ width: 64px; height: 64px; display: grid; place-items: center; background: {CREAM}; flex: none; }}
.fw-tile.mint {{ background: {MINT}; }} .fw-tile.sm {{ width: 46px; height: 46px; }}
.fw-card {{ background: #fff; border: 1px solid {LINE}; margin-bottom: 1.2rem; }}
.fw-card .band {{ height: 30px; }}
.fw-card .in {{ padding: 1.6rem 1.8rem; }}
.fw-card .row {{ display: flex; align-items: center; gap: 1.4rem; }}
.fw-card .label {{ font-family: 'Archivo', sans-serif; font-stretch: 125%; font-weight: 800; letter-spacing: .3em;
  color: {GREEN}; text-transform: uppercase; font-size: .92rem; }}
.fw-card h4 {{ font-family: 'Archivo', sans-serif; font-stretch: 80%; font-weight: 900; font-size: 1.55rem; line-height: 1.05; margin: .2rem 0 0; }}
.fw-card p {{ color: #45423b; line-height: 1.6; }}
.fw-meter {{ margin: .45rem 0; }}
.fw-meter .t {{ display: flex; justify-content: space-between; font-family: 'IBM Plex Mono', monospace; font-size: .7rem;
  letter-spacing: .1em; text-transform: uppercase; color: #55524a; }}
.fw-meter .track {{ height: 8px; background: {CREAM}; margin-top: 4px; }}
.fw-meter .fill {{ height: 8px; background: #14c27a; }}
.fw-stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(190px, 1fr)); border: 1px solid {LINE}; background: #fff; margin: 1.6rem 0; }}
.fw-stat {{ padding: 1.4rem 1.6rem; border-right: 1px solid {LINE}; }}
.fw-stat:last-child {{ border-right: 0; }}
.fw-stat .v {{ font-family: 'Archivo', sans-serif; font-stretch: 66%; font-weight: 900; font-size: 3.2rem; line-height: 1; }}
.fw-stat .l {{ font-family: 'IBM Plex Mono', monospace; text-transform: uppercase; letter-spacing: .1em; font-size: .72rem; color: #55524a; margin-top: .4rem; }}
.fw-fact {{ display: flex; gap: 1rem; align-items: flex-start; background: #fff; border: 1px solid {LINE}; padding: 1rem 1.2rem; margin-bottom: .6rem; }}
.fw-fact .src {{ font-family: 'IBM Plex Mono', monospace; font-size: .72rem; letter-spacing: .06em; color: #77736a; margin-top: .35rem; }}
.fw-fact .src a {{ color: {GREEN}; }}
.fw-checks {{ list-style: none; padding: 0; margin: 1rem 0; }}
.fw-checks li {{ display: flex; gap: .9rem; align-items: center; margin: .55rem 0; }}
.fw-checks .c {{ width: 30px; height: 30px; border-radius: 50%; background: #14c27a; display: grid; place-items: center; flex: none; }}
.fw-acc {{ background: #fff; border: 1px solid {LINE}; }}
.fw-acc .r {{ display: grid; grid-template-columns: 28px 1.3fr 1fr 1fr 150px; gap: 1rem; align-items: center; padding: 1rem 1.3rem; border-bottom: 1px solid {LINE}; }}
.fw-acc .r:last-child {{ border-bottom: 0; }}
.fw-acc .r.h {{ background: {PAPER}; font-family: 'IBM Plex Mono', monospace; font-size: .7rem; letter-spacing: .1em; text-transform: uppercase; color: #77736a; }}
.fw-acc b {{ font-weight: 700; }}
.fw-acc .note {{ grid-column: 2 / -1; color: #6d695f; font-size: .86rem; margin-top: -.5rem; }}
.fw-dark {{ background: {TEAL}; color: #eaf6f2; padding: 3rem 2.6rem; margin: 1.8rem 0; }}
.fw-dark .fw-display {{ color: #fff; }}
.fw-dark .fw-lead {{ color: #d4ece6; }}
.fw-menu {{ background: {TEAL_2}; }}
.fw-menu .i {{ display: flex; justify-content: space-between; align-items: center; padding: 1.25rem 1.6rem;
  font-family: 'IBM Plex Mono', monospace; letter-spacing: .12em; text-transform: uppercase; color: #fff; font-size: .9rem; }}
.fw-menu .i.on {{ background: #fff; color: {INK}; margin: 0 .5rem; }}
.fw-hero {{ position: relative; background: {TEAL} center/cover no-repeat; text-align: center; padding: 5.5rem 2rem 5rem; margin: -1.2rem 0 0; overflow: hidden; }}
.fw-hero .word {{ font-family: 'Instrument Sans', sans-serif; color: {MINT}; font-size: 3.2rem; font-weight: 500; letter-spacing: -.02em; }}
.fw-hero .fw-eyebrow {{ justify-content: center; }}
.fw-hero .fw-display {{ color: #fff; font-size: clamp(2.8rem, 7vw, 6rem); max-width: 60rem; margin: 0 auto; }}
.fw-hero .fw-lead {{ color: #e2f3ee; margin: 1.6rem auto 2rem; text-align: center; }}
.fw-vtabs {{ display: flex; border-left: 1px solid {LINE}; }}
.fw-vtabs div {{ writing-mode: vertical-rl; font-family: 'IBM Plex Mono', monospace; letter-spacing: .12em; text-transform: uppercase;
  font-size: .8rem; padding: 1.4rem .7rem; border-right: 1px solid {LINE}; background: {PAPER}; color: #8c887e; }}
.fw-vtabs div.on {{ background: #fff; color: {INK}; }}
.fw-foot {{ background: #fff; border: 1px solid {LINE}; margin-top: 3.5rem; }}
.fw-foot .top {{ display: grid; grid-template-columns: 1.2fr 1fr 1fr 1fr; gap: 2rem; padding: 2.6rem 2.4rem; }}
.fw-foot h5 {{ font-family: 'Archivo', sans-serif; font-stretch: 70%; font-weight: 900; text-transform: uppercase; font-size: 1.5rem; margin: 0 0 1rem; }}
.fw-foot a, .fw-foot span.l {{ display: block; font-family: 'IBM Plex Mono', monospace; letter-spacing: .1em; text-transform: uppercase;
  font-size: .78rem; color: {INK} !important; text-decoration: none; margin: .55rem 0; }}
.fw-foot .bar {{ display: flex; justify-content: space-between; align-items: center; background: {CREAM}; border-top: 1px solid {LINE}; }}
.fw-foot .bar .mk {{ background: {INK}; padding: 1rem 1.4rem; }}
.fw-foot .bar .c {{ font-size: .85rem; color: #55524a; flex: 1; padding: 0 1.4rem; }}
.fw-foot .bar .cta {{ background: {INK}; color: {MINT} !important; padding: 1.3rem 1.8rem; font-family: 'IBM Plex Mono', monospace;
  letter-spacing: .14em; text-transform: uppercase; font-size: .8rem; text-decoration: none; }}
.fw-pat-band {{ background: url('{_b64(_band_svg())}') left center / auto 100% repeat-x; }}
.fw-pat-planks {{ background: url('{_b64(_planks_svg())}') center / 420px repeat; }}
.fw-pat-planks-mint {{ background: url('{_b64(_planks_svg(MINT, "#0faa66"))}') center / 420px repeat; }}
.fw-pat-wave {{ background: url('{_b64(_wave_svg())}') center bottom / cover no-repeat; }}
.fw-pat-stripes {{ background: url('{_b64(_stripes_svg())}') center / 300px repeat; }}
.fw-hero-bg {{ background-image: url('{_b64(_rings_svg())}'); }}
@media (max-width: 760px) {{
  .fw-acc .r {{ grid-template-columns: 22px 1fr; }} .fw-acc .r > :nth-child(n+3) {{ grid-column: 2; }}
  .fw-foot .top {{ grid-template-columns: 1fr 1fr; }} .fw-dark {{ padding: 2rem 1.2rem; }}
}}
</style>
"""


def html(s):
    """Render raw HTML (dedented and flattened so markdown never turns it into a code block)."""
    s = textwrap.dedent(s)
    st.markdown(" ".join(line.strip() for line in s.splitlines() if line.strip()), unsafe_allow_html=True)


def setup():
    st.markdown(_css(), unsafe_allow_html=True)
    _plotly_theme()


# ---------------------------------------------------------------- building blocks
def header(eyebrow, title, lead=None, right=None, size=""):
    r = f'<p class="fw-lead">{lead}</p>' if lead else (right or "")
    html(f"""<div class="fw-head"><div><div class="fw-eyebrow">{eyebrow}</div>
    <h1 class="fw-display {size}">{title}</h1></div>{r}</div>""")


def eyebrow(text, mint=False):
    html(f'<div class="fw-eyebrow {"mint" if mint else ""}">{text}</div>')


def badge(level):
    return f'<span class="fw-badge" style="background:{LEVEL_COLOR.get(level, "#ccc")}">{level}</span>'


def pill(text, href, outline=False):
    dot = "" if outline else f'<span class="dot">{icon("arrow", 18, "#fff", 2)}</span>'
    return f'<a class="fw-pill {"outline" if outline else ""}" href="{href}" target="_self">{text}{dot}</a>'


def meter(label, value):
    v = max(0.0, min(1.0, float(value)))
    return (f'<div class="fw-meter"><div class="t"><span>{label}</span><span>{v:.2f}</span></div>'
            f'<div class="track"><div class="fill" style="width:{v * 100:.0f}%"></div></div></div>')


def stats(items):
    cells = "".join(f'<div class="fw-stat"><div class="v">{v}</div><div class="l">{lab}</div></div>' for v, lab in items)
    html(f'<div class="fw-stats">{cells}</div>')


def checks(items):
    lis = "".join(f'<li><span class="c">{icon("check", 16, "#fff", 2.4)}</span><span>{t}</span></li>' for t in items)
    return f'<ul class="fw-checks">{lis}</ul>'


def tile(name, mint=False, small=False, color=INK):
    return f'<div class="fw-tile {"mint" if mint else ""} {"sm" if small else ""}">{icon(name, 22 if small else 28, color)}</div>'


def card(label, icon_name, body="", band="fw-pat-band", mint_tile=True, right=""):
    html(f"""<div class="fw-card"><div class="band {band}"></div><div class="in">
    <div class="row">{tile(icon_name, mint_tile)}<div class="label" style="flex:1">{label}</div>{right}</div>
    <div>{body}</div></div></div>""")


def fact_box(f):
    gap = f.get("kind") == "gap"
    src = " · ".join(f'<a href="{psi_link(p)}" target="_blank">{p}</a>' for p in f["psi_ids"])
    tag = "EVIDENCE GAP" if gap else "COMPUTED FROM NASA RUNS"
    t = tile("warning" if gap else "check", mint=not gap, small=True)
    if gap:
        t = t.replace('class="fw-tile', f'style="background:{CORAL}" class="fw-tile')
    html(f'<div class="fw-fact">{t}<div><div>{f["text"]}</div><div class="src">{tag}{(" · " + src) if src else ""}</div></div></div>')


STATUS_STYLE = {"match": ("#14c27a", "MATCH"), "near": ("#f2b632", "CLOSE"), "mismatch": (CORAL, "DIFFERS"),
                "unknown": ("#d9d4c7", "NOT REPORTED")}


def certificate(checks_):
    rows = ['<div class="r h"><span></span><span>Check</span><span>Mission</span><span>NASA run</span><span>Status</span></div>']
    for c in checks_:
        col, lab = STATUS_STYLE[c.status]
        rows.append(f'<div class="r"><span>{icon("chevron", 16)}</span><b>{c.name}</b><span class="fw-mono">{c.target}</span>'
                    f'<span class="fw-mono">{c.evidence}</span><span class="fw-badge" style="background:{col}">{lab}</span>'
                    + (f'<span></span><span class="note">{c.note}</span>' if c.note else "") + "</div>")
    html(f'<div class="fw-acc">{"".join(rows)}</div>')


def footer():
    links = [("Mission Explorer", "mission"), ("Atmosphere Map", "atmosphere"), ("Prevent · Detect · Suppress", "pillars"),
             ("Compare Runs", "compare"), ("Ask FireWise", "ask")]
    trust = [("Data Reliability", "data_audit"), ("Method & Sources", "about")]
    ext = [("NASA PSI ↗", "https://psi.nasa.gov"), ("NASA NTRS ↗", "https://ntrs.nasa.gov"),
           ("Space Apps 2026 ↗", "https://www.spaceappschallenge.org")]
    a = lambda xs, ext_=False: "".join(  # noqa: E731
        f'<a href="{u}" target="{"_blank" if ext_ else "_self"}">{t}</a>' for t, u in xs)
    html(f"""<div class="fw-foot"><div class="top">
    <div><div style="width:64px">{_logo_mark()}</div><p class="fw-muted" style="margin-top:1rem;max-width:18rem">
    Mission-aware fire-safety evidence from NASA microgravity combustion data.</p></div>
    <div><h5>Explore</h5>{a(links)}</div><div><h5>Trust</h5>{a(trust)}</div><div><h5>Sources</h5>{a(ext, True)}</div></div>
    <div class="bar"><div class="mk">{icon("flame", 22, MINT, 2)}</div>
    <div class="c">© 2026 Team Errorists · NASA Space Apps Challenge · Data: NASA PSI (CC0) · Not endorsed by NASA</div>
    <a class="cta" href="mission" target="_self">Open explorer →</a></div></div>""")


def _logo_mark():
    return f'<div style="background:{INK};width:64px;height:64px;display:grid;place-items:center">{icon("flame", 30, MINT, 2)}</div>'


def psi_link(pid):
    return f"https://psi.nasa.gov/physci/repo/data/{pid}"


# ---------------------------------------------------------------- charts
def _plotly_theme():
    if "firewise" in pio.templates:
        return
    t = go.layout.Template()
    t.layout = go.Layout(
        font=dict(family="Instrument Sans, sans-serif", color=INK, size=13),
        title=dict(font=dict(family="Archivo, sans-serif", size=17, color=INK), x=0.01),
        paper_bgcolor="#fff", plot_bgcolor=PAPER,
        colorway=[TEAL_2, "#14c27a", ORANGE, "#3cb4ff", PINK, "#c9b400", INK],
        xaxis=dict(gridcolor=LINE, zerolinecolor=LINE, linecolor=LINE, title=dict(font=dict(family="IBM Plex Mono, monospace", size=11))),
        yaxis=dict(gridcolor=LINE, zerolinecolor=LINE, linecolor=LINE, title=dict(font=dict(family="IBM Plex Mono, monospace", size=11))),
        legend=dict(font=dict(family="IBM Plex Mono, monospace", size=11), bgcolor="rgba(0,0,0,0)"),
        margin=dict(t=50, l=10, r=10, b=10), hoverlabel=dict(font=dict(family="IBM Plex Mono, monospace")),
    )
    pio.templates["firewise"] = t
    pio.templates.default = "plotly_white+firewise"


# ---------------------------------------------------------------- data + widgets
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
        return {"key": "custom", "name": "Custom environment", "short": "Custom", "gravity_g": g, "pressure_kpa": p,
                "o2_fraction": x, "status": "user-defined", "note": "Values set by you."}
    return {"key": k, **ms[k]}


def fmt_pct(v):
    return "–" if pd.isna(v) else f"{v:.1%}"
