"""
Phase 5: Temporal Engine Design
Implements 30-day simulation with stress contagion dynamics
"""

import pandas as pd
import numpy as np
import networkx as nx
import json
from pathlib import Path
from tqdm import tqdm

# Configuration
AGENT_COHORT_PATH = Path(__file__).parent.parent / "analysis" / "agent_cohort.csv"
NETWORK_PATH = Path(__file__).parent.parent / "analysis" / "social_network.graphml"
INFLUENCERS_PATH = Path(__file__).parent.parent / "analysis" / "influencers.json"
OUTPUT_DIR = Path(__file__).parent.parent / "analysis"
OUTPUT_DIR.mkdir(exist_ok=True)

class TemporalEngine:
    """Simulates 30-day digital stress contagion"""
    
    def __init__(self, agents_df, network, random_seed=42):
        """
        Initialize temporal engine
        
        Args:
            agents_df: DataFrame with agent attributes
            network: NetworkX graph
            random_seed: Random seed for reproducibility
        """
        self.agents_df = agents_df.copy()
        self.G = network
        self.n_agents = len(agents_df)
        self.random_seed = random_seed
        np.random.seed(random_seed)
        
        # Simulation parameters
        self.n_days = 30
        self.alpha = 0.6  # Weight of personal usage on stress
        self.beta = 0.3   # Weight of peer influence on stress
        self.gamma = 0.1  # Weight of resilience (negative)
        self.delta = 0.02 # Self-feedback: high stress increases usage
        self.stress_cap = 100.0  # Maximum stress level
        self.usage_min = 30.0    # Minimum app usage (minutes)
        
        print("="*60)
        print("TEMPORAL ENGINE INITIALIZATION")
        print("="*60)
        print(f"✓ Loaded {self.n_agents} agents")
        print(f"✓ Loaded network with {self.G.number_of_edges()} edges")
        print(f"✓ Random seed: {random_seed}")
        print(f"\nSimulation Parameters:")
        print(f"  • Time horizon: {self.n_days} days")
        print(f"  • α (personal usage weight): {self.alpha}")
        print(f"  • β (peer influence weight): {self.beta}")
        print(f"  • γ (resilience weight): {self.gamma}")
        print(f"  • δ (self-feedback rate): {self.delta}")
        print(f"  • Stress cap: {self.stress_cap}")
    
    def initialize_state(self):
        """Initialize agent states for day 0"""
        print("\n" + "="*60)
        print("INITIALIZING AGENT STATES")
        print("="*60)
        
        # Create state tracking dataframe
        state_cols = ['agent_id', 'day', 'stress', 'usage', 'peer_influence', 
                      'persona', 'intervention_active']
        self.daily_states = []
        
        # Day 0 initial state
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
        
        print(f"✓ Initialized {self.n_agents} agent states for day 0")
        print(f"✓ Initial stress: {np.mean([s['stress'] for s in self.daily_states]):.2f} ± {np.std([s['stress'] for s in self.daily_states]):.2f}")
    
    def compute_peer_influence(self, agent_id, day):
        """
        Compute average stress of neighbors
        
        Args:
            agent_id: Agent ID
            day: Current day
            
        Returns:
            Average neighbor stress
        """
        neighbors = list(self.G.neighbors(agent_id))
        
        if len(neighbors) == 0:
            return 0.0
        
        # Get neighbor stress levels from previous day
        neighbor_stress = []
        prev_day_states = [s for s in self.daily_states if s['day'] == day - 1]
        
        for neighbor_id in neighbors:
            neighbor_state = next((s for s in prev_day_states if s['agent_id'] == neighbor_id), None)
            if neighbor_state:
                neighbor_stress.append(neighbor_state['stress'])
        
        return np.mean(neighbor_stress) if neighbor_stress else 0.0
    
    def update_agent_state(self, agent_id, day, intervention_agents=None):
        """
        Update agent state for current day using contagion equation
        
        Stress_t = α * Usage_t + β * AvgNeighborStress_{t-1} * Susceptibility - γ * Resilience
        Usage_t = Usage_{t-1} * (1 + δ * Stress_{t-1}/100) * Variability
        
        Args:
            agent_id: Agent ID
            day: Current day
            intervention_agents: Set of agent IDs under intervention (quarantine)
            
        Returns:
            Updated state dict
        """
        if intervention_agents is None:
            intervention_agents = set()
        
        # Get agent attributes
        agent = self.agents_df[self.agents_df['agent_id'] == agent_id].iloc[0]
        
        # Get previous day state
        prev_state = next((s for s in self.daily_states if s['agent_id'] == agent_id and s['day'] == day - 1))
        
        # Compute peer influence (average neighbor stress)
        avg_neighbor_stress = self.compute_peer_influence(agent_id, day)
        
        # Check if under intervention
        is_intervened = agent_id in intervention_agents
        
        # Update usage with self-feedback and daily variability
        if is_intervened:
            # Intervention: clamp usage to 50% of baseline
            new_usage = agent['app_usage'] * 0.5
        else:
            stress_factor = 1 + self.delta * (prev_state['stress'] / 100.0)
            variability_noise = np.random.normal(1.0, 0.1)  # ±10% daily noise
            new_usage = prev_state['usage'] * stress_factor * variability_noise * agent['variability']
            new_usage = max(self.usage_min, new_usage)  # Floor at minimum usage
        
        # Normalize usage for stress calculation (scale to 0-100)
        usage_normalized = min(100, (new_usage / 600.0) * 100)  # 600 min = 10 hrs as max
        
        # Compute stress using contagion equation
        peer_contribution = avg_neighbor_stress * agent['susceptibility']
        
        if is_intervened:
            # Intervention: reduce peer influence by 70%
            peer_contribution *= 0.3
        
        new_stress = (
            self.alpha * usage_normalized +
            self.beta * peer_contribution -
            self.gamma * agent['resilience'] * 10  # Scale resilience effect
        )
        
        # Cap stress at maximum
        new_stress = max(0, min(self.stress_cap, new_stress))
        
        # Create new state
        new_state = {
            'agent_id': agent_id,
            'day': day,
            'stress': new_stress,
            'usage': new_usage,
            'peer_influence': avg_neighbor_stress,
            'persona': agent['persona'],
            'intervention_active': is_intervened
        }
        
        return new_state
    
    def simulate(self, intervention_day=None, intervention_agents=None, verbose=True):
        """
        Run 30-day simulation
        
        Args:
            intervention_day: Day to start intervention (None for no intervention)
            intervention_agents: Set of agent IDs to intervene on (None for no intervention)
            verbose: Print progress
            
        Returns:
            DataFrame with all daily states
        """
        if verbose:
            print("\n" + "="*60)
            print("RUNNING 30-DAY SIMULATION")
            print("="*60)
            
            if intervention_day and intervention_agents:
                print(f"\n✓ Intervention scheduled:")
                print(f"  • Day: {intervention_day}")
                print(f"  • Agents affected: {len(intervention_agents)}")
        
        # Initialize state
        self.initialize_state()
        
        # Simulate days 1-30
        iterator = tqdm(range(1, self.n_days + 1), desc="Simulating days") if verbose else range(1, self.n_days + 1)
        
        for day in iterator:
            # Determine if intervention is active
            active_intervention = intervention_agents if (intervention_day and day >= intervention_day) else None
            
            # Update all agents
            for agent_id in range(self.n_agents):
                new_state = self.update_agent_state(agent_id, day, active_intervention)
                self.daily_states.append(new_state)
        
        # Convert to DataFrame
        results_df = pd.DataFrame(self.daily_states)
        
        if verbose:
            print(f"\n✓ Simulation complete")
            print(f"✓ Generated {len(results_df)} state records")
            print(f"\n✓ Final day stats:")
            final_day = results_df[results_df['day'] == self.n_days]
            print(f"  • Avg stress: {final_day['stress'].mean():.2f} ± {final_day['stress'].std():.2f}")
            print(f"  • Peak stress: {final_day['stress'].max():.2f}")
            print(f"  • Agents in burnout (stress > 80): {(final_day['stress'] > 80).sum()}")
        
        return results_df
    
    def compute_summary_metrics(self, results_df):
        """Compute summary metrics from simulation results"""
        metrics = {}
        
        # Overall metrics
        metrics['total_records'] = len(results_df)
        metrics['n_agents'] = self.n_agents
        metrics['n_days'] = self.n_days
        
        # Initial vs final stress
        day_0 = results_df[results_df['day'] == 0]
        day_final = results_df[results_df['day'] == self.n_days]
        
        metrics['initial_stress_mean'] = float(day_0['stress'].mean())
        metrics['initial_stress_std'] = float(day_0['stress'].std())
        metrics['final_stress_mean'] = float(day_final['stress'].mean())
        metrics['final_stress_std'] = float(day_final['stress'].std())
        metrics['stress_change'] = float(metrics['final_stress_mean'] - metrics['initial_stress_mean'])
        
        # Peak stress
        metrics['peak_stress_overall'] = float(results_df['stress'].max())
        
        # Day of peak (when did average stress peak?)
        daily_avg_stress = results_df.groupby('day')['stress'].mean()
        metrics['peak_stress_day'] = int(daily_avg_stress.idxmax())
        metrics['peak_stress_value'] = float(daily_avg_stress.max())
        
        # Burnout count (stress > 80)
        metrics['burnout_count_initial'] = int((day_0['stress'] > 80).sum())
        metrics['burnout_count_final'] = int((day_final['stress'] > 80).sum())
        
        # Total stress area under curve (cumulative stress)
        metrics['total_stress_auc'] = float(results_df.groupby('agent_id')['stress'].sum().sum())
        
        # Average stress area per agent
        metrics['avg_stress_auc_per_agent'] = metrics['total_stress_auc'] / self.n_agents
        
        return metrics

