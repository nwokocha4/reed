"""Seeded graded/settled case generator for the LCR compliance task.

Deterministic (fixed seed). Writes cases under cases/:
  settled_01, settled_02   no trap on display: n far from the five sample branch
  graded_01 .. graded_06   one trap each, listed below

Every record belongs to exactly one source file. results.csv and legacy.txt
carry disjoint sets of sample_id values, so the union is a plain concatenation
and duplicate suppression never decides an answer.

  g1  five samples collected where ten were required: average of the two
      highest, not the maximum (141.80(c)(3)(i)(D) against (E))
  g2  three eligible samples: maximum rule, and the count falls short of the
      required minimum
  g3  tier filtering: active Tier 1 sites displace Tier 2 sites for lead while
      copper tiers differ and keep every site eligible
  g4  sequential pair selection: first liter is informational, fifth liter is
      the compliance sample, half pairs excluded
  g5  invalidation: approved invalidation excludes the high result, an
      unapproved invalid mark does not
  g6  schedule chain: prior period exceedance, reduction approval expiry,
      population move across minimum count rows, triennial then annual
"""
import csv
import os
import random

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cases")
R = random.Random(20261101)

HEADER_SYS = ["system_id", "period", "population_served"]
HEADER_INV = ["system_id", "site_id", "tier_lead", "tier_copper", "active",
              "service_status", "requires_pair"]
HEADER_RES = ["system_id", "site_id", "sample_id", "period", "contaminant", "liter",
              "value", "unit", "qualifier", "invalid_flag", "collection_date"]
HEADER_APP = ["system_id", "sample_id", "approval_type", "effective_date", "expiry_date"]


