import json
import pandas as pd

# Load targeting strategy comparison
with open('scenarioRandom/targeting_strategy_comparison.json') as f:
    data = json.load(f)

print('TARGETING STRATEGY COMPARISON (from JSON):')
strategies = data['strategies']
for strat_name, strat_data in strategies.items():
    print(f'\n{strat_name.upper()}:')
    for key, val in strat_data.items():
        print(f'  {key}: {val}')

# Load CSV for more details
targeting_results = pd.read_csv('scenarioRandom/targeting_strategy_results.csv')
print('\n\nTARGETING STRATEGY RESULTS (from CSV):')
print(targeting_results.to_string())

# Compare against report Table 3
print('\n\nREPORT TABLE 3 CLAIMS vs ACTUAL:')
print('\nTOP INFLUENCERS:')
print(f'  Report: Avg Degree 10.8 (should be from agents [32, 85, 78, 59, 66] with degrees [12, 11, 10, 10, 11])')
print(f'  Avg calculated: {(12+11+10+10+11)/5:.1f}')
print(f'  Report: Final Stress 40.09 (Best) - Actual: {strategies["top_influencers"]["final_stress"]}')
print(f'  Report: Burnout Cases 3.60 (Worst) - Actual: {strategies["top_influencers"]["burnout_count"]}')

print('\nRANDOM:')
print(f'  Report: Avg Degree 5.4 - Actual: needs calculation')
random_agents = strategies['random_agents']['agent_ids']
print(f'  Random agent IDs: {random_agents}')
print(f'  Report: Final Stress 41.00 - Actual: {strategies["random_agents"]["final_stress"]}')
print(f'  Report: Burnout Cases 3.40 - Actual: {strategies["random_agents"]["burnout_count"]}')

print('\nLOW DEGREE (ISOLATED):')
print(f'  Report: Avg Degree 2.0 - Actual: needs calculation')
isolated_agents = strategies['low_degree']['agent_ids']
print(f'  Isolated agent IDs: {isolated_agents}')
print(f'  Report: Final Stress 41.62 (Worst) - Actual: {strategies["low_degree"]["final_stress"]}')
print(f'  Report: Burnout Cases 3.20 (Best) - Actual: {strategies["low_degree"]["burnout_count"]}')
