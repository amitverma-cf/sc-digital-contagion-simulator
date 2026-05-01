import pandas as pd
import numpy as np

baseline = pd.read_csv('analysis/metrics_baseline_all_runs.csv')
intervention = pd.read_csv('analysis/metrics_intervention_all_runs.csv')

print('BASELINE SCENARIO:')
print('Final stress mean (all runs):')
print('  ', baseline['final_stress_mean'].values)
print(f'  Mean: {baseline["final_stress_mean"].mean():.2f} ± {baseline["final_stress_mean"].std():.2f}')

print('\nBurnout count final (all runs):')
print('  ', baseline['burnout_count_final'].values)
print(f'  Mean: {baseline["burnout_count_final"].mean():.1f} ± {baseline["burnout_count_final"].std():.1f}')

print('\n\nINTERVENTION SCENARIO:')
print('Final stress mean (all runs):')
print('  ', intervention['final_stress_mean'].values)
print(f'  Mean: {intervention["final_stress_mean"].mean():.2f} ± {intervention["final_stress_mean"].std():.2f}')

print('\nBurnout count final (all runs):')
print('  ', intervention['burnout_count_final'].values)
print(f'  Mean: {intervention["burnout_count_final"].mean():.1f} ± {intervention["burnout_count_final"].std():.1f}')

# Calculate stress reduction
baseline_mean = baseline["final_stress_mean"].mean()
intervention_mean = intervention["final_stress_mean"].mean()
reduction_pct = ((baseline_mean - intervention_mean) / baseline_mean) * 100

print(f'\n\nSTRESS REDUCTION:')
print(f'  Baseline mean: {baseline_mean:.2f}')
print(f'  Intervention mean: {intervention_mean:.2f}')
print(f'  Reduction: {reduction_pct:.1f}%')

# Check burnout change
baseline_burnout = baseline["burnout_count_final"].mean()
intervention_burnout = intervention["burnout_count_final"].mean()
burnout_change_pct = ((intervention_burnout - baseline_burnout) / baseline_burnout) * 100

print(f'\n\nBURNOUT CHANGE:')
print(f'  Baseline: {baseline_burnout:.1f}')
print(f'  Intervention: {intervention_burnout:.1f}')
print(f'  Change: {burnout_change_pct:.1f}%')
