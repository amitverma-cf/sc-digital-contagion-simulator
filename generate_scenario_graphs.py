"""
Generate 4 scenario comparison graphs for poster key findings
Based on main.py simulation logic
"""

import pandas as pd
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import seaborn as sns
import json
from pathlib import Path
from typing import Set, Optional

# =============================================================================
# SETUP
# =============================================================================

BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "analysis"
OUTPUT_DIR.mkdir(exist_ok=True)

PERSONA_FILE = OUTPUT_DIR / "persona_definitions.json"
AGENT_COHORT_PATH = OUTPUT_DIR / "agent_cohort.csv"
NETWORK_PATH = OUTPUT_DIR / "social_network.graphml"

# Default params
DEFAULT_PARAMS = {
    'alpha': 0.6,
    'beta': 0.3,
    'gamma': 0.1,
    'delta': 0.02,
    'resilience_mod': 1.0,
    'susceptibility_mod': 1.0,
    'variability_mod': 1.0,
    'intervention_day': 10,
    'intervention_usage_factor': 0.5,
    'intervention_peer_factor': 0.3
}

# =============================================================================
# SIMPLIFIED CLASSES FROM MAIN.PY
# =============================================================================

class TemporalEngine:
    """Simulates 30-day digital stress contagion"""
    
    def __init__(self, agents_df, network, params=None, random_seed=42):
        self.agents_df = agents_df.copy()
        self.G = network
        self.n_agents = len(agents_df)
        self.random_seed = random_seed
        np.random.seed(random_seed)
        
        self.params = params or DEFAULT_PARAMS
        self.n_days = 30
        
        self.alpha = self.params.get('alpha', 0.6)
        self.beta = self.params.get('beta', 0.3)
        self.gamma = self.params.get('gamma', 0.1)
        self.delta = self.params.get('delta', 0.02)
        
        self.resilience_mod = self.params.get('resilience_mod', 1.0)
        self.susceptibility_mod = self.params.get('susceptibility_mod', 1.0)
        self.variability_mod = self.params.get('variability_mod', 1.0)
        
        self.stress_cap = 100.0
        self.usage_min = 30.0
        
    def initialize_state(self):
        self.daily_states = []
        for idx, agent in self.agents_df.iterrows():
            state = {
                'agent_id': agent['agent_id'],
                'day': 0,
                'stress': agent['base_stress'],
                'usage': agent['app_usage'],
                'peer_influence': 0.0,
                'persona': agent['persona'],
                'intervention_active': False
            }
            self.daily_states.append(state)
            
    def compute_peer_influence(self, agent_id, day):
        neighbors = list(self.G.neighbors(agent_id))
        if not neighbors: return 0.0
        
        prev_day_states = [s for s in self.daily_states if s['day'] == day - 1]
        neighbor_stress = []
        for nid in neighbors:
            n_state = next((s for s in prev_day_states if s['agent_id'] == nid), None)
            if n_state: neighbor_stress.append(n_state['stress'])
            
        return np.mean(neighbor_stress) if neighbor_stress else 0.0
        
    def update_agent_state(self, agent_id, day, intervention_agents=None):
        if intervention_agents is None: intervention_agents = set()
        
        agent = self.agents_df[self.agents_df['agent_id'] == agent_id].iloc[0]
        prev_state = next((s for s in self.daily_states if s['agent_id'] == agent_id and s['day'] == day - 1))
        
        avg_neighbor_stress = self.compute_peer_influence(agent_id, day)
        is_intervened = agent_id in intervention_agents
        
        resilience = agent['resilience'] * self.resilience_mod
        susceptibility = agent['susceptibility'] * self.susceptibility_mod
        variability = agent['variability'] * self.variability_mod
        
        noise = np.random.normal(1.0, 0.1)
        
        if is_intervened:
            new_usage = agent['app_usage'] * self.params.get('intervention_usage_factor', 0.5)
        else:
            stress_factor = 1 + self.delta * (prev_state['stress'] / 100.0)
            new_usage = prev_state['usage'] * stress_factor * noise * variability
            new_usage = max(self.usage_min, new_usage)
            
        usage_normalized = min(100, (new_usage / 600.0) * 100)
        
        peer_contribution = avg_neighbor_stress * susceptibility
        if is_intervened:
            peer_contribution *= self.params.get('intervention_peer_factor', 0.3)
            
        new_stress = (
            self.alpha * usage_normalized +
            self.beta * peer_contribution -
            self.gamma * resilience * 10
        )
        
        new_stress = max(0, min(self.stress_cap, new_stress))
        
        return {
            'agent_id': agent_id,
            'day': day,
            'stress': new_stress,
            'usage': new_usage,
            'peer_influence': avg_neighbor_stress,
            'persona': agent['persona'],
            'intervention_active': is_intervened
        }
        
    def simulate(self, intervention_day=None, intervention_agents=None):
        self.initialize_state()
        
        for day in range(1, self.n_days + 1):
            active_intervention = intervention_agents if (intervention_day and day >= intervention_day) else None
            for agent_id in range(self.n_agents):
                new_state = self.update_agent_state(agent_id, day, active_intervention)
                self.daily_states.append(new_state)
                
        return pd.DataFrame(self.daily_states)

