"""Graded checks for the censored-data ROS estimation task (pytest entry).

Each graded case is staged fresh under /app, the submitted /app/solve.py is
run as an unprivileged user, and every output row is keyed by
(system_id, period, contaminant), order free. p90 and UCL95 must each match
within 1e-4; every other column must match exactly. check_rows is also
imported by the authoring evidence scorer, so keep it dependency free.
"""
import csv
import json
import os

import pytest

from conftest import EXPECTED_PATH, GRADED_DIR, OUTPUT_DIR, run_case

TOL = 1e-4
HEADER = ["system_id", "period", "contaminant", "n", "n_censored",
          "p90_mg_per_L", "ucl95_mg_per_L", "exceedance"]


def _key(r):
    return (r.get("system_id", ""), r.get("period", ""), r.get("contaminant", ""))


def check_rows(got, exp_rows):
    """Compare output rows against expected rows. Returns a detail string."""
    exp = {_key(r): r for r in exp_rows}
    seen = {}
    for r in got:
        key = _key(r)
        if key in seen:
            raise AssertionError("duplicated key %r" % (key,))
        seen[key] = r
        if key not in exp:
            raise AssertionError("unknown key %r" % (key,))
        e = exp[key]
        for col in ("p90_mg_per_L", "ucl95_mg_per_L"):
            try:
                gv = float(r[col])
                ev = float(e[col])
            except (ValueError, TypeError):
                raise AssertionError("nonnumeric %s for %r" % (col, key))
            if abs(gv - ev) > TOL:
                raise AssertionError(
                    "%s miss for %r: got %s want %s" % (col, key, gv, ev))
        for col in ("n", "n_censored", "exceedance"):
            if r.get(col, "") != e[col]:
                raise AssertionError(
                    "%s mismatch for %r: got %r want %r"
                    % (col, key, r.get(col), e[col]))
    missing = set(exp) - set(seen)
    if missing:
        raise AssertionError("missing rows %r" % sorted(missing))
    return "ok (%d rows)" % len(exp)


def _header_ok(case):
    path = os.path.join(OUTPUT_DIR, "%s_estimate.csv" % case)
    with open(path, newline="", encoding="utf-8-sig") as f:
        header = next(csv.reader(f))
    assert header == HEADER, "header mismatch in %s: %r" % (case, header)


def _cases():
    return sorted(d for d in os.listdir(GRADED_DIR)
                  if os.path.isdir(os.path.join(GRADED_DIR, d)))


def _expected():
    with open(EXPECTED_PATH, encoding="utf-8") as f:
        return json.load(f)


@pytest.mark.parametrize("case", _cases())
def test_case(case):
    rows = run_case(case)
    _header_ok(case)
    check_rows(rows, _expected()[case])
