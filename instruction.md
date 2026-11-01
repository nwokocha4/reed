# LCR Compliance
Reconstruct compliance; one table per case. Governed by 40 CFR 141.80(c)(3),141.86(a)-(e) in /app/data/reference/lcr_excerpts.pdf (counts). PDF wins if silent; practice wins if stated.
Cases in /app/data; settled have signed sheets. Files: systems, inventory, results+legacy (disjoint, union), approvals (INVALIDATION names sample else ALL).
ug/L/1000; U/</0 lowest. Apply all rules; drops never count. Join on system+site. invalid Y out only with matching INVALIDATION in dates. Tier per contaminant: keep highest with active site. Lead pair Y: fifth counts; lone liter drops site; else NA. Survivors=eligible_n.
Pct: 0=0.0000+violation; <5 max; =5 mean top2; >5 ceil(n*.9)th ascending; ties site_id,date. Half-up 4dp. Exceed if >0.010 lead, >1.3 copper.
Minimum from PDF only; standard unless reduction covers period; triennial wins if holds. Minimum=violation only. Prior two=preceding present; gaps none; early missing compliant but need approval.
STANDARD if exceed/violation/default; ANNUAL if clean+annual+>=1 prior exceed; TRIENNIAL if clean+tri+clean current+prior2. Followup NONE alone; MON_VIOLATION if short; PE/SLR lead only; WQP exceeding only; join MON_VIOLATION|PE|SLR|WQP.
Run python3 /app/solve.py; write /app/output/<case>_compliance.csv header system_id,period,contaminant,eligible_n,percentile_mg_per_L,exceedance,schedule,followup. Key system+period+contaminant. Missing/dup/unknown/nonnumeric fail. Tol 0.0001; else exact.
You have 28800 seconds. Do not cheat.
