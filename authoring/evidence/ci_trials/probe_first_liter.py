"""Blind probe C: representative agent attempt that averages both liters
at sequential sites instead of selecting the fifth. Expected: REWARD 0 on
graded_04.
"""
import os
import sys
from decimal import Decimal

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "..", "..", "solution"))
import solve as ref

_orig = ref.eligible_records


def eligible_records(records, inventory, approvals, system_id, period, contaminant):
    rows = _orig(records, inventory, approvals, system_id, period, contaminant)
    if contaminant == "LEAD":
        inv = ref.inv_lookup(inventory)
        extra = []
        for r in records:
            if r["system_id"] != system_id or r["period"] != period:
                continue
            if r["contaminant"] != "LEAD":
                continue
            site = inv.get((system_id, r["site_id"]))
            if site is None or site.get("requires_pair") != "Y":
                continue
            if str(r["liter"]).strip() != "1":
                continue
            coll = ref.parse_date(r["collection_date"])
            if (str(r.get("invalid_flag", "N")).strip() == "Y"
                    and ref.approval_covers(approvals, system_id,
                                            r["sample_id"], "INVALIDATION", coll)):
                continue
            try:
                extra.append((r, ref.norm_concentration(r["value"], r["unit"],
                                                        r.get("qualifier", ""))))
            except (ValueError, TypeError):
                continue
        rows = rows + extra
    return rows


ref.eligible_records = eligible_records
ref.main()
