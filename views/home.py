import streamlit as st

from firewise import data, ui

runs = ui.runs()
inv = ui.investigations()
pubs = ui.publications()

# ---- hero
ui.html(f"""
<div class="fw-hero fw-hero-bg">
  <div style="display:flex;justify-content:center;margin-bottom:.6rem">
  <div style="background:rgba(255,255,255,.08);border-radius:50%;padding:18px;border:1px solid rgba(43,240,154,.35)">{ui.logo(130)}</div></div>
  <div class="word">FireWise</div>
  <div class="fw-eyebrow mint plain" style="margin-top:1.4rem">The mission fire-evidence engine</div>
  <h1 class="fw-display">Know what the evidence really says</h1>
  <p class="fw-lead">FireWise turns decades of NASA microgravity combustion experiments into ranked, traceable
  evidence for spacecraft, Moon and Mars fire safety - and shows exactly where the evidence stops.</p>
  {ui.pill("Explore a mission", "mission")}
</div>""")

ui.stats([
    (f"{len(runs):,}", "NASA experimental runs"),
    (len(inv), "Combustion investigations"),
    (f"{len(pubs):,}", "Linked publications"),
    ("0", "Runs that are direct evidence for the Moon"),
])

# ---- problem
ui.header("The problem", "Same keywords.<br>Different physics.",
          lead="A Moon base may breathe ~30% oxygen at 70 kPa in one-sixth gravity. Almost every NASA fire "
               "experiment ran in 21% oxygen, 101 kPa and microgravity. A search engine still hands you those "
               "results. FireWise checks the conditions first - run by run.")

# ---- pillars block (dark, menu + card)
pillars = {
    "prevention": ("Prevention", "Will this material ignite and spread a flame?",
                   "BASS · BASS-II · Saffire I-III", "Solid materials burned in microgravity, from 2 cm films to "
                   "spacecraft-scale fabric sheets."),
    "detection": ("Detection", "What does early smoke look like to a detector?", "SAME · SAME-R",
                  "Smoke from overheated spacecraft materials, aged and measured before flames appear."),
    "suppression": ("Suppression", "What makes a flame go out?", "FLEX · CFI-G context",
                    "Fuel droplets burned in air, CO₂ and helium mixtures at several pressures."),
}
ui.html("""<div class="fw-dark"><div class="fw-head" style="margin-bottom:1.6rem">
<h2 class="fw-display">Three safety questions</h2>
<p class="fw-lead">One evidence engine organised around NASA's fire-safety priorities: prevent, detect, suppress.</p>
</div></div>""")
for key, (name, q, src, desc) in pillars.items():
    n = int((runs["pillar"] == key).sum())
    ui.card(name, ui.PILLAR_ICON[key], band=ui.PILLAR_PATTERN[key],
            right=ui.pill("Explore", "pillars"),
            body=f"""<div style="display:grid;grid-template-columns:1fr 1fr;gap:2rem;margin-top:1.4rem">
            <h4>{q}</h4><p style="margin:0">{desc}<br><span class="fw-mono" style="color:#0f8a52">{n} runs · {src}</span></p></div>""")

