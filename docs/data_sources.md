# Data sources

## Already pulled automatically

`scripts/psi_fetch.py` reads the public JSON that the PSI website itself uses (no login, CC0 data).

| PSI id | Investigation | Pillar | Experimental table | PSI page |
|---|---|---|---|---|
| PSI-26 | BASS | prevention | yes | https://psi.nasa.gov/physci/repo/data/PSI-26 |
| PSI-25 | BASS-II | prevention | yes | https://psi.nasa.gov/physci/repo/data/PSI-25 |
| PSI-98 | Saffire-I | prevention | yes | https://psi.nasa.gov/physci/repo/data/PSI-98 |
| PSI-99 | Saffire-II | prevention | yes | https://psi.nasa.gov/physci/repo/data/PSI-99 |
| PSI-100 | Saffire-III | prevention | yes | https://psi.nasa.gov/physci/repo/data/PSI-100 |
| PSI-102 | SAME | detection | yes | https://psi.nasa.gov/physci/repo/data/PSI-102 |
| PSI-101 | SAME-R | detection | yes | https://psi.nasa.gov/physci/repo/data/PSI-101 |
| PSI-69 | FLEX | suppression | yes | https://psi.nasa.gov/physci/repo/data/PSI-69 |
| PSI-159 | ACME CFI-G | physics | yes (normal + inverse flames) | https://psi.nasa.gov/physci/repo/data/PSI-159 |

Metadata + publications also pulled for: PSI-10 ACME Flame Design, PSI-20 ACME BRE, PSI-21 ACME CLD Flame,
PSI-22 ACME E-FIELD, PSI-23 ACME s-Flame, PSI-39 CFI, PSI-47 DAFT/DAFT-2, PSI-60, PSI-62 (BASS modelling),
PSI-68 FLEX-2, PSI-106 SLICE, PSI-107 SPICE, PSI-115, PSI-117, PSI-142.

Full file list (16,372 files): `data/catalog/psi_files.csv`. Most volume is raw video (hundreds of GB) - not needed.

## Manual downloads

Some older ("legacy") PSI files return 404 through the API and must be downloaded from the PSI web page:
open the PSI page above → *Data files and documents* → download → save into
`data/raw/psi/<PSI-id>/<category>/`. Current list is the `fail` rows in `data/catalog/download_log.csv`, e.g.

- PSI-26 `Reports/PSI-26_Reports_BASS_FinalReport.pdf` and `PSI-26_Reports_SPICE_FinalReport.pdf`
- PSI-98 / PSI-100 `Engineering Documents/... SAFFIRE Offgassing Testing Strategy.pdf`

## Literature

NASA Technical Reports Server API (no key): `https://ntrs.nasa.gov/api/citations/search?q=<words>`
Example: microgravity flame spread spacecraft fire safety. Record id, title, year, URL.

## Licence and attribution

PSI data: CC0 1.0. Cite as "NASA Physical Sciences Informatics (PSI), <investigation>, <PSI id>, accessed Nov 2026",
and the DOI shown on each PSI page (also in `data/curated/investigations.csv`).
