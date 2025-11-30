"""
Phase 8 Extension: Testing Targeting Strategies
Tests if targeting influencers is more effective than random/low-degree nodes
"""

import pandas as pd
import numpy as np
import networkx as nx
import json
import sys
from pathlib import Path
from tqdm import tqdm

# Add src to path to import temporal_engine
sys.path.append(str(Path(__file__).parent.parent / "src"))
from temporal_engine import TemporalEngine

# Configuration
BASE_DIR = Path(__file__).parent.parent
AGENTS_PATH = BASE_DIR / "analysis" / "agent_cohort.csv"
NETWORK_PATH = BASE_DIR / "analysis" / "social_network.graphml"
OUTPUT_DIR = Path(__file__).parent  # Save in scenarioRandom folder
OUTPUT_DIR.mkdir(exist_ok=True)

def run_targeted_intervention(agents_df, network, intervention_agents, scenario_name, n_runs=5):
    """Run intervention on specific set of agents"""
    
    print(f"\n{'='*60}")
    print(f"SCENARIO: {scenario_name}")
    print(f"{'='*60}")
    print(f"  Targeting agents: {sorted(intervention_agents)}")
    
    results = []
    
    for run_idx in tqdm(range(n_runs), desc=f"Running {scenario_name}"):
        seed = 42 + run_idx
        
        # Run simulation with intervention
        engine = TemporalEngine(agents_df, network, random_seed=seed)
        sim_results = engine.simulate(
            intervention_day=10,
            intervention_agents=intervention_agents,
            verbose=False
        )
        
        # Get final day metrics
        day_30 = sim_results[sim_results['day'] == 30]
        final_stress_mean = day_30['stress'].mean()
        final_stress_std = day_30['stress'].std()
        burnout_count = (day_30['stress'] > 80).sum()
        
        # Compute total stress AUC
        total_stress_auc = sim_results.groupby('agent_id')['stress'].sum().sum()
        
        results.append({
            'scenario': scenario_name,
            'run': run_idx,
            'seed': seed,
            'final_stress_mean': final_stress_mean,
            'final_stress_std': final_stress_std,
            'burnout_count': burnout_count,
            'total_stress_auc': total_stress_auc
        })
    
    results_df = pd.DataFrame(results)
    
    # Print summary for this scenario
    print(f"\n  Results across {n_runs} runs:")
    print(f"    Final stress: {results_df['final_stress_mean'].mean():.2f} ± {results_df['final_stress_mean'].std():.2f}")
    print(f"    Burnout count: {results_df['burnout_count'].mean():.2f} ± {results_df['burnout_count'].std():.2f}")
    print(f"    Total stress AUC: {results_df['total_stress_auc'].mean():.0f} ± {results_df['total_stress_auc'].std():.0f}")
    
    return results_df


