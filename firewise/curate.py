"""
Turn the raw PSI experimental tables into one tidy, run-level table.

Rules we follow (see docs/science_notes.md):
  * never overwrite a NASA value silently - the raw cell is kept next to the parsed one
  * anything we assume (cabin pressure, fill-down of blank cells...) gets a flag
  * unknown stays empty, we do not guess numbers

run:  python -m firewise.curate
"""
import json
import re
from pathlib import Path

import pandas as pd

from firewise import units

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "psi"
OUT = ROOT / "data" / "curated"

CABIN_KPA = units.ATM_KPA  # ISS / Cygnus run near sea-level pressure

# which fire-safety question each investigation mainly informs
PILLAR = {
    "PSI-25": "prevention", "PSI-26": "prevention",
    "PSI-98": "prevention", "PSI-99": "prevention", "PSI-100": "prevention",
    "PSI-101": "detection", "PSI-102": "detection",
    "PSI-69": "suppression",
    "PSI-159": "combustion physics",
}

MATERIALS = [
    # (regex, family, state)
    (r"pmma|plexiglas|acrylic", "PMMA", "solid"),
    (r"sibal|cotton.?fiberglass", "SIBAL (cotton-fiberglass)", "solid"),
    (r"nomex", "Nomex", "solid"),
    (r"ultem", "Ultem", "solid"),
    (r"silicone", "Silicone", "solid"),
    (r"kapton", "Kapton", "solid"),
    (r"teflon|ptfe", "Teflon (PTFE)", "solid"),
    (r"pyrell", "Pyrell foam", "solid"),
    (r"lampwick", "Lampwick (cotton)", "solid"),
    (r"dibutyl", "Dibutyl phthalate", "liquid"),
    (r"candle|wax", "Candle wax", "solid"),
    (r"methanol", "Methanol", "liquid"),
    (r"heptane", "n-Heptane", "liquid"),
    (r"ethane", "Ethane", "gas"),
    (r"ethylene", "Ethylene", "gas"),
    (r"methane", "Methane", "gas"),
    (r"propane", "Propane", "gas"),
    (r"butane", "n-Butane", "gas"),
]


def material(text):
    s = str(text or "").lower()
    for pat, fam, state in MATERIALS:
        if re.search(pat, s):
            return fam, state
    return None, None


def geometry(text):
    s = str(text or "").lower()
    for g in ("sphere", "rod", "cylinder", "slab", "sheet", "film", "fabric"):
        if g in s:
            return g
    return None


def _table(pid, name_part=""):
    files = sorted((RAW / pid / "Experimental table").glob("*.csv"))
    files = [f for f in files if name_part in f.name]
    if not files:
        raise FileNotFoundError(f"no experimental table for {pid} ({name_part})")
    try:
        df = pd.read_csv(files[0], dtype=str, encoding="utf-8-sig", keep_default_na=False)
    except UnicodeDecodeError:  # a few PSI tables were saved from Excel on Windows
        df = pd.read_csv(files[0], dtype=str, encoding="cp1252", keep_default_na=False)
    df.columns = [re.sub(r"\s+", " ", c).strip() for c in df.columns]
    return df, files[0].name


def _base(pid, inv, source, row_no):
    return {
        "psi_id": pid, "investigation": inv, "pillar": PILLAR[pid],
        "gravity": "microgravity", "gravity_g": 0.0,
        "source_file": source, "source_row": row_no + 2,  # +header, 1-based
        "flags": [],
    }


