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

- BASS / BASS-II burned in the Microgravity Science Glovebox, which uses ISS cabin air → pressure set to 101.3 kPa
  and **flagged as assumed** on every run.
- Saffire burned inside Cygnus at cabin pressure → same treatment.
- FLEX "Burning rate; mm" is read as the burning-rate constant K in mm²/s (d²-law), the unit used in FLEX papers.
- Unlabelled BASS-II film/rod samples are PMMA (the BASS-II sample set); flagged as inferred.
- Saffire-II blank material cells are carried down from the row above; flagged.

## Known gaps (these are findings, show them in the demo)

- No PSI combustion run in partial gravity.
- No solid-fuel run near 30% O₂ / 70 kPa (lunar planning atmosphere).
- FLEX has droplet runs at ~70 kPa and up to 34% O₂ - the closest PSI evidence to habitat atmospheres, but liquids only.
- Smoke data only at cabin pressure.

## Benchmark caveats

FireWise-Eval currently has 12 questions labelled by the team. That is a sanity check, not a scientific result.
Before quoting numbers to judges: 25-30 questions, labelled by someone who did not write MACE, and state n.