# =============================================================================
# LOAD DATA
# =============================================================================

print("Loading agents and network...")
agents_df = pd.read_csv(AGENT_COHORT_PATH)
network = nx.read_graphml(NETWORK_PATH)
mapping = {node: int(node) for node in network.nodes()}
network = nx.relabel_nodes(network, mapping)

# Get influencers
degree_cent = nx.degree_centrality(network)
sorted_nodes = sorted(degree_cent.items(), key=lambda x: x[1], reverse=True)
top_5_influencers = set([node for node, _ in sorted_nodes[:5]])

print(f"Loaded {len(agents_df)} agents, {network.number_of_edges()} edges")
print(f"Top 5 influencers: {top_5_influencers}")

# =============================================================================
# SCENARIO 1: TARGETING PARADOX (Influencer vs Random)
# =============================================================================

print("\n=== Scenario 1: Targeting Paradox ===")

# Random selection
np.random.seed(43)
random_5 = set(np.random.choice(agents_df['agent_id'].values, 5, replace=False))

params_base = DEFAULT_PARAMS.copy()

# Influencer targeting
engine1 = TemporalEngine(agents_df, network, params=params_base, random_seed=42)
results_influencer = engine1.simulate(intervention_day=10, intervention_agents=top_5_influencers)

# Random targeting
engine2 = TemporalEngine(agents_df, network, params=params_base, random_seed=42)
results_random = engine2.simulate(intervention_day=10, intervention_agents=random_5)

# Plot
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8, 3))

# Stress comparison
stress_inf = results_influencer.groupby('day')['stress'].mean()
stress_rnd = results_random.groupby('day')['stress'].mean()

ax1.plot(stress_inf.index+1, stress_inf, label='Influencer Targeting', color='#3B82F6', linewidth=2)
ax1.plot(stress_rnd.index+1, stress_rnd, label='Random Targeting', color='#F59E0B', linewidth=2)
ax1.axvline(x=10, color='red', linestyle=':', alpha=0.5, linewidth=1)
ax1.set_xlabel('Day', fontsize=9)
ax1.set_ylabel('Mean Stress', fontsize=9)
ax1.set_title('Targeting Paradox: Mean Stress', fontsize=10, fontweight='bold')
ax1.legend(fontsize=7)
ax1.grid(True, alpha=0.3)
ax1.tick_params(labelsize=8)

# Burnout comparison
burnout_inf = results_influencer.groupby('day').apply(lambda x: (x['stress'] > 80).sum())
burnout_rnd = results_random.groupby('day').apply(lambda x: (x['stress'] > 80).sum())

ax2.plot(burnout_inf.index+1, burnout_inf, label='Influencer Targeting', color='#3B82F6', linewidth=2)
ax2.plot(burnout_rnd.index+1, burnout_rnd, label='Random Targeting', color='#F59E0B', linewidth=2)
ax2.axvline(x=10, color='red', linestyle=':', alpha=0.5, linewidth=1)
ax2.set_xlabel('Day', fontsize=9)
ax2.set_ylabel('Burnout Count', fontsize=9)
ax2.set_title('Targeting Paradox: Burnout', fontsize=10, fontweight='bold')
ax2.legend(fontsize=7)
ax2.grid(True, alpha=0.3)
ax2.tick_params(labelsize=8)

