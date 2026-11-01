# Input field description

Each case directory (for example `/app/data/settled_01`) holds five input
files. The brief in `instruction.md` governs every choice; this note only
describes the fields.

- `systems.csv` with header `system_id,period,population_served`. One row
  per public water system and monitoring period. `period` is `YYYYMM`.
  Population changes mid record move the system across minimum count rows.
- `inventory.csv` with header
  `system_id,site_id,tier_lead,tier_copper,active,service_status,requires_pair`.
  Tiers are `T1`, `T2`, `T3`. `active` is `Y` or `N`. `service_status` is one
  of `ACTIVE`, `REFUSED`, `INACCESSIBLE`, `DEMOLISHED`. `requires_pair` is
  `Y` when the site has a lead service line under approved sequential
  sampling and must submit a first liter plus a fifth liter pair, else `N`.
- `results.csv` with header
  `system_id,site_id,sample_id,period,contaminant,liter,value,unit,qualifier,invalid_flag,collection_date`.
  `contaminant` is `LEAD` or `COPPER`. `liter` is `1`, `5`, or `NA`.
  `value` is numeric as reported. `unit` is `mg/L` or `ug/L`. `qualifier`
  is empty, `J`, `B`, `U`, or of the form `<MDL` such as `<0.001`.
  `invalid_flag` is `Y` or `N`. `collection_date` is `YYYY-MM-DD`.
- `legacy.txt`, a fixed width legacy export with one record per line:
  `system_id(0:8) site_id(8:16) sample_id(16:26) period(26:32)
  contaminant(32:38) liter(38:40) value(40:52) unit(52:60)
  qualifier(60:64) invalid_flag(64:65) date(65:75)`.
  Values are right justified within each field. The two source files carry
  disjoint records, keyed by `sample_id`; parse both and union all records.
- `approvals.csv` with header
  `system_id,sample_id,approval_type,effective_date,expiry_date`.
  `approval_type` is one of `INVALIDATION`, `ANNUAL`, `TRIENNIAL`. For
  `INVALIDATION` the `sample_id` names the invalidated sample; for `ANNUAL`
  and `TRIENNIAL` the `sample_id` is `ALL`.

Settled cases additionally carry `<case>_signed.csv`, the unit's finished
compliance table for that case, for the agent's own checking only. The
`reference/` directory holds the governing rule excerpts and is not a case.
