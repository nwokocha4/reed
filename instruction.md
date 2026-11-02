# Lead ROS estimates
Estimate the 90th percentile per cell from censored tap data; one table per case. Method authority: /app/data/reference/lcr_ros_method.pdf (Cunnane, per-row units, delta UCL). PDF wins if silent; practice wins if stated.
Cases in /app/data (reference/ excluded); settled have signed sheets. Files: systems (roster), results (single source).
Cells: roster system+period x LEAD,COPPER; other periods/contaminants never count. Unparseable/blank values skipped, not censored.
Units: ug/L /1000 per row by its own unit; mixed units. Censored if qualifier U or <, or conc<=0; J/B are detects. Counts: n rows used, n_censored among them.
Order: joint ascending conc; censored below detect at ties. z=Cunnane (i-0.4)/(n+0.2). Line: OLS log-detects on z (detects only). Impute each censored at own z. mu mean, sigma sample sd (n-1) of completed logs. p90=exp(mu+z.90*sigma); se=sigma*sqrt(1/n+z.90^2/(2(n-1))); UCL95=exp(mu+z.90*sigma+z.95*se).
Edges: empty=0.0000/0.0000 n0; all-censored=min limit both; single detect=its value both; n=1 row value both; sigma0 UCL=p90. Half-up 4dp. Exceed if UCL>0.010 lead, >1.3 copper (p90 never decides).
Run python3 /app/solve.py; write /app/output/<case>_estimate.csv header system_id,period,contaminant,n,n_censored,p90_mg_per_L,ucl95_mg_per_L,exceedance. Key system+period+contaminant. Missing/dup/unknown/nonnumeric fail. p90+UCL tol 0.0001; else exact.
You have 28800 seconds. Do not cheat.
