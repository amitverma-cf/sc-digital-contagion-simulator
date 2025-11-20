"""
Phase 7: Visualization Production
Creates network graph, temporal heatmap, and intervention comparison visualizations
"""

import pandas as pd
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import seaborn as sns
import json
from pathlib import Path

# Configuration
OUTPUT_DIR = Path(__file__).parent.parent / "analysis"
NETWORK_PATH = OUTPUT_DIR / "social_network.graphml"
INFLUENCERS_PATH = OUTPUT_DIR / "influencers.json"
BASELINE_RUN0 = OUTPUT_DIR / "simulation_baseline_run0.csv"
INTERVENTION_RUN0 = OUTPUT_DIR / "simulation_intervention_run0.csv"
SCENARIO_COMPARISON = OUTPUT_DIR / "scenario_comparison.json"

def create_network_visualization():
    """Create network topology visualization with personas"""
    print("\n" + "="*60)
    print("CREATING NETWORK VISUALIZATION")
    print("="*60)
    
    # Load network
    G = nx.read_graphml(NETWORK_PATH)
    mapping = {node: int(node) for node in G.nodes()}
    G = nx.relabel_nodes(G, mapping)
    
    # Load influencers
    with open(INFLUENCERS_PATH, 'r') as f:
        influencer_data = json.load(f)
    influencer_ids = set(influencer_data['influencer_ids'])
    
    # Color map
    persona_colors = {
        'Minimalist': '#3498db',
        'Moderate User': '#2ecc71',
        'Active User': '#f39c12',
        'Heavy User': '#e74c3c',
        'Digital Addict': '#9b59b6'
    }
    
    node_colors = [persona_colors.get(G.nodes[node].get('persona', 'Unknown'), '#95a5a6') 
                   for node in G.nodes()]
    
    # Layout
    pos = nx.spring_layout(G, k=0.5, iterations=50, seed=42)
    
    fig, ax = plt.subplots(figsize=(14, 10))
    
    # Draw edges
    nx.draw_networkx_edges(G, pos, alpha=0.15, width=0.8, ax=ax, edge_color='#bdc3c7')
    
    # Draw regular nodes
    regular_nodes = [n for n in G.nodes() if n not in influencer_ids]
    nx.draw_networkx_nodes(G, pos, nodelist=regular_nodes,
                           node_color=[persona_colors.get(G.nodes[node].get('persona', 'Unknown'), '#95a5a6') 
                                      for node in regular_nodes],
                           node_size=120, alpha=0.85, ax=ax, 
                           linewidths=1, edgecolors='white')
    
    # Draw influencer nodes (highlighted)
    nx.draw_networkx_nodes(G, pos, nodelist=list(influencer_ids),
                           node_color='gold', node_size=400, 
                           alpha=1.0, ax=ax, linewidths=3, edgecolors='#e67e22')
    
    # Add labels for influencers only
    influencer_labels = {node: f'{node}' for node in influencer_ids}
    nx.draw_networkx_labels(G, pos, influencer_labels, font_size=10, 
                            font_weight='bold', font_color='black', ax=ax)
    
    ax.set_title('Social Network: Digital Contagion Simulator\n(100 Agents with Homophily-Based Connections)',
                 fontsize=16, fontweight='bold', pad=20)
    ax.axis('off')
    
    # Legend
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor=color, label=persona, edgecolor='white', linewidth=1)
        for persona, color in persona_colors.items()
    ]
    legend_elements.append(Patch(facecolor='gold', label='Top 5 Influencers', 
                                  edgecolor='#e67e22', linewidth=2))
    
    ax.legend(handles=legend_elements, loc='upper left', fontsize=11, 
              framealpha=0.95, edgecolor='black')
    
    # Add network stats
    stats_text = f"Nodes: {G.number_of_nodes()} | Edges: {G.number_of_edges()} | Avg Degree: {2*G.number_of_edges()/G.number_of_nodes():.1f}"
    ax.text(0.5, -0.05, stats_text, ha='center', va='top', 
            transform=ax.transAxes, fontsize=11, style='italic')
    
    plt.tight_layout()
    output_path = OUTPUT_DIR / "viz_network_final.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"✓ Saved network visualization to {output_path}")
    plt.close()

