import streamlit as st

from firewise import data, mace, ui

ui.header("Method & sources", "How we decide.<br>What we use.",
          lead="The MACE method, the scientific limits we respect, the NASA data behind every number and how it "
               "connects back to life on Earth.")

ui.html("""<div class="fw-dark"><div class="fw-eyebrow mint">MACE</div>
<h2 class="fw-display sm">Mission-Aware, Condition-constrained Evidence</h2>
<p class="fw-lead" style="max-width:56rem;margin-top:1rem">Every NASA run is scored on three separate axes. A single
"92% relevant" score would hide exactly what an engineer needs to know, so the three are never merged for display.</p></div>""")
c = st.columns(3, gap="medium")
for col, (name, ic, q, built, band) in zip(c, [
    ("Relevance", "search", "Does it study my safety question?", "pillar match · material match · BM25 keyword score",
     "fw-pat-band"),
    ("Applicability", "scale", "Were its conditions close to my mission?",
     "gravity · O₂ partial pressure · O₂ fraction · pressure · material · atmosphere type", "fw-pat-planks-mint"),
    ("Data quality", "database", "How much was measured, not assumed?",
     "completeness of outcome fields · inferred / assumed flags", "fw-pat-band"),
]):
    with col:
        ui.card(name, ic, band=band, body=f"<h4 style='margin-top:1.2rem'>{q}</h4><p class='fw-mono' "
                                          f"style='font-size:.72rem;margin-top:.8rem'>{built}</p>")

ui.header("Levels", "The rule", size="sm")
ui.html(f"""<div class="fw-acc">
<div class="r" style="grid-template-columns:170px 1fr">{ui.badge("DIRECT")}<span>Same pillar, same gravity regime, no condition differs.</span></div>
<div class="r" style="grid-template-columns:170px 1fr">{ui.badge("SUPPORTING")}<span>Right question, but at least one condition differs - or it is physics-only context.</span></div>
<div class="r" style="grid-template-columns:170px 1fr">{ui.badge("EXTRAPOLATED")}<span>Gravity <b>and</b> atmosphere differ. Usable only as a hypothesis.</span></div>
<div class="r" style="grid-template-columns:170px 1fr"><span class="fw-mono">Tolerances</span><span>pO₂ ±{mace.PO2_MATCH} kPa (close ±{mace.PO2_NEAR}) · O₂ fraction ±{mace.XO2_MATCH:.1%} · total pressure ±{mace.P_MATCH:.0%}</span></div>
</div>""")

ui.header("Limits", "Science we respect", size="sm")
limits = ["PSI holds no partial-gravity combustion data - lunar and Martian results are never interpolated between 0 g and 1 g.",
          "Same O₂ partial pressure is not the same flammability: O₂ fraction, total pressure, flow and geometry all matter.",
          "CFI-G burner mixtures (up to 85% O₂) are combustion physics, not cabin atmospheres.",
          "Smoke (SAME) comes from heated, non-flaming samples and is never compared with flame data.",
          "Droplet extinction (FLEX) is never plotted against solid flame spread.",
          "Rocket propulsion is out of scope, as the challenge brief asks."]
ui.html(f'<div class="fw-card"><div class="in">{ui.checks(limits)}</div></div>')

ui.header("Space to Earth", "Why it matters here too", size="sm")
items = data.earth_links()
cols = st.columns(2, gap="medium")
for i, it in enumerate(items):
    with cols[i % 2]:
        ui.html(f"""<div class="fw-card"><div class="in"><div class="row">{ui.tile("spark", mint=(i == 0), small=True)}
        <h4 style="margin:0;font-size:1.25rem">{it['title']}</h4></div><p style="margin-top:1rem">{it['text']}</p>
        <a class="fw-mono" href="{it['url']}" target="_blank" style="color:#0f8a52">{it['source']} ↗</a></div></div>""")

ui.header("NASA data", "Sources", size="sm")
inv = ui.investigations()
show = inv[["psi_id", "acronym", "title", "pillar", "hardware", "doi", "license", "total_gb", "url"]]
st.dataframe(show, hide_index=True, width="stretch",
             column_config={"url": st.column_config.LinkColumn("PSI page"),
                            "total_gb": st.column_config.NumberColumn("data on PSI (GB)", format="%.1f")})
st.caption("NASA Physical Sciences Informatics (PSI), https://psi.nasa.gov - Combustion Science. Files released under "
           "CC0 1.0. Publications per investigation: data/curated/publications.csv.")

ui.html("""<div class="fw-dark" style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:1rem">
<div><div class="fw-eyebrow mint">Team</div><h2 class="fw-display sm">Errorists</h2>
<p class="fw-lead" style="margin-top:.6rem">NASA Space Apps Challenge 2026 · Batticaloa, Sri Lanka · Flame in Freefall</p></div>
<div class="fw-pat-planks-mint" style="width:220px;height:140px"></div></div>""")
ui.footer()
