"""Margins report: for every graded value, report the distance to the
nearest trap boundary, proving no graded decision sits on an edge.

Covers per-row unit conversion, censor flags, tie order, zero rows, the
UCL exceedance rule, Cunnane positions, the stray-period roster, and the
edge branches. Boundaries that are the point (exact action level equality)
are noted, not measured.
"""
import importlib.util
import os
import sys

TASK = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(TASK, "solution"))
sys.path.insert(0, os.path.join(TASK, "tests"))
from test_outputs import check_rows  # noqa: F401  (pins the graded rows)
import solve

CASES = os.path.join(TASK, "tests", "graded")
VARIANTS = os.path.join(TASK, "authoring", "evidence", "ci_trials", "variants")


def cell(case, sid, period, cont, variant=None):
    if variant is None:
        rows = solve.solve_case(os.path.join(CASES, case))
    else:
        spec = importlib.util.spec_from_file_location(
            variant, os.path.join(VARIANTS, variant + ".py"))
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        rows = mod.solve_case(os.path.join(CASES, case))
    for r in rows:
        if (r["system_id"], r["period"], r["contaminant"]) == (sid, period, cont):
            return r
    raise KeyError((case, sid, period, cont))


def main():
    notes = []
    r = cell("graded_01", "PWS101", "202403", "LEAD")
    v = cell("graded_01", "PWS101", "202403", "LEAD",
             variant="v01_no_unit_conversion")
    notes.append("g1 per-row units p90 %s ucl %s vs no-conversion p90 %s ucl %s: "
                 "ucl margin %.4f (%.0fx tol)"
                 % (r["p90_mg_per_L"], r["ucl95_mg_per_L"],
                    v["p90_mg_per_L"], v["ucl95_mg_per_L"],
                    abs(float(v["ucl95_mg_per_L"]) - float(r["ucl95_mg_per_L"])),
                    abs(float(v["ucl95_mg_per_L"]) - float(r["ucl95_mg_per_L"])) / 0.0001))
    r = cell("graded_02", "PWS102", "202404", "LEAD")
    v = cell("graded_02", "PWS102", "202404", "LEAD",
             variant="v02_censor_flags_ignored")
    notes.append("g2 censor flags p90 %s ucl %s %s vs all-detect p90 %s ucl %s %s: "
                 "ucl margin %.4f (%.0fx tol), finding flips"
                 % (r["p90_mg_per_L"], r["ucl95_mg_per_L"], r["exceedance"],
                    v["p90_mg_per_L"], v["ucl95_mg_per_L"], v["exceedance"],
                    abs(float(v["ucl95_mg_per_L"]) - float(r["ucl95_mg_per_L"])),
                    abs(float(v["ucl95_mg_per_L"]) - float(r["ucl95_mg_per_L"])) / 0.0001))
    r = cell("graded_03", "PWS103", "202405", "LEAD")
    v = cell("graded_03", "PWS103", "202405", "LEAD",
             variant="v03_tie_censored_above")
    notes.append("g3 tie order p90 %s ucl %s vs censored-above p90 %s ucl %s: "
                 "p90 margin %.4f (%.0fx tol)"
                 % (r["p90_mg_per_L"], r["ucl95_mg_per_L"],
                    v["p90_mg_per_L"], v["ucl95_mg_per_L"],
                    abs(float(v["p90_mg_per_L"]) - float(r["p90_mg_per_L"])),
                    abs(float(v["p90_mg_per_L"]) - float(r["p90_mg_per_L"])) / 0.0001))
    r = cell("graded_04", "PWS104", "202406", "LEAD")
    v = cell("graded_04", "PWS104", "202406", "LEAD",
             variant="v04_zero_rows_dropped")
    notes.append("g4 zero rows n=%s ucl %s %s vs dropped n=%s ucl %s %s: "
                 "ucl margin %.4f (%.0fx tol), finding flips"
                 % (r["n"], r["ucl95_mg_per_L"], r["exceedance"],
                    v["n"], v["ucl95_mg_per_L"], v["exceedance"],
                    abs(float(v["ucl95_mg_per_L"]) - float(r["ucl95_mg_per_L"])),
                    abs(float(v["ucl95_mg_per_L"]) - float(r["ucl95_mg_per_L"])) / 0.0001))
    r = cell("graded_05", "PWS105", "202407", "LEAD")
    notes.append("g5 ucl exceedance p90 %s below 0.010 with ucl %s above: "
                 "finding %s; p90 rule would say NO"
                 % (r["p90_mg_per_L"], r["ucl95_mg_per_L"], r["exceedance"]))
    r = cell("graded_06", "PWS106", "202407", "LEAD")
    notes.append("g6 all-censored reports minimum p90 %s ucl %s n=%s nc=%s"
                 % (r["p90_mg_per_L"], r["ucl95_mg_per_L"], r["n"], r["n_censored"]))
    r = cell("graded_06", "PWS106", "202408", "LEAD")
    v = cell("graded_06", "PWS106", "202408", "LEAD",
             variant="v06_censored_in_regression")
    notes.append("g6 lone detect p90 %s ucl %s vs censored-in-regression p90 %s ucl %s: "
                 "ucl margin %.4f (%.0fx tol)"
                 % (r["p90_mg_per_L"], r["ucl95_mg_per_L"],
                    v["p90_mg_per_L"], v["ucl95_mg_per_L"],
                    abs(float(v["ucl95_mg_per_L"]) - float(r["ucl95_mg_per_L"])),
                    abs(float(v["ucl95_mg_per_L"]) - float(r["ucl95_mg_per_L"])) / 0.0001))
    r = cell("graded_01", "PWS101", "202403", "LEAD")
    v = cell("graded_01", "PWS101", "202403", "LEAD",
             variant="v07_percentile_at_z95")
    notes.append("g1 percentile quantile p90 %s ucl %s vs z95 p90 %s ucl %s: "
                 "p90 margin %.4f (%.0fx tol)"
                 % (r["p90_mg_per_L"], r["ucl95_mg_per_L"],
                    v["p90_mg_per_L"], v["ucl95_mg_per_L"],
                    abs(float(v["p90_mg_per_L"]) - float(r["p90_mg_per_L"])),
                    abs(float(v["p90_mg_per_L"]) - float(r["p90_mg_per_L"])) / 0.0001))
    r = cell("graded_06", "PWS106", "202409", "LEAD")
    notes.append("g6 empty roster cell p90 %s ucl %s n=%s: blank value and ZINC "
                 "rows never count" % (r["p90_mg_per_L"], r["ucl95_mg_per_L"], r["n"]))
    r = cell("graded_05", "PWS105", "202407", "COPPER")
    notes.append("copper flat at 0.3 pins zero variance: ucl %s equals p90 %s"
                 % (r["ucl95_mg_per_L"], r["p90_mg_per_L"]))
    notes.append("equality at the action level is compliant by definition "
                 "(boundary is the point); graded cases avoid halfway rounding values")
    print("\n".join(notes))
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           "margins_report.txt"), "w") as f:
        f.write("\n".join(notes) + "\n")


if __name__ == "__main__":
    main()
