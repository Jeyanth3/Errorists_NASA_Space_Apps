# Submission checklist (Space Apps 2026)

Submission closes **Sun 15 Nov, 23:59 local time**. We aim for 22:00.

## Eligibility
- [ ] All 4 members registered, same local event (Batticaloa), visible on the team's Members tab (max 6)
- [ ] Every field on the Project page filled, English
- [ ] Demo: ≤30 s video **or** ≤7 slides, public link, no login
- [ ] Final project link public (GitHub repo + deployed app), tested in a private window
- [ ] Both confirmation boxes ticked (terms + original work / references listed)
- [ ] At least one NASA data source named (we use NASA PSI)

## Project page fields (draft text)

**Project name:** FireWise

**High-level summary (draft):**
FireWise is a mission-aware evidence dashboard for spacecraft fire safety. It turns 1,065 experimental runs from
NASA's Physical Sciences Informatics combustion repository (BASS, BASS-II, Saffire I-III, SAME, SAME-R, FLEX,
ACME CFI-G) into ranked, traceable evidence for prevention, detection and suppression. A user picks a mission -
ISS, a lunar habitat, a pressurized rover or a Mars base - and FireWise's MACE engine scores every NASA run
separately for relevance, physical applicability (gravity, oxygen partial pressure, oxygen fraction, pressure,
material) and data quality, labels it DIRECT, SUPPORTING or EXTRAPOLATED, and shows a condition certificate
explaining why. It makes evidence gaps visible - for example, no PSI run matches a 30% O₂ / 70 kPa lunar
atmosphere in partial gravity - so engineers know what is known, what is assumed and what must be tested next.

**Detailed description:** use README sections "What it does", "Why it is different", "Scientific limits",
plus tools: Python, Streamlit, pandas, Plotly, rank-bm25, NetworkX, pytest, GitHub Actions.

**NASA data:** NASA PSI (https://psi.nasa.gov) - PSI-25, 26, 69, 98, 99, 100, 101, 102, 159 experimental
tables; metadata and publication lists for all 24 Combustion Science investigations.

**Space agency partner data / references:** list every library (requirements.txt), any image or paper used,
external partial-gravity papers (with DOI).

**Use of Super Intelligence (SI) - required by the rules:**
The Space Apps rules require teams to say where SI tools were used, and for code and data to
"acknowledge SI generation in descriptive text and metadata". Judges see those acknowledgements.
Write this field honestly, and make sure the repo carries a matching note before submitting.

## Branding
- [ ] No NASA logo, meatball, worm or mission patches anywhere (app, video, slides)
- [ ] "Not endorsed by NASA" line stays in the footer
- [ ] Any SI-generated image/video carries a visible watermark

## Last 30 minutes
- [ ] Open every link from a phone on mobile data
- [ ] Tag release `v1.0` on GitHub
- [ ] Submit → screenshot confirmation → post in team chat
