"""Lead and Copper Rule tap-monitoring compliance reconstruction.

Reads every case directory directly under <base>/data (excluding `reference`),
parses the five input files, applies the office eligibility pipeline, computes
the 90th percentile per contaminant, derives schedule and follow-up flags, and
writes one compliance table per case to <base>/output/<case>_compliance.csv.

Base defaults to /app; override with LCR_BASE for local testing.
"""
import csv
import math
import os
import sys
from datetime import date
from decimal import Decimal, ROUND_HALF_UP

BASE = os.environ.get("LCR_BASE", "/app")
AL = {"LEAD": Decimal("0.010"), "COPPER": Decimal("1.3")}
TIER_RANK = {"T1": 3, "T2": 2, "T3": 1}


def parse_date(s):
    s = (s or "").strip()
    y, m, d = int(s[0:4]), int(s[5:7]), int(s[8:10])
    return date(y, m, d)


def period_start(period):
    return date(int(period[0:4]), int(period[4:6]), 1)


def to_mg(value, unit):
    v = Decimal(str(value).strip())
    if str(unit).strip() == "ug/L":
        v = v / Decimal(1000)
    return v


def norm_concentration(value, unit, qualifier):
    q = str(qualifier or "").strip()
    if q == "U" or q.startswith("<"):
        return Decimal(0)
    return to_mg(value, unit)


def read_csv_rows(path):
    with open(path, newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def parse_legacy(path):
    recs = []
    if not os.path.exists(path):
        return recs
    with open(path, encoding="utf-8-sig") as f:
        for line in f:
            if not line.strip():
                continue
            line = line.rstrip("\n")
            def fld(a, b):
                return line[a:b].strip() if len(line) >= b else line[a:].strip()
            recs.append({
                "system_id": fld(0, 8),
                "site_id": fld(8, 16),
                "sample_id": fld(16, 26),
                "period": fld(26, 32),
                "contaminant": fld(32, 38),
                "liter": fld(38, 40),
                "value": fld(40, 52),
                "unit": fld(52, 60),
                "qualifier": fld(60, 64),
                "invalid_flag": fld(64, 65),
                "collection_date": fld(65, 75),
            })
    return recs


def load_case(case_dir):
    systems = read_csv_rows(os.path.join(case_dir, "systems.csv"))
    inventory = read_csv_rows(os.path.join(case_dir, "inventory.csv"))
    results = read_csv_rows(os.path.join(case_dir, "results.csv"))
    legacy = parse_legacy(os.path.join(case_dir, "legacy.txt"))
    approvals = read_csv_rows(os.path.join(case_dir, "approvals.csv"))
    # Union by sample_id; results.csv wins on collision.
    by_id = {}
    for r in legacy:
        by_id[r["sample_id"]] = r
    for r in results:
        by_id[r["sample_id"]] = r
    return systems, inventory, list(by_id.values()), approvals


def inv_lookup(inventory):
    return {(r["system_id"], r["site_id"]): r for r in inventory}


def approval_covers(approvals, system_id, sample_id, kind, coll):
    for a in approvals:
        if a["system_id"] != system_id:
            continue
        if a["approval_type"] != kind:
            continue
        if kind == "INVALIDATION" and a["sample_id"] != sample_id:
            continue
        eff = parse_date(a["effective_date"])
        exp = parse_date(a["expiry_date"])
        if eff <= coll <= exp:
            return True
    return False


def reduction_covers(approvals, system_id, period, kind):
    ps = period_start(period)
    for a in approvals:
        if a["system_id"] != system_id or a["approval_type"] != kind:
            continue
        if parse_date(a["effective_date"]) <= ps <= parse_date(a["expiry_date"]):
            return True
    return False


def eligible_records(records, inventory, approvals, system_id, period, contaminant):
    inv = inv_lookup(inventory)
    tier_key = "tier_lead" if contaminant == "LEAD" else "tier_copper"
    # Highest tier with at least one active-service site for this contaminant.
    best = 0
    for (sid, _), row in inv.items():
        if sid != system_id:
            continue
        if row.get("active") == "Y" and row.get("service_status") == "ACTIVE":
            best = max(best, TIER_RANK.get(row.get(tier_key, ""), 0))
    if best == 0:
        return []
    # Group candidate records by site after invalidation + tier filtering.
    by_site = {}
    for r in records:
        if r["system_id"] != system_id or r["period"] != period:
            continue
        if r["contaminant"] != contaminant:
            continue
        site = inv.get((system_id, r["site_id"]))
        if site is None:
            continue
        if TIER_RANK.get(site.get(tier_key, ""), 0) != best:
            continue
        coll = parse_date(r["collection_date"])
        if str(r.get("invalid_flag", "N")).strip() == "Y":
            if approval_covers(approvals, system_id, r["sample_id"], "INVALIDATION", coll):
                continue
        try:
            conc = norm_concentration(r["value"], r["unit"], r.get("qualifier", ""))
        except (ValueError, TypeError):
            continue
        by_site.setdefault(r["site_id"], []).append((r, conc))
    # Liter selection.
    out = []
    for site_id, items in by_site.items():
        site = inv[(system_id, site_id)]
        if contaminant == "LEAD" and site.get("requires_pair") == "Y":
            liters = {str(r["liter"]).strip() for r, _ in items}
            if "5" in liters and "1" in liters:
                out.extend([(r, c) for r, c in items if str(r["liter"]).strip() == "5"])
            # else: half a pair, the site is excluded entirely
        else:
            out.extend([(r, c) for r, c in items if str(r["liter"]).strip() == "NA"])
    return out


def percentile_value(items):
    """items: list of (record, conc). Returns (rounded Decimal, n)."""
    n = len(items)
    if n == 0:
        return Decimal("0.0000"), 0
    ordered = sorted(items, key=lambda t: (t[1], t[0]["site_id"], t[0]["collection_date"]))
    concs = [c for _, c in ordered]
    if n < 5:
        raw = concs[-1]
    elif n == 5:
        raw = concs[-1]
    else:
        idx = int(math.ceil(n * 0.9))  # 1-based
        raw = concs[idx - 1]
    return raw.quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP), n


