"""Blind probe C: representative agent attempt that judges exceedance by
the point estimate instead of the UCL95. Expected: REWARD 0 on graded_05.
"""
import os
import re
import sys

SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   "..", "..", "..", "solution", "solve.py")
text = open(SRC).read()
text = text.replace("exc = \"YES\" if ucl > AL[cont] else \"NO\"",
                    "exc = \"YES\" if p90 > AL[cont] else \"NO\"")
ns = {}
exec(compile(text, SRC, "exec"), ns)
ns["main"]()
