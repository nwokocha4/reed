"""Evidence scorer: run a candidate solve.py against the graded cases with
the same row checker the verifier uses, without Docker.

Usage: python3 score_with_verifier.py <candidate-solve.py>
Prints per case pass or fail with the first mismatch, then REWARD 0 or 1.
"""
import csv
import json
import os
import shutil
import subprocess
import sys
import tempfile

TASK = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(TASK, "tests"))
from test_outputs import check_rows

GRADED = os.path.join(TASK, "tests", "graded")
TIME_LIMIT = 300


def run_candidate(cand, case):
    work = tempfile.mkdtemp(prefix="lcr_ev_")
    try:
        datadir = os.path.join(work, "data")
        os.makedirs(os.path.join(datadir, case))
        for fn in os.listdir(os.path.join(GRADED, case)):
            shutil.copy2(os.path.join(GRADED, case, fn),
                         os.path.join(datadir, case, fn))
        os.makedirs(os.path.join(work, "output"), exist_ok=True)
        env = dict(os.environ, LCR_BASE=work)
        proc = subprocess.run([sys.executable, cand], capture_output=True,
                              text=True, timeout=TIME_LIMIT, env=env, cwd=work)
        if proc.returncode != 0:
            return False, "exit %d: %s" % (
                proc.returncode, (proc.stderr or "")[-1500:])
        out = os.path.join(work, "output", "%s_compliance.csv" % case)
        if not os.path.exists(out):
            return False, "missing output for %s" % case
        with open(out, newline="", encoding="utf-8-sig") as f:
            rows = list(csv.DictReader(f))
        try:
            return True, check_rows(rows, EXPECTED[case])
        except AssertionError as e:
            return False, str(e)
    except subprocess.TimeoutExpired:
        return False, "time limit exceeded"
    finally:
        shutil.rmtree(work, ignore_errors=True)


EXPECTED = json.load(open(os.path.join(TASK, "tests", "expected.json")))


def main():
    cand = sys.argv[1]
    all_ok = True
    for case in sorted(EXPECTED):
        ok, info = run_candidate(cand, case)
        print("%s: %s %s" % ("PASS" if ok else "FAIL", case, info))
        all_ok &= ok
    print("REWARD %d" % (1 if all_ok else 0))
    sys.exit(0 if all_ok else 1)


if __name__ == "__main__":
    main()