# ---------------------------------------------------------------- BASS / BASS-II
def bass2():
    df, src = _table("PSI-25")
    rows = []
    for i, r in df.iterrows():
        mat_txt = r.get("Fuel Sample Material", "")
        if "clean" in mat_txt.lower() or not mat_txt.strip():
            continue  # housekeeping rows (e.g. 'SOOT Cleaning'), not burns
        fam, state = material(mat_txt)
        rec = _base("PSI-25", "BASS-II", src, i)
        if fam is None and re.search(r"film|rod|spherical|micron", mat_txt.lower()):
            fam, state = "PMMA", "solid"
            rec["flags"].append("material inferred: unlabeled film/rod -> PMMA (BASS-II sample set)")
        o2 = units.first_number(r.get("Calibrated initial O2 % by vol"))
        rec.update({
            "run_id": f"BASS2-{r.get('Test #', i)}",
            "date": r.get("Date"),
            "fuel_raw": mat_txt, "fuel": fam, "fuel_state": state,
            "geometry": geometry(mat_txt) or ("fabric" if fam and "SIBAL" in fam else None),
            "thickness_mm": _thickness_from_label(mat_txt),
            "diameter_mm": _rod_diameter(mat_txt),
            "o2_fraction": units.to_fraction(o2),
            "pressure_kpa": CABIN_KPA,
            "flow_setting_raw": f"fan {r.get('Fan display', '')} / air {r.get('Air display', '')}",
            "co_final_ppm": units.first_number(r.get("Final CO (ppm)")),
            "pi": r.get("PI"),
        })
        rec["flags"].append("pressure assumed ~1 atm (MSG in ISS cabin)")
        if o2 is not None and o2 > 30:
            rec["flags"].append("O2 reading looks odd - check raw row")
        rows.append(rec)
    return rows


def _rod_diameter(txt):
    """'3/8" clear rod' -> 9.525 mm."""
    s = str(txt).lower()
    if "rod" not in s:
        return None
    m = re.search(r"(\d+)\s*/\s*(\d+)", s)
    if m:
        return round(float(m.group(1)) / float(m.group(2)) * 25.4, 2)
    m = re.search(r"(\d*\.\d+)", s)
    return round(float(m.group(1)) * 25.4, 2) if m else None


def _thickness_from_label(txt):
    s = str(txt).lower()
    m = re.search(r"(\d+)\s*micron", s)
    if m:
        return float(m.group(1)) / 1000
    m = re.search(r"(\d*\.?\d+)\s*mm", s)
    if m:
        return float(m.group(1))
    return None


def bass1():
    df, src = _table("PSI-26")
    rows = []
    for i, r in df.iterrows():
        mat_txt = r.get("Fuel Sample Material", "")
        if "clean" in mat_txt.lower() or not mat_txt.strip():
            continue
        fam, state = material(mat_txt)
        geo = geometry(mat_txt)
        if fam is None and geo == "sphere":
            fam, state = "PMMA", "solid"  # BASS spheres are PMMA per the investigation description
            flag = "material inferred: unnamed sphere -> PMMA"
        else:
            flag = None
        size = units.length_mm(re.search(r"\d+\s*cm", mat_txt).group()) if re.search(r"\d+\s*cm", mat_txt) else None
        rec = _base("PSI-26", "BASS", src, i)
        rec.update({
            "run_id": f"BASS-{r.get('As Run Test #', i)}-{r.get('Test #', '')}",
            "date": r.get("Date"),
            "fuel_raw": mat_txt, "fuel": fam, "fuel_state": state,
            "geometry": geo or ("fabric" if fam and ("SIBAL" in fam or "Nomex" in fam) else None),
            "diameter_mm": size if geo == "sphere" else None,
            "width_mm": size if geo != "sphere" else None,
            "o2_fraction": None,
            "pressure_kpa": CABIN_KPA,
            "flow_dir": "opposed" if "opposed" in mat_txt.lower() else None,
        })
        rec["flags"].append("pressure assumed ~1 atm (MSG in ISS cabin)")
        if flag:
            rec["flags"].append(flag)
        rows.append(rec)
    return rows