def create_temporal_heatmap():
    """Create temporal heatmap showing stress contagion over 30 days"""
    print("\n" + "="*60)
    print("CREATING TEMPORAL HEATMAP")
    print("="*60)
    
    # Load baseline simulation
    df = pd.read_csv(BASELINE_RUN0)
    
    # Pivot to matrix format: agents x days
    stress_matrix = df.pivot(index='agent_id', columns='day', values='stress')
    
    # Sort by final day stress (descending) for better visualization
    final_stress = stress_matrix[30]
    stress_matrix = stress_matrix.loc[final_stress.sort_values(ascending=False).index]
    
    fig, ax = plt.subplots(figsize=(16, 10))
    
    # Create heatmap
    sns.heatmap(stress_matrix, cmap='YlOrRd', vmin=0, vmax=100,
                cbar_kws={'label': 'Stress Level (0-100)', 'shrink': 0.8},
                xticklabels=5, yticklabels=10, ax=ax, linewidths=0)
    
    ax.set_xlabel('Day', fontsize=13, fontweight='bold')
    ax.set_ylabel('Agent ID (sorted by final stress)', fontsize=13, fontweight='bold')
    ax.set_title('Temporal Heatmap: 30-Day Stress Contagion Evolution\n(Baseline Scenario - No Intervention)',
                 fontsize=15, fontweight='bold', pad=15)
    
    # Add horizontal lines to separate stress zones
    high_stress_agents = (final_stress > 60).sum()
    if high_stress_agents > 0:
        ax.axhline(y=high_stress_agents, color='white', linewidth=2, linestyle='--', alpha=0.7)
        ax.text(31, high_stress_agents/2, 'High\nStress', va='center', ha='left', 
                fontsize=10, fontweight='bold', color='white',
                bbox=dict(boxstyle='round', facecolor='red', alpha=0.7))
    
    plt.tight_layout()
    output_path = OUTPUT_DIR / "viz_temporal_heatmap_final.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"✓ Saved temporal heatmap to {output_path}")
    plt.close()

