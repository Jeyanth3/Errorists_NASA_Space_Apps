import streamlit as st

from firewise import ui

st.markdown(ui.CSS, unsafe_allow_html=True)
runs = ui.runs()
inv = ui.investigations()
pubs = ui.publications()

st.markdown("""
<div class="fw-hero">
<h1>🔥 FireWise</h1>
<p><b>Which NASA fire experiments actually apply to <i>your</i> mission - and which only look like they do?</b><br>
FireWise turns decades of microgravity combustion data from NASA's PSI repository into ranked, traceable
evidence for spacecraft, lunar and Martian fire safety.</p>
</div>
""", unsafe_allow_html=True)
st.write("")

c = st.columns(4)
c[0].metric("NASA experimental runs", f"{len(runs):,}")
c[1].metric("Combustion investigations indexed", len(inv))
c[2].metric("Linked publications", f"{len(pubs):,}")
c[3].metric("Runs with flagged assumptions", f"{(runs['data_flags'] != '').sum():,}")

st.subheader("The problem")
st.markdown(
    "A habitat on the Moon may run at **~30% oxygen and 70 kPa** in **one-sixth gravity**. Almost every NASA "
    "fire experiment was run in **21% oxygen, 101 kPa, and microgravity**. A normal search engine will happily "
    "return those results for a lunar question. FireWise checks the physics first and tells you, run by run, "
    "**what matches, what differs, and what has never been tested**.")

st.subheader("Three safety questions, one evidence engine")
cols = st.columns(3)
blurbs = {
    "prevention": ("Prevention", "Will this material ignite and spread a flame?", "BASS · BASS-II · Saffire I-III"),
    "detection": ("Detection", "What does early smoke look like to a detector?", "SAME · SAME-R"),
    "suppression": ("Suppression", "What makes a flame go out?", "FLEX (+ CFI-G physics)"),
}
for col, (k, (name, q, src)) in zip(cols, blurbs.items()):
    n = (runs["pillar"] == k).sum()
    col.markdown(f'<div class="fw-card"><h4>{ui.PILLAR_ICON[k]} {name}</h4><p>{q}<br><br>'
                 f'<b>{n} runs</b> · {src}</p></div>', unsafe_allow_html=True)

st.subheader("How to use it (2 minutes)")
st.markdown("""
1. **🚀 Mission Explorer** - pick ISS, Moon base, rover or Mars base and a safety goal. Get NASA investigations ranked
   into **DIRECT / SUPPORTING / EXTRAPOLATED** evidence, with a condition certificate for each run.
2. **🗺️ Atmosphere Map** - see where your habitat sits against every condition NASA has actually tested.
3. **🧯 Prevent · Detect · Suppress** - the key measured findings for each pillar, with charts.
4. **💬 Ask FireWise** - ask in plain English; answers are built only from NASA runs and cite their PSI source.
5. **🔎 Data Reliability** - every assumption and metadata conflict we found, in the open.
""")

st.subheader("Evidence levels")
st.markdown(
    f"{ui.badge('DIRECT')} same safety question, same gravity, matching atmosphere &nbsp;&nbsp; "
    f"{ui.badge('SUPPORTING')} right question, at least one condition differs &nbsp;&nbsp; "
    f"{ui.badge('EXTRAPOLATED')} different gravity <i>and</i> atmosphere - context only, never a measurement",
    unsafe_allow_html=True)

st.caption("Data: NASA Physical Sciences Informatics (PSI), Combustion Science, CC0. FireWise is an independent "
           "Space Apps 2026 project by team Errorists and is not endorsed by NASA.")
