# Lead and Copper Tap Monitoring Compliance — State Primacy Unit Brief

You are supporting the state primacy agency drinking water compliance unit. Your program reconstructs Lead and
Copper Rule compliance for community water systems from raw submittals and writes one compliance table per case.

## 1. Governing standard and where it lives

The governing text is the EPA Lead and Copper Rule at 40 CFR 141.80(c)(3) plus 141.86(a) through 141.86(e),
vintage as reproduced in `/app/data/reference/lcr_excerpts.pdf`. That PDF also carries the required minimum
sample count table by population served and the Nevada state guidance worked example. The PDF controls where
this brief is silent. Where this brief states an office practice, the office practice controls.

## 2. Inputs (absolute paths)

Each case is a directory under `/app/data`, for example `/app/data/settled_01`. Two cases are settled work
the unit has already closed: `settled_01` and `settled_02`. Each of those two carries a sheet the unit
signed, named `<case>_signed.csv`, holding the finished compliance table for that case. The signed sheets
are for your own checking only. Every case directory contains these input files:

- `systems.csv` with header `system_id,period,population_served`. One row per public water system
  and monitoring period. Population changes mid record move the system across minimum count rows.
- `inventory.csv` with header
  `system_id,site_id,tier_lead,tier_copper,active,service_status,requires_pair`.
  Tiers are `T1`, `T2`, `T3`. `active` is `Y` or `N`. `service_status` is one of
  `ACTIVE`, `REFUSED`, `INACCESSIBLE`, `DEMOLISHED`. `requires_pair` is `Y` when the site has a lead
  service line under approved sequential sampling and must submit a first liter plus a fifth liter pair,
  else `N`. The pair rule is a lead rule only. Copper is always a single sample and carries liter `NA`
  even at a site with `requires_pair` equal to `Y`.
- `results.csv` with header
  `system_id,site_id,sample_id,period,contaminant,liter,value,unit,qualifier,invalid_flag,collection_date`.
  `period` is `YYYYMM`. `contaminant` is `LEAD` or `COPPER`. `liter` is `1`, `5`, or `NA`.
  `value` is numeric as reported. `unit` is `mg/L` or `ug/L`. `qualifier` is empty, `J`, `B`, `U`,
  or of the form `<MDL` such as `<0.001`. `invalid_flag` is `Y` or `N`. `collection_date` is `YYYY-MM-DD`.
- `legacy.txt`, a fixed width legacy export with one record per line, fields
  `system_id(0:8) site_id(8:16) sample_id(16:26) period(26:32) contaminant(32:38) liter(38:40)`
  `value(40:52) unit(52:60) qualifier(60:64) invalid_flag(64:65) date(65:75)`.
  Values are right justified within each field. `contaminant` is padded, for example `LEAD  `.
  `unit` is `mg/L` or `ug/L` padded. The two source files carry disjoint records, keyed by `sample_id`.
  A record appears in exactly one of them. Parse both files and union all records, then treat the union
  as the only list of results.
- `approvals.csv` with header `system_id,sample_id,approval_type,effective_date,expiry_date`.
  `approval_type` is one of `INVALIDATION`, `ANNUAL`, `TRIENNIAL`.
  For `INVALIDATION` the `sample_id` names the invalidated sample and dates bound the approval.
  For `ANNUAL` and `TRIENNIAL` the `sample_id` is `ALL` and the dates bound the reduction approval.

All concentrations are converted to mg per L before calculation by dividing `ug/L` values by 1000.
A result flagged `U` or reported with a less than sign is replaced by zero for calculation and ranked lowest.
`J` and `B` flags are used as reported unless invalidated. The office REDUCED_ANNUAL convention below
deliberately departs from reader expectation and must be applied as written.

## 3. Eligibility pipeline (office practice, applied in this order)

Apply every factor, limit, and alternative selection whose conditions are met. Dropped records never count
toward counts. Nothing in this section is optional.

1. Normalize units and qualifiers to a common table as stated above.
2. Join each result to inventory on `system_id` plus `site_id`. Records with no inventory entry are dropped.
3. Exclusion by invalidation. A record with `invalid_flag` equal to `Y` is excluded only when a matching
   approval record exists with equal `system_id` and equal `sample_id` and with collection date on or
   after `effective_date` and on or before `expiry_date` and with type `INVALIDATION`. Any invalid
   marked record without such an approval is included as a valid result.
4. Tier filtering, evaluated separately for lead and copper within each system and period. Retain only
   samples from the highest tier for which at least one site with that tier for that contaminant is
   listed in inventory as active service for that period. Active service means `active` equals `Y` and
   `service_status` equals `ACTIVE`. Lower tier samples are dropped entirely and never count toward counts.
   A retained tier site with no result simply contributes nothing.
