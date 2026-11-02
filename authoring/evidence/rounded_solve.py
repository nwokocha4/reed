"""Rounded intermediate run: wraps the reference so every converted
concentration is rounded to four places at creation, the way a hand
computation would carry it. Must still earn REWARD 1, proving the tolerance
bands admit sound work.
"""
import os
import sys
from decimal import Decimal, ROUND_HALF_UP

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "..", "solution"))
import solve as ref


def q4(x):
    return Decimal(str(x)).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)


_orig_to_mg = ref.to_mg


def to_mg(value, unit):
    return float(q4(_orig_to_mg(value, unit)))


ref.to_mg = to_mg
ref.main()