def write_case(name, systems, inventory, results, approvals):
    d = os.path.join(OUT, name)
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, "systems.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=HEADER_SYS)
        w.writeheader()
        w.writerows(systems)
    with open(os.path.join(d, "inventory.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=HEADER_INV)
        w.writeheader()
        w.writerows(inventory)
    with open(os.path.join(d, "results.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=HEADER_RES)
        w.writeheader()
        for r in results:
            if r["_where"] == "csv":
                w.writerow({k: r[k] for k in HEADER_RES})
    with open(os.path.join(d, "legacy.txt"), "w") as f:
        for r in results:
            if r["_where"] != "legacy":
                continue
            line = (r["system_id"].ljust(8) + r["site_id"].ljust(8)
                    + r["sample_id"].ljust(10) + r["period"].ljust(6)
                    + r["contaminant"].ljust(6) + str(r["liter"]).ljust(2)
                    + str(r["value"]).rjust(12) + r["unit"].ljust(8)
                    + (r["qualifier"] or "").ljust(4) + r["invalid_flag"]
                    + r["collection_date"].ljust(10))
            f.write(line + "\n")
    with open(os.path.join(d, "approvals.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=HEADER_APP)
        w.writeheader()
        w.writerows(approvals)
    for r in results:
        r.pop("_where", None)


def mkres(sid, site, snum, period, cont, liter, value, unit="mg/L", qual="",
          inv="N", day="05", where="csv"):
    return {"system_id": sid, "site_id": site,
            "sample_id": "S%05d" % snum, "period": period, "contaminant": cont,
            "liter": liter, "value": str(value), "unit": unit, "qualifier": qual,
            "invalid_flag": inv, "collection_date": "%s-%s-%s" % (period[0:4], period[4:6], day),
            "_where": where}


def mkinv(sid, site, tl="T1", tc="T1", pair="N"):
    return {"system_id": sid, "site_id": site, "tier_lead": tl, "tier_copper": tc,
            "active": "Y", "service_status": "ACTIVE", "requires_pair": pair}


sid_counter = [1000]


def nxt():
    sid_counter[0] += 1
    return sid_counter[0]


# ---------------------------------------------------------------- settled
def settled_cases():
    """n of 20 and 10. Both sit far from the five sample branch and from any
    boundary, so the visible sheets show the plain ceiling rank and nothing else."""

    sys_rows = [{"system_id": "PWS001", "period": "202401", "population_served": "2500"}]
    inv, res = [], []
    lead_vals = [0.002, 0.003, 0.001, 0.004, 0.002, 0.005, 0.003, 0.002, 0.001, 0.004,
                 0.003, 0.002, 0.005, 0.001, 0.003, 0.002, 0.004, 0.001, 0.003, 0.002]
    for i, v in enumerate(lead_vals):
        site = "ST%03d" % (i + 1)
        inv.append(mkinv("PWS001", site))
        where = "legacy" if i % 3 == 0 else "csv"
        res.append(mkres("PWS001", site, nxt(), "202401", "LEAD", "NA", v, where=where))
    for i in range(20):
        site = "ST%03d" % (i + 1)
        where = "legacy" if i % 4 == 0 else "csv"
        res.append(mkres("PWS001", site, nxt(), "202401", "COPPER", "NA",
                         round(0.2 + 0.01 * i, 4), where=where))
    write_case("settled_01", sys_rows, inv, res, [])

    sys_rows = [{"system_id": "PWS002", "period": "202402", "population_served": "400"}]
    inv, res = [], []
    for i in range(10):
        site = "ST%03d" % (i + 1)
        inv.append(mkinv("PWS002", site))
        where = "legacy" if i % 2 else "csv"
        if i == 0:
            res.append(mkres("PWS002", site, nxt(), "202402", "LEAD", "NA", 0.001,
                             qual="U", where=where))
        elif i == 1:
            res.append(mkres("PWS002", site, nxt(), "202402", "LEAD", "NA", 4.0,
                             unit="ug/L", where=where))
        else:
            res.append(mkres("PWS002", site, nxt(), "202402", "LEAD", "NA",
                             round(0.002 + 0.0005 * i, 4), where=where))
        res.append(mkres("PWS002", site, nxt(), "202402", "COPPER", "NA", 0.3,
                         where="legacy" if i % 3 == 0 else "csv"))
    write_case("settled_02", sys_rows, inv, res, [])


# ---------------------------------------------------------------- graded
def graded_01_five_sample_avg():
    """Population 450 asks for ten samples. Exactly five arrive, so the five
    sample branch applies and the percentile is the mean of the two highest,
    0.0095. Taking the maximum instead reports 0.0110, which flips the finding."""
    sys_rows = [{"system_id": "PWS101", "period": "202403", "population_served": "450"}]
    inv = [mkinv("PWS101", "ST%03d" % (i + 1)) for i in range(5)]
    vals = [0.004, 0.006, 0.007, 0.008, 0.011]
    res = []
    for i, v in enumerate(vals):
        where = "legacy" if i in (1, 3) else "csv"
        res.append(mkres("PWS101", "ST%03d" % (i + 1), nxt(), "202403", "LEAD", "NA",
                         v, where=where))
    for i in range(5):
        where = "legacy" if i == 2 else "csv"
        res.append(mkres("PWS101", "ST%03d" % (i + 1), nxt(), "202403", "COPPER", "NA",
                         0.4, where=where))
    write_case("graded_01", sys_rows, inv, res, [])


def graded_02_fewer_than_five():
    """Three eligible samples against a required minimum of ten. The percentile
    is the maximum, 0.0130, and the count shortfall raises the monitoring flag."""
    sys_rows = [{"system_id": "PWS102", "period": "202404", "population_served": "450"}]
    inv = [mkinv("PWS102", "ST%03d" % (i + 1)) for i in range(3)]
    vals = [0.006, 0.013, 0.009]
    res = []
    for i, v in enumerate(vals):
        where = "legacy" if i == 1 else "csv"
        res.append(mkres("PWS102", "ST%03d" % (i + 1), nxt(), "202404", "LEAD", "NA",
                         v, where=where))
    for i in range(3):
        res.append(mkres("PWS102", "ST%03d" % (i + 1), nxt(), "202404", "COPPER", "NA",
                         0.5, where="csv"))
    write_case("graded_02", sys_rows, inv, res, [])


def graded_03_tier_filter():
    """Active Tier 1 lead sites exist, so Tier 2 lead results never count: six
    eligible lead samples, 90th percentile 0.0080. Keeping every site gives ten
    samples and 0.0280, an exceedance that is not there. Every site carries
    copper tier T2, so the copper tier filter holds all six copper results."""
    sys_rows = [{"system_id": "PWS103", "period": "202405", "population_served": "95"}]
    inv, res = [], []
    t1_vals = [0.003, 0.004, 0.005, 0.006, 0.007, 0.008]
    for i, v in enumerate(t1_vals):
        site = "T1S%02d" % (i + 1)
        inv.append(mkinv("PWS103", site, tl="T1", tc="T2"))
        where = "legacy" if i >= 4 else "csv"
        res.append(mkres("PWS103", site, nxt(), "202405", "LEAD", "NA", v, where=where))
        res.append(mkres("PWS103", site, nxt(), "202405", "COPPER", "NA",
                         0.3, where="legacy" if i == 0 else "csv"))
    t2_vals = [0.020, 0.025, 0.030, 0.028]
    for i, v in enumerate(t2_vals):
        site = "T2S%02d" % (i + 1)
        inv.append(mkinv("PWS103", site, tl="T2", tc="T2"))
        res.append(mkres("PWS103", site, nxt(), "202405", "LEAD", "NA", v, where="csv"))
    write_case("graded_03", sys_rows, inv, res, [])


def graded_04_pair_selection():
    """Four sequential sites and three single sites. Two sequential sites send
    only the first liter and are excluded outright. The fifth liter governs the
    two complete pairs, so five lead samples survive and the mean of the two
    highest is 0.0095. Reading first liters instead admits 0.0300 and flips the
    finding. Copper at these sites is a single sample and keeps all seven."""
    sys_rows = [{"system_id": "PWS104", "period": "202406", "population_served": "95"}]
    inv = [mkinv("PWS104", "PAIR%02d" % (i + 1), pair="Y") for i in range(4)]
    inv += [mkinv("PWS104", "SGL%02d" % (i + 1), pair="N") for i in range(3)]
    res = []
    res.append(mkres("PWS104", "PAIR01", nxt(), "202406", "LEAD", "1", 0.004, where="csv"))
    res.append(mkres("PWS104", "PAIR01", nxt(), "202406", "LEAD", "5", 0.012, where="legacy"))
    res.append(mkres("PWS104", "PAIR02", nxt(), "202406", "LEAD", "1", 0.003, where="csv"))
    res.append(mkres("PWS104", "PAIR02", nxt(), "202406", "LEAD", "5", 0.006, where="csv"))
    res.append(mkres("PWS104", "PAIR03", nxt(), "202406", "LEAD", "1", 0.030, where="legacy"))
    res.append(mkres("PWS104", "PAIR04", nxt(), "202406", "LEAD", "1", 0.028, where="legacy"))
    for site, v in [("SGL01", 0.005), ("SGL02", 0.007), ("SGL03", 0.004)]:
        res.append(mkres("PWS104", site, nxt(), "202406", "LEAD", "NA", v, where="csv"))
    for i, row in enumerate(inv):
        res.append(mkres("PWS104", row["site_id"], nxt(), "202406", "COPPER", "NA", 0.35,
                         where="legacy" if i % 3 == 0 else "csv"))
    write_case("graded_04", sys_rows, inv, res, [])


def graded_05_invalidation():
    """Two systems with the same seven lead results, the top one flagged invalid.
    PWS105 holds an approved invalidation, so six samples stand and the
    percentile is 0.0090. PWS106 has no approval, so the 0.0500 result counts and
    the percentile is 0.0500. The high values sit only in the legacy export."""
    approvals = []
    sys_rows = [{"system_id": "PWS105", "period": "202407", "population_served": "95"}]
    inv, res = [], []
    vals = [0.003, 0.004, 0.005, 0.006, 0.007, 0.009, 0.050]
    for i, v in enumerate(vals):
        inv.append(mkinv("PWS105", "ST%03d" % (i + 1)))
        res.append(mkres("PWS105", "ST%03d" % (i + 1), nxt(), "202407", "LEAD", "NA", v,
                         inv="Y" if i == 6 else "N",
                         where="legacy" if i == 6 else ("legacy" if i % 3 == 0 else "csv")))
    for i in range(7):
        res.append(mkres("PWS105", "ST%03d" % (i + 1), nxt(), "202407", "COPPER", "NA", 0.4,
                         where="csv"))
    approvals.append({"system_id": "PWS105", "sample_id": res[6]["sample_id"],
                      "approval_type": "INVALIDATION",
                      "effective_date": "2024-07-01", "expiry_date": "2024-07-31"})

    sys_rows.append({"system_id": "PWS106", "period": "202407", "population_served": "95"})
    for i, v in enumerate(vals):
        inv.append(mkinv("PWS106", "ST%03d" % (i + 1)))
        res.append(mkres("PWS106", "ST%03d" % (i + 1), nxt(), "202407", "LEAD", "NA", v,
                         inv="Y" if i == 6 else "N",
                         where="legacy" if i == 6 else ("legacy" if i % 3 == 0 else "csv")))
    for i in range(7):
        res.append(mkres("PWS106", "ST%03d" % (i + 1), nxt(), "202407", "COPPER", "NA", 0.4,
                         where="csv"))
    write_case("graded_05", sys_rows, inv, res, approvals)


def graded_06_schedule_chain():
    """Three periods at population 400, 400, and 600. January exceeds for lead at
    0.0130. The triennial approval lapses on 15 January 2024 so February is
    standard. March moves to the 501 to 3300 row, needs twenty samples, holds an
    annual reduction so ten suffice, and shows one prior exceedance, so the
    office convention gives REDUCED_ANNUAL."""
    sys_rows = [
        {"system_id": "PWS107", "period": "202401", "population_served": "400"},
        {"system_id": "PWS107", "period": "202402", "population_served": "400"},
        {"system_id": "PWS107", "period": "202403", "population_served": "600"},
    ]
    inv = [mkinv("PWS107", "ST%03d" % (i + 1)) for i in range(10)]
    res = []
    p1 = [0.002, 0.003, 0.004, 0.005, 0.006, 0.007, 0.008, 0.009, 0.013, 0.014]
    for i, v in enumerate(p1):
        res.append(mkres("PWS107", "ST%03d" % (i + 1), nxt(), "202401", "LEAD", "NA", v,
                         where="legacy" if i == 9 else "csv"))
        res.append(mkres("PWS107", "ST%03d" % (i + 1), nxt(), "202401", "COPPER", "NA", 0.3,
                         where="csv"))
    for i in range(10):
        res.append(mkres("PWS107", "ST%03d" % (i + 1), nxt(), "202402", "LEAD", "NA",
                         round(0.002 + 0.0002 * i, 4),
                         where="legacy" if i % 4 == 0 else "csv"))
        res.append(mkres("PWS107", "ST%03d" % (i + 1), nxt(), "202402", "COPPER", "NA", 0.3,
                         where="csv"))
    for i in range(10):
        res.append(mkres("PWS107", "ST%03d" % (i + 1), nxt(), "202403", "LEAD", "NA",
                         round(0.002 + 0.0002 * i, 4),
                         where="legacy" if i % 5 == 0 else "csv"))
        res.append(mkres("PWS107", "ST%03d" % (i + 1), nxt(), "202403", "COPPER", "NA",
                         1.5 if i >= 8 else 0.3,
                         where="legacy" if i >= 8 else "csv"))
    approvals = [
        {"system_id": "PWS107", "sample_id": "ALL", "approval_type": "TRIENNIAL",
         "effective_date": "2023-01-01", "expiry_date": "2024-01-15"},
        {"system_id": "PWS107", "sample_id": "ALL", "approval_type": "ANNUAL",
         "effective_date": "2024-03-01", "expiry_date": "2025-03-01"},
    ]
    write_case("graded_06", sys_rows, inv, res, approvals)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    settled_cases()
    graded_01_five_sample_avg()
    graded_02_fewer_than_five()
    graded_03_tier_filter()
    graded_04_pair_selection()
    graded_05_invalidation()
    graded_06_schedule_chain()
    print("cases written to", OUT)
