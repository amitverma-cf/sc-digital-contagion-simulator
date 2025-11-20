"""
Phase 6: Scenario & Intervention Suite
Runs baseline and intervention scenarios with multiple seeds for statistical validity
"""

import pandas as pd
import numpy as np
import networkx as nx
import json
from pathlib import Path
from tqdm import tqdm
import sys

# Import temporal engine
from temporal_engine import TemporalEngine

# Configuration
AGENT_COHORT_PATH = Path(__file__).parent.parent / "analysis" / "agent_cohort.csv"
NETWORK_PATH = Path(__file__).parent.parent / "analysis" / "social_network.graphml"
INFLUENCERS_PATH = Path(__file__).parent.parent / "analysis" / "influencers.json"
OUTPUT_DIR = Path(__file__).parent.parent / "analysis"
OUTPUT_DIR.mkdir(exist_ok=True)

def load_influencers():
    """Load influencer IDs"""
    with open(INFLUENCERS_PATH, 'r') as f:
        data = json.load(f)
    return set(data['influencer_ids'])

def run_scenario(agents_df, network, scenario_name, n_runs=5, intervention_day=None, intervention_agents=None):
    """
    Run a scenario with multiple seeds
    
    Args:
        agents_df: DataFrame with agent attributes
        network: NetworkX graph
        scenario_name: Name of scenario
        n_runs: Number of simulation runs with different seeds
        intervention_day: Day to start intervention (None for baseline)
        intervention_agents: Set of agent IDs to intervene
        
    Returns:
        List of (results_df, metrics) tuples
    """
    print("\n" + "="*60)
    print(f"SCENARIO: {scenario_name}")
    print("="*60)
    print(f"  Runs: {n_runs}")
    if intervention_day:
        print(f"  Intervention day: {intervention_day}")
        print(f"  Agents affected: {len(intervention_agents)}")
    
    all_results = []
    all_metrics = []
    
    for run_idx in tqdm(range(n_runs), desc=f"Running {scenario_name}"):
        seed = 42 + run_idx  # Different seed for each run
        
        engine = TemporalEngine(agents_df, network, random_seed=seed)
        results_df = engine.simulate(
            intervention_day=intervention_day,
            intervention_agents=intervention_agents,
            verbose=False
        )
        metrics = engine.compute_summary_metrics(results_df)
        metrics['run_id'] = run_idx
        metrics['seed'] = seed
        metrics['scenario'] = scenario_name
        
        all_results.append(results_df)
        all_metrics.append(metrics)
    
    return all_results, all_metrics

def compute_aggregated_metrics(metrics_list):
    """Compute mean and std across multiple runs"""
    agg = {}
    
    # Numeric metrics to aggregate
    numeric_keys = [
        'initial_stress_mean', 'final_stress_mean', 'stress_change',
        'peak_stress_overall', 'peak_stress_value',
        'burnout_count_initial', 'burnout_count_final',
        'total_stress_auc', 'avg_stress_auc_per_agent'
    ]
    
    for key in numeric_keys:
        values = [m[key] for m in metrics_list]
        agg[f'{key}_mean'] = np.mean(values)
        agg[f'{key}_std'] = np.std(values)
        agg[f'{key}_min'] = np.min(values)
        agg[f'{key}_max'] = np.max(values)
    
    return agg

