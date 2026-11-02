"""Rebuild check: regenerate cases from the seeded generator and the
reference PDF from the builder, and confirm they match the committed trees.

Run from the task folder: python3 authoring/provenance/verify_rebuild.py.
Compares the regenerated output against authoring/provenance/cases,
tests/graded, environment/data/settled_* (results/systems only; the signed
sheets are oracle outputs and are skipped), and
environment/data/reference/lcr_ros_method.pdf.
"""
import filecmp
import hashlib
import os
import shutil
import sys
import tempfile

TASK = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROV = os.path.join(TASK, "authoring", "provenance")
SKIP_SUFFIXES = ("_signed.csv",)


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def tree_files(root):
    out = {}
    for dirpath, _, files in os.walk(root):
        for fn in sorted(files):
            if fn.endswith(SKIP_SUFFIXES):
                continue
            p = os.path.join(dirpath, fn)
            out[os.path.relpath(p, root)] = p
    return out


def compare(a, b, label):
    fa, fb = tree_files(a), tree_files(b)
    if set(fa) != set(fb):
        print("FAIL %s: name sets differ" % label)
        print("  only in %s: %s" % (a, sorted(set(fa) - set(fb))[:10]))
        print("  only in %s: %s" % (b, sorted(set(fb) - set(fa))[:10]))
        return False
    bad = [k for k in sorted(fa) if not filecmp.cmp(fa[k], fb[k], shallow=False)]
    if bad:
        print("FAIL %s: %d files differ, first: %s" % (label, len(bad), bad[:5]))
        return False
    print("OK %s: %d files identical" % (label, len(fa)))
    return True


def main():
    ok = True
    sys.path.insert(0, os.path.join(PROV, "reference_build"))
    sys.path.insert(0, PROV)
    work = tempfile.mkdtemp(prefix="ros_rebuild_")
    try:
        from ref_common import PAGES, build_pdf
        fresh_pdf = os.path.join(work, "lcr_ros_method.pdf")
        build_pdf(fresh_pdf, PAGES)
        live_pdf = os.path.join(TASK, "environment", "data",
                                "reference", "lcr_ros_method.pdf")
        if sha256(fresh_pdf) != sha256(live_pdf):
            print("FAIL pdf: rebuilt lcr_ros_method.pdf differs from committed copy")
            ok = False
        else:
            print("OK pdf: rebuilt lcr_ros_method.pdf matches (%s)"
                  % sha256(live_pdf)[:16])
        import seeded_generator as gen
        staged = os.path.join(work, "cases")
        os.makedirs(staged)
        gen.OUT = staged
        gen.sid_counter[0] = 1000
        gen.settled_cases()
        gen.graded_01_unit_conversion()
        gen.graded_02_censor_flags()
        gen.graded_03_tie_order()
        gen.graded_04_zero_rows()
        gen.graded_05_ucl_exceedance()
        gen.graded_06_edge_branches()
        ok &= compare(staged, os.path.join(PROV, "cases"), "cases-vs-generator")
        ok &= compare(os.path.join(staged, "settled_01"),
                      os.path.join(TASK, "environment", "data", "settled_01"),
                      "settled_01-vs-environment")
        ok &= compare(os.path.join(staged, "settled_02"),
                      os.path.join(TASK, "environment", "data", "settled_02"),
                      "settled_02-vs-environment")
        for g in ("graded_01", "graded_02", "graded_03",
                  "graded_04", "graded_05", "graded_06"):
            ok &= compare(os.path.join(staged, g),
                          os.path.join(TASK, "tests", "graded", g),
                          "%s-vs-tests" % g)
    finally:
        shutil.rmtree(work, ignore_errors=True)
    print("REBUILD", "OK" if ok else "FAILED")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
