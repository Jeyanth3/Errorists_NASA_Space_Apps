# FireWise - hackathon plan

**Deadline:** Sunday 15 Nov 2026, 23:59 Sri Lanka time (Batticaloa local event).
**Our own deadline:** submitted by **22:00 Sunday** - two hours of buffer.
Every task below is a GitHub issue under the matching milestone. Owners are a starting point - swap freely, just
re-assign the issue.

| | Owner (GitHub) | Main area |
|---|---|---|
| A | `bhaveenthank` | lead, MACE engine, integration, final merge |
| B | `Jeyanth3` | NASA data: parsing, extra investigations, validation |
| C | `Manojh1811` | dashboard UX, charts, deployment |
| D | `pathi02` | science checks, evaluation, story + demo |

---

## Phase 0 - Setup (Sat 09:00-10:30) ✅ mostly done

- [x] Repo, CI, project skeleton, working app
- [x] NASA PSI data pulled: 24 combustion investigations, 10 investigations curated to 1,065 run records
- [ ] Everyone: accept the GitHub invite, clone, run `streamlit run app.py`, run `pytest -q`
- [ ] Everyone: be on the Space Apps team page, same local event (Batticaloa), not waitlisted
- [ ] A: create the Space Apps project page, paste the summary from `docs/submission_checklist.md`

**Exit check:** all four laptops show the dashboard; CI badge green.

## Phase 1 - Data you can defend (Sat 10:30-14:00) - owner B, helper D

- [ ] Hand-check 10 random rows per investigation in `data/curated/runs.csv` against the raw NASA CSV
- [ ] Add FLEX-2 (PSI-68), CFI (PSI-39), DAFT (PSI-47) experimental tables to `firewise/curate.py`
- [ ] SAME / SAME-R: pull particle-size results from the downloaded reports (`data/raw/psi/PSI-101`, `PSI-102`)
      into a small `data/curated/smoke_particles.csv` (value, unit, report, page)
- [ ] Saffire: spread rates from the analysed-data files if present
- [ ] Review each flag in the Data Reliability page; confirm or fix (open a "Data problem" issue for each)
- [ ] Verify the Saffire-I date conflict with a NASA source and update `firewise/audit.py`

**Exit check:** `pytest -q` green, no un-flagged assumption, every new number has file + row/page.

## Phase 2 - Intelligence (Sat 14:00-20:00) - owner A, helper D

- [ ] Grow FireWise-Eval to 25-30 questions; **B or C labels them without looking at MACE output**
- [ ] Add two baselines to `evaluation/benchmark.py`: BM25 + simple metadata filter; report all numbers honestly
- [ ] Tune tolerances in `mace.py` only with a written reason in `docs/science_notes.md`
- [ ] Gravity-transfer notes: 3-4 peer-reviewed partial-gravity papers (title, year, DOI) shown on Mission Explorer
      as *external context* - clearly separate from PSI evidence
- [ ] Optional: connect an LLM key (`.env`) so Ask FireWise rephrases answers - facts stay template-built

**Exit check:** benchmark table in README updated; no claim in the UI without a source.

## Phase 3 - Product polish & deploy (Sat 20:00 - Sun 10:00) - owner C

- [ ] Deploy to Streamlit Community Cloud (public URL, no login) - see `docs/TEAM_GUIDE.md`
- [ ] Mobile check (phone width) and dark/light readability
- [ ] First-time-user flow: Overview → Mission Explorer in < 3 clicks; add one-line help under every control
- [ ] Download buttons: ranked evidence (CSV) and condition certificate
- [ ] Representative NASA images (already downloaded under `data/raw/psi/*/Representative Image(s)`) on Overview
- [ ] Sleep in shifts. Nobody codes 24 h straight.

**Exit check:** public URL opens in a private browser window on a phone.

## Phase 4 - Validation (Sun 10:00-18:00) - owner D, all

- [ ] 3 people outside the team try the app with no help; write down where they got stuck; fix the top 3
- [ ] Open every Earth-benefit link in `configs/earth_benefits.yaml`; correct wording if needed
- [ ] Re-read every number on screen against `runs.csv`
- [ ] **18:00 feature freeze.** After this only bug fixes.

## Phase 5 - Story & submission (Sun 18:00-22:00) - owner D + A

- [ ] Demo: 30-second video **or** max 7 slides (title + intro count). Script in `docs/demo_script.md`
- [ ] Fill every project-page field (`docs/submission_checklist.md`), English only, public links tested in a private window
- [ ] Repo public, README final, release tag `v1.0`
- [ ] Submit by 22:00. Screenshot the confirmation.

---

### Judging criteria → where we score

| Criterion (1-5 each) | Our evidence |
|---|---|
| Impact | Moon/Mars habitat fire safety; shows what NASA has *not* tested yet → what to test next |
| Creativity | MACE: three separate scores + rule-based evidence levels + condition certificate, not a chatbot over PDFs |
| Validity | 1,065 real runs, provenance per value, 34 automated tests, benchmark vs BM25, honest limits page |
| Relevance | NASA PSI data is the core of every screen; all three pillars the brief names |
| Presentation | 30 s story: "the search engine says yes, the physics says no" |
