# Ablation 06: Burnout Meaningfulness

Status: Complete.

## Objective
Assess whether burnout is meaningful without forcing results, using metric-only analysis on existing outputs.

## Inputs Used
- version_delta/results_100/delta_simulation_records.csv
- version_delta/results_100/delta_run_metrics.csv
- version_delta/ablations/02_peak_days_1_30/
- version_delta/ablations/04_gamma_005_100/ablation04_simulation_records.csv
- version_delta/ablations/04_gamma_005_100/ablation04_run_metrics.csv

## Exact Changes From Core Delta
- No core changes. Metric-only analysis on existing simulation records for core delta and gamma=0.05.

## Files Generated
- version_delta/ablations/06_burnout_meaningfulness/ablation06_core_burnout_metrics.csv
- version_delta/ablations/06_burnout_meaningfulness/ablation06_core_summary.csv
- version_delta/ablations/06_burnout_meaningfulness/ablation06_core_paired_differences.csv
- version_delta/ablations/06_burnout_meaningfulness/ablation06_core_paired_summary.csv
- version_delta/ablations/06_burnout_meaningfulness/ablation06_core_threshold_sensitivity.csv
- version_delta/ablations/06_burnout_meaningfulness/ablation06_gamma005_burnout_metrics.csv
- version_delta/ablations/06_burnout_meaningfulness/ablation06_gamma005_summary.csv
- version_delta/ablations/06_burnout_meaningfulness/ablation06_gamma005_paired_differences.csv
- version_delta/ablations/06_burnout_meaningfulness/ablation06_gamma005_paired_summary.csv
- version_delta/ablations/06_burnout_meaningfulness/ablation06_gamma005_threshold_sensitivity.csv
- version_delta/ablations/06_burnout_meaningfulness/ablation06_threshold_sensitivity.csv
- version_delta/ablations/06_burnout_meaningfulness/ablation06_summary.json

## Metrics Computed
- Day-30 burnout count, peak burnout days 1-30, ever-burnout days 1-30
- Severe exposure: severe agent-days, persistent 3-day burnout counts, consecutive 2-day burnout counts
- Tail stress: day-30 p90/p95, day-30 top-10% mean, days 1-30 p95
- Severe stress burden (sum of stress above 80)

## Results
Core delta (100 nodes):
- Baseline day-30 burnout mean 0.167 vs intervention 0.133 (paired diff 0.033).
- Severe agent-days mean 3.667 vs 3.467 (paired diff 0.200).
- Severe stress burden mean 0.603 vs 0.548 (paired diff 0.055).
- Tail stress reductions: day-30 p95 diff 1.067; top-10% mean diff 0.786; days 1-30 p95 diff 0.859.
- Peak/ever burnout days 1-30 unchanged (paired diff 0.0).

Gamma=0.05 (100 nodes):
- Baseline day-30 burnout mean 0.967 vs intervention 0.967 (paired diff 0.000).
- Severe agent-days mean 21.5 vs 19.833 (paired diff 1.667).
- Severe stress burden mean 100.106 vs 97.888 (paired diff 2.218).
- Tail stress reductions: day-30 p95 diff 1.130; top-10% mean diff 0.815; days 1-30 p95 diff 1.060.
- Peak/ever burnout days 1-30 reduced (paired diffs 0.267 and 0.233).

Threshold sensitivity: Skipped for both datasets because threshold-80 metrics are non-zero and do not require recalibration.

Final Recommendation Label: Use severe-stress exposure instead of final-day burnout.

## Interpretation
- Core delta has rare day-30 burnout, but non-zero severe exposure and tail stress; the intervention signal shows up more consistently in severe-stress exposure than in day-30 burnout.
- Gamma=0.05 produces high burnout counts but day-30 burnout does not respond to intervention, while severe exposure and tail metrics still show reductions.
- Burnout presence is not a stable endpoint; severe-stress exposure is a more meaningful outcome for intervention effects.

## Limitations
- Metric-only; no new simulations or model changes.
- Results are constrained to 100-node runs and the existing gamma=0.05 ablation.

## Hallucination Check
- Numbers from saved artifacts: Yes (ablation06_summary.json, CSVs listed above).
- P-values computed: No.
- Core Delta files modified: No.
- Safe to cite in final report: Yes.

## Revert Instructions
Delete this folder and remove the change-log entry for this ablation.