def run_single_simulation(agents_df, network, seed, intervention_day=None, intervention_agents=None):
    """Helper function to run a single simulation"""
    engine = TemporalEngine(agents_df, network, random_seed=seed)
    results_df = engine.simulate(
        intervention_day=intervention_day,
        intervention_agents=intervention_agents,
        verbose=False
    )
    metrics = engine.compute_summary_metrics(results_df)
    return results_df, metrics

def main():
    """Execute temporal engine pipeline"""
    print("\n" + "="*60)
    print("PHASE 5: TEMPORAL ENGINE DESIGN")
    print("="*60 + "\n")
    
    # Load data
    agents_df = pd.read_csv(AGENT_COHORT_PATH)
    network = nx.read_graphml(NETWORK_PATH)
    
    # Convert node labels to integers (GraphML stores as strings)
    mapping = {node: int(node) for node in network.nodes()}
    network = nx.relabel_nodes(network, mapping)
    
    print(f"✓ Loaded {len(agents_df)} agents")
    print(f"✓ Loaded network with {network.number_of_edges()} edges")
    
    # Run baseline simulation (no intervention)
    print("\n" + "="*60)
    print("BASELINE SIMULATION (No Intervention)")
    print("="*60)
    
    engine = TemporalEngine(agents_df, network, random_seed=42)
    baseline_results = engine.simulate(intervention_day=None, intervention_agents=None)
    baseline_metrics = engine.compute_summary_metrics(baseline_results)
    
    # Save baseline results
    baseline_path = OUTPUT_DIR / "simulation_baseline.csv"
    baseline_results.to_csv(baseline_path, index=False)
    print(f"\n✓ Saved baseline results to {baseline_path}")
    
    baseline_metrics_path = OUTPUT_DIR / "simulation_baseline_metrics.json"
    with open(baseline_metrics_path, 'w') as f:
        json.dump(baseline_metrics, f, indent=2)
    print(f"✓ Saved baseline metrics to {baseline_metrics_path}")
    
    # Save engine specification
    spec_path = OUTPUT_DIR / "temporal_engine_specification.txt"
    with open(spec_path, 'w', encoding='utf-8') as f:
        f.write("="*80 + "\n")
        f.write("TEMPORAL ENGINE SPECIFICATION\n")
        f.write("="*80 + "\n\n")
        
        f.write("SIMULATION MODEL: Agent-Based Stress Contagion\n")
        f.write("-"*80 + "\n")
        f.write("Description: Daily update model where stress propagates through social\n")
        f.write("             connections and influences digital usage behavior\n\n")
        
        f.write("UPDATE EQUATIONS:\n")
        f.write("-"*80 + "\n")
        f.write("Stress Update:\n")
        f.write(f"  Stress_t = α * Usage_normalized_t + β * AvgNeighborStress_{{t-1}} * Susceptibility - γ * Resilience\n")
        f.write(f"  where:\n")
        f.write(f"    α = {engine.alpha} (personal usage weight)\n")
        f.write(f"    β = {engine.beta} (peer influence weight)\n")
        f.write(f"    γ = {engine.gamma} (resilience weight)\n\n")
        
        f.write("Usage Update:\n")
        f.write(f"  Usage_t = Usage_{{t-1}} * (1 + δ * Stress_{{t-1}}/100) * Variability * Noise\n")
        f.write(f"  where:\n")
        f.write(f"    δ = {engine.delta} (self-feedback rate)\n")
        f.write(f"    Variability ~ agent-specific [0.8, 1.2]\n")
        f.write(f"    Noise ~ N(1.0, 0.1) (daily randomness)\n\n")
        
        f.write("PARAMETERS:\n")
        f.write("-"*80 + "\n")
        f.write(f"  • Time horizon: {engine.n_days} days\n")
        f.write(f"  • Stress cap: {engine.stress_cap}\n")
        f.write(f"  • Minimum usage: {engine.usage_min} min/day\n\n")
        
        f.write("BASELINE METRICS:\n")
        f.write("-"*80 + "\n")
        for key, value in baseline_metrics.items():
            if isinstance(value, float):
                f.write(f"  {key}: {value:.2f}\n")
            else:
                f.write(f"  {key}: {value}\n")
    
    print(f"✓ Saved engine specification to {spec_path}")
    
    print("\n" + "="*60)
    print("PHASE 5 COMPLETE ✓")
    print("="*60)
    print(f"\nOutputs saved to: {OUTPUT_DIR}")
    print("  - simulation_baseline.csv")
    print("  - simulation_baseline_metrics.json")
    print("  - temporal_engine_specification.txt")

if __name__ == "__main__":
    main()
