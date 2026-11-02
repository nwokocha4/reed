# Input field description

Each case directory (for example `/app/data/settled_01`) holds two input
files. The brief in `instruction.md` governs every choice; this note only
describes the fields.

- `systems.csv` with header `system_id,period,population_served`. One row
  per public water system and monitoring period. `period` is `YYYYMM`. This
  roster defines the reported cells: each roster row times LEAD and COPPER.
  Results rows for other periods never count.
- `results.csv` with header
  `system_id,site_id,sample_id,period,contaminant,liter,value,unit,qualifier,invalid_flag,collection_date`.
  `contaminant` is `LEAD` or `COPPER`; other values are ignored. `liter`
  is carried but unused. `value` is numeric as reported, possibly blank
  (the row is then skipped). `unit` is `mg/L` or `ug/L`, converted per row
  (`ug/L` divided by 1000). `qualifier` is empty, `J`, `B`, `U`, or of the
  form `<MDL`; `U` and `<` mark censored limits, `J`/`B`/empty are detects.
  `invalid_flag` and `collection_date` are carried but unused.

Settled cases additionally carry `<case>_signed.csv`, the unit's finished
estimate table for that case, for the agent's own checking only. The
`reference/` directory holds the governing method note and is not a case.
