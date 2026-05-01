#!/usr/bin/env python
import pandas as pd
import numpy as np
import json

# Load agent cohort
agents = pd.read_csv('analysis/agent_cohort.csv')

# Count personas
print('PERSONA DISTRIBUTION FROM AGENT COHORT:')
total = len(agents)
for persona in ['Minimalist', 'Moderate User', 'Active User', 'Heavy User', 'Digital Addict']:
    count = len(agents[agents['persona'] == persona])
    pct = (count / total) * 100
    print(f'{persona}: {count} ({pct:.1f}%)')

# Check persona stats
print('\n\nPERSONA STATISTICS FROM AGENT COHORT:')
for persona in ['Minimalist', 'Moderate User', 'Active User', 'Heavy User', 'Digital Addict']:
    data = agents[agents['persona'] == persona]
    print(f'\n{persona}:')
    print(f'  Count: {len(data)}')
    print(f'  Screen Time: {data["screen_time"].mean():.1f} ± {data["screen_time"].std():.1f} hrs/day')
    print(f'  App Usage: {data["app_usage"].mean():.0f} ± {data["app_usage"].std():.0f} min/day')

# Load simulation results to check if values match report
print('\n\nSIMULATION RESULTS TO VERIFY:')
baseline_metrics = pd.read_csv('analysis/metrics_baseline_all_runs.csv')
intervention_metrics = pd.read_csv('analysis/metrics_intervention_all_runs.csv')

print('Baseline final stress:')
print(baseline_metrics['final_mean_stress'].describe())
print('\nIntervention final stress:')
print(intervention_metrics['final_mean_stress'].describe())

# Check if any result file contains burnout numbers
print('\n\nFiles in analysis/:')
import os
for f in sorted(os.listdir('analysis/')):
    print(f)
