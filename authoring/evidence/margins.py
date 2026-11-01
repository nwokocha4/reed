"""Margins report: for every graded value, report the distance to the
nearest trap boundary, proving no graded decision sits on an edge.

Covers the five sample average against the maximum, the small count
maximum against the nearest rank, tier displacement, pair selection, the
invalidation on off switch, the schedule convention, and the reduced
minimum boundary. Boundaries that are the point (exact action level
equality) are noted, not measured.
"""
import os
import sys

TASK = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(TASK, "solution"))
sys.path.insert(0, os.path.join(TASK, "tests"))
from test_outputs import check_rows  # noqa: F401  (pins the graded rows)
import solve

CASES = os.path.join(TASK, "tests", "graded")


def cell(case, sid, period, cont):
    rows = solve.solve_case(os.path.join(CASES, case))
    for r in rows:
        if (r["system_id"], r["period"], r["contaminant"]) == (sid, period, cont):
            return r
    raise KeyError((case, sid, period, cont))


def main():
    notes = []
    r = cell("graded_01", "PWS101", "202403", "LEAD")
    got, alt = float(r["percentile_mg_per_L"]), 0.0110
    notes.append("g1 five sample avg %s vs max %.4f: margin %.4f (%.0fx tol)"
                 % (r["percentile_mg_per_L"], alt, abs(got - alt),
                    abs(got - alt) / 0.0001))
    r = cell("graded_02", "PWS102", "202404", "LEAD")
    notes.append("g2 max of three %s vs required minimum 10: shortfall 7 samples"
                 % r["percentile_mg_per_L"])
    r = cell("graded_03", "PWS103", "202405", "LEAD")
    got, alt = float(r["percentile_mg_per_L"]), 0.0280
    notes.append("g3 tier kept %s vs unfiltered %.4f: margin %.4f (%.0fx tol)"
                 % (r["percentile_mg_per_L"], alt, abs(got - alt),
                    abs(got - alt) / 0.0001))
    r = cell("graded_04", "PWS104", "202406", "LEAD")
    got, alt = float(r["percentile_mg_per_L"]), 0.0120
    notes.append("g4 fifth liter %s vs first liter mix %.4f: margin %.4f (%.0fx tol)"
                 % (r["percentile_mg_per_L"], alt, abs(got - alt),
                    abs(got - alt) / 0.0001))
    a = cell("graded_05", "PWS105", "202407", "LEAD")
    b = cell("graded_05", "PWS106", "202407", "LEAD")
    notes.append("g5 approved invalidation %s vs unapproved %s: margin %.4f (%.0fx tol)"
                 % (a["percentile_mg_per_L"], b["percentile_mg_per_L"],
                    abs(float(a["percentile_mg_per_L"]) - float(b["percentile_mg_per_L"])),
                    abs(float(a["percentile_mg_per_L"]) - float(b["percentile_mg_per_L"])) / 0.0001))
    r = cell("graded_06", "PWS107", "202403", "LEAD")
    notes.append("g6 schedule %s with prior exceedance Jan 0.0130: convention decides, "
                 "clean record reading would give STANDARD_SEMIANNUAL" % r["schedule"])
    r = cell("graded_06", "PWS107", "202403", "COPPER")
    notes.append("g6 copper %s vs action level 1.3: exceedance by %.4f"
                 % (r["percentile_mg_per_L"],
                    float(r["percentile_mg_per_L"]) - 1.3))
    notes.append("equality at the action level is compliant by definition "
                 "(boundary is the point); graded cases avoid halfway rounding values")
    print("\n".join(notes))
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           "margins_report.txt"), "w") as f:
        f.write("\n".join(notes) + "\n")


if __name__ == "__main__":
    main()
