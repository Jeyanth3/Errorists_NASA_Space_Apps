# Data

| folder | what | in git? |
|---|---|---|
| `raw/psi/meta/` | PSI investigation metadata (JSON, as served by PSI) | yes |
| `raw/psi/PSI-xx/Experimental table/` | NASA experimental tables, untouched | yes |
| `raw/psi/PSI-xx/<other>/` | reports, papers, analysed data, images (~1 GB) | no - run the fetch script |
| `catalog/` | list of combustion investigations and every PSI file (16k rows) | yes |
| `curated/` | Run records, investigation and publication indexes, FLEX-2 fuel ranges, DAFT sessions, SLICE test days and SPICE readings. Rebuild with `python -m firewise.curate`. | yes |
| `audits/` | metadata conflicts we found | yes |

Re-create everything:

```bash
python scripts/psi_fetch.py catalog --ids 1-200
python scripts/psi_fetch.py files
python scripts/psi_fetch.py download --max-mb 8
python -m firewise.curate
```

All PSI files are CC0 1.0 (public domain). Source: https://psi.nasa.gov