def create_intervention_comparison():
    """Create line chart comparing baseline vs intervention scenarios"""
    print("\n" + "="*60)
    print("CREATING INTERVENTION COMPARISON")
    print("="*60)
    
    # Load data
    baseline_df = pd.read_csv(BASELINE_RUN0)
    intervention_df = pd.read_csv(INTERVENTION_RUN0)
    
    # Compute daily average stress
    baseline_daily = baseline_df.groupby('day')['stress'].agg(['mean', 'std'])
    intervention_daily = intervention_df.groupby('day')['stress'].agg(['mean', 'std'])
    
    # Load scenario comparison for effect size
    with open(SCENARIO_COMPARISON, 'r') as f:
        comparison = json.load(f)
    
    reduction_pct = comparison['effect']['stress_reduction_pct']
    intervention_day = comparison['config']['intervention_day']
    
    fig, ax = plt.subplots(figsize=(14, 8))
    
    # Plot baseline
    ax.plot(baseline_daily.index, baseline_daily['mean'], 
            linewidth=3, color='#e74c3c', label='Baseline (No Intervention)', marker='o', markersize=5)
    ax.fill_between(baseline_daily.index,
                     baseline_daily['mean'] - baseline_daily['std'],
                     baseline_daily['mean'] + baseline_daily['std'],
                     alpha=0.2, color='#e74c3c')
    
    # Plot intervention
    ax.plot(intervention_daily.index, intervention_daily['mean'],
            linewidth=3, color='#27ae60', label='Influencer Quarantine', marker='s', markersize=5)
    ax.fill_between(intervention_daily.index,
                     intervention_daily['mean'] - intervention_daily['std'],
                     intervention_daily['mean'] + intervention_daily['std'],
                     alpha=0.2, color='#27ae60')
    
    # Mark intervention start
    ax.axvline(x=intervention_day, color='#3498db', linestyle='--', linewidth=2, 
               label=f'Intervention Start (Day {intervention_day})', alpha=0.7)
    
    # Annotations
    final_baseline = baseline_daily.loc[30, 'mean']
    final_intervention = intervention_daily.loc[30, 'mean']
    
    ax.annotate(f'Baseline Final\nStress: {final_baseline:.1f}',
                xy=(30, final_baseline), xytext=(26, final_baseline + 5),
                arrowprops=dict(arrowstyle='->', color='#e74c3c', lw=2),
                fontsize=10, fontweight='bold', color='#e74c3c',
                bbox=dict(boxstyle='round', facecolor='white', edgecolor='#e74c3c', alpha=0.9))
    
    ax.annotate(f'Intervention Final\nStress: {final_intervention:.1f}\n({reduction_pct:.1f}% reduction)',
                xy=(30, final_intervention), xytext=(26, final_intervention - 8),
                arrowprops=dict(arrowstyle='->', color='#27ae60', lw=2),
                fontsize=10, fontweight='bold', color='#27ae60',
                bbox=dict(boxstyle='round', facecolor='white', edgecolor='#27ae60', alpha=0.9))
    
    ax.set_xlabel('Day', fontsize=13, fontweight='bold')
    ax.set_ylabel('Average Network Stress', fontsize=13, fontweight='bold')
    ax.set_title('Intervention Effectiveness: Targeting Top Influencers\n(Average Stress ± Standard Deviation Across Network)',
                 fontsize=15, fontweight='bold', pad=15)
    ax.legend(fontsize=11, loc='upper right', framealpha=0.95, edgecolor='black')
    ax.grid(alpha=0.3, linestyle='--')
    ax.set_xlim(-0.5, 30.5)
    
    plt.tight_layout()
    output_path = OUTPUT_DIR / "viz_intervention_comparison_final.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"✓ Saved intervention comparison to {output_path}")
    plt.close()