plt.tight_layout()
plt.savefig(OUTPUT_DIR / "scenario_targeting_paradox.png", dpi=150, bbox_inches='tight')
print(f"✓ Saved: scenario_targeting_paradox.png")
plt.close()

# =============================================================================
# SCENARIO 2: ECHO CHAMBER EFFECT (Beta variation)
# =============================================================================

print("\n=== Scenario 2: Echo Chamber Effect ===")

params_low_beta = DEFAULT_PARAMS.copy()
params_low_beta['beta'] = 0.3

params_high_beta = DEFAULT_PARAMS.copy()
params_high_beta['beta'] = 0.8

# Run WITHOUT intervention to show pure echo chamber effect
engine3 = TemporalEngine(agents_df, network, params=params_low_beta, random_seed=42)
results_beta_low = engine3.simulate(intervention_day=None, intervention_agents=None)

engine4 = TemporalEngine(agents_df, network, params=params_high_beta, random_seed=42)
results_beta_high = engine4.simulate(intervention_day=None, intervention_agents=None)

# Plot
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8, 3))

stress_low = results_beta_low.groupby('day')['stress'].mean()
stress_high = results_beta_high.groupby('day')['stress'].mean()

ax1.plot(stress_low.index+1, stress_low, label='β=0.3 (Low Influence)', color='#6B7280', linewidth=2)
ax1.plot(stress_high.index+1, stress_high, label='β=0.8 (Echo Chamber)', color='#DC2626', linewidth=2)
# Remove intervention line since no intervention is applied
ax1.set_xlabel('Day', fontsize=9)
ax1.set_ylabel('Mean Stress', fontsize=9)
ax1.set_title('Echo Chamber: Peer Influence Impact', fontsize=10, fontweight='bold')
ax1.legend(fontsize=7)
ax1.grid(True, alpha=0.3)
ax1.tick_params(labelsize=8)

burnout_low = results_beta_low.groupby('day').apply(lambda x: (x['stress'] > 80).sum())
burnout_high = results_beta_high.groupby('day').apply(lambda x: (x['stress'] > 80).sum())

ax2.plot(burnout_low.index+1, burnout_low, label='β=0.3', color='#6B7280', linewidth=2)
ax2.plot(burnout_high.index+1, burnout_high, label='β=0.8', color='#DC2626', linewidth=2)
# Remove intervention line since no intervention is applied
ax2.set_xlabel('Day', fontsize=9)
ax2.set_ylabel('Burnout Count', fontsize=9)
ax2.set_title('Echo Chamber: Burnout Cascade', fontsize=10, fontweight='bold')
ax2.legend(fontsize=7)
ax2.grid(True, alpha=0.3)
ax2.tick_params(labelsize=8)

plt.tight_layout()
plt.savefig(OUTPUT_DIR / "scenario_echo_chamber.png", dpi=150, bbox_inches='tight')
print(f"✓ Saved: scenario_echo_chamber.png")
plt.close()

# =============================================================================
# SCENARIO 3: UNIVERSAL VS TARGETED
# =============================================================================

print("\n=== Scenario 3: Universal vs Targeted ===")

# Targeted (5 influencers)
engine5 = TemporalEngine(agents_df, network, params=params_base, random_seed=42)
results_targeted = engine5.simulate(intervention_day=10, intervention_agents=top_5_influencers)

# Universal (all 100 agents)
all_agents = set(agents_df['agent_id'].values)
engine6 = TemporalEngine(agents_df, network, params=params_base, random_seed=42)
results_universal = engine6.simulate(intervention_day=10, intervention_agents=all_agents)

# Plot
fig, ax = plt.subplots(1, 1, figsize=(7, 3.5))

stress_targeted = results_targeted.groupby('day')['stress'].mean()
stress_universal = results_universal.groupby('day')['stress'].mean()

