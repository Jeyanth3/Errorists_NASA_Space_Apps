# Team guide

## 1. First time setup (15 min)

```bash
git clone https://github.com/bhaveenthank/Errorists_NASA_Space_Apps.git
cd Errorists_NASA_Space_Apps
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
streamlit run app.py               # opens http://localhost:8501
pytest -q                          # should say "34 passed"
```

Python 3.10+ needed. VS Code with the Python + Ruff extensions is recommended.

The big NASA files (~1 GB of reports, papers, images) are not in git. If you need them:

```bash
python scripts/psi_fetch.py files
python scripts/psi_fetch.py download --max-mb 8 --only PSI-101,PSI-102
```

## 2. Daily flow

1. Pick an issue on GitHub, assign yourself, move it to "in progress" (comment is fine).
2. `git checkout main && git pull`
3. `git checkout -b <your-name>/<short-topic>`  e.g. `jeyanth/flex2-table`
4. Small commits, clear messages: `parse FLEX-2 experimental table`
5. Before pushing: `ruff check . --fix && pytest -q`
6. `git push -u origin <branch>` → open a Pull Request → CI runs.
7. **No review needed** - if CI is green, merge it yourself (squash). If CI is red, the PR shows the error; fix it first.
8. Delete the branch after merging.

`main` should always run. Never push broken code to main directly.

## 3. Where things live

| I want to... | file |
|---|---|
| parse a new NASA table | `firewise/curate.py` → add a function, call it in `build()`, run `python -m firewise.curate` |
| change ranking rules | `firewise/mace.py` (write the reason in `docs/science_notes.md`) |
| add a finding sentence | `firewise/insights.py` |
| change a page | `views/<page>.py` |
| add a mission atmosphere | `configs/missions.yaml` |
| add a test | `tests/` |

After changing `curate.py`, commit the regenerated `data/curated/*.csv` too - CI checks they match.

## 4. Data rules (judges check Validity)

- Never type a number by hand into the app. It must come from a NASA file, with file + row (or report + page).
- Unknown stays empty. Do not guess.
- If you assume or infer something, add a flag on the run (see `rec["flags"]` in `curate.py`).
- If NASA metadata looks wrong, keep the original and log it in `firewise/audit.py`.

## 5. Deploy (Streamlit Community Cloud, free)

1. Repo must be public (the lead flips it on Sunday, or earlier if everyone agrees).
2. https://share.streamlit.io → sign in with GitHub → *Create app* → repo `Errorists_NASA_Space_Apps`,
   branch `main`, file `app.py`, Python 3.12.
3. Optional secrets (Settings → Secrets): `FIREWISE_LLM_KEY = "..."`
4. Copy the public URL into the README and the Space Apps project page.
5. Request a FortiGuard web-filter classification for the URL (Space Apps recommends it so judges can open it).

## 6. If something breaks

- `ModuleNotFoundError` → you forgot `source .venv/bin/activate` or `pip install -r requirements-dev.txt`
- CI fails on "data/curated is out of date" → run `python -m firewise.curate` and commit the CSVs
- Page error in the browser → run `pytest -q tests/test_pages.py` to see the traceback