# ---------------------------------------------------------------- Saffire
def saffire():
    rows = []
    for pid, inv in (("PSI-98", "Saffire-I"), ("PSI-99", "Saffire-II"), ("PSI-100", "Saffire-III")):
        df, src = _table(pid)
        cols = {c.lower(): c for c in df.columns}

        def col(*keys):
            for k in keys:
                for lc, c in cols.items():
                    if k in lc:
                        return c
            return None

        last_mat = None
        for i, r in df.iterrows():
            sample = str(r.get(col("sample number"), "")).strip()
            if not re.match(r"^(S\d|\d-\d)", sample):
                continue  # notes / flow-vis rows
            mat_txt = r.get(col("material"), "").strip()
            rec = _base(pid, inv, src, i)
            if not mat_txt and last_mat:
                mat_txt = last_mat
                rec["flags"].append("material blank in source - carried down from previous row")
            last_mat = mat_txt or last_mat
            fam, state = material(mat_txt)
            spread = None
            sp_col = col("g spread length")
            if sp_col and "mm/s" in str(r.get(sp_col, "")):
                spread = units.first_number(r.get(sp_col))
            burn = r.get(col("burn time"), "")
            rec.update({
                "run_id": f"{inv.upper()}-{sample}",
                "fuel_raw": mat_txt, "fuel": fam, "fuel_state": state,
                "geometry": "fabric" if fam and ("SIBAL" in fam or "Nomex" in fam) else "sheet",
                "thickness_mm": units.length_mm(_unit_hint(r.get(col("thickness"), ""), col("thickness"))),
                "length_mm": units.length_mm(_unit_hint(r.get(col("length"), ""), col("length"))),
                "width_mm": units.length_mm(_unit_hint(r.get(col("width"), ""), col("width"))),
                "flow_cm_s": units.first_number(r.get(col("air flow"))),
                "flow_dir": str(r.get(col("direction"), "")).strip().lower() or None,
                "o2_fraction": units.to_fraction(units.range_mean(r.get(col("percent o2"), ""))),
                "pressure_kpa": CABIN_KPA,
                "ignition_power_w": units.first_number(r.get(col("ignition power"))),
                "burn_time_s": units.first_number(burn),
                "spread_rate_mm_s": spread,
                "outcome": "no sustained burning" if "insignificant" in str(burn).lower() else
                           ("burned" if units.first_number(burn) else None),
                "scale": "large (spacecraft-scale)",
            })
            rec["flags"].append("pressure assumed ~1 atm (Cygnus cabin)")
            if pid in ("PSI-98", "PSI-100") and rec["thickness_mm"] and rec["thickness_mm"] > 1:
                rec["flags"].append("SIBAL thickness reported in cm (e.g. 0.37 cm); Saffire-II lists the "
                                    "same fabric as 0.37 mm - unit in source is suspect")
            if "037 mm" in str(r.get(col("thickness"), "")):
                rec["flags"].append("thickness '037 mm' in source - read as 0.37 mm")
                rec["thickness_mm"] = 0.37
            rows.append(rec)
    return rows


def _unit_hint(val, colname):
    """Some Saffire columns keep the unit in the header, e.g. 'Sample Width (cm)'."""
    v = str(val).strip()
    if not v:
        return v
    if colname and "(cm)" in colname and not re.search(r"[a-z]", v.lower()):
        return v + " cm"
    return v


