# Lead and Copper Tap Monitoring Compliance

State primacy unit brief. The agent reconstructs Lead and Copper Rule
compliance for community water systems from raw submittals and writes one
compliance table per case. The governing text is the EPA Lead and Copper
Rule excerpts reproduced in `environment/data/reference/lcr_excerpts.pdf`;
the instruction brief states the office practice that controls where the
rule is silent.

## Difficulty

Each graded case turns on one procedural convention that runs against the
reader's first instinct, and each convention moves at least one graded
value well beyond the 0.0001 tolerance. The five sample branch averages
the two highest results, so graded_01 reports 0.0095 where the maximum
reads 0.0110, a fifteen times tolerance miss that also flips the finding.
Below five samples the percentile is the maximum and the shortfall still
raises the monitoring flag, which graded_02 exercises at three samples
against a required ten. Tier filtering is evaluated separately per
contaminant, so active Tier 1 lead sites displace every Tier 2 lead result
while copper tiers keep all six sites, which graded_03 exercises to hold
the lead percentile at 0.0080 instead of 0.0280. Sequential pair sites use
the fifth liter only and drop half pairs outright, which graded_04
exercises to hold five lead samples at 0.0095 instead of admitting 0.0300
first liters. An invalid mark without a matching dated approval counts as
reported, so graded_05 holds PWS106 at 0.0500 while the approved PWS105
sits at 0.0090. The reduced annual schedule requires a prior period
exceedance under the office convention, which graded_06 exercises across a
population move, an expired triennial approval, and a recomputed prior
exceedance to land March at REDUCED_ANNUAL.

## Reference solution

`solution/solve.py` parses both result sources and unions them by
sample identifier, normalizes units and qualifiers, joins to inventory,
applies the invalidation approval test, filters tiers separately per
contaminant, selects the compliance liter for sequential lead sites, and
computes the ordered percentile chain with Decimal arithmetic rounded half
up to four places. It then derives the required minimum from the rule
table with the covering reduction approval, evaluates the schedule
conventions including the prior two period test recomputed from raw data,
and emits the followup flags in fixed order. `solution/solve.sh` stages
the reference into place and smoke runs it on the settled cases.
`authoring/provenance/verify_rebuild.py` regenerates the cases and the
reference PDF from the seeds and confirms they match the committed trees,
and `authoring/provenance/sha256_cases.txt` pins every input file.

## Verification

`tests/test_outputs.py` with `tests/conftest.py` stages each graded case
fresh under `/app`, runs the submitted `/app/solve.py` with a time limit,
and keys every output row by system plus period plus contaminant with
order free. Missing rows, duplicated keys, unknown keys, and nonnumeric
percentiles fail the case. Percentiles must match within 0.0001 and every
other column must match exactly, including token order in the followup
column. `tests/expected.json` holds the oracle rows. `tests/test.sh` runs
the suite and emits CTRF. Reward is 1 only when every row of every case
passes.
