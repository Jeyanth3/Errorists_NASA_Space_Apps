from firewise import data


def test_core_investigations_present():
    r = data.runs()
    for inv in ["BASS", "BASS-II", "Saffire-I", "Saffire-II", "Saffire-III", "SAME", "SAME-R", "FLEX", "ACME CFI-G"]:
        assert (r["investigation"] == inv).any(), inv


def test_run_ids_unique_and_traceable():
    r = data.runs()
    assert r["run_id"].is_unique
    assert r["source_file"].notna().all() and r["source_row"].notna().all()


def test_pillars_valid():
    assert set(data.runs()["pillar"]) <= {"prevention", "detection", "suppression", "combustion physics"}


def test_flex_values_sane():
    f = data.runs().query("investigation == 'FLEX'")
    assert f["o2_fraction"].between(0.1, 0.5).all()
    assert f["pressure_kpa"].dropna().between(20, 400).all()  # one run has no pressure in the NASA table
    assert set(f["outcome"].dropna()) <= {"extinction", "disruption", "completion"}


def test_assumptions_are_flagged():
    r = data.runs()
    solids = r[r["investigation"] == "BASS-II"]
    assert solids["data_flags"].str.contains("pressure assumed").all()
    bass = r[r["investigation"] == "BASS"].set_index("run_id")
    assert bass["notes"].str.contains("As Run_Test Matrix.xlsx", regex=False).all()
    assert not bass["data_flags"].str.contains("pressure assumed").any()
    assert bass.at["BASS-1-1", "o2_fraction"] == 0.221
    assert abs(bass.at["BASS-1-1", "pressure_kpa"] - 0.97 * 101.325) < 1e-8


def test_context_observations_are_excluded_from_run_counts():
    runs = data.runs()
    assert not runs["psi_id"].isin(["PSI-47", "PSI-68", "PSI-106", "PSI-107"]).any()
    cfi = runs[runs["psi_id"] == "PSI-39"]
    assert len(cfi) == 79
    assert cfi.loc[cfi["run_id"] == "CFI-1206", "pressure_kpa"].item() == 101.325


def test_conflicts_and_bounds_do_not_become_measurements():
    runs = data.runs().set_index("run_id")
    assert runs.loc[["SAMER-57"], "fuel"].isna().all()
    assert "Teflon at row 75" in runs.at["SAMER-57", "data_flags"]
    assert runs.loc[["SAFFIRE-II-2-7", "SAFFIRE-II-2-8"], "thickness_mm"].isna().all()
    assert runs.loc[["BASS2-M5"], "co_final_ppm"].isna().all()
