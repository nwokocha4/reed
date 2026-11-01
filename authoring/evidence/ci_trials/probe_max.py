"""Blind probe A: representative agent attempt that reads the five sample
branch as a plain ceiling rank. Keeps the maximum at n=5 instead of
averaging the two highest. Expected: REWARD 0 on graded_01.
"""
import os
import sys
from decimal import Decimal

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "..", "..", "solution"))
import solve as ref

_orig = ref.percentile_value


def percentile_value(items):
    n = len(items)
    if n == 0:
        return Decimal("0.0000"), 0
    ordered = sorted(items, key=lambda t: (t[1], t[0]["site_id"],
                                           t[0]["collection_date"]))
    concs = [c for _, c in ordered]
    import math
    raw = concs[int(math.ceil(n * 0.9)) - 1]
    return raw.quantize(Decimal("0.0001")), n


ref.percentile_value = percentile_value
ref.main()
