# Lead 90th-Percentile Estimation from Censored Tap Data

Taxonomy: TB-Science domain `Science`, field `Earth`; repository track `science-environmental-sciences` (environmental water-quality compliance).

State primacy unit brief. The agent estimates the 90th percentile of lead
and copper tap concentrations from censored monitoring data with sampling
uncertainty, writing one estimate table per case. The governing text is the
method note in `environment/data/reference/lcr_ros_method.pdf`; the
instruction brief states the office practice that controls where the note
is silent.

## Difficulty

Each graded case turns on one procedural convention that runs against the
reader's first instinct, and each convention moves at least one graded
value well beyond the 0.0001 tolerance. Per-row unit conversion divides
each ug/L value by 1000 by its own unit, so graded_01 reports a lead
UCL95 of 0.0087 where reading every value as mg/L reports 119.05. Censor
flags treat U and <-qualified limits as censored while J and B stay
detects, so graded_02 holds the lead UCL95 at 0.0063 instead of 0.0104.
Tie order ranks a censored limit below a detect at the same value, so
graded_03 reports p90 0.0095 and UCL95 0.0168 instead of 0.0150 and 0.0331.
Reported zeros are censored observations that stay in n, so graded_04
holds n=9 with UCL95 0.0092 instead of n=5 with 0.0102, which also flips
the finding. The exceedance test reads the UCL95, not the point estimate,
so graded_05 reports YES with p90 0.0096 below the action level and UCL95
0.0146 above it. The edge cells report the minimum limit when all rows are
censored, the lone detect among limits, the single row value at n=1, and
0.0000 for an empty roster cell, which graded_06 exercises together with
blank-value and off-contaminant rows that never count.

## Reference solution

`solution/solve.py` groups usable results by system, period, and
contaminant, converts units per row, marks censored rows, sorts jointly
with censored-below-detect ties, fits OLS on log-detects at Cunnane normal
quantiles, imputes censored ranks, and reports p90 with the delta-method
UCL95, half up to four places. `solution/solve.sh` stages the reference
into place and smoke runs it on the settled cases.
`authoring/provenance/verify_rebuild.py` regenerates the cases and the
reference PDF from the seeds and confirms they match the committed trees,
and `authoring/provenance/sha256_cases.txt` pins every input file.

## Verification

`tests/test_outputs.py` with `tests/conftest.py` stages each graded case
fresh under `/app`, runs the submitted `/app/solve.py` with a time limit,
and keys every output row by system plus period plus contaminant with
order free. Missing rows, duplicated keys, unknown keys, and nonnumeric
p90/UCL95 values fail the case. p90 and UCL95 must each match within
0.0001 and every other column must match exactly. `tests/expected.json`
holds the oracle rows. `tests/test.sh` runs the suite and emits CTRF.
Reward is 1 only when every row of every case passes.
