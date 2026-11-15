# Science notes and limits

## Evidence classes

| Source | How FireWise treats it |
|---|---|
| NASA PSI experimental tables | primary evidence; every value traceable to file + row |
| PSI metadata / publications | context, search, citations |
| External peer-reviewed papers (partial gravity etc.) | **separately labelled context**, never mixed into PSI evidence |
| Our own reasoning (MACE levels, gaps) | labelled as assessment, rules are in code |

## Things we will not do

1. **No gravity interpolation.** Flames in partial gravity are not "between" 0 g and 1 g; weak buoyant flow can make
   some thin materials more flammable at partial g than in either limit. So a microgravity run is never DIRECT
   evidence for the Moon or Mars.
2. **pO₂ is not the whole story.** 30% O₂ at 70.3 kPa has about the same O₂ partial pressure (21.1 kPa) as sea-level
   air (21.3 kPa), but less nitrogen to soak up heat. We check O₂ fraction and total pressure separately.
3. **Burner ≠ cabin.** ACME CFI-G uses up to 85% O₂ burner mixtures. These are combustion-physics conditions only.
4. **Smoke ≠ flame.** SAME/SAME-R heat samples without flaming; their results are never compared with flame data.
5. **Droplet ≠ solid.** FLEX extinction is not compared with BASS/Saffire flame spread.
6. Rocket propulsion is out of scope (challenge brief).

## Tolerances used in MACE

| check | match | close | why |
|---|---|---|---|
| O₂ partial pressure | ±2.5 kPa | ±6 kPa | ~ ±2 percentage points of O₂ at 1 atm, the spread of ISS cabin O₂ |
| O₂ fraction | ±2.5 pts | ±6 pts | same reasoning |
| total pressure | ±10 % | ±30 % | 10 % ≈ normal cabin variation |

Change these only with a reason written here.

## Assumptions in the curated data

- BASS (PSI-26) uses the oxygen fraction and pressure recorded in its as-run workbook. On 15 November 2026 all 121 test records matched on as-run test number, test number, sample number and material (ignoring capitalization, commas and whitespace). The checked-in extract is `data/reference/bass_as_run.csv`. Its worksheet row points to columns J/K (fan/air displays), AA/AB (oxygen/pressure), and AD (observations) on `as run matrix`. Excel stores the oxygen percentages as fractions. Pressure is converted from atm to kPa. The display settings are preserved as text because they can change during a run. The workbook is a separate source from the missing final report.
- BASS-II uses an assumed ISS cabin pressure of 101.325 kPa, flagged on every run.
- Saffire burned inside Cygnus at cabin pressure → same treatment.
- FLEX "Burning rate; mm" is read as the burning-rate constant K in mm²/s (d²-law), the unit used in FLEX papers.
- Unlabelled BASS-II film/rod samples are PMMA (the BASS-II sample set); flagged as inferred.
- Saffire-II blank material cells are carried down from the row above; flagged.

## Known gaps (these are findings, show them in the demo)

- No PSI combustion run in partial gravity.
- No solid-fuel run near 30% O₂ / 70 kPa (lunar planning atmosphere).
- FLEX has droplet runs at ~70 kPa and up to 34% O₂ - the closest PSI evidence to habitat atmospheres, but liquids only.
- Smoke data only at cabin pressure.

## Source audit, 14 November 2026

Compared all 15 source CSVs used here with fresh downloads from NASA PSI. File contents matched after normalizing line endings. Source rows below are CSV record numbers, counting the header as row 1.

For each investigation in `runs.csv`, an independent CSV reader checked ten randomly selected records, or every record for smaller investigations. The sample used Python's `random.Random(20261114).sample` separately for each investigation in export order. All 81 records matched the checked fields after the corrections below. This verifies selected fields, not every derived value.