# ---------------------------------------------------------------- SAME / SAME-R
def same():
    rows = []
    df, src = _table("PSI-102")
    for i, r in df.iterrows():
        mat_txt = r.get("Sample Material", "")
        fam, state = material(mat_txt)
        rec = _base("PSI-102", "SAME", src, i)
        rec.update({
            "run_id": f"SAME-{r.get('Sample #', i)}",
            "fuel_raw": mat_txt, "fuel": fam, "fuel_state": state,
            "flow_cm_s": units.first_number(r.get("Air Flow (cm/s)")),
            "weight_loss_mg_min": units.first_number(r.get("Weight loss rate (mg/min)")),
            "aging_s": (units.first_number(r.get("Aging Duration (minutes)")) or 0) * 60 or None,
            "process": "pyrolysis smoke (heated sample, not flaming)",
            "pressure_kpa": CABIN_KPA,
        })
        if "same conditions" in mat_txt.lower():
            rec["flags"].append("conditions given as 'same as 1-4' - values not repeated in table")
        rows.append(rec)

    df, src = _table("PSI-101")
    for i, r in df.iterrows():
        mat_txt = r.get("Sample Type", "")
        fam, state = material(mat_txt)
        rec = _base("PSI-101", "SAME-R", src, i)
        rec.update({
            "run_id": f"SAMER-{r.get('SAME Test #', i)}",
            "date": r.get("Date"),
            "fuel_raw": mat_txt, "fuel": fam, "fuel_state": state,
            "flow_cm_s": units.first_number(r.get("Inlet velocity (cm/s)")),
            "heater_ratio": units.first_number(r.get("Rt/R0")),
            "duration_s": units.first_number(r.get("Duration (sec)")),
            "aging_s": units.first_number(r.get("Net aging time (sec)")),
            "process": "pyrolysis smoke (heated sample, not flaming)",
            "notes": r.get("Description"),
            "pressure_kpa": CABIN_KPA,
        })
        rows.append(rec)
    return rows


# ---------------------------------------------------------------- FLEX
def flex():
    df, src = _table("PSI-69")
    rows = []
    for i, r in df.iterrows():
        fam, state = material(r.get("Fuel"))
        p_kpa = units.first_number(r.get("Ambient pressure; mmHg"))
        p_kpa = units.mmhg_to_kpa(p_kpa) if p_kpa else None
        x_n2 = units.first_number(r.get("N initial ambient composition; mole fraction"))
        x_co2 = units.first_number(r.get("CO initial ambient composition; mole fraction"))
        x_he = units.first_number(r.get("He initial ambient composition; mole fraction"))
        dil = max((("N2", x_n2 or 0), ("CO2", x_co2 or 0), ("He", x_he or 0)), key=lambda t: t[1])
        end = str(r.get("Test end", "")).strip()
        end = {"Disr": "Disruption"}.get(end, end)
        rec = _base("PSI-69", "FLEX", src, i)
        rec.update({
            "run_id": f"FLEX-{r.get('FLEX Test #', i)}-{r.get('FLEX Identifier', '')}",
            "date": r.get("Test Date"),
            "fuel_raw": r.get("Fuel"), "fuel": fam, "fuel_state": state, "geometry": "droplet",
            "pressure_kpa": p_kpa,
            "o2_fraction": units.first_number(r.get("O initial ambient composition; mole fraction")),
            "n2_fraction": x_n2, "co2_fraction": x_co2, "he_fraction": x_he,
            "diluent": dil[0],
            "diameter_mm": units.first_number(r.get("Droplet initial diameter; mm")),
            "extinction_diameter_mm": units.first_number(r.get("Visible flame extinction diameter; mm")),
            "burning_rate_k": units.first_number(r.get("Burning rate; mm")),
            "burn_time_s": units.first_number(r.get("Burn time; s")),
            "outcome": end.lower() or None,
        })
        rec["flags"].append("burning-rate column header says 'mm'; treated as K (mm^2/s) per FLEX papers")
        rows.append(rec)
    return rows


