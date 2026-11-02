#!/bin/sh
# Verifier entrypoint: run the graded checks and emit CTRF for the pipeline.
# The harness reads the verdict from /logs/verifier/reward.txt, so it must be
# written on every path: 1 only when every row of every case passes, else 0.
set -e
cd /tests
mkdir -p /logs/verifier
if python3 -m pytest test_outputs.py -v --ctrf /logs/verifier/ctrf.json; then
  echo 1 > /logs/verifier/reward.txt
else
  echo 0 > /logs/verifier/reward.txt
fi
exit 0
