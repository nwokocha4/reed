"""Lead 90th-percentile estimation from censored tap data with sampling uncertainty.

Reads every case directory directly under <base>/data (excluding `reference`),
groups tap results by system, period and contaminant, applies the reference
estimation method (lognormal regression on order statistics with a delta-method
upper confidence limit), and writes one estimate table per case to
<base>/output/<case>_estimate.csv.

Base defaults to /app; override with LCR_BASE for local testing.
Method authority: environment/data/reference/lcr_ros_method.pdf.
"""

import csv
import math
import os
import statistics
from decimal import Decimal, ROUND_HALF_UP

BASE = os.environ.get("LCR_BASE", "/app")
AL = {"LEAD": 0.010, "COPPER": 1.3}
NORM = statistics.NormalDist()
Z90 = NORM.inv_cdf(0.9)
Z95 = NORM.inv_cdf(0.95)


def to_mg(value, unit):
    v = float(str(value).strip())
    if str(unit).strip() == "ug/L":
        v = v / 1000.0
    return v


def is_censored(qualifier):
    q = str(qualifier or "").strip()
    return q == "U" or q.startswith("<")


def read_csv_rows(path):
    with open(path, newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def q4(x):
    return Decimal(str(x)).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)


def load_case(case_dir):
    systems = read_csv_rows(os.path.join(case_dir, "systems.csv"))
    results = read_csv_rows(os.path.join(case_dir, "results.csv"))
    return systems, results


def case_cells(systems, results):
    """Group normalized observations by (system, period, contaminant)."""
    roster = [(r["system_id"], r["period"]) for r in systems]
    obs = {}
    for r in results:
        if r.get("contaminant") not in ("LEAD", "COPPER"):
            continue
        try:
            conc = to_mg(r["value"], r["unit"])
        except (ValueError, TypeError, AttributeError):
            continue
        cens = is_censored(r.get("qualifier", ""))
        if conc <= 0:
            cens = True
        key = (r["system_id"], r["period"], r["contaminant"])
        obs.setdefault(key, []).append({"conc": conc, "censored": cens})
    return roster, obs


def ros_estimate(items):
    """Lognormal ROS estimate of the 90th percentile and its one-sided UCL95.

    items: list of {"conc": mg/L float, "censored": bool}.
    Returns (p90, ucl95, n, n_censored).
    """
    n = len(items)
    if n == 0:
        return 0.0, 0.0, 0, 0
    nc = sum(1 for o in items if o["censored"])
    if n == 1:
        v = items[0]["conc"]
        return v, v, 1, nc
    # Joint ascending order; a censored limit ranks below a detect reported
    # at the same numeric value since the true value is at or below the limit.
    ordered = sorted(items, key=lambda o: (o["conc"], 0 if o["censored"] else 1))
    # Cunnane plotting positions for every rank.
    z_all = [NORM.inv_cdf((i + 1 - 0.4) / (n + 0.2)) for i in range(n)]
    det_pairs = [(math.log(o["conc"]), z)
                 for o, z in zip(ordered, z_all)
                 if not o["censored"] and o["conc"] > 0]
    if not det_pairs:
        dl = min(o["conc"] for o in ordered)
        return dl, dl, n, nc
    if len(det_pairs) == 1:
        p90 = math.exp(det_pairs[0][0])
        return p90, p90, n, nc
    ys = [p[0] for p in det_pairs]
    zs = [p[1] for p in det_pairs]
    k = len(ys)
    ybar = sum(ys) / k
    zbar = sum(zs) / k
    szz = sum((z - zbar) ** 2 for z in zs)
    if szz == 0:
        p90 = math.exp(ybar)
        return p90, p90, n, nc
    szy = sum((z - zbar) * (y - ybar) for z, y in zip(zs, ys))
    slope = szy / szz
    intercept = ybar - slope * zbar
    # Impute each censored observation from the fitted line at its own rank.
    full = list(ys)
    for o, z in zip(ordered, z_all):
        if o["censored"]:
            full.append(intercept + slope * z)
    mu = sum(full) / n
    if n > 1:
        var = sum((v - mu) ** 2 for v in full) / (n - 1)
        sigma = math.sqrt(max(var, 0.0))
    else:
        sigma = 0.0
    logp90 = mu + Z90 * sigma
    p90 = math.exp(logp90)
    if sigma == 0.0:
        ucl = p90
    else:
        se = sigma * math.sqrt(1.0 / n + Z90 ** 2 / (2.0 * (n - 1)))
        ucl = math.exp(logp90 + Z95 * se)
    return p90, ucl, n, nc


def solve_case(case_dir):
    systems, results = load_case(case_dir)
    roster, obs = case_cells(systems, results)
    seen = sorted(set(roster))
    rows = []
    for sid, per in seen:
        for cont in ("LEAD", "COPPER"):
            items = obs.get((sid, per, cont), [])
            p90, ucl, n, nc = ros_estimate(items)
            exc = "YES" if ucl > AL[cont] else "NO"
            rows.append({
                "system_id": sid,
                "period": per,
                "contaminant": cont,
                "n": str(n),
                "n_censored": str(nc),
                "p90_mg_per_L": format(q4(p90), ".4f"),
                "ucl95_mg_per_L": format(q4(ucl), ".4f"),
                "exceedance": exc,
            })
    rows.sort(key=lambda r: (r["system_id"], r["period"], r["contaminant"]))
    return rows


def main():
    data = os.path.join(BASE, "data")
    outdir = os.path.join(BASE, "output")
    os.makedirs(outdir, exist_ok=True)
    cases = sorted(d for d in os.listdir(data)
                   if os.path.isdir(os.path.join(data, d)) and d != "reference")
    for case in cases:
        rows = solve_case(os.path.join(data, case))
        with open(os.path.join(outdir, "%s_estimate.csv" % case), "w",
                  newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=["system_id", "period", "contaminant",
                                              "n", "n_censored",
                                              "p90_mg_per_L", "ucl95_mg_per_L",
                                              "exceedance"])
            w.writeheader()
            w.writerows(rows)
        print("wrote %s (%d rows)" % (case, len(rows)))


if __name__ == "__main__":
    main()
