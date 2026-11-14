import pytest

from firewise import units


def test_lunar_po2_matches_sea_level():
    # 30% O2 at 10.2 psi ~ 21.1 kPa, close to sea-level air (21.3 kPa)
    p = units.psi_to_kpa(10.2)
    assert p == pytest.approx(70.3, abs=0.1)
    assert units.o2_partial_kpa(0.30, p) == pytest.approx(21.1, abs=0.1)


def test_mmhg():
    assert units.mmhg_to_kpa(760) == pytest.approx(101.325, abs=0.01)


@pytest.mark.parametrize("raw,mm", [("0.37 mm", 0.37), (".33 cm", 3.3), ("100 micron", 0.1), ("29 cm", 290)])
def test_lengths(raw, mm):
    assert units.length_mm(raw) == pytest.approx(mm)


@pytest.mark.parametrize("raw,val", [("~ 21.5", 21.5), ("22.1 to 22.0", 22.05), ("21.5 - 21.7", 21.6), ("n/a", None)])
def test_messy_numbers(raw, val):
    got = units.range_mean(raw) if val is not None else units.first_number(raw)
    assert got == (pytest.approx(val) if val is not None else None)


def test_fraction():
    assert units.to_fraction(21) == 0.21
    assert units.to_fraction(0.34) == 0.34
