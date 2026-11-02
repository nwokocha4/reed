#!/bin/sh
# Verifier entrypoint: run the graded checks as nobody-written files allow,
# emit CTRF for the pipeline, and fail the image build trial on any mismatch.
set -e
cd /tests
python3 -m pytest test_outputs.py -v --ctrf /tmp/ctrf.json
