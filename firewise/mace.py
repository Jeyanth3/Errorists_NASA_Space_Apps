"""
MACE - Mission-Aware, Condition-constrained Evidence ranking.

Given a mission question Q = (mission, safety goal, material, conditions, outcome),
every NASA run gets three separate scores instead of one "relevance %":

  relevance      does this experiment study the thing we asked about?
  applicability  how close are its physical conditions to the mission?
  quality        how much of it was actually measured (vs assumed / missing)?

and one evidence level:

  DIRECT        same safety question, same gravity regime, conditions match
  SUPPORTING    right question, but at least one condition differs
  EXTRAPOLATED  gravity regime differs AND the atmosphere differs - any use
                of it for the mission is an extrapolation, never a measurement

The comparison certificate lists every check so a person can see *why*.
All rules are plain code below; no language model decides a level.
"""
import math
from dataclasses import dataclass, field

import pandas as pd

from firewise import data

# --- tolerances (kept simple and visible on purpose) -------------------------
PO2_MATCH, PO2_NEAR = 2.5, 6.0          # kPa
XO2_MATCH, XO2_NEAR = 0.025, 0.06       # mole fraction
P_MATCH, P_NEAR = 0.10, 0.30            # relative difference in total pressure

PILLARS = ("prevention", "detection", "suppression")
# combustion-physics data can *support* prevention/suppression questions, never detection
SUPPORTS = {"combustion physics": {"prevention": 0.45, "suppression": 0.45, "detection": 0.0}}

OUTCOME_VARS = {
    "prevention": ["spread_rate_mm_s", "burn_time_s", "outcome", "o2_fraction"],
    "detection": ["aging_s", "flow_cm_s", "weight_loss_mg_min", "heater_ratio"],
    "suppression": ["outcome", "extinction_diameter_mm", "burning_rate_k", "co2_fraction", "he_fraction"],
}


@dataclass
class Query:
    goal: str                      # prevention | detection | suppression
    gravity_g: float = 0.0
    pressure_kpa: float = 101.3
    o2_fraction: float = 0.21
    material: str | None = None    # family name as in runs.csv, or None
    mission_name: str = "custom"
    text: str = ""

    @property
    def po2_kpa(self):
        return self.o2_fraction * self.pressure_kpa


@dataclass
class Check:
    name: str
    target: str
    evidence: str
    status: str          # match | near | mismatch | unknown
    note: str = ""


@dataclass
class Assessment:
    run_id: str
    investigation: str
    psi_id: str
    level: str
    relevance: float
    applicability: float
    quality: float
    checks: list = field(default_factory=list)

    @property
    def score(self):
        # used only to order runs *inside* a level
        return round(0.45 * self.relevance + 0.35 * self.applicability + 0.20 * self.quality, 4)


def query_from_mission(key, goal, material=None, **override):
    m = data.missions()[key]
    q = Query(goal=goal, gravity_g=m["gravity_g"], pressure_kpa=m["pressure_kpa"],
              o2_fraction=m["o2_fraction"], material=material, mission_name=m["name"])
    for k, v in override.items():
        setattr(q, k, v)
    return q


def _isnum(v):
    """True for a real number (not None / NaN / text)."""
    if isinstance(v, bool) or not isinstance(v, (int, float)):
        return False
    return not math.isnan(v)


def _missing(v):
    return v is None or (isinstance(v, float) and math.isnan(v)) or str(v).strip() == ""


def _gravity_label(g):
    if g < 0.01:
        return "microgravity"
    if abs(g - 0.165) < 0.03:
        return "lunar (0.165 g)"
    if abs(g - 0.38) < 0.04:
        return "martian (0.38 g)"
    if abs(g - 1) < 0.05:
        return "Earth (1 g)"
    return f"{g:.2f} g"


