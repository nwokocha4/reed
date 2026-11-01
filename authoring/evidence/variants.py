"""Single trap variants: each one flips exactly one office convention in a
copy of the reference solution, proving that convention decides the grade.

Writes variant programs under ci_trials/variants/ and scores each with the
evidence scorer. Every variant is expected to earn REWARD 0.
"""
import os
import subprocess
import sys

TASK = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(TASK, "solution", "solve.py")
OUTDIR = os.path.join(TASK, "authoring", "evidence", "ci_trials", "variants")
SCORER = os.path.join(TASK, "authoring", "evidence", "score_with_verifier.py")

# Each entry: name plus a list of (old, new) replacements applied once.
# Anchors are single exact source lines, verified against solve.py.
VARIANTS = [
    ("v01_five_sample_max",
     [("    elif n == 5:\n        raw = (concs[-1] + concs[-2]) / Decimal(2)\n",
       "    elif n == 5:\n        raw = concs[-1]\n")]),
    ("v02_fewer_than_five_mean",
     [("    if n < 5:\n        raw = concs[-1]\n",
       "    if n < 5:\n        raw = sum(concs, Decimal(0)) / Decimal(n)\n")]),
    ("v03_tier_shared_copper",
     [("    tier_key = \"tier_lead\" if contaminant == \"LEAD\" else \"tier_copper\"\n",
       "    tier_key = \"tier_copper\"\n")]),
    ("v04_first_liter_counts",
     [("                out.extend([(r, c) for r, c in items "
       "if str(r[\"liter\"]).strip() == \"5\"])\n",
       "                out.extend([(r, c) for r, c in items "
       "if str(r[\"liter\"]).strip() in (\"1\", \"5\")])\n")]),
    ("v05_invalid_flag_alone",
     [("        if str(r.get(\"invalid_flag\", \"N\")).strip() == \"Y\":\n"
       "            if approval_covers(approvals, system_id, r[\"sample_id\"], "
       "\"INVALIDATION\", coll):\n"
       "                continue\n",
       "        if str(r.get(\"invalid_flag\", \"N\")).strip() == \"Y\":\n"
       "            continue\n")]),
    ("v06_reduced_needs_clean_record",
     [("                elif annual and not exc and not viol and prior_exc:\n"
       "                    sched = \"REDUCED_ANNUAL\"\n",
       "                elif annual and not exc and not viol and not prior_exc:\n"
       "                    sched = \"REDUCED_ANNUAL\"\n")]),
    ("v07_reduced_column_always",
     [("            req = required_minimum(pop[(sid, per)], "
       "reduced=(annual or triennial))",
       "            req = required_minimum(pop[(sid, per)], reduced=True)")]),
    ("v08_legacy_only",
     [("    for r in results:\n        by_id[r[\"sample_id\"]] = r\n",
       "    for r in results:\n        pass\n")]),
]


def main():
    os.makedirs(OUTDIR, exist_ok=True)
    src = open(SRC).read()
    summary = {}
    for name, subs in VARIANTS:
        text = src
        for old, new in subs:
            if old not in text:
                summary[name] = "PATTERN NOT FOUND: %r" % old[:80]
                print("%s: %s" % (name, summary[name]))
                break
            text = text.replace(old, new, 1)
        else:
            path = os.path.join(OUTDIR, name + ".py")
            open(path, "w").write(text)
            proc = subprocess.run([sys.executable, SCORER, path],
                                  capture_output=True, text=True)
            reward = "REWARD 1" in proc.stdout
            summary[name] = "REWARD %d (want 0)" % (1 if reward else 0)
            print("%s: %s" % (name, summary[name]))
            for line in proc.stdout.splitlines():
                if line.startswith("FAIL"):
                    print("   ", line)
                    break
    print("---")
    bad = [k for k, v in summary.items() if "REWARD 0" not in v]
    print("variants failing to fail:", bad if bad else "none")
    sys.exit(0 if not bad else 1)


if __name__ == "__main__":
    main()
