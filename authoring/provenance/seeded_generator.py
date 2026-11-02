"""Seeded graded/settled case generator for the censored-data ROS task.

Deterministic (fixed values, sequential sample ids). Writes cases under
cases/:
  settled_01, settled_02   no trap on display; settled_02 carries censored
                           and ug/L rows so the signed sheet exercises them
  graded_01 .. graded_06   one trap each, listed below

Every record lives in results.csv (single source). systems.csv is the roster.

  g1  unit conversion: lead reported in ug/L alongside mg/L copper; each row
      converts by its own unit (ug/L / 1000). A stray out-of-roster row must
      not count.
  g2  censor flags: U and <-qualified limits (plus J/B detects) are censored;
      treating every row as a detect flips the finding.
  g3  tie order: a censored limit ranks below a detect at the same value;
      ranking it above moves both graded values far beyond tolerance.
  g4  zeros count: value 0 (or below) is censored and stays in n; dropping
      zero rows flips the finding.
  g5  UCL exceedance: p90 sits below the action level while UCL95 sits above,
      so the finding is YES; judging by p90 alone says NO.
  g6  edge branches: an all-censored cell reports its minimum, a lone detect
      reports itself, n=1 reports its value, an empty roster cell reports
      0.0000; unparseable and off-contaminant rows never count.
"""
import csv
import os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cases")

HEADER_SYS = ["system_id", "period", "population_served"]
HEADER_RES = ["system_id", "site_id", "sample_id", "period", "contaminant", "liter",
              "value", "unit", "qualifier", "invalid_flag", "collection_date"]


