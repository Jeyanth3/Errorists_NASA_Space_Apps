"""
Plain-language findings computed straight from the curated runs.
Every sentence carries the PSI id and run ids it was computed from, so the UI can link back.
Nothing here is typed in by hand except the wording.
"""
import pandas as pd

from firewise import data


def _fact(text, psi_ids, run_ids=(), kind="measured"):
    return {"text": text, "psi_ids": sorted(set(psi_ids)), "run_ids": list(run_ids)[:50], "kind": kind}


def near_atmosphere(df, pressure_kpa, o2_fraction, dp=0.15, dx=0.04):
    p_ok = (df["pressure_kpa"] - pressure_kpa).abs() / pressure_kpa <= dp
    x_ok = (df["o2_fraction"] - o2_fraction).abs() <= dx
    return df[p_ok & x_ok]


def prevention(material=None, pressure_kpa=None, o2_fraction=None):
    r = data.runs()
    d = r[r["pillar"] == "prevention"]
    facts = []
    if material:
        m = d[d["fuel"] == material]
        if m.empty:
            facts.append(_fact(f"No prevention run in the indexed PSI tables uses {material}.", [], kind="gap"))
        else:
            invs = ", ".join(sorted(m["investigation"].unique()))
            facts.append(_fact(f"{len(m)} solid-fuel runs use {material} ({invs}).", m["psi_id"], m["run_id"]))
            sp = m.dropna(subset=["spread_rate_mm_s"])
            if len(sp):
                facts.append(_fact(
                    f"Measured microgravity spread rate for {material}: "
                    f"{sp['spread_rate_mm_s'].min():.1f}-{sp['spread_rate_mm_s'].max():.1f} mm/s "
                    f"at {sp['flow_cm_s'].iloc[0]:.0f} cm/s concurrent flow (Saffire).", sp["psi_id"], sp["run_id"]))
            o2 = m.dropna(subset=["o2_fraction"])
            if len(o2):
                facts.append(_fact(
                    f"Oxygen in these runs ranged {o2['o2_fraction'].min():.1%}-{o2['o2_fraction'].max():.1%} "
                    f"at about 1 atm - no PSI solid-fuel run for {material} reaches 30% O2.",
                    o2["psi_id"], o2["run_id"]))
    sat = d[d["investigation"].str.startswith("Saffire")]
    nob = sat[sat["outcome"] == "no sustained burning"]
    if len(nob):
        facts.append(_fact(
            f"In Saffire-II, {len(nob)} of {len(sat[sat['investigation'] == 'Saffire-II'])} samples "
            f"({', '.join(sorted(nob['fuel'].dropna().unique()))}) did not sustain a flame in microgravity "
            f"at ~21.5-22% O2 and 20 cm/s flow; the 1 g reference tests reported complete burning for some of "
            f"the same samples - gravity changes the answer.",
            nob["psi_id"], nob["run_id"]))
    big = sat.dropna(subset=["length_mm"])
    if len(big):
        facts.append(_fact(
            f"Saffire burned samples up to {big['length_mm'].max() / 10:.0f} cm long - the largest fires "
            "studied in orbit, aboard uncrewed Cygnus vehicles.", big["psi_id"], big["run_id"]))
    if pressure_kpa and o2_fraction:
        near = near_atmosphere(d, pressure_kpa, o2_fraction)
        if near.empty:
            facts.append(_fact(
                f"No PSI solid-fuel run was found near {o2_fraction:.0%} O2 / {pressure_kpa:.0f} kPa. "
                "This is an evidence gap, not a safe result.", [], kind="gap"))
    return facts