def compare(run, q):
    """Build the condition certificate for one run against one query."""
    checks = []
    flags = str(run.get("data_flags") or "")

    # gravity
    rg = run.get("gravity_g", 0.0) or 0.0
    same_g = abs(rg - q.gravity_g) < 0.01
    checks.append(Check(
        "Gravity", _gravity_label(q.gravity_g), _gravity_label(rg),
        "match" if same_g else "mismatch",
        "" if same_g else "Results cannot be interpolated between 0 g and 1 g - buoyancy changes the "
                          "flow around a flame non-linearly. Treat as context only."))

    # oxygen partial pressure, the main driver of flame chemistry
    po2 = run.get("po2_kpa")
    if _isnum(po2):
        d = abs(po2 - q.po2_kpa)
        st = "match" if d <= PO2_MATCH else "near" if d <= PO2_NEAR else "mismatch"
        checks.append(Check("O2 partial pressure", f"{q.po2_kpa:.1f} kPa", f"{po2:.1f} kPa", st,
                            "pressure assumed (cabin)" if "pressure assumed" in flags else ""))
    else:
        checks.append(Check("O2 partial pressure", f"{q.po2_kpa:.1f} kPa", "not reported", "unknown"))

    # oxygen fraction - matters separately (dilution, heat capacity)
    x = run.get("o2_fraction")
    if _isnum(x):
        d = abs(x - q.o2_fraction)
        st = "match" if d <= XO2_MATCH else "near" if d <= XO2_NEAR else "mismatch"
        checks.append(Check("O2 fraction", f"{q.o2_fraction:.0%}", f"{x:.1%}", st))
    else:
        checks.append(Check("O2 fraction", f"{q.o2_fraction:.0%}", "not reported", "unknown"))

    # total pressure
    p = run.get("pressure_kpa")
    if _isnum(p):
        rel = abs(p - q.pressure_kpa) / q.pressure_kpa
        st = "match" if rel <= P_MATCH else "near" if rel <= P_NEAR else "mismatch"
        note = "assumed cabin pressure, not measured" if "pressure assumed" in flags else ""
        checks.append(Check("Total pressure", f"{q.pressure_kpa:.1f} kPa", f"{p:.1f} kPa", st, note))
    else:
        checks.append(Check("Total pressure", f"{q.pressure_kpa:.1f} kPa", "not reported", "unknown"))

    # material
    if q.material:
        fam = run.get("fuel")
        if fam == q.material:
            st, note = "match", ""
        elif _missing(fam):
            st, note = "unknown", ""
        else:
            same_state = _state_of(q.material) == run.get("fuel_state")
            st = "near" if same_state else "mismatch"
            note = "same fuel state, different material" if same_state else "different fuel state (solid/liquid/gas)"
        checks.append(Check("Material", q.material, "n/a" if _missing(fam) else str(fam), st, note))

    # diluent (only meaningful for suppression)
    if q.goal == "suppression" and _isnum(run.get("co2_fraction")):
        dil = run.get("diluent", "N2")
        label = {"N2": "N2 (ordinary air balance)", "CO2": "CO2 added", "He": "He added"}.get(dil, dil)
        checks.append(Check("Diluent / suppressant", "any", label, "match",
                            "CO2 and He are suppressant-like diluents tested in FLEX"))

    if "burner mixtures" in flags:
        checks.append(Check("Atmosphere type", "habitable cabin", "burner test mixture", "mismatch",
                            "CFI-G oxygen levels are burner settings, not crew atmospheres"))
    return checks


def _state_of(material):
    r = data.runs()
    s = r.loc[r["fuel"] == material, "fuel_state"]
    return s.iloc[0] if len(s) else None


def _relevance(run, q, text_score=0.0):
    pillar = run["pillar"]
    if pillar == q.goal:
        base = 1.0
    else:
        base = SUPPORTS.get(pillar, {}).get(q.goal, 0.1)
    mat = 0.0
    if q.material:
        mat = 1.0 if run.get("fuel") == q.material else (0.4 if run.get("fuel_state") == _state_of(q.material) else 0.0)
    w_mat = 0.2 if q.material else 0.0
    return round((0.75 - w_mat) * base + w_mat * mat + 0.25 * text_score, 4)


_STATUS_SCORE = {"match": 1.0, "near": 0.6, "mismatch": 0.15, "unknown": 0.4}


def _applicability(checks):
    if not checks:
        return 0.0
    weights = {"Gravity": 2.0, "O2 partial pressure": 2.0, "O2 fraction": 1.0, "Total pressure": 1.0,
               "Material": 1.5, "Atmosphere type": 1.5, "Diluent / suppressant": 0.5}
    num = sum(weights.get(c.name, 1.0) * _STATUS_SCORE[c.status] for c in checks)
    den = sum(weights.get(c.name, 1.0) for c in checks)
    return round(num / den, 4)


