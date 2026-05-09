# Ablation 04: Gamma 0.05 (100 Nodes)

Status: Run complete.

## Objective
Test gamma=0.05 on the 100-node network while keeping all other parameters unchanged.

## Inputs Used
- version_delta/plan2.md
- version_delta/delta_report.md
- version_delta/results_100/
- analysis/persona_definitions.json

## Exact Changes From Core Delta
- Gamma changed from 0.10 to 0.05.
- Topology and targets loaded from version_delta/results_100 outputs.

## Files Generated
- ablation04_simulation_records.csv
- ablation04_run_metrics.csv
- ablation04_aggregated_metrics.json
- ablation04_daily_summary.csv
- ablation04_trajectory.png
- ablation04_burnout.png
- ablation04_targets.json
- run_ablation_04.py

## Metrics Computed
- final mean stress
- final max stress
- day-30 burnout count
- day-1-to-day-30 peak burnout count
- total stress AUC
- final mean usage
- paired baseline-intervention differences

## Results
Gamma 0.05 (100 nodes, 30 runs):
- Final mean stress (baseline): 38.088
- Final mean stress (intervention): 35.545
- Final mean stress difference: 2.543 (baseline - intervention)
- Final mean stress reduction: 6.677%
- Day-30 burnout mean (baseline): 0.967
- Day-30 burnout mean (intervention): 0.967
- Peak burnout count (days 1-30) mean (baseline): 1.300
- Peak burnout count (days 1-30) mean (intervention): 1.033
- Total stress AUC difference: 4796.557 (baseline - intervention)

Comparison to core Delta gamma 0.10 (from version_delta/results_100/delta_aggregated_metrics.json):
- Day-30 burnout mean increased (baseline 0.167 → 0.967; intervention 0.133 → 0.967).
- Final mean stress reduction direction is stable (baseline > intervention in both).

## Interpretation
Gamma 0.05 increases day-30 burnout counts compared to the core gamma 0.10 run.
Intervention still reduces final mean stress and total stress AUC, so the effect direction remains stable.
This is a calibration ablation only and does not change the core Delta default.

## Limitations
- Uses the fixed 100-node topology and targets from core Delta outputs.
- Day-30 burnout remains a low-count metric; treat absolute values cautiously.

## Hallucination Check
- Numbers from saved artifacts: Yes (ablation04_aggregated_metrics.json, core delta_aggregated_metrics.json).
- P-values computed: No.
- Core Delta files modified: No.
- Safe to cite in final report: Yes, as calibration ablation.

## Revert Instructions
Delete this folder and remove the change-log entry for this ablation.
