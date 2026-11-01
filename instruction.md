# Lead and Copper Tap Monitoring Compliance

Your program reconstructs Lead and Copper Rule compliance and writes one compliance table per case.

## 1. Governing standard

The governing text is 40 CFR 141.80(c)(3) plus 141.86(a) through 141.86(e), as reproduced in `/app/data/reference/lcr_excerpts.pdf`, which also carries the required minimum sample count table and the Nevada worked example. The PDF controls where this brief is silent. Office practice below controls where stated.

## 2. Inputs

Each case is a directory under `/app/data`. `settled_01` and `settled_02` each carry a `<case>_signed.csv` finished table for your own checking only. Every case directory holds:

- `systems.csv`, header `system_id,period,population_served`. One row per system and monitoring period (`YYYYMM`). Population can change mid record.
- `inventory.csv`, header `system_id,site_id,tier_lead,tier_copper,active,service_status,requires_pair`. Tiers `T1`,`T2`,`T3`; `active` `Y`/`N`; `service_status` one of `ACTIVE`,`REFUSED`,`INACCESSIBLE`,`DEMOLISHED`. `requires_pair` `Y` means approved sequential lead site needing a first plus fifth liter pair. Copper always uses liter `NA`.
- `results.csv`, header `system_id,site_id,sample_id,period,contaminant,liter,value,unit,qualifier,invalid_flag,collection_date`. `contaminant` `LEAD`/`COPPER`; `liter` `1`,`5`,`NA`; `unit` `mg/L`/`ug/L`; `qualifier` empty,`J`,`B`,`U`, or `<MDL`; `collection_date` `YYYY-MM-DD`.
- `legacy.txt`, fixed width: `system_id(0:8) site_id(8:16) sample_id(16:26) period(26:32) contaminant(32:38) liter(38:40) value(40:52) unit(52:60) qualifier(60:64) invalid_flag(64:65) date(65:75)`. The two sources hold disjoint records keyed by `sample_id`; parse both and union them.
- `approvals.csv`, header `system_id,sample_id,approval_type,effective_date,expiry_date`. Types `INVALIDATION`,`ANNUAL`,`TRIENNIAL`. `INVALIDATION` names the sample; reduction rows use `ALL`.

Convert `ug/L` to mg/L by dividing by 1000. Results flagged `U` or with `<` become zero and rank lowest. `J` and `B` are used as reported. The `REDUCED_ANNUAL` convention below departs from expectation; apply it as written.

## 3. Eligibility (office practice, in this order)

Apply every factor, limit, and alternative selection whose conditions are met. Dropped records never count. Nothing here is optional.

1. Normalize units and qualifiers as above.
2. Join results to inventory on `system_id` plus `site_id`; drop unmatched records.
3. A record with `invalid_flag` `Y` is excluded only with a matching `INVALIDATION` approval (equal `system_id` and `sample_id`, collection date within `effective_date` to `expiry_date`). Otherwise it counts.
4. Tier filtering runs separately per contaminant, system, and period. Keep only samples from the highest tier having at least one active-service site (`active` `Y` and `service_status` `ACTIVE`). Lower tiers are dropped entirely.
5. Liter selection is lead only. At `requires_pair` `Y` sites the fifth liter is the compliance sample and the first is informational; a lone liter excludes the site. Other lead sites and all copper use the `NA` record.
6. Survivors per system, period, and contaminant form `eligible_n`.

## 4. Percentile and exceedance

Test small counts first. Zero gives `0.0000`, no exceedance, plus a monitoring violation. Below five the percentile is the maximum. At five it is the average of the two highest. Above five it is the `ceiling(eligible_n * 0.9)`-th value (1 based) of the ascending list. Break ties by `site_id`, then `collection_date`. Compute in full precision, round half up to four decimals. Exceedance is strict greater than on the rounded value against 0.010 mg/L lead and 1.3 mg/L copper; equality is compliant. Write `YES` or `NO`.

## 5. Minimum count, schedule, followup

Take the minimum table strictly from the PDF; this brief restates no row. Use the standard column unless a reduction approval covers the period (period start within `effective_date` to `expiry_date`); where annual and triennial both cover a period, triennial governs when its conditions hold. The minimum sets the violation flag only, never the percentile. Prior two periods are the two preceding periods present; gaps create none, and missing early periods count compliant while still requiring an approval.

- `STANDARD_SEMIANNUAL`: current exceedance, or a violation that period, or the default with no applicable reduction.
- `REDUCED_ANNUAL`: no exceedance, no violation, annual approval on file, plus at least one exceedance in the prior two periods.
- `REDUCED_TRIENNIAL`: no exceedance, no violation, triennial approval on file, plus no exceedance in current and prior two periods.
- Followup: `NONE` alone; `MON_VIOLATION` when the minimum is unmet (schedule stays `STANDARD_SEMIANNUAL`); `PE` and `SLR` only on the lead row after a lead exceedance; `WQP` on the exceeding contaminant row only. Join as `MON_VIOLATION|PE|SLR|WQP`; `NONE` never combines.

## 6. Run, outputs, grading

Run `python3 /app/solve.py`. It reads every case directory directly under `/app/data` except `reference` and writes `/app/output/<case>_compliance.csv` with header `system_id,period,contaminant,eligible_n,percentile_mg_per_L,exceedance,schedule,followup`. Row key is system plus period plus contaminant, order free. Missing, duplicated, unknown, or nonnumeric rows fail. Percentile tolerance is 0.0001; counts are exact integers; strings and token order are exact.

You have 28800 seconds to complete this task. Do not cheat by using online solutions or hints specific to this task.
