# Ablation 02: Peak Metrics for Days 1-30

Status: Run complete.

## Objective
Recompute peak stress and peak burnout excluding day 0 initialization.

## Inputs Used
- version_delta/delta_report.md
- version_delta/results_100/
- version_delta/results_1000/

## Exact Changes From Core Delta
- No core Delta files modified.
- Peaks recomputed for days 1-30 using existing simulation records.

## Files Generated
- ablation02_results.json
- ablation02_results_100_peaks_by_run.csv
- ablation02_results_100_summary.csv
- ablation02_results_100_paired_differences.csv
- ablation02_results_1000_peaks_by_run.csv
- ablation02_results_1000_summary.csv
- ablation02_results_1000_paired_differences.csv
- run_ablation_02.py

## Metrics Computed
- Peak stress days 1-30
- Peak burnout count days 1-30
- Day of peak stress days 1-30
- Day of peak burnout days 1-30
- Paired differences (baseline - intervention)

## Results
Results (days 1-30 only):

results_100:
- Baseline peak stress mean: 79.987
- Intervention peak stress mean: 79.973
- Baseline peak burnout mean: 0.467
- Intervention peak burnout mean: 0.467
- Paired peak stress difference mean: 0.014
- Paired peak burnout difference mean: 0.000

results_1000:
- Baseline peak stress mean: 80.357
- Intervention peak stress mean: 80.357
- Baseline peak burnout mean: 0.700
- Intervention peak burnout mean: 0.700
- Paired peak stress difference mean: 0.000
- Paired peak burnout difference mean: 0.000

All numeric results are from ablation02_results.json.

## Interpretation
Day 1-30 peak metrics remove day-0 initialization effects. Peaks are similar between baseline and intervention.
Final report should prefer day-30 burnout and day-1-to-day-30 peak metrics instead of day-0-included peaks.

## Limitations
- Peaks are computed from existing Delta outputs only; no rerun was performed.
- Peak metrics are sensitive to rare stress spikes and should be interpreted cautiously.

## Hallucination Check
- Numbers from saved artifacts: Yes (ablation02_results.json and CSV outputs).
- P-values computed: No.
- Core Delta files modified: No.
- Safe to cite in final report: Yes, as supplementary analysis.

## Revert Instructions
Delete this folder and remove the change-log entry for this ablation.
