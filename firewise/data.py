"""Loading helpers shared by the app, the engine and the tests."""
from functools import lru_cache
from pathlib import Path

import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parents[1]
CURATED = ROOT / "data" / "curated"


@lru_cache(maxsize=1)
def runs():
    df = pd.read_csv(CURATED / "runs.csv")
    df["data_flags"] = df["data_flags"].fillna("")
    return df


@lru_cache(maxsize=1)
def investigations():
    return pd.read_csv(CURATED / "investigations.csv").fillna("")


@lru_cache(maxsize=1)
def publications():
    return pd.read_csv(CURATED / "publications.csv").fillna("")


@lru_cache(maxsize=1)
def missions():
    with open(ROOT / "configs" / "missions.yaml") as fh:
        return yaml.safe_load(fh)


@lru_cache(maxsize=1)
def earth_links():
    with open(ROOT / "configs" / "earth_benefits.yaml") as fh:
        return yaml.safe_load(fh)