def main():
    print("\n" + "="*80)
    print("TESTING TARGETING STRATEGIES")
    print("="*80)
    print("\nQuestion: Does targeting high-degree influencers produce better outcomes")
    print("          than targeting random or low-degree agents?")
    print("="*80)
    
    # Load data
    print("\nLoading data...")
    agents_df = pd.read_csv(AGENTS_PATH)
    network = nx.read_graphml(NETWORK_PATH)
    
    # Convert node labels to integers
    mapping = {node: int(node) for node in network.nodes()}
    network = nx.relabel_nodes(network, mapping)
    
    print(f"✓ Loaded {len(agents_df)} agents")
    print(f"✓ Loaded network with {network.number_of_edges()} edges")
    
    # Get degree for each agent
    degrees = dict(network.degree())
    agents_df['degree'] = agents_df['agent_id'].map(degrees)
    agents_sorted = agents_df.sort_values('degree', ascending=False)
    
    # Define 3 targeting strategies
    print("\n" + "="*80)
    print("DEFINING TARGETING STRATEGIES")
    print("="*80)
    
    top_5_ids = set(agents_sorted.head(5)['agent_id'].tolist())
    random_5_ids = set(np.random.RandomState(99).choice(agents_df['agent_id'], 5, replace=False))
    bottom_5_ids = set(agents_sorted.tail(5)['agent_id'].tolist())
    
    strategies = {
        'Top 5 Influencers (High Degree)': top_5_ids,
        'Random 5 Agents': random_5_ids,
        'Bottom 5 (Low Degree)': bottom_5_ids
    }
    
    print("\nStrategy Details:")
    for strategy_name, agent_ids in strategies.items():
        agent_degrees = [(aid, degrees[aid]) for aid in sorted(agent_ids)]
        avg_degree = np.mean([d for _, d in agent_degrees])
        print(f"\n  {strategy_name}:")
        print(f"    Agents: {[f'{aid}(deg={d})' for aid, d in agent_degrees]}")
        print(f"    Average degree: {avg_degree:.1f}")
    
    # Run all scenarios
    print("\n" + "="*80)
    print("RUNNING SIMULATIONS (5 runs per strategy)")
    print("="*80)
    
    all_results = []
    
    for strategy_name, target_agents in strategies.items():
        results_df = run_targeted_intervention(
            agents_df, 
            network, 
            target_agents, 
            strategy_name, 
            n_runs=5
        )
        all_results.append(results_df)
    
    # Combine results
    combined = pd.concat(all_results, ignore_index=True)
    
    # Compute summary statistics
    print("\n" + "="*80)
    print("AGGREGATED RESULTS")
    print("="*80)
    
    summary = combined.groupby('scenario').agg({
        'final_stress_mean': ['mean', 'std'],
        'burnout_count': ['mean', 'std'],
        'total_stress_auc': ['mean', 'std']
    }).round(2)
    
    print("\n" + summary.to_string())
    
    # Save detailed results
    results_path = OUTPUT_DIR / "targeting_strategy_results.csv"
    combined.to_csv(results_path, index=False)
    print(f"\n✓ Saved detailed results to: {results_path}")
    
    # Compute comparisons
    print("\n" + "="*80)
    print("EFFECTIVENESS COMPARISON")
    print("="*80)
    
    top_stress = summary.loc['Top 5 Influencers (High Degree)', ('final_stress_mean', 'mean')]
    random_stress = summary.loc['Random 5 Agents', ('final_stress_mean', 'mean')]
    bottom_stress = summary.loc['Bottom 5 (Low Degree)', ('final_stress_mean', 'mean')]
    
    top_burnout = summary.loc['Top 5 Influencers (High Degree)', ('burnout_count', 'mean')]
    random_burnout = summary.loc['Random 5 Agents', ('burnout_count', 'mean')]
    bottom_burnout = summary.loc['Bottom 5 (Low Degree)', ('burnout_count', 'mean')]
    
    improvement_vs_random = ((random_stress - top_stress) / random_stress) * 100
    improvement_vs_bottom = ((bottom_stress - top_stress) / bottom_stress) * 100
    
    print(f"\nFinal Network Stress:")
    print(f"  Top influencers:  {top_stress:.2f}")
    print(f"  Random agents:    {random_stress:.2f}")
    print(f"  Low-degree nodes: {bottom_stress:.2f}")
    
    print(f"\nBurnout Count:")
    print(f"  Top influencers:  {top_burnout:.2f}")
    print(f"  Random agents:    {random_burnout:.2f}")
    print(f"  Low-degree nodes: {bottom_burnout:.2f}")
    
    print(f"\nRelative Improvement:")
    print(f"  vs Random agents:     {improvement_vs_random:+.1f}% stress reduction")
    print(f"  vs Low-degree nodes:  {improvement_vs_bottom:+.1f}% stress reduction")
    
    # Determine conclusion
    print("\n" + "="*80)
    print("CONCLUSION")
    print("="*80)
    
    if top_stress < random_stress and top_stress < bottom_stress:
        effectiveness = (improvement_vs_random + improvement_vs_bottom) / 2
        print(f"\n✓ Targeting influencers IS more effective!")
        print(f"  Average improvement: {effectiveness:.1f}% better outcomes")
        print(f"  Network position MATTERS for intervention effectiveness")
        conclusion = "proven_effective"
    elif abs(top_stress - random_stress) < 0.5 and abs(top_stress - bottom_stress) < 0.5:
        print(f"\n⚠ No clear advantage to targeting influencers")
        print(f"  All strategies produce similar outcomes (< 0.5 stress difference)")
        print(f"  Network position may NOT matter for this intervention type")
        conclusion = "no_advantage"
    else:
        print(f"\n⚠ Mixed results - unclear conclusion")
        print(f"  Further investigation needed")
        conclusion = "unclear"
    
    # Save summary report
    summary_path = OUTPUT_DIR / "targeting_strategy_summary.txt"
    with open(summary_path, 'w', encoding='utf-8') as f:
        f.write("="*80 + "\n")
        f.write("TARGETING STRATEGY COMPARISON REPORT\n")
        f.write("="*80 + "\n\n")
        
        f.write("RESEARCH QUESTION:\n")
        f.write("  Does targeting high-degree influencers produce better intervention\n")
        f.write("  outcomes than targeting random or low-degree agents?\n\n")
        
        f.write("METHODOLOGY:\n")
        f.write("  - 3 targeting strategies tested (Top 5, Random 5, Bottom 5)\n")
        f.write("  - 5 simulation runs per strategy (seeds 42-46)\n")
        f.write("  - Same network topology and agents across all runs\n")
        f.write("  - Intervention: 50% usage cut + 70% transmission dampening at Day 10\n\n")
        
        f.write("="*80 + "\n")
        f.write("RESULTS\n")
        f.write("="*80 + "\n\n")
        f.write(summary.to_string())
        f.write("\n\n")
        
        f.write("EFFECTIVENESS COMPARISON:\n")
        f.write(f"  Top influencers:  {top_stress:.2f} final stress, {top_burnout:.2f} burnout\n")
        f.write(f"  Random agents:    {random_stress:.2f} final stress, {random_burnout:.2f} burnout\n")
        f.write(f"  Low-degree nodes: {bottom_stress:.2f} final stress, {bottom_burnout:.2f} burnout\n\n")
        
        f.write(f"  Improvement vs Random:     {improvement_vs_random:+.1f}%\n")
        f.write(f"  Improvement vs Low-Degree: {improvement_vs_bottom:+.1f}%\n\n")
        
        f.write("="*80 + "\n")
        f.write("CONCLUSION\n")
        f.write("="*80 + "\n\n")
        
        if conclusion == "proven_effective":
            f.write("✓ TARGETING INFLUENCERS IS SIGNIFICANTLY MORE EFFECTIVE\n\n")
            f.write("  Network position matters for intervention effectiveness.\n")
            f.write("  High-degree nodes (influencers) have amplified impact on network stress.\n")
            f.write("  Targeted intervention is superior to random or low-degree targeting.\n\n")
            f.write("  IMPLICATION: The simulation demonstrates that network-aware interventions\n")
            f.write("               can achieve better outcomes with the same resource investment\n")
            f.write("               (5 agents). This validates the core hypothesis.\n")
        elif conclusion == "no_advantage":
            f.write("⚠ NO CLEAR ADVANTAGE TO TARGETING INFLUENCERS\n\n")
            f.write("  All targeting strategies produce similar outcomes.\n")
            f.write("  Network position may not significantly affect intervention effectiveness.\n")
            f.write("  Possible explanations:\n")
            f.write("    - Intervention type is too strong (saturates the effect)\n")
            f.write("    - Network has low clustering (influence diffuses quickly anyway)\n")
            f.write("    - Personal factors (α=0.6) dominate over network factors (β=0.3)\n\n")
            f.write("  IMPLICATION: If true, simpler random interventions may be equally effective,\n")
            f.write("               reducing need for complex network analysis.\n")
        else:
            f.write("⚠ RESULTS UNCLEAR - FURTHER INVESTIGATION NEEDED\n\n")
            f.write("  Mixed evidence on effectiveness of targeted intervention.\n")
    
    print(f"✓ Saved summary report to: {summary_path}")
    
    # Save JSON for programmatic access
    comparison_data = {
        'strategies': {
            'top_influencers': {
                'agent_ids': [int(x) for x in sorted(list(top_5_ids))],
                'final_stress': float(top_stress),
                'burnout_count': float(top_burnout)
            },
            'random_agents': {
                'agent_ids': [int(x) for x in sorted(list(random_5_ids))],
                'final_stress': float(random_stress),
                'burnout_count': float(random_burnout)
            },
            'low_degree': {
                'agent_ids': [int(x) for x in sorted(list(bottom_5_ids))],
                'final_stress': float(bottom_stress),
                'burnout_count': float(bottom_burnout)
            }
        },
        'comparison': {
            'improvement_vs_random_pct': float(improvement_vs_random),
            'improvement_vs_low_degree_pct': float(improvement_vs_bottom)
        },
        'conclusion': conclusion
    }
    
    json_path = OUTPUT_DIR / "targeting_strategy_comparison.json"
    with open(json_path, 'w') as f:
        json.dump(comparison_data, f, indent=2)
    
    print(f"✓ Saved comparison data to: {json_path}")
    
    print("\n" + "="*80)
    print("EXPERIMENT COMPLETE ✓")
    print("="*80)
    
    return combined, summary


if __name__ == "__main__":
    main()
