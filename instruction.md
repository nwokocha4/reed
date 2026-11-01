# Lead and Copper Tap Monitoring Compliance

Reconstruct Lead and Copper Rule compliance; write one compliance table per case.

## 1. Governing standard

Governing text is 40 CFR 141.80(c)(3) and 141.86(a)-(e) in `/app/data/reference/lcr_excerpts.pdf`, with the minimum count table and Nevada example. The PDF controls where silent; office practice below controls where stated.

## 2. Inputs

Each case is a directory under `/app/data`. `settled_01`/`settled_02` carry `<case>_signed.csv` for checking only. Each holds:

- `systems.csv`, header `system_id,period,population_served`. One row per system and period (`YYYYMM`); population can change mid record.
- `inventory.csv`, header `system_id,site_id,tier_lead,tier_copper,active,service_status,requires_pair`. Tiers `T1`,`T2`,`T3`; `active` `Y`/`N`; `service_status` one of `ACTIVE`,`REFUSED`,`INACCESSIBLE`,`DEMOLISHED`. `requires_pair` `Y` means sequential lead site needing first plus fifth liter pair. Copper always uses `NA`.
- `results.csv`, header `system_id,site_id,sample_id,period,contaminant,liter,value,unit,qualifier,invalid_flag,collection_date`. `contaminant` `LEAD`/`COPPER`; `liter` `1`,`5`,`NA`; `unit` `mg/L`/`ug/L`; `qualifier` empty,`J`,`B`,`U`, or `<MDL`; `collection_date` `YYYY-MM-DD`.
- `legacy.txt`, fixed width: `system_id(0:8) site_id(8:16) sample_id(16:26) period(26:32) contaminant(32:38) liter(38:40) value(40:52) unit(52:60) qualifier(60:64) invalid_flag(64:65) date(65:75)`. The two sources hold disjoint records keyed by `sample_id`; parse both and union them.
- `approvals.csv`, header `system_id,sample_id,approval_type,effective_date,expiry_date`. Types `INVALIDATION`,`ANNUAL`,`TRIENNIAL`. `INVALIDATION` names the sample; reduction rows use `ALL`.

`ug/L` values divide by 1000. `U` or `<` become zero and rank lowest. `J`/`B` are used as reported. Apply `REDUCED_ANNUAL` as written even though it departs from expectation.

## 3. Eligibility (office practice, in this order)

Apply every factor, limit, and alternative selection whose conditions are met. Dropped records never count; nothing is optional.

1. Normalize units and qualifiers as above.
2. Join results to inventory on `system_id` plus `site_id`; drop unmatched records.
3. `invalid_flag` `Y` is excluded only with matching `INVALIDATION` approval (equal `system_id`/`sample_id`, collection date within dates). Otherwise it counts.
4. Tier filtering runs separately per contaminant, system, period. Keep only the highest tier with an active-service site (`active` `Y`, `service_status` `ACTIVE`); drop lower tiers entirely.
5. Liter selection is lead only. At `requires_pair` `Y` sites the fifth liter counts and the first is informational; a lone liter excludes the site. All else uses `NA`.
6. Survivors per system, period, and contaminant form `eligible_n`.

## 4. Percentile and exceedance

Small counts first. Zero gives `0.0000`, no exceedance, plus violation. Below five use the maximum; at five average the two highest; above five use the `ceiling(eligible_n*0.9)`-th ascending value (1 based). Ties break by `site_id`, then `collection_date`. Full precision, round half up to four decimals. Exceedance is strictly greater than rounded 0.010 lead, 1.3 copper; equality complies. Write `YES`/`NO`.

## 5. Minimum count, schedule, followup

Take the minimum table strictly from the PDF; no row is restated here. Use standard unless a reduction covers the period (period start within dates); triennial governs where both cover and its conditions hold. Minimum sets the violation flag only. Prior two periods are the two preceding periods present; gaps create none; missing early periods count compliant but still need an approval.

- `STANDARD_SEMIANNUAL`: current exceedance, violation, or default with no reduction.
- `REDUCED_ANNUAL`: no exceedance, no violation, annual approval on file, plus at least one exceedance in the prior two periods.
- `REDUCED_TRIENNIAL`: no exceedance, no violation, triennial approval on file, plus no exceedance in current and prior two periods.
- Followup: `NONE` alone; `MON_VIOLATION` when minimum unmet (schedule stays `STANDARD_SEMIANNUAL`); `PE`/`SLR` only on lead row after lead exceedance; `WQP` on exceeding row only. Join as `MON_VIOLATION|PE|SLR|WQP`; `NONE` never combines.

## 6. Run, outputs, grading

Run `python3 /app/solve.py`. It reads each case under `/app/data` except `reference` and writes `/app/output/<case>_compliance.csv` with header `system_id,period,contaminant,eligible_n,percentile_mg_per_L,exceedance,schedule,followup`. Row key is system plus period plus contaminant, order free. Missing/duplicated/unknown/nonnumeric rows fail. Percentile tolerance 0.0001; counts exact; strings and token order exact.

You have 28800 seconds to complete this task. Do not cheat by using online solutions or hints specific to this task.
