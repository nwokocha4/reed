"""Rounded intermediate run: wraps the reference so every Decimal value is
rounded to four places at creation, the way a hand computation would carry
it. Must still earn REWARD 1, proving the tolerance bands admit sound work.
"""
import os
import sys
from decimal import Decimal, ROUND_HALF_UP

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "..", "solution"))
import solve as ref


def q4(x):
    return Decimal(x).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)


_orig_to_mg = ref.to_mg


def to_mg(value, unit):
    return q4(_orig_to_mg(value, unit))


_orig_norm = ref.norm_concentration


def norm_concentration(value, unit, qualifier):
    return q4(_orig_norm(value, unit, qualifier))


ref.to_mg = to_mg
ref.norm_concentration = norm_concentration

_orig_percentile = ref.percentile_value


def percentile_value(items):
    items = [(r, q4(c)) for r, c in items]
    n = len(items)
    if n == 0:
        return Decimal("0.0000"), 0
    ordered = sorted(items, key=lambda t: (t[1], t[0]["site_id"],
                                           t[0]["collection_date"]))
    concs = [c for _, c in ordered]
    if n < 5:
        raw = q4(concs[-1])
    elif n == 5:
        raw = q4((concs[-1] + concs[-2]) / Decimal(2))
    else:
        import math
        raw = q4(concs[int(math.ceil(n * 0.9)) - 1])
    return raw.quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP), n


ref.percentile_value = percentile_value
ref.main()