# ---------------------------------------------------------------- ACME CFI-G
def cfig():
    rows = []
    for part, kind in (("Normal", "normal"), ("Inverse", "inverse")):
        df, src = _table("PSI-159", part)
        for i, r in df.iterrows():
            if not str(r.get("Fuel", "")).strip():
                continue
            fam, state = material(r.get("Fuel"))
            xo2 = r.get("XO2 before test") or r.get("XO2")
            p_bar = units.first_number(r.get("approx p (bar)"))
            hot = str(r.get("Hot ignition", "")).strip().lower()
            ext = str(r.get("Self-ext or flow term") or r.get("Self -ext or flow term") or "").strip().upper()
            rec = _base("PSI-159", "ACME CFI-G", src, i)
            rec.update({
                "run_id": f"CFIG-{kind[0].upper()}-{r.get('Test', i)}".replace(" ", ""),
                "fuel_raw": r.get("Fuel"), "fuel": fam, "fuel_state": state, "geometry": f"{kind} spherical burner flame",
                "o2_fraction": units.first_number(xo2),
                "pressure_kpa": p_bar * units.BAR_TO_KPA if p_bar else None,
                "burn_time_s": units.first_number(r.get("burn time (sec)")),
                "cool_flame": str(r.get("Cool flame?") or r.get("TFP") or "").strip() or None,
                "adiabatic_temp_k": units.first_number(r.get("Tad (K)")),
                "outcome": ("no ignition" if hot == "no" else "flash" if hot == "flash" else
                            "self-extinguished" if ext == "SE" else "flow terminated" if ext == "FT" else
                            ("ignited" if hot == "yes" else None)),
                "notes": r.get("Comments"),
            })
            rec["flags"].append("burner mixtures are combustion-physics conditions, not cabin atmospheres")
            rows.append(rec)
    return rows


# ---------------------------------------------------------------- investigations + pubs
def investigations():
    inv, pubs = [], []
    for f in sorted((RAW / "meta").glob("PSI-*.json"), key=lambda p: int(p.stem.split("-")[1])):
        d = json.loads(f.read_text())
        pid = f.stem
        text = " ".join(str(d.get(k) or "") for k in ("objective", "hypothesis", "approach", "researchImpacts", "description"))
        inv.append({
            "psi_id": pid,
            "acronym": d.get("investigationAcronym") or pid,
            "title": (d.get("title") or d.get("projectTitle") or "").strip(),
            "pillar": PILLAR.get(pid, "background"),
            "sub_area": d.get("subResearchArea") or "",
            "hardware": (d.get("experimentHardware") or "").strip(),
            "platform": d.get("flightProgram") or "",
            "start": d.get("investigationStartDate") or "",
            "end": d.get("investigationEndDate") or "",
            "doi": d.get("doi") or "",
            "license": d.get("licenseName") or "",
            "total_gb": round(float(d.get("totalFileSize") or 0) / 1e9, 2),
            "n_files": len(d.get("added") or []),
            "objective": (d.get("objective") or "").strip(),
            "impact": (d.get("researchImpacts") or "").strip(),
            "text": re.sub(r"\s+", " ", text).strip(),
            "url": f"https://psi.nasa.gov/physci/repo/data/{pid}",
        })
        for p in d.get("publications") or []:
            if p.get("title"):
                pubs.append({"psi_id": pid, "acronym": inv[-1]["acronym"], "title": p["title"].strip(),
                             "authors": p.get("authorList", ""), "doi": p.get("doi", "")})
    return pd.DataFrame(inv), pd.DataFrame(pubs)


def build():
    rows = bass2() + bass1() + saffire() + same() + flex() + cfig()
    runs = pd.DataFrame(rows)
    runs["po2_kpa"] = runs["o2_fraction"] * runs["pressure_kpa"]
    runs["flags"] = runs["flags"].apply(lambda x: " | ".join(x))
    runs = runs.rename(columns={"flags": "data_flags"})
    runs = runs.drop_duplicates("run_id", keep="first")
    inv, pubs = investigations()
    OUT.mkdir(parents=True, exist_ok=True)
    runs.to_csv(OUT / "runs.csv", index=False)
    inv.to_csv(OUT / "investigations.csv", index=False)
    pubs.to_csv(OUT / "publications.csv", index=False)
    return runs, inv, pubs


if __name__ == "__main__":
    runs, inv, pubs = build()
    print(f"{len(runs)} runs | {len(inv)} investigations | {len(pubs)} publications")
    print(runs.groupby(["investigation", "pillar"]).size().to_string())
