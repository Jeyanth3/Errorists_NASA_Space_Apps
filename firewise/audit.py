"""Data reliability checks: metadata conflicts + per-column completeness."""
import json

import pandas as pd

from firewise import data

ROOT = data.ROOT


def metadata_conflicts():
    """Conflicts we found while reading PSI. Original value is kept, nothing is overwritten."""
    meta = {p.stem: json.loads(p.read_text()) for p in (ROOT / "data/raw/psi/meta").glob("PSI-*.json")}
    rows = []
    s1 = meta.get("PSI-98", {})
    rows.append({
        "psi_id": "PSI-98", "field": "investigationStartDate / EndDate",
        "nasa_value": f"{s1.get('investigationStartDate', '')} - {s1.get('investigationEndDate', '')}",
        "conflicting_evidence": "Hardware field and description say Saffire-I flew in a Cygnus vehicle; "
                                "Saffire-I burned in June 2016 after Cygnus OA-6 left the ISS.",
        "proposed": "2016 (flight date)", "status": "needs team verification"})
    rows.append({
        "psi_id": "PSI-98", "field": "Experimental table: Sample Length / Width (cm)",
        "nasa_value": "Length 40.6, Width 94",
        "conflicting_evidence": "Saffire-III table lists the same sample size as Length 94, Width 40.6.",
        "proposed": "Length 94, Width 40.6", "status": "likely swapped columns"})
    rows.append({
        "psi_id": "PSI-98 / PSI-100", "field": "Sample Thickness",
        "nasa_value": "0.37 cm / .33 cm",
        "conflicting_evidence": "Saffire-II lists the same SIBAL fabric as 0.37 mm (written '037 mm').",
        "proposed": "0.37 mm / 0.33 mm", "status": "unit suspect - kept as reported, flagged"})
    rows.append({
        "psi_id": "PSI-69", "field": "Burning rate; mm",
        "nasa_value": "header unit 'mm'",
        "conflicting_evidence": "Droplet burning-rate constant K is a d^2-law slope in mm^2/s (FLEX publications).",
        "proposed": "mm^2/s", "status": "unit corrected in display, raw kept"})
    rows.append({
        "psi_id": "PSI-25 / PSI-26", "field": "investigation naming",
        "nasa_value": "PSI-25 = BASS-II, PSI-26 = BASS",
        "conflicting_evidence": "Several third-party summaries swap the two ids.",
        "proposed": "follow PSI", "status": "verified against PSI metadata"})
    rows.append({
        "psi_id": "PSI-99", "field": "Experimental table: Material",
        "nasa_value": "blank for samples 2-6 and 2-9",
        "conflicting_evidence": "Rows sit directly below SIBAL (2-5) and PMMA (2-8) rows of identical size.",
        "proposed": "carry material down", "status": "inferred, flagged on the run"})
    df = pd.DataFrame(rows)
    out = ROOT / "data/audits/metadata_conflicts.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out, index=False)
    return df


KEY_FIELDS = ["fuel", "o2_fraction", "pressure_kpa", "flow_cm_s", "outcome", "burn_time_s",
              "spread_rate_mm_s", "thickness_mm", "diameter_mm"]


def completeness():
    r = data.runs()
    g = r.groupby("investigation")[KEY_FIELDS].apply(lambda d: d.notna().mean().round(2))
    return g


def flag_summary():
    r = data.runs()
    f = r.assign(flag=r["data_flags"].str.split(" | ", regex=False)).explode("flag")
    f = f[f["flag"].fillna("") != ""]
    return f.groupby(["investigation", "flag"]).size().reset_index(name="runs")


if __name__ == "__main__":
    print(metadata_conflicts().to_string())
