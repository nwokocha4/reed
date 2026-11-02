"""Blind probe B: representative agent attempt that treats every row as a
detect and ignores censor flags. Expected: REWARD 0 on graded_02.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "..", "..", "solution"))
import solve as ref


def is_censored(qualifier):
    return False


ref.is_censored = is_censored
ref.main()
