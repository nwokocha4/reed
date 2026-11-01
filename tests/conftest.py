"""Shared fixtures for the LCR verifier.

Every graded case is run in isolation as an unprivileged user against the
paths the instruction promises: the case lands in /app/data/<case> and the
program writes /app/output/<case>_compliance.csv. Nothing about the run
depends on the agent having seen the verifier.
"""
import csv
import json
import os
import shutil
import subprocess
import sys

import pytest

TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
GRADED_DIR = os.path.join(TESTS_DIR, "graded")
EXPECTED_PATH = os.path.join(TESTS_DIR, "expected.json")
APP_DIR = "/app"
DATA_DIR = os.path.join(APP_DIR, "data")
OUTPUT_DIR = os.path.join(APP_DIR, "output")
SOLVE = os.path.join(APP_DIR, "solve.py")
TIME_LIMIT = 300
NOBODY = 65534


def _chmod_tree(path, dir_mode=0o755, file_mode=0o644):
    for root, dirs, files in os.walk(path):
        os.chmod(root, dir_mode)
        for d in dirs:
            os.chmod(os.path.join(root, d), dir_mode)
        for f in files:
            os.chmod(os.path.join(root, f), file_mode)


def _drop_privileges():
    if os.geteuid() == 0:
        os.setgid(NOBODY)
        os.setuid(NOBODY)


@pytest.fixture(scope="session")
def expected():
    with open(EXPECTED_PATH, encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="session")
def cases():
    names = sorted(d for d in os.listdir(GRADED_DIR)
                   if os.path.isdir(os.path.join(GRADED_DIR, d)))
    assert names, "no graded cases present"
    return names


@pytest.fixture(scope="session", autouse=True)
def app_layout():
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    yield


def run_case(case):
    """Run the submitted program on one graded case. Returns the loaded rows."""
    assert os.path.exists(SOLVE), "artifact /app/solve.py was not produced"
    if os.path.isdir(DATA_DIR):
        shutil.rmtree(DATA_DIR)
    if os.path.isdir(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)
    os.makedirs(DATA_DIR)
    os.makedirs(OUTPUT_DIR)
    shutil.copytree(os.path.join(GRADED_DIR, case), os.path.join(DATA_DIR, case))
    os.chmod(SOLVE, 0o755)
    _chmod_tree(APP_DIR, 0o777, 0o755)
    # Privilege drop is a Linux facility; on other platforms run directly.
    kw = {"cwd": APP_DIR}
    if os.name == "posix":
        kw["preexec_fn"] = _drop_privileges
    proc = subprocess.run(
        [sys.executable, SOLVE],
        capture_output=True, text=True, timeout=TIME_LIMIT,
        **kw
    )
    out = os.path.join(OUTPUT_DIR, "%s_compliance.csv" % case)
    assert proc.returncode == 0, "program exited %d: %s" % (
        proc.returncode, (proc.stderr or "")[-3000:])
    assert os.path.exists(out), "no output file at %s" % out
    with open(out, newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))
