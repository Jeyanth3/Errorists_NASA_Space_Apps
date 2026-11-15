<p align="center"><img src="assets/campfire.png" alt="FireWise logo" width="140"></p>

# FireWise

**Mission-aware, evidence-grounded fire-safety insights from NASA microgravity combustion data.**
NASA Space Apps Challenge 2026 · *Flame in Freefall* · Team **Errorists** (Batticaloa, Sri Lanka)

> A Moon base may breathe ~30% oxygen at 70 kPa in one-sixth gravity. Nearly every NASA fire experiment ran in
> 21% oxygen, 101 kPa and microgravity. A search engine will still hand you those results.
> **FireWise checks the physics first** - and tells you, run by run, what matches your mission, what differs,
> and what has never been tested.

---

## What it does

| Page | What you get |
|---|---|
| 🚀 **Mission Explorer** | Choose ISS / Moon base / rover / Mars base (or your own atmosphere) + prevention, detection or suppression. NASA investigations ranked into **DIRECT · SUPPORTING · EXTRAPOLATED** evidence with a per-run condition certificate. |
| 🗺️ **Atmosphere Map** | Every NASA run on an O₂-vs-pressure map with iso-pO₂ lines and mission atmospheres as stars - see the evidence gaps at a glance. |
| 🧯 **Prevent · Detect · Suppress** | Key measured findings per safety pillar, only comparing like with like. |
| ⚖️ **Compare Runs** | Two runs side by side + a verdict on whether the comparison is physically fair. |
| 💬 **Ask FireWise** | Plain-English questions → structured query → answer built only from NASA numbers, each with its PSI source. |
| 🔎 **Data Reliability** | Every assumption, inference and NASA metadata conflict we found, plus an evidence graph. |

## Why it is different - MACE

**M**ission-**A**ware, **C**ondition-constrained **E**vidence ranking scores each run on three *separate* axes:

- **Relevance** - does it study my safety question?
- **Applicability** - gravity, O₂ partial pressure, O₂ fraction, total pressure, material, atmosphere type
- **Data quality** - measured vs assumed vs missing

The evidence level comes from explicit rules (`firewise/mace.py`), never from a language model.
A high-relevance run with the wrong gravity is shown - but labelled as an extrapolation.

FireWise-Eval (12 hand-labelled questions, `python -m evaluation.benchmark`):

| system | goal accuracy | top-1 hit | unsafe "applicable" claims |
|---|---|---|---|
| BM25 keyword search | - | 42% | 42% |
| MACE | 100% | 100% | 0% |

*Small, team-labelled set - see `docs/science_notes.md` for limits.*

## NASA data

1,065 experimental runs from the NASA **Physical Sciences Informatics (PSI)** Combustion Science repository (CC0):

| Pillar | Investigations |
|---|---|
| Prevention | BASS (PSI-26), BASS-II (PSI-25), Saffire-I/II/III (PSI-98/99/100) |
| Detection | SAME (PSI-102), SAME-R (PSI-101) |
| Suppression | FLEX (PSI-69) |
| Combustion physics (context) | CFI (PSI-39), ACME CFI-G (PSI-159) |

Four additional tables contain FLEX-2 fuel ranges, DAFT instrument sessions, SLICE test days and SPICE burner readings. See the **Method & sources** page for these records and [the source audit](docs/science_notes.md#source-audit-14-november-2026) for verification details and missing files.

Plus metadata and 352 publications for all 24 PSI combustion investigations. See `data/README.md`.

## Run it

```bash
git clone https://github.com/bhaveenthank/Errorists_NASA_Space_Apps.git
cd Errorists_NASA_Space_Apps
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
streamlit run app.py
```

Checks: `pytest -q` and `ruff check .` (both run on every push / PR).

## Project layout

```
app.py                 navigation
views/                 one file per page
firewise/              curate.py (raw → runs), mace.py (ranking), insights.py, assistant.py, search.py, audit.py
configs/               mission atmospheres, Earth-benefit links
data/                  raw NASA tables, curated CSVs, audits
scripts/psi_fetch.py   pulls metadata + files from PSI
evaluation/            FireWise-Eval benchmark
docs/                  plan, team guide, science notes, demo script, submission checklist
```

## Scientific limits

PSI holds no partial-gravity combustion data, so FireWise never presents a lunar or Martian result as measured and
never interpolates between 0 g and 1 g. Burner mixtures (CFI-G) are not treated as cabin atmospheres. Details in
`docs/science_notes.md`.

## Use of SI tools

Following the Space Apps 2026 rules, we note that SI (AI) coding assistants were used to help write parts of the
code, data-curation scripts and documentation in this repository. The team chose the challenge, the approach and
the scientific rules, and reviewed, tested and is responsible for all of it. All data values come from NASA PSI
files, not from SI generation. No SI-generated images, audio or video are used.

## Team Errorists

Bhaveenthan · Jeyanth · Manojh · Pathi

*Independent Space Apps project, not endorsed by NASA. NASA data courtesy of NASA PSI.*
