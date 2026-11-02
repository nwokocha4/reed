# Lead ROS estimates
Estimate the 90th percentile per cell from censored tap data; one table per case. Method authority: /app/data/reference/lcr_ros_method.pdf, the office method note (sections 1-4). The note governs estimation; this brief covers only case, file, cell, and output mechanics.
Cases in /app/data (reference/ excluded); settled have signed sheets. Files: systems (roster), results (single source).
Cells: roster system+period x LEAD,COPPER; other periods/contaminants never count. Unparseable/blank values skipped, not censored.
Apply the office method note: per-row units (note §1), laboratory censor-flag convention (note §1), joint ordering with limit-below-detect ties (note §2), Cunnane plotting positions with OLS on log-detects and imputation at own rank (note §2), lognormal mean/sample-sd parameters with 90th percentile and delta-method UCL95 (notes §§2-3), and degenerate-cell reporting (note §4). Report p90 and UCL95 in mg/L half up to 4dp; counts n rows used, n_censored among them.
Exceedance follows the regulatory action levels: UCL95 above 0.010 lead or 1.3 copper; the point estimate alone never decides.
Run python3 /app/solve.py; write /app/output/<case>_estimate.csv header system_id,period,contaminant,n,n_censored,p90_mg_per_L,ucl95_mg_per_L,exceedance. Key system+period+contaminant. Missing/dup/unknown/nonnumeric fail. p90+UCL tol 0.0001; else exact.
You have 28800 seconds. Do not cheat.