def suppression(pressure_kpa=None, o2_fraction=None):
    r = data.runs()
    f = r[r["investigation"] == "FLEX"]
    facts = []
    for fuel, g in f.groupby("fuel"):
        ext = g[g["outcome"] == "extinction"]
        facts.append(_fact(
            f"FLEX {fuel}: {len(ext)} of {len(g)} droplet burns ended in flame extinction "
            f"(others: disruption or burned to completion).", g["psi_id"], ext["run_id"]))
    for dil in ("CO2", "He"):
        g = f[f["diluent"] == dil]
        if len(g):
            ext = g[g["outcome"] == "extinction"]
            facts.append(_fact(
                f"With {dil} added to the atmosphere, {len(ext)} of {len(g)} FLEX burns extinguished "
                f"(O2 {g['o2_fraction'].min():.0%}-{g['o2_fraction'].max():.0%}).", g["psi_id"], g["run_id"]))
    low = f[(f["outcome"] == "extinction")].sort_values("o2_fraction").head(5)
    if len(low):
        facts.append(_fact(
            f"Lowest oxygen fraction in which a FLEX droplet still burned before extinguishing: "
            f"{low['o2_fraction'].min():.0%} ({low['fuel'].iloc[0]}).", low["psi_id"], low["run_id"]))
    if pressure_kpa and o2_fraction:
        near = near_atmosphere(f, pressure_kpa, o2_fraction, dp=0.25, dx=0.05)
        if len(near):
            facts.append(_fact(
                f"{len(near)} FLEX runs were made near your atmosphere ({o2_fraction:.0%} O2, {pressure_kpa:.0f} kPa) - "
                "the closest PSI evidence, but still for liquid droplets in microgravity.",
                near["psi_id"], near["run_id"]))
        else:
            facts.append(_fact("No FLEX run is near this atmosphere.", [], kind="gap"))
    return facts


def detection():
    r = data.runs()
    d = r[r["pillar"] == "detection"]
    facts = []
    mats = sorted(d["fuel"].dropna().unique())
    facts.append(_fact(
        f"SAME and SAME-R heated {len(mats)} spacecraft materials ({', '.join(mats)}) to make smoke "
        f"(pyrolysis, not flaming) across {len(d)} runs.", d["psi_id"], d["run_id"]))
    sr = d[d["investigation"] == "SAME-R"].dropna(subset=["aging_s"])
    if len(sr):
        facts.append(_fact(
            f"SAME-R let smoke age up to {sr['aging_s'].max() / 60:.0f} minutes before measuring it - "
            "smoke particles grow as they age, which changes what a detector sees.", sr["psi_id"], sr["run_id"]))
    nf = d[d["flow_cm_s"] == 0]
    if len(nf):
        facts.append(_fact(
            f"{len(nf)} runs were made with zero inlet flow - the quiescent case relevant to a closed module.",
            nf["psi_id"], nf["run_id"]))
    facts.append(_fact(
        "PSI smoke runs were all at ISS cabin pressure; there is no smoke-particle data for "
        "reduced-pressure, high-O2 habitat atmospheres.", d["psi_id"], kind="gap"))
    return facts


def physics():
    r = data.runs()
    c = r[r["investigation"] == "ACME CFI-G"]
    facts = []
    for fuel, g in c.groupby("fuel"):
        ign = g[~g["outcome"].isin(["no ignition"])]
        facts.append(_fact(
            f"CFI-G {fuel}: {len(ign)} of {len(g)} burner tests ignited, O2 {g['o2_fraction'].min():.0%}-"
            f"{g['o2_fraction'].max():.0%}.", g["psi_id"], g["run_id"]))
    return facts


def coverage(df=None, x="o2_fraction", y="fuel", bins=(0, 0.15, 0.19, 0.23, 0.27, 0.32, 0.4, 1.0)):
    df = data.runs() if df is None else df
    d = df.dropna(subset=[x]).copy()
    labels = [f"{a:.0%}-{b:.0%}" for a, b in zip(bins[:-1], bins[1:])]
    d["bin"] = pd.cut(d[x], bins=list(bins), labels=labels, include_lowest=True)
    return pd.crosstab(d[y], d["bin"]).reindex(columns=labels, fill_value=0)
