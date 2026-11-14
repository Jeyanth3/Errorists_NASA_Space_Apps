"""Small unit helpers. Kept dependency-free on purpose (pint felt like overkill here)."""
import math
import re

PSI_TO_KPA = 6.894757
MMHG_TO_KPA = 0.1333224
BAR_TO_KPA = 100.0
ATM_KPA = 101.325
G0 = 9.80665  # m/s^2

GRAVITY = {
    "microgravity": 0.0,
    "moon": 0.1654,
    "mars": 0.3794,
    "earth": 1.0,
}


def psi_to_kpa(p):
    return p * PSI_TO_KPA


def mmhg_to_kpa(p):
    return p * MMHG_TO_KPA


def o2_partial_kpa(o2_fraction, total_kpa):
    """Dalton's law: pO2 = X_O2 * P."""
    if o2_fraction is None or total_kpa is None:
        return None
    return o2_fraction * total_kpa


def to_fraction(v):
    """Accept 0.21 or 21 (percent) and return a mole fraction."""
    if v is None or (isinstance(v, float) and math.isnan(v)):
        return None
    v = float(v)
    return v / 100.0 if v > 1.0 else v


_num = re.compile(r"[-+]?\d*\.?\d+")


def first_number(text):
    """Pull the first number out of messy table cells like '~ 21.5', '0.37 mm', '22.1 to 22.0'."""
    if text is None:
        return None
    if isinstance(text, (int, float)):
        return None if (isinstance(text, float) and math.isnan(text)) else float(text)
    s = str(text).strip()
    if not s or s.lower() in {"n/a", "na", "none", "-", "?"}:
        return None
    m = _num.search(s.replace(",", ""))
    return float(m.group()) if m else None


def length_mm(text):
    """'0.37 mm' -> 0.37, '.33 cm' -> 3.3, '100 micron' -> 0.1, bare number -> as given."""
    v = first_number(text)
    if v is None:
        return None
    s = str(text).lower()
    if "micron" in s or "µm" in s or "um " in s:
        return v / 1000.0
    if "cm" in s:
        return v * 10.0
    return v


def range_mean(text):
    """'22.1 to 22.0' or '21.5 - 21.7' -> mean, else first number."""
    if text is None:
        return None
    nums = [float(x) for x in _num.findall(str(text))]
    if not nums:
        return None
    if len(nums) >= 2 and ("to" in str(text) or " - " in str(text)):
        return sum(nums[:2]) / 2
    return nums[0]