# ---- how it works: tab strip
ui.header("How it works", "Question in.<br>Evidence out.", size="sm")
t1, t2, t3, t4, t5 = st.tabs(["Mission", "Rank", "Certify", "Map gaps", "Ask"])
steps = [
    (t1, "rocket", "Pick a mission", "Choose ISS, a Moon base, a pressurised rover, a Mars base - or set gravity, "
     "pressure and oxygen yourself.", ["Gravity, pressure and O₂ fraction", "Oxygen partial pressure by Dalton's law",
                                       "Planning status shown for every atmosphere"], "mission"),
    (t2, "list", "Rank three ways", "Every NASA run is scored for relevance, physical applicability and data quality - "
     "never merged into one misleading number.", ["DIRECT · SUPPORTING · EXTRAPOLATED levels",
                                                  "Rules in code, not a language model", "Investigation roll-up"], "mission"),
    (t3, "check", "See why", "A condition certificate lists each check: gravity, O₂, pressure, material, atmosphere "
     "type - match, close or differs.", ["Raw NASA record + file and row", "Assumptions flagged on the run",
                                         "Fair-comparison verdicts"], "compare"),
    (t4, "map", "Find the gaps", "The atmosphere map plots every run against mission atmospheres so untested ground "
     "is obvious.", ["Iso-pO₂ lines", "Material × oxygen coverage", "Lunar envelope check"], "atmosphere"),
    (t5, "chat", "Ask in plain English", "Questions become structured queries; answers are built only from NASA "
     "numbers with PSI sources.", ["Works offline", "Optional model only rephrases", "Caveats always shown"], "ask"),
]
for tab, ic, title, text, bullets, page in steps:
    with tab:
        a, b = st.columns([1.1, 1], gap="large")
        with a:
            ui.html(f"""<div style="background:#fff;border:1px solid #e4dfd3;padding:2.2rem 2.4rem;height:100%">
            {ui.tile(ic)}<h3 class="fw-display xs" style="margin-top:1.6rem">{title}</h3>
            <p class="fw-lead" style="font-size:1.02rem;margin-top:.8rem">{text}</p>{ui.checks(bullets)}
            <a class="fw-mono" href="{page}" target="_self" style="color:#1f1f1f;text-decoration:none">↳ Learn more</a></div>""")
        with b:
            ui.html('<div class="fw-pat-planks-mint" style="height:100%;min-height:340px"></div>')

# ---- evidence levels grid (pattern cards)
ui.header("Evidence levels", "Honest by design", size="sm",
          right=ui.pill("Read the method", "about", outline=True))
c1, c2 = st.columns([1, 1], gap="medium")
with c1:
    ui.html(f"""<div class="fw-card" style="margin:0"><div class="fw-pat-wave" style="height:260px"></div>
    <div class="in">{ui.tile("check")}<h4 style="margin-top:1.2rem">Direct</h4>
    <p>Same safety question, same gravity regime, matching atmosphere. The only level you may treat as
    measured evidence for your mission.</p>{ui.badge("DIRECT")}</div></div>""")
with c2:
    for lvl, ic, pat, text in (
        ("SUPPORTING", "info", "fw-pat-planks", "Right question, but at least one condition differs - or it is "
                                                "combustion physics context."),
        ("EXTRAPOLATED", "warning", "fw-pat-stripes", "Different gravity and atmosphere. Use it to decide what to "
                                                      "test next, never as an answer."),
    ):
        ui.html(f"""<div class="fw-card" style="display:flex;margin-bottom:1rem"><div class="in" style="flex:1">
        {ui.tile(ic)}<h4 style="margin-top:1rem">{lvl.title()}</h4><p style="margin:.4rem 0 .8rem">{text}</p>{ui.badge(lvl)}</div>
        <div class="{pat}" style="width:120px"></div></div>""")

# ---- missions strip
ui.header("Missions", "One engine.<br>Every habitat.", size="sm")
ms = data.missions()
cols = st.columns(len(ms))
for col, (k, m) in zip(cols, ms.items()):
    with col:
        ui.html(f"""<div style="background:#fff;border:1px solid #e4dfd3;padding:1.4rem;min-height:250px">
        {ui.tile(ui.MISSION_ICON[k], mint=True, small=True)}
        <div class="fw-mono" style="color:#0f8a52;margin-top:1.2rem">{m['status']}</div>
        <h4 style="font-family:Archivo;font-stretch:80%;font-weight:900;font-size:1.3rem;margin:.4rem 0">{m['name']}</h4>
        <div class="fw-mono" style="font-size:.74rem;line-height:1.9">{m['gravity_g']:g} g · {m['pressure_kpa']:.0f} kPa<br>
        {m['o2_fraction']:.0%} O₂ · pO₂ {m['o2_fraction'] * m['pressure_kpa']:.1f} kPa</div></div>""")

ui.footer()