def write_case(name, systems, results):
    d = os.path.join(OUT, name)
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, "systems.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=HEADER_SYS)
        w.writeheader()
        w.writerows(systems)
    with open(os.path.join(d, "results.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=HEADER_RES)
        w.writeheader()
        w.writerows(results)


sid_counter = [1000]


def nxt():
    sid_counter[0] += 1
    return sid_counter[0]


def mkres(sid, site, period, cont, value, unit="mg/L", qual="",
          inv="N", day="05"):
    return {"system_id": sid, "site_id": site,
            "sample_id": "S%05d" % nxt(), "period": period, "contaminant": cont,
            "liter": "NA", "value": str(value), "unit": unit, "qualifier": qual,
            "invalid_flag": inv, "collection_date": "%s-%s-%s" % (period[0:4], period[4:6], day)}


# ---------------------------------------------------------------- settled
def settled_cases():
    """Plain cells far from every trap boundary. settled_02 carries one
    U-qualified limit and one ug/L value so the signed sheet shows them."""

    sys_rows = [{"system_id": "PWS001", "period": "202401", "population_served": "2500"}]
    res = []
    for i, v in enumerate([0.002, 0.0025, 0.003, 0.0035, 0.004,
                           0.0045, 0.005, 0.0055, 0.006, 0.0065]):
        res.append(mkres("PWS001", "ST%03d" % (i + 1), "202401", "LEAD", v))
    for i in range(10):
        res.append(mkres("PWS001", "ST%03d" % (i + 1), "202401", "COPPER", 0.3))
    write_case("settled_01", sys_rows, res)

    sys_rows = [{"system_id": "PWS002", "period": "202402", "population_served": "400"}]
    res = []
    for i, v in enumerate([0.003, 0.004, 0.005, 0.006, 0.007]):
        res.append(mkres("PWS002", "ST%03d" % (i + 1), "202402", "LEAD", v))
    res.append(mkres("PWS002", "ST006", "202402", "LEAD", 0.002, qual="U"))
    res.append(mkres("PWS002", "ST007", "202402", "LEAD", 4.5, unit="ug/L"))
    for i, v in enumerate([0.2, 0.25, 0.3, 0.35, 0.4]):
        res.append(mkres("PWS002", "ST%03d" % (i + 1), "202402", "COPPER", v))
    write_case("settled_02", sys_rows, res)


# ---------------------------------------------------------------- graded
def graded_01_unit_conversion():
    """Lead arrives in ug/L (2..6 with one 6.5 mg/L row mixed in) beside mg/L
    copper. Per-row conversion puts the lead UCL95 at 0.0087, NO. Reading
    every value as mg/L reports grams per liter and a false exceedance. The
    202402 stray row is outside the roster and never counts."""
    sys_rows = [{"system_id": "PWS101", "period": "202403", "population_served": "450"}]
    res = []
    for i, v in enumerate([2, 2.5, 3, 3.5, 4, 4.5, 5, 5.5, 6]):
        res.append(mkres("PWS101", "ST%03d" % (i + 1), "202403", "LEAD", v,
                         unit="ug/L"))
    res.append(mkres("PWS101", "ST010", "202403", "LEAD", 0.0065))
    res.append(mkres("PWS101", "ST011", "202402", "LEAD", 0.999))
    for i in range(6):
        res.append(mkres("PWS101", "ST%03d" % (i + 1), "202403", "COPPER", 0.3))
    write_case("graded_01", sys_rows, res)


def graded_02_censor_flags():
    """Five detects (one J, one B) plus a U limit and a <-style limit. The
    censored ranks impute low, so the UCL95 stays at 0.0063, NO. Treating
    every row as a detect lifts the UCL95 to 0.0104, a false YES."""
    sys_rows = [{"system_id": "PWS102", "period": "202404", "population_served": "450"}]
    res = []
    quals = ["J", "", "B", "", ""]
    for i, (v, q) in enumerate(zip([0.003, 0.0035, 0.004, 0.0045, 0.005], quals)):
        res.append(mkres("PWS102", "ST%03d" % (i + 1), "202404", "LEAD", v,
                         qual=q))
    res.append(mkres("PWS102", "ST006", "202404", "LEAD", 0.001, qual="U"))
    res.append(mkres("PWS102", "ST007", "202404", "LEAD", 0.0015, qual="<0.0015"))
    for i in range(3):
        res.append(mkres("PWS102", "ST%03d" % (i + 1), "202404", "COPPER", 0.5))
    write_case("graded_02", sys_rows, res)


def graded_03_tie_order():
    """A U-qualified limit of 0.008 ties a detect at 0.008. Ranking the
    limit below the detect (the true value is at or below the limit) gives
    p90 0.0095 and UCL95 0.0168. Ranking it above reports 0.0150 / 0.0331."""
    sys_rows = [{"system_id": "PWS103", "period": "202405", "population_served": "95"}]
    res = []
    for i, v in enumerate([0.002, 0.004, 0.006, 0.008]):
        res.append(mkres("PWS103", "ST%03d" % (i + 1), "202405", "LEAD", v))
    res.append(mkres("PWS103", "ST005", "202405", "LEAD", 0.008, qual="U"))
    for i in range(4):
        res.append(mkres("PWS103", "ST%03d" % (i + 1), "202405", "COPPER", 0.3))
    write_case("graded_03", sys_rows, res)


def graded_04_zero_rows():
    """Five detects plus four reported zeros. Zeros are censored observations
    and stay in n (n=9, nc=4): UCL95 0.0092, NO. Dropping zero rows reports
    n=5 with UCL95 0.0102, a false YES."""
    sys_rows = [{"system_id": "PWS104", "period": "202406", "population_served": "95"}]
    res = []
    for i, v in enumerate([0.002, 0.003, 0.004, 0.005, 0.006]):
        res.append(mkres("PWS104", "ST%03d" % (i + 1), "202406", "LEAD", v))
    for i in range(4):
        res.append(mkres("PWS104", "STZ%02d" % (i + 1), "202406", "LEAD", 0))
    for i, v in enumerate([0.2, 0.25, 0.3, 0.35, 0.4]):
        res.append(mkres("PWS104", "ST%03d" % (i + 1), "202406", "COPPER", v))
    write_case("graded_04", sys_rows, res)


def graded_05_ucl_exceedance():
    """Eight detects whose fitted p90 (0.0096) sits below the lead action
    level while the one-sided UCL95 (0.0146) sits above: the finding is YES.
    Judging exceedance by the point estimate alone says NO. Copper is flat
    at 0.3, pinning the zero-variance branch (UCL equals p90)."""
    sys_rows = [{"system_id": "PWS105", "period": "202407", "population_served": "95"}]
    res = []
    for i, v in enumerate([0.002, 0.003, 0.004, 0.005, 0.006, 0.007, 0.008, 0.009]):
        res.append(mkres("PWS105", "ST%03d" % (i + 1), "202407", "LEAD", v))
    for i in range(6):
        res.append(mkres("PWS105", "ST%03d" % (i + 1), "202407", "COPPER", 0.3))
    write_case("graded_05", sys_rows, res)


def graded_06_edge_branches():
    """One system, three periods. 202407 lead is all-censored (reports the
    minimum 0.0050); 202408 lead has a lone detect among limits (reports the
    detect 0.0090) and copper has a single row (reports its value); 202409
    is an empty roster cell (0.0000). The blank-value and ZINC rows never
    count."""
    sys_rows = [
        {"system_id": "PWS106", "period": "202407", "population_served": "95"},
        {"system_id": "PWS106", "period": "202408", "population_served": "95"},
        {"system_id": "PWS106", "period": "202409", "population_served": "95"},
    ]
    res = [
        mkres("PWS106", "ST001", "202407", "LEAD", 0.005, qual="U"),
        mkres("PWS106", "ST002", "202407", "LEAD", 0.008, qual="<0.008"),
        mkres("PWS106", "ST003", "202407", "LEAD", "", qual="U"),
        mkres("PWS106", "ST001", "202408", "LEAD", 0.009),
        mkres("PWS106", "ST002", "202408", "LEAD", 0.005, qual="U"),
        mkres("PWS106", "ST003", "202408", "LEAD", 0.004, qual="U"),
        mkres("PWS106", "ST004", "202408", "ZINC", 0.5),
        mkres("PWS106", "ST001", "202408", "COPPER", 0.007),
    ]
    write_case("graded_06", sys_rows, res)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    settled_cases()
    graded_01_unit_conversion()
    graded_02_censor_flags()
    graded_03_tie_order()
    graded_04_zero_rows()
    graded_05_ucl_exceedance()
    graded_06_edge_branches()
    print("cases written to", OUT)