| Investigation | Rows checked | Fields compared with NASA |
|---|---:|---|
| BASS-II / BASS | 10 / 10 | Source material and date, initial oxygen and final CO for BASS-II, test identifiers for BASS |
| Saffire-I / II / III | 2 / 9 / 2 | Sample ID, flow speed and direction, populated source material, burn time when supplied |
| SAME / SAME-R | 8 / 10 | Source material, flow speed, aging and mass loss for SAME, date, duration and description for SAME-R |
| FLEX / CFI | 10 / 10 | Fuel, pressure conversion and oxygen, plus FLEX date and burn time or CFI helium and test ID |
| ACME CFI-G | 10 | Fuel, oxygen, pressure and burn time across the normal and inverse tables |

Every data cell in the four additional curated tables matched its corresponding source cell, covering 491 rows. FLEX-2 has eight fuel/range entries, DAFT has two instrument sessions, SLICE has twelve daily summaries including calibrations, and SPICE has 469 burner readings with repeated ignition times and changing flow settings. The Method & sources page exposes these tables. They are excluded from individual-run rankings.

CFI (PSI-39) contains 87 source rows. Eight repeat earlier tests with identical fields after trimming whitespace. The 79 distinct CFI runs retain their first source row and the published atmosphere and fuel. The table gives conditions only.

Specific discrepancies and decisions:

- SAME-R test 57 has matching test conditions at rows 57 and 75. NASA labels the material Lampwick in the first and Teflon in the second. One flagged record retains both labels with the resolved material left empty. SAME and SAME-R cabin pressures are now explicitly flagged as assumptions.
- Saffire-II 2-8 gives a figure reference for thickness. Sample 2-7 lists two materials, thicknesses and lengths. Their dimension fields remain empty wherever the table does not give a single value.
- BASS-II M5 gives final CO as `>500` ppm. M5 and the over-range entries retain a flag and an empty numeric result. The BASS date `5/15/2103` is preserved and flagged at source row 111.
- BASS cross-check: PSI-26 table row 3 records a 2 cm PMMA sphere. The official presentation *BASS: An Overview of Recent ISS Results*, page 34, shows a 2 cm PMMA sphere burning at 17% oxygen and 12 cm/s. Several source rows have that material and size. The slide gives no test ID, so its conditions and outcome cannot be assigned to row 3.

### Eight legacy source entries

On 14 November, the PSI download service generated links for these entries, but the storage service returned HTTP 404 (`NoSuchKey`). Requests through the website's ZIP service returned HTTP 500. No placeholder files were created.

| NASA entry | Available supporting material |
|---|---|
| PSI-26 BASS and SPICE final reports | The BASS results presentation is available under PSI-26 / Presentations. The 28-page SPICE final report is available under PSI-107 / Reports. Its catalog size differs from the PSI-26 entry, so its original PSI-107 identity is retained. |
| PSI-98 and PSI-100 Saffire offgassing strategy | Both entries point to the same missing archive object. Preparation details remain unverified. |
| PSI-102 XML entries 16904, 16912, 16937, 16942 | All four have a catalog size of zero bytes. NASA provides five populated XLS workbooks in those same run folders. Their sizes matched the catalog and the detector time series opened successfully. The XML contents cannot be verified. |

The five locally downloaded workbooks cover silicone run 05 (two workbooks), Kapton run 14, Teflon run 26 and cotton lampwick run 31. The raw files retain their NASA names under `data/raw/psi/PSI-102/Analyzed Data/`. Detector voltages and timestamps should retain their original units until a documented calibration is applied.

Sources: [BASS](https://psi.nasa.gov/physci/repo/data/PSI-26), [SPICE](https://psi.nasa.gov/physci/repo/data/PSI-107), [Saffire-I](https://psi.nasa.gov/physci/repo/data/PSI-98), [Saffire-III](https://psi.nasa.gov/physci/repo/data/PSI-100), [SAME](https://psi.nasa.gov/physci/repo/data/PSI-102).

## Benchmark caveats

FireWise-Eval currently has 12 questions labelled by the team. That is a sanity check, not a scientific result.
Before quoting numbers to judges: 25-30 questions, labelled by someone who did not write MACE, and state n.
