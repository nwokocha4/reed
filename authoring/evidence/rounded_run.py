"""Rounded run wrapper: scores the intermediate rounding variant and
records the result for the evidence folder."""
import os
import subprocess
import sys

TASK = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SCORER = os.path.join(TASK, "authoring", "evidence", "score_with_verifier.py")
ROUNDED = os.path.join(TASK, "authoring", "evidence", "rounded_solve.py")
NOP = os.path.join(TASK, "authoring", "evidence", "nop_solve.py")

for cand, want in ((os.path.join(TASK, "solution", "solve.py"), 1),
                   (ROUNDED, 1), (NOP, 0)):
    proc = subprocess.run([sys.executable, SCORER, cand],
                          capture_output=True, text=True)
    reward = 1 if "REWARD 1" in proc.stdout else 0
    status = "OK" if reward == want else "UNEXPECTED"
    print("%s: %s want REWARD %d got REWARD %d" % (status, os.path.basename(cand),
                                                  want, reward))