def _quality(run, goal):
    vars_ = OUTCOME_VARS[goal] if run["pillar"] == goal else ["outcome", "burn_time_s"]
    have = sum(1 for v in vars_ if not _missing(run.get(v)))
    q = have / len(vars_)
    flags = str(run.get("data_flags") or "")
    penalty = 0.05 * flags.count("inferred") + 0.05 * flags.count("suspect") + 0.03 * flags.count("assumed")
    return round(max(0.0, min(1.0, 0.25 + 0.75 * q - penalty)), 4)


def _level(checks, relevance_pillar_ok):
    st = {c.name: c.status for c in checks}
    gravity_bad = st.get("Gravity") == "mismatch"
    atm_bad = any(st.get(k) == "mismatch" for k in ("O2 partial pressure", "O2 fraction", "Total pressure", "Atmosphere type"))
    any_off = any(s in ("mismatch", "near") for s in st.values())
    if not relevance_pillar_ok:
        return "EXTRAPOLATED" if (gravity_bad or atm_bad) else "SUPPORTING"
    if gravity_bad and atm_bad:
        return "EXTRAPOLATED"
    if not any_off and "unknown" not in (st.get("O2 partial pressure"), st.get("Gravity")):
        return "DIRECT"
    return "SUPPORTING"


LEVEL_ORDER = {"DIRECT": 0, "SUPPORTING": 1, "EXTRAPOLATED": 2}


def assess(q, runs=None, text_scores=None):
    """Score every run. Returns a DataFrame sorted by level then score."""
    runs = data.runs() if runs is None else runs
    text_scores = text_scores or {}
    out = []
    for _, r in runs.iterrows():
        run = r.to_dict()
        if run["pillar"] != q.goal and SUPPORTS.get(run["pillar"], {}).get(q.goal, 0) == 0:
            continue  # e.g. smoke data is not evidence for a flame-spread question
        checks = compare(run, q)
        rel = _relevance(run, q, text_scores.get(run["psi_id"], 0.0))
        a = Assessment(run["run_id"], run["investigation"], run["psi_id"],
                       _level(checks, run["pillar"] == q.goal), rel, _applicability(checks), _quality(run, q.goal), checks)
        out.append(a)
    if not out:
        return pd.DataFrame()
    df = pd.DataFrame([{
        "run_id": a.run_id, "investigation": a.investigation, "psi_id": a.psi_id, "level": a.level,
        "relevance": a.relevance, "applicability": a.applicability, "quality": a.quality, "score": a.score,
        "checks": a.checks,
    } for a in out])
    df["_lvl"] = df["level"].map(LEVEL_ORDER)
    return df.sort_values(["_lvl", "score"], ascending=[True, False]).drop(columns="_lvl").reset_index(drop=True)


def rank_investigations(assessed):
    """Roll run scores up to investigation level."""
    if assessed.empty:
        return assessed
    g = assessed.groupby(["psi_id", "investigation"])
    df = g.agg(
        runs=("run_id", "count"),
        best_level=("level", lambda s: min(s, key=LEVEL_ORDER.get)),
        relevance=("relevance", "max"),
        applicability=("applicability", lambda s: s.nlargest(5).mean()),
        quality=("quality", "mean"),
        direct=("level", lambda s: (s == "DIRECT").sum()),
        supporting=("level", lambda s: (s == "SUPPORTING").sum()),
        extrapolated=("level", lambda s: (s == "EXTRAPOLATED").sum()),
    ).reset_index()
    df["_lvl"] = df["best_level"].map(LEVEL_ORDER)
    df["score"] = (0.45 * df["relevance"] + 0.35 * df["applicability"] + 0.20 * df["quality"]).round(3)
    return df.sort_values(["_lvl", "score"], ascending=[True, False]).drop(columns="_lvl").reset_index(drop=True)


def certificate_table(checks):
    icon = {"match": "✅ match", "near": "🟡 close", "mismatch": "❌ differs", "unknown": "❔ not reported"}
    return pd.DataFrame([{"Check": c.name, "Mission": c.target, "NASA run": c.evidence,
                          "Status": icon[c.status], "Why it matters": c.note} for c in checks])