def create_supplementary_visualizations():
    """Create additional supporting visualizations"""
    print("\n" + "="*60)
    print("CREATING SUPPLEMENTARY VISUALIZATIONS")
    print("="*60)
    
    # Load data
    baseline_df = pd.read_csv(BASELINE_RUN0)
    
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    
    # 1. Stress evolution by persona
    ax = axes[0, 0]
    for persona in baseline_df['persona'].unique():
        persona_data = baseline_df[baseline_df['persona'] == persona]
        daily_mean = persona_data.groupby('day')['stress'].mean()
        ax.plot(daily_mean.index, daily_mean.values, linewidth=2.5, 
                label=persona, marker='o', markersize=4, alpha=0.8)
    
    ax.set_xlabel('Day', fontsize=11, fontweight='bold')
    ax.set_ylabel('Average Stress', fontsize=11, fontweight='bold')
    ax.set_title('Stress Evolution by Persona', fontsize=12, fontweight='bold')
    ax.legend(fontsize=9, loc='best')
    ax.grid(alpha=0.3)
    
    # 2. Burnout count over time
    ax = axes[0, 1]
    baseline_burnout = baseline_df.groupby('day').apply(lambda x: (x['stress'] > 80).sum())
    intervention_df = pd.read_csv(INTERVENTION_RUN0)
    intervention_burnout = intervention_df.groupby('day').apply(lambda x: (x['stress'] > 80).sum())
    
    ax.plot(baseline_burnout.index, baseline_burnout.values, linewidth=3, 
            color='#e74c3c', label='Baseline', marker='o')
    ax.plot(intervention_burnout.index, intervention_burnout.values, linewidth=3,
            color='#27ae60', label='Intervention', marker='s')
    
    ax.set_xlabel('Day', fontsize=11, fontweight='bold')
    ax.set_ylabel('Agents in Burnout (Stress > 80)', fontsize=11, fontweight='bold')
    ax.set_title('Burnout Count Over Time', fontsize=12, fontweight='bold')
    ax.legend(fontsize=10)
    ax.grid(alpha=0.3)
    ax.axvline(x=10, color='#3498db', linestyle='--', alpha=0.5, label='Intervention Start')
    
    # 3. Final stress distribution
    ax = axes[1, 0]
    baseline_final = baseline_df[baseline_df['day'] == 30]['stress']
    intervention_final = intervention_df[intervention_df['day'] == 30]['stress']
    
    ax.hist(baseline_final, bins=20, alpha=0.6, color='#e74c3c', 
            label=f'Baseline (μ={baseline_final.mean():.1f})', edgecolor='black')
    ax.hist(intervention_final, bins=20, alpha=0.6, color='#27ae60',
            label=f'Intervention (μ={intervention_final.mean():.1f})', edgecolor='black')
    
    ax.axvline(baseline_final.mean(), color='#e74c3c', linestyle='--', linewidth=2)
    ax.axvline(intervention_final.mean(), color='#27ae60', linestyle='--', linewidth=2)
    
    ax.set_xlabel('Final Stress (Day 30)', fontsize=11, fontweight='bold')
    ax.set_ylabel('Number of Agents', fontsize=11, fontweight='bold')
    ax.set_title('Final Stress Distribution Comparison', fontsize=12, fontweight='bold')
    ax.legend(fontsize=10)
    ax.grid(axis='y', alpha=0.3)
    
    # 4. Peer influence analysis
    ax = axes[1, 1]
    baseline_sample = baseline_df[(baseline_df['day'] >= 15) & (baseline_df['day'] <= 20)]
    
    ax.scatter(baseline_sample['peer_influence'], baseline_sample['stress'],
               alpha=0.3, s=30, c=baseline_sample['day'], cmap='viridis')
    
    # Add trend line
    z = np.polyfit(baseline_sample['peer_influence'], baseline_sample['stress'], 1)
    p = np.poly1d(z)
    x_trend = np.linspace(baseline_sample['peer_influence'].min(), 
                          baseline_sample['peer_influence'].max(), 100)
    ax.plot(x_trend, p(x_trend), "r--", linewidth=2, label=f'Trend: y={z[0]:.2f}x+{z[1]:.1f}')
    
    ax.set_xlabel('Peer Influence (Neighbor Avg Stress)', fontsize=11, fontweight='bold')
    ax.set_ylabel('Agent Stress', fontsize=11, fontweight='bold')
    ax.set_title('Peer Influence vs Agent Stress (Days 15-20)', fontsize=12, fontweight='bold')
    ax.legend(fontsize=10)
    ax.grid(alpha=0.3)
    
    plt.suptitle('Supplementary Analysis: Stress Contagion Dynamics', 
                 fontsize=14, fontweight='bold', y=1.00)
    plt.tight_layout()
    output_path = OUTPUT_DIR / "viz_supplementary_analysis.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"✓ Saved supplementary visualizations to {output_path}")
    plt.close()

def main():
    """Execute visualization pipeline"""
    print("\n" + "="*60)
    print("PHASE 7: VISUALIZATION PRODUCTION")
    print("="*60)
    
    # Create three main visualizations
    create_network_visualization()
    create_temporal_heatmap()
    create_intervention_comparison()
    
    # Create supplementary visualizations
    create_supplementary_visualizations()
    
    print("\n" + "="*60)
    print("PHASE 7 COMPLETE ✓")
    print("="*60)
    print(f"\nOutputs saved to: {OUTPUT_DIR}")
    print("  PRIMARY VISUALIZATIONS:")
    print("  - viz_network_final.png")
    print("  - viz_temporal_heatmap_final.png")
    print("  - viz_intervention_comparison_final.png")
    print("  SUPPLEMENTARY:")
    print("  - viz_supplementary_analysis.png")

if __name__ == "__main__":
    main()
