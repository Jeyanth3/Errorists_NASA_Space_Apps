from firewise import assistant


def test_parse_lunar_question():
    q = assistant.parse("How flammable is PMMA in a lunar habitat at 30% oxygen and 10.2 psi?")
    assert q.goal == "prevention" and q.material == "PMMA"
    assert abs(q.o2_fraction - 0.30) < 1e-9 and abs(q.pressure_kpa - 70.3) < 0.1
    assert q.gravity_g > 0.1


def test_parse_goals():
    assert assistant.parse("smoke detector response to Teflon").goal == "detection"
    assert assistant.parse("does CO2 extinguish droplet flames").goal == "suppression"


def test_answer_has_sources_and_caveats():
    a = assistant.answer("Would a fabric fire spread in a Mars base?", use_llm=False)
    assert a["caveats"], "partial-gravity question must carry a caveat"
    assert all("psi_ids" in f for f in a["facts"])