5. Liter selection, lead only. For lead at sites with `requires_pair` equal to `Y` the fifth liter result
   is the compliance sample and the first liter is informational only. When only one liter of a required
   pair is present the site is excluded entirely. The unselected liter never counts toward counts. Lead at
   sites with `N` and every copper record use the single `NA` liter record.
6. The surviving count per system plus period plus contaminant is `eligible_n`.

## 4. Percentile and exceedance

Compute the percentile by the following ordered chain. Test small counts first so ceiling ranking never
applies at five.

- When `eligible_n` is zero write `0.0000` with no exceedance and a monitoring violation flag.
- When `eligible_n` is below five the percentile is the maximum concentration.
- When `eligible_n` equals five the percentile is the average of the highest and second highest concentrations.
- Otherwise the percentile is the value at index equal to ceiling of `eligible_n` times 0.9, counted as
  1 based on the ascending ordered eligible list. Ties are ordered by `site_id` ascending then by
  `collection_date` ascending before ranks are assigned.

Perform arithmetic in full precision then round half up to four decimals for reporting. The exceedance test
applies strict greater than to that rounded value against 0.010 mg per L for lead and 1.3 mg per L for
copper. Equality is compliant. The exceedance column carries the exact token `YES` when the action level is
exceeded and `NO` otherwise. Graded cases exclude exact halfway values such as 0.01005 so rounding
convention is never the deciding factor.

## 5. Required minimum count, schedule, and follow up

Extract the required minimum sample count table strictly from the rule PDF in the reference folder. The
instruction restates no row of that table. Use the standard column unless a valid reduction approval covers
the period, in which case use the reduced column. An approval covers a period when period start falls on or
after `effective_date` and on or before `expiry_date`. When both an annual approval and a triennial approval
cover the same period, triennial controls when its conditions are met and annual applies only otherwise.
Reconstruction of required minimum count drives a monitoring violation flag and does not change the
percentile. At least one graded case changes population mid record so the tier moves, at least one
reduction approval expires mid record, at least one reduced monitoring minimum count is the applicable
threshold, and at least one prior period exceedance must be recomputed from raw data rather than read from
a status field.

Prior two periods means the two preceding periods present in that system record in time order. Gaps from
reduced schedules do not create phantom periods. Missing early periods at the start of a record are treated
as compliant with no exceedance for schedule tests, but a reduction approval is still required.

Schedule tokens appear only in the schedule column. Follow up tokens appear only in the followup column.

- `STANDARD_SEMIANNUAL` covers a current exceedance for that contaminant, a monitoring violation in that
  period, and the default when no reduction approval on file applies, including a system with no current
  exceedance and no prior exceedance and no approval.
- `REDUCED_ANNUAL` requires no current exceedance plus no violation plus annual approval on file plus at
  least one exceedance in the prior two periods under office convention as written.
- `REDUCED_TRIENNIAL` requires no current exceedance plus no violation plus triennial approval on file
  plus no exceedance in current and prior two periods.
- `NONE` means no follow up required and appears alone.
- `MON_VIOLATION` marks required minimum count not met, unapproved small counts, or zero eligible samples,
  with schedule remaining `STANDARD_SEMIANNUAL`.
- `PE` marks public education required and attaches only to the lead row after a lead exceedance.
- `SLR` marks service line replacement evaluation required and attaches only to the lead row after a lead
  exceedance.
- `WQP` marks water quality parameter monitoring required and attaches to the row of the contaminant that
  exceeded. A copper only exceedance therefore carries `WQP` on the copper row while the paired lead row
  carries `NONE`.

Multiple flags are joined by pipe in fixed order: monitoring violation first, then public education, then
service line evaluation, then water quality monitoring, for example `PE|SLR|WQP`. `NONE` never combines.

## 6. Run command, output files, tolerances, failure conditions

Run the program with `python3 /app/solve.py`. The program discovers every case directory directly under
`/app/data`, excluding the `reference` directory, parses all five input files in each case, and writes one
file per case to `/app/output/<case>_compliance.csv` with exact header
`system_id,period,contaminant,eligible_n,percentile_mg_per_L,exceedance,schedule,followup`.
Row keys are system identifier plus period plus contaminant with order free. Missing rows, duplicated keys,
unknown systems, and nonnumeric percentiles fail the case. Absolute tolerance is 0.0001 mg per L on
percentile values and it brackets only floating representation and the stated four decimal rounding, since
ranking and averaging are otherwise exact. The tolerance is tight enough that a maximum against an average
of the two highest cannot pass, because 0.0110 against 0.0095 differs by 0.0015, fifteen times the tolerance.
Eligible counts are exact integers with no tolerance. Period strings and contaminant strings and finding
strings are exact with no whitespace trimming and no case folding and token order is graded literally.

You have 28800 seconds to complete this task. Do not cheat by using online solutions or hints specific to this task.
