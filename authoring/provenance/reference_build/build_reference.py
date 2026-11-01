import sys, os, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ref_common import PAGES, build_pdf

if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "lcr_excerpts.pdf"
    build_pdf(out, PAGES)
    print("wrote", out)
