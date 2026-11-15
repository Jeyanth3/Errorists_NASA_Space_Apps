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
| PSI-39 | CFI | physics | individual droplet tests | https://psi.nasa.gov/physci/repo/data/PSI-39 |
| PSI-68 | FLEX-2 | physics | fuel-specific operating ranges | https://psi.nasa.gov/physci/repo/data/PSI-68 |
| PSI-47 | DAFT | detection | instrument sessions | https://psi.nasa.gov/physci/repo/data/PSI-47 |
| PSI-106 | SLICE | physics | daily test summaries | https://psi.nasa.gov/physci/repo/data/PSI-106 |
| PSI-107 | SPICE | physics | burner readings | https://psi.nasa.gov/physci/repo/data/PSI-107 |

Metadata + publications also pulled for: PSI-10 ACME Flame Design, PSI-20 ACME BRE, PSI-21 ACME CLD Flame,
PSI-22 ACME E-FIELD, PSI-23 ACME s-Flame, PSI-39 CFI, PSI-47 DAFT/DAFT-2, PSI-60, PSI-62 (BASS modelling),
PSI-68 FLEX-2, PSI-106 SLICE, PSI-107 SPICE, PSI-115, PSI-117, PSI-142.

Full file list (16,372 files): `data/catalog/psi_files.csv`. Most volume is raw video (hundreds of GB) - not needed.

## Manual downloads

Eight older PSI entries failed through the website's download service on 14 November 2026. The [source audit](science_notes.md#eight-legacy-source-entries) records the affected entries, the available reports and the five detector workbooks. To retrieve an available file, open the investigation's **Data files and documents** tab and select the file by its original name.

## Literature

NASA Technical Reports Server API (no key): `https://ntrs.nasa.gov/api/citations/search?q=<words>`
Example: microgravity flame spread spacecraft fire safety. Record id, title, year, URL.

## Licence and attribution

PSI data: CC0 1.0. Cite as "NASA Physical Sciences Informatics (PSI), <investigation>, <PSI id>, accessed Nov 2026",
and the DOI shown on each PSI page (also in `data/curated/investigations.csv`).