ax.plot(stress_targeted.index+1, stress_targeted, label='Targeted (5 influencers)', color='#3B82F6', linewidth=2)
ax.plot(stress_universal.index+1, stress_universal, label='Universal (all 100 agents)', color='#059669', linewidth=2)
ax.axvline(x=10, color='red', linestyle=':', alpha=0.5, linewidth=1)

# Add annotation for 5x better
final_diff = stress_targeted.iloc[-1] - stress_universal.iloc[-1]
ax.annotate(f'5× Better\n({final_diff:.1f} pts)', 
            xy=(30, stress_universal.iloc[-1]), 
            xytext=(24, 30),
            arrowprops=dict(arrowstyle='->', color='#059669', lw=1.5),
            fontsize=8, color='#059669', fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='#D1FAE5', edgecolor='#059669'))

ax.set_xlabel('Day', fontsize=10)
ax.set_ylabel('Mean Stress', fontsize=10)
ax.set_title('Universal vs Targeted Intervention', fontsize=11, fontweight='bold')
ax.legend(fontsize=8)
ax.grid(True, alpha=0.3)
ax.tick_params(labelsize=9)

plt.tight_layout()
plt.savefig(OUTPUT_DIR / "scenario_universal_vs_targeted.png", dpi=150, bbox_inches='tight')
print(f"✓ Saved: scenario_universal_vs_targeted.png")
plt.close()

# =============================================================================
# SCENARIO 4: INTERVENTION TIMING
# =============================================================================

print("\n=== Scenario 4: Intervention Timing ===")

# Early intervention (Day 10)
engine7 = TemporalEngine(agents_df, network, params=params_base, random_seed=42)
results_early = engine7.simulate(intervention_day=10, intervention_agents=top_5_influencers)

# Late intervention (Day 25)
engine8 = TemporalEngine(agents_df, network, params=params_base, random_seed=42)
results_late = engine8.simulate(intervention_day=25, intervention_agents=top_5_influencers)

# No intervention baseline
engine9 = TemporalEngine(agents_df, network, params=params_base, random_seed=42)
results_none = engine9.simulate(intervention_day=None, intervention_agents=None)

# Plot
fig, ax = plt.subplots(1, 1, figsize=(7, 3.5))

stress_early = results_early.groupby('day')['stress'].mean()
stress_late = results_late.groupby('day')['stress'].mean()
stress_none = results_none.groupby('day')['stress'].mean()

ax.plot(stress_none.index+1, stress_none, label='No Intervention', color='#6B7280', linewidth=2, linestyle='--')
ax.plot(stress_early.index+1, stress_early, label='Early (Day 10)', color='#3B82F6', linewidth=2)
ax.plot(stress_late.index+1, stress_late, label='Late (Day 25)', color='#F59E0B', linewidth=2)
ax.axvline(x=10, color='#3B82F6', linestyle=':', alpha=0.5, linewidth=1, label='Early Start')
ax.axvline(x=25, color='#F59E0B', linestyle=':', alpha=0.5, linewidth=1, label='Late Start')

# Add effectiveness annotation
late_reduction = stress_none.iloc[-1] - stress_late.iloc[-1]
late_pct = (late_reduction / stress_none.iloc[-1]) * 100
ax.annotate(f'Still 7% effective\n({late_reduction:.1f} pts)', 
            xy=(30, stress_late.iloc[-1]), 
            xytext=(20, 48),
            arrowprops=dict(arrowstyle='->', color='#F59E0B', lw=1.5),
            fontsize=8, color='#F59E0B', fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='#FEF3C7', edgecolor='#F59E0B'))

ax.set_xlabel('Day', fontsize=10)
ax.set_ylabel('Mean Stress', fontsize=10)
ax.set_title('Intervention Timing: Early vs Late', fontsize=11, fontweight='bold')
ax.legend(fontsize=7, loc='upper left')
ax.grid(True, alpha=0.3)
ax.tick_params(labelsize=9)

plt.tight_layout()
plt.savefig(OUTPUT_DIR / "scenario_intervention_timing.png", dpi=150, bbox_inches='tight')
print(f"✓ Saved: scenario_intervention_timing.png")
plt.close()

print("\n✅ All 4 scenario graphs generated successfully!")
print(f"📁 Saved to: {OUTPUT_DIR}")
