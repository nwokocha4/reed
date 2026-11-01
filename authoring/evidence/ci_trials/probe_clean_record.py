"""Blind probe B: representative agent attempt that applies the intuitive
clean record reading of reduced monitoring: an annual reduction needs no
prior exceedance. Expected: REWARD 0 on graded_06 schedule.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "..", "..", "solution"))
import solve as ref

_orig = ref.solve_case


def solve_case(case_dir):
    rows = _orig(case_dir)
    for r in rows:
        if r["schedule"] == "REDUCED_ANNUAL":
            r["schedule"] = "STANDARD_SEMIANNUAL"
    return rows


ref.solve_case = solve_case
ref.main()
