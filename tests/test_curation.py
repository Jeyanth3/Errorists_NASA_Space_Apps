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
    solids = r[r["investigation"].isin(["BASS", "BASS-II"])]
    assert solids["data_flags"].str.contains("pressure assumed").all()