def main():
    """Execute scenario suite"""
    print("\n" + "="*60)
    print("PHASE 6: SCENARIO & INTERVENTION SUITE")
    print("="*60 + "\n")
    
    # Load data
    agents_df = pd.read_csv(AGENT_COHORT_PATH)
    network = nx.read_graphml(NETWORK_PATH)
    
    # Convert node labels to integers
    mapping = {node: int(node) for node in network.nodes()}
    network = nx.relabel_nodes(network, mapping)
    
    # Load influencers
    influencer_ids = load_influencers()
    
    print(f"✓ Loaded {len(agents_df)} agents")
    print(f"✓ Loaded network with {network.number_of_edges()} edges")
    print(f"✓ Loaded {len(influencer_ids)} influencers")
    
    # Configuration
    N_RUNS = 5
    INTERVENTION_DAY = 10
    
    # Scenario A: Baseline (no intervention)
    print("\n" + "="*60)
    print("SCENARIO A: BASELINE (No Intervention)")
    print("="*60)
    
    baseline_results, baseline_metrics = run_scenario(
        agents_df, network,
        scenario_name="Baseline",
        n_runs=N_RUNS,
        intervention_day=None,
        intervention_agents=None
    )
    
    # Scenario B: Influencer quarantine
    print("\n" + "="*60)
    print("SCENARIO B: INFLUENCER QUARANTINE")
    print("="*60)
    
    intervention_results, intervention_metrics = run_scenario(
        agents_df, network,
        scenario_name="Influencer_Quarantine",
        n_runs=N_RUNS,
        intervention_day=INTERVENTION_DAY,
        intervention_agents=influencer_ids
    )
    
    # Aggregate metrics
    print("\n" + "="*60)
    print("AGGREGATING RESULTS")
    print("="*60)
    
    baseline_agg = compute_aggregated_metrics(baseline_metrics)
    intervention_agg = compute_aggregated_metrics(intervention_metrics)
    
    # Compute intervention effect
    effect = {
        'stress_reduction': baseline_agg['final_stress_mean_mean'] - intervention_agg['final_stress_mean_mean'],
        'stress_reduction_pct': ((baseline_agg['final_stress_mean_mean'] - intervention_agg['final_stress_mean_mean']) / 
                                  baseline_agg['final_stress_mean_mean']) * 100,
        'burnout_reduction': baseline_agg['burnout_count_final_mean'] - intervention_agg['burnout_count_final_mean'],
        'auc_reduction': baseline_agg['total_stress_auc_mean'] - intervention_agg['total_stress_auc_mean'],
        'auc_reduction_pct': ((baseline_agg['total_stress_auc_mean'] - intervention_agg['total_stress_auc_mean']) /
                              baseline_agg['total_stress_auc_mean']) * 100
    }
    
    print("\n✓ Aggregated metrics computed")
    print(f"\n✓ Intervention Effect:")
    print(f"  • Stress reduction: {effect['stress_reduction']:.2f} ({effect['stress_reduction_pct']:.1f}%)")
    print(f"  • Burnout reduction: {effect['burnout_reduction']:.2f} agents")
    print(f"  • Total stress AUC reduction: {effect['auc_reduction_pct']:.1f}%")
    
    # Save results
    print("\n" + "="*60)
    print("SAVING RESULTS")
    print("="*60)
    
    # Save all baseline runs
    for idx, (results_df, metrics) in enumerate(zip(baseline_results, baseline_metrics)):
        path = OUTPUT_DIR / f"simulation_baseline_run{idx}.csv"
        results_df.to_csv(path, index=False)
    print(f"✓ Saved {len(baseline_results)} baseline simulation runs")
    
    # Save all intervention runs
    for idx, (results_df, metrics) in enumerate(zip(intervention_results, intervention_metrics)):
        path = OUTPUT_DIR / f"simulation_intervention_run{idx}.csv"
        results_df.to_csv(path, index=False)
    print(f"✓ Saved {len(intervention_results)} intervention simulation runs")
    
    # Save individual metrics
    baseline_metrics_df = pd.DataFrame(baseline_metrics)
    baseline_metrics_df.to_csv(OUTPUT_DIR / "metrics_baseline_all_runs.csv", index=False)
    
    intervention_metrics_df = pd.DataFrame(intervention_metrics)
    intervention_metrics_df.to_csv(OUTPUT_DIR / "metrics_intervention_all_runs.csv", index=False)
    print("✓ Saved individual run metrics")
    
    # Save aggregated comparison
    comparison = {
        'baseline': {k: float(v) if isinstance(v, (np.floating, np.integer)) else v for k, v in baseline_agg.items()},
        'intervention': {k: float(v) if isinstance(v, (np.floating, np.integer)) else v for k, v in intervention_agg.items()},
        'effect': {k: float(v) if isinstance(v, (np.floating, np.integer)) else v for k, v in effect.items()},
        'config': {
            'n_runs': int(N_RUNS),
            'intervention_day': int(INTERVENTION_DAY),
            'n_influencers': len(influencer_ids),
            'influencer_ids': [int(x) for x in influencer_ids]
        }
    }
    
    with open(OUTPUT_DIR / "scenario_comparison.json", 'w') as f:
        json.dump(comparison, f, indent=2)
    print("✓ Saved aggregated scenario comparison")
    
    # Save readable report
    report_path = OUTPUT_DIR / "scenario_report.txt"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("="*80 + "\n")
        f.write("SCENARIO COMPARISON REPORT\n")
        f.write("="*80 + "\n\n")
        
        f.write(f"Configuration:\n")
        f.write(f"  • Number of simulation runs per scenario: {N_RUNS}\n")
        f.write(f"  • Intervention day: {INTERVENTION_DAY}\n")
        f.write(f"  • Influencers quarantined: {len(influencer_ids)}\n\n")
        
        f.write("="*80 + "\n")
        f.write("SCENARIO A: BASELINE (No Intervention)\n")
        f.write("="*80 + "\n\n")
        f.write(f"Final Stress: {baseline_agg['final_stress_mean_mean']:.2f} ± {baseline_agg['final_stress_mean_std']:.2f}\n")
        f.write(f"Peak Stress: {baseline_agg['peak_stress_overall_mean']:.2f} ± {baseline_agg['peak_stress_overall_std']:.2f}\n")
        f.write(f"Burnout Count: {baseline_agg['burnout_count_final_mean']:.2f} ± {baseline_agg['burnout_count_final_std']:.2f}\n")
        f.write(f"Total Stress AUC: {baseline_agg['total_stress_auc_mean']:.2f} ± {baseline_agg['total_stress_auc_std']:.2f}\n\n")
        
        f.write("="*80 + "\n")
        f.write("SCENARIO B: INFLUENCER QUARANTINE\n")
        f.write("="*80 + "\n\n")
        f.write(f"Final Stress: {intervention_agg['final_stress_mean_mean']:.2f} ± {intervention_agg['final_stress_mean_std']:.2f}\n")
        f.write(f"Peak Stress: {intervention_agg['peak_stress_overall_mean']:.2f} ± {intervention_agg['peak_stress_overall_std']:.2f}\n")
        f.write(f"Burnout Count: {intervention_agg['burnout_count_final_mean']:.2f} ± {intervention_agg['burnout_count_final_std']:.2f}\n")
        f.write(f"Total Stress AUC: {intervention_agg['total_stress_auc_mean']:.2f} ± {intervention_agg['total_stress_auc_std']:.2f}\n\n")
        
        f.write("="*80 + "\n")
        f.write("INTERVENTION EFFECT\n")
        f.write("="*80 + "\n\n")
        f.write(f"Stress Reduction: {effect['stress_reduction']:.2f} points ({effect['stress_reduction_pct']:.1f}%)\n")
        f.write(f"Burnout Reduction: {effect['burnout_reduction']:.2f} agents\n")
        f.write(f"Total Stress AUC Reduction: {effect['auc_reduction_pct']:.1f}%\n\n")
        
        f.write("CONCLUSION:\n")
        if effect['stress_reduction_pct'] > 10:
            f.write("✓ Significant stress reduction achieved through targeted intervention.\n")
        else:
            f.write("⚠ Modest stress reduction observed.\n")
    
    print(f"✓ Saved scenario report to {report_path}")
    
    print("\n" + "="*60)
    print("PHASE 6 COMPLETE ✓")
    print("="*60)
    print(f"\nKey Findings:")
    print(f"  • Baseline final stress: {baseline_agg['final_stress_mean_mean']:.2f} ± {baseline_agg['final_stress_mean_std']:.2f}")
    print(f"  • Intervention final stress: {intervention_agg['final_stress_mean_mean']:.2f} ± {intervention_agg['final_stress_mean_std']:.2f}")
    print(f"  • Reduction: {effect['stress_reduction_pct']:.1f}%")

if __name__ == "__main__":
    main()
