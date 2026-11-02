"""Single trap variants: each one flips exactly one method convention in a
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
    ("v01_no_unit_conversion",
     [("    if str(unit).strip() == \"ug/L\":\n        v = v / 1000.0\n",
       "    if str(unit).strip() == \"ug/L\":\n        pass\n")]),
    ("v02_censor_flags_ignored",
     [("    q = str(qualifier or \"\").strip()\n"
       "    return q == \"U\" or q.startswith(\"<\")\n",
       "    q = str(qualifier or \"\").strip()\n"
       "    return False\n")]),
    ("v03_tie_censored_above",
     [("    ordered = sorted(items, key=lambda o: (o[\"conc\"], 0 if o[\"censored\"] else 1))\n",
       "    ordered = sorted(items, key=lambda o: (o[\"conc\"], 1 if o[\"censored\"] else 0))\n")]),
    ("v04_zero_rows_dropped",
     [("        cens = is_censored(r.get(\"qualifier\", \"\"))\n        if conc <= 0:\n            cens = True\n",
       "        cens = is_censored(r.get(\"qualifier\", \"\"))\n        if conc <= 0:\n            continue\n")]),
    ("v05_p90_decides_finding",
     [("            exc = \"YES\" if ucl > AL[cont] else \"NO\"\n",
       "            exc = \"YES\" if p90 > AL[cont] else \"NO\"\n")]),
    ("v06_censored_in_regression",
     [("                 if not o[\"censored\"] and o[\"conc\"] > 0]\n",
       "                 if o[\"conc\"] > 0]\n")]),
    ("v07_percentile_at_z95",
     [("    logp90 = mu + Z90 * sigma\n",
       "    logp90 = mu + Z95 * sigma\n"),
      ("        se = sigma * math.sqrt(1.0 / n + Z90 ** 2 / (2.0 * (n - 1)))\n",
       "        se = sigma * math.sqrt(1.0 / n + Z95 ** 2 / (2.0 * (n - 1)))\n")]),
    ("v08_stray_period_counts",
     [("    roster = [(r[\"system_id\"], r[\"period\"]) for r in systems]\n",
       "    roster = [(r[\"system_id\"], r[\"period\"]) for r in systems]\n"
       "    roster = list({(r[\"system_id\"], r[\"period\"]) for r in systems} | {(r[\"system_id\"], r[\"period\"]) for r in results})\n")]),
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
