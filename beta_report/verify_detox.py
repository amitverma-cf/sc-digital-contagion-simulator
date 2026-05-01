import pandas as pd
import numpy as np

# Load all data
baseline = pd.read_csv('analysis/metrics_baseline_all_runs.csv')
detox = pd.read_csv('scenarioDetox/detox_results_all_runs.csv')

baseline_stress = baseline['final_stress_mean'].mean()
detox_stress = detox['final_stress_mean'].mean()

baseline_burnout = baseline['burnout_count_final'].mean()
detox_burnout = detox['burnout_count'].mean()

stress_reduction_pct = ((baseline_stress - detox_stress) / baseline_stress) * 100
burnout_reduction_pct = ((baseline_burnout - detox_burnout) / baseline_burnout) * 100

print('DETOX SCENARIO VERIFICATION:')
print(f'\nBaseline final stress: {baseline_stress:.2f}')
print(f'Detox final stress: {detox_stress:.2f}')
print(f'Stress reduction: {stress_reduction_pct:.1f}%')

print(f'\nBaseline burnout: {baseline_burnout:.1f}')
print(f'Detox burnout: {detox_burnout:.1f}')
print(f'Burnout reduction: {burnout_reduction_pct:.1f}%')

print('\n\nREPORT CLAIMS vs ACTUAL:')
print(f'Report claims: Final stress 30.20 (29.1% reduction)')
print(f'Actual: Final stress {detox_stress:.2f} ({stress_reduction_pct:.1f}% reduction)')
print(f'MATCH: {abs(detox_stress - 30.20) < 0.5 and abs(stress_reduction_pct - 29.1) < 1.0}')

print(f'\nReport claims: Burnout cases 0.6 (89.7% reduction)')
print(f'Actual: Burnout cases {detox_burnout:.1f} ({burnout_reduction_pct:.1f}% reduction)')
print(f'MATCH: {abs(detox_burnout - 0.6) < 0.5 and abs(burnout_reduction_pct - 89.7) < 5.0}')