def required_minimum(population, reduced):
    pop = int(population)
    table = [
        (100000, None, 100, 50),
        (10000, 100000, 60, 30),
        (3300, 10000, 40, 20),
        (500, 3300, 20, 10),
        (100, 500, 10, 5),
    ]
    for lo, hi, std, red in table:
        if hi is None:
            if pop > lo:
                return red if reduced else std
        elif lo < pop <= hi:
            return red if reduced else std
    return 5  # population 100 or fewer


def solve_case(case_dir):
    systems, inventory, records, approvals = load_case(case_dir)
    # Population per system+period.
    pop = {(r["system_id"], r["period"]): r["population_served"] for r in systems}
    sys_periods = {}
    for (sid, per) in pop:
        sys_periods.setdefault(sid, []).append(per)
    for sid in sys_periods:
        sys_periods[sid] = sorted(sys_periods[sid])
    # First pass: percentiles + exceedances.
    cell = {}
    for sid, periods in sys_periods.items():
        for per in periods:
            for cont in ("LEAD", "COPPER"):
                elig = eligible_records(records, inventory, approvals, sid, per, cont)
                pct, n = percentile_value(elig)
                exc = "YES" if pct > AL[cont] else "NO"
                cell[(sid, per, cont)] = {"n": n, "pct": pct, "exc": exc}
    # Second pass: schedule + followup (needs prior exceedances).
    rows = []
    for sid, periods in sys_periods.items():
        for i, per in enumerate(periods):
            annual = reduction_covers(approvals, sid, per, "ANNUAL")
            triennial = reduction_covers(approvals, sid, per, "TRIENNIAL")
            req = required_minimum(pop[(sid, per)], reduced=(annual or triennial))
            priors = {}
            for cont in ("LEAD", "COPPER"):
                hist = [cell[(sid, p, cont)]["exc"] == "YES" for p in periods[:i]]
                priors[cont] = hist[-2:] if len(hist) >= 2 else hist
            for cont in ("LEAD", "COPPER"):
                c = cell[(sid, per, cont)]
                viol = c["n"] < req
                exc = c["exc"] == "YES"
                prior_exc = any(e for e in priors[cont])
                if exc or viol:
                    sched = "STANDARD_SEMIANNUAL"
                elif triennial and not exc and not any(
                    cell[(sid, p, cont)]["exc"] == "YES" for p in periods[:i][-2:]
                ) and not any(
                    cell[(sid, p, cont)]["exc"] == "YES" for p in [per]
                ):
                    sched = "REDUCED_TRIENNIAL"
                elif annual and not exc and not viol and prior_exc:
                    sched = "REDUCED_ANNUAL"
                else:
                    sched = "STANDARD_SEMIANNUAL"
                flags = []
                if viol:
                    flags.append("MON_VIOLATION")
                if exc and cont == "LEAD":
                    flags += ["PE", "SLR", "WQP"]
                elif exc and cont == "COPPER":
                    flags.append("WQP")
                foll = "|".join(flags) if flags else "NONE"
                rows.append({
                    "system_id": sid,
                    "period": per,
                    "contaminant": cont,
                    "eligible_n": str(c["n"]),
                    "percentile_mg_per_L": format(c["pct"], ".4f"),
                    "exceedance": c["exc"],
                    "schedule": sched,
                    "followup": foll,
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
        with open(os.path.join(outdir, "%s_compliance.csv" % case), "w",
                  newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=["system_id", "period", "contaminant",
                                              "eligible_n", "percentile_mg_per_L",
                                              "exceedance", "schedule", "followup"])
            w.writeheader()
            w.writerows(rows)
        print("wrote %s (%d rows)" % (case, len(rows)))


if __name__ == "__main__":
    main()
