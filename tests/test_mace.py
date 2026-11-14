from firewise import mace


def levels(q):
    return set(mace.assess(q)["level"])


def test_lunar_never_direct():
    # PSI has no partial-gravity data: nothing may be DIRECT for the Moon
    for goal in ("prevention", "detection", "suppression"):
        q = mace.query_from_mission("lunar_habitat", goal)
        assert "DIRECT" not in levels(q)


def test_iss_has_direct_evidence():
    q = mace.query_from_mission("iss", "suppression")
    assert "DIRECT" in levels(q)


def test_smoke_data_not_used_for_flame_questions():
    a = mace.assess(mace.query_from_mission("iss", "prevention"))
    assert not a["investigation"].isin(["SAME", "SAME-R"]).any()


def test_burner_data_is_only_context():
    a = mace.assess(mace.query_from_mission("iss", "prevention"))
    assert (a.loc[a["investigation"] == "ACME CFI-G", "level"] == "EXTRAPOLATED").all()


def test_material_mismatch_downgrades():
    a = mace.assess(mace.query_from_mission("iss", "prevention", "PMMA")).set_index("run_id")
    silicone = a.loc[a.index.str.startswith("SAFFIRE-II-2-1")]
    assert (silicone["level"] != "DIRECT").all()


def test_certificate_lists_gravity():
    q = mace.query_from_mission("mars_habitat", "prevention")
    first = mace.assess(q).iloc[0]
    names = [c.name for c in first["checks"]]
    assert "Gravity" in names
    assert next(c for c in first["checks"] if c.name == "Gravity").status == "mismatch"


def test_scores_bounded():
    a = mace.assess(mace.query_from_mission("exploration_atm", "suppression"))
    for col in ("relevance", "applicability", "quality"):
        assert a[col].between(0, 1).all()
