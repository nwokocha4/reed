#!/bin/sh
# Smoke: stage the reference solution as /app/solve.py and run it on the
# settled cases. Inside the task container /app/data already holds the data;
# from a repo checkout the data is staged under a temp dir instead.
set -e
REF="$(cd "$(dirname "$0")" && pwd)/solve.py"
if [ -d /app/data ]; then
  cp "$REF" /app/solve.py
  python3 /app/solve.py
  ls /app/output
else
  STAGE="${LCR_SMOKE_DIR:-/tmp/lcr_smoke}"
  rm -rf "$STAGE"
  mkdir -p "$STAGE/output"
  cp -r "$(cd "$(dirname "$0")/../environment" && pwd)/data" "$STAGE/data"
  LCR_BASE="$STAGE" python3 "$REF"
  ls "$STAGE/output"
fi
