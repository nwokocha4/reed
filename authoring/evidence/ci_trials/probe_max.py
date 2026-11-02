"""Blind probe A: representative agent attempt that reads every value as
mg/L and skips unit conversion. Expected: REWARD 0 on graded_01.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "..", "..", "solution"))
import solve as ref

_orig = ref.to_mg


def to_mg(value, unit):
    return float(str(value).strip())


ref.to_mg = to_mg
ref.main()
