# Ablation 01: 1000-Node LFR Mu Validation

Status: Run complete (no valid graph found).

## Objective
Fix or investigate the 1000-node LFR mixing validation issue where target mu=0.1 but measured mixing was higher.

## Inputs Used
- version_delta/plan2.md
- version_delta/delta_report.md
- version_delta/results_1000/
- analysis/persona_definitions.json

## Exact Changes From Core Delta
- No core Delta files modified.
- Only ablation-local LFR generation attempts were run.

## Files Generated
- ablation01_candidates.csv (candidate LFR metrics by seed)
- run_ablation_01.py (ablation script)

## Metrics Computed
- Actual mixing parameter per candidate seed
- Mean degree, edge count, connected components, community count, clustering coefficient per candidate seed

## Results
No candidate graph met the mixing tolerance requirement.

Summary:
- Target mixing parameter: 0.10
- Mixing tolerance: 0.05
- Seeds attempted: 42 to 81 (40 attempts)
- Accepted seed: None

Candidate metrics are saved in ablation01_candidates.csv. Typical measured mixing values were around 0.197 to 0.206, which exceeds the tolerance.

## Interpretation
The current 1000-node LFR configuration did not produce a valid graph within the tolerance after 40 attempts.
This ablation cannot replace the existing results_1000 output. Any 1000-node results remain exploratory unless a valid graph is generated.

## Limitations
- No valid 1000-node graph was accepted, so no simulations were run in this ablation.
- Candidate metrics are limited to the attempted seed range.

## Hallucination Check
- Numbers from saved artifacts: Yes (ablation01_candidates.csv).
- P-values computed: No.
- Core Delta files modified: No.
- Safe to cite in final report: No. No accepted graph or simulation outputs.

## Revert Instructions
Delete this folder and remove the change-log entry for this ablation.
