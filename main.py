import gradio as gr
import pandas as pd
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import seaborn as sns
import json
import sys
from pathlib import Path
from tqdm import tqdm
import io

# =============================================================================
# CONFIGURATION & CONSTANTS
# =============================================================================

BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "analysis"
OUTPUT_DIR.mkdir(exist_ok=True)
DATA_PATH = BASE_DIR / "user_behavior_dataset.csv"

# Paths
PERSONA_FILE = OUTPUT_DIR / "persona_definitions.json"
AGENT_COHORT_PATH = OUTPUT_DIR / "agent_cohort.csv"
NETWORK_PATH = OUTPUT_DIR / "social_network.graphml"
INFLUENCERS_PATH = OUTPUT_DIR / "influencers.json"

# Default Simulation Parameters
DEFAULT_PARAMS = {
    'alpha': 0.6,       # Personal usage weight
    'beta': 0.3,        # Peer influence weight
    'gamma': 0.1,       # Resilience weight
    'delta': 0.02,      # Self-feedback rate
    'resilience_mod': 1.0,     # Global modifier for agent resilience
    'susceptibility_mod': 1.0, # Global modifier for agent susceptibility
    'variability_mod': 1.0,    # Global modifier for agent variability
    'intervention_day': 10,
    'intervention_usage_factor': 0.5,
    'intervention_peer_factor': 0.3
}

# =============================================================================
# PHASE 3: AGENT FACTORY
# =============================================================================

class AgentFactory:
    """Factory for creating synthetic student agents"""
    
    def __init__(self, persona_definitions_path, n_agents=100, random_seed=42):
        self.n_agents = n_agents
        self.random_seed = random_seed
        np.random.seed(random_seed)
        
        # Load persona definitions
        if not persona_definitions_path.exists():
            raise FileNotFoundError(f"Persona definitions not found at {persona_definitions_path}. Please run Phase 1 & 2 first (or ensure the file exists).")
            
        with open(persona_definitions_path, 'r') as f:
            self.personas = json.load(f)
        self.persona_names = list(self.personas.keys())

    def create_agent_cohort(self):
        # Compute probabilities
        total = sum(p['count'] for p in self.personas.values())
        probabilities = {name: p['count'] / total for name, p in self.personas.items()}
        
        agents = []
        for i in range(self.n_agents):
            persona_name = np.random.choice(self.persona_names, p=[probabilities[p] for p in self.persona_names])
            persona = self.personas[persona_name]
            char = persona['characteristics']
            
            # Sample attributes
            agent = {
                'agent_id': i,
                'persona': persona_name,
                'app_usage': max(30, np.random.normal(char['app_usage_mean'], char['app_usage_std'])),
                'screen_time': max(1.0, np.random.normal(char['screen_time_mean'], char['screen_time_std'])),
                'battery_drain': max(300, np.random.normal(char['battery_drain_mean'], char['battery_drain_std'])),
                'apps_installed': max(10, int(np.random.normal(char['apps_installed_mean'], char['apps_installed_std']))),
                'data_usage': max(100, np.random.normal(char['data_usage_mean'], char['data_usage_std'])),
                'behavior_class': char['behavior_class_mode'],
                'age': max(18, min(59, int(np.random.normal(char['age_mean'], char['age_std'])))),
            }
            
            # Derived metrics
            agent['base_stress'] = (agent['behavior_class'] - 1) / 4.0 * 100.0
            agent['resilience'] = np.random.uniform(0.7, 1.3)
            agent['susceptibility'] = np.random.uniform(0.5, 1.5)
            agent['variability'] = np.random.uniform(0.8, 1.2)
            
            agents.append(agent)
            
        return pd.DataFrame(agents)

# =============================================================================
# PHASE 4: NETWORK TOPOLOGY
# =============================================================================

class NetworkBuilder:
    """Builds social network with homophily-based connections"""
    
    def __init__(self, agents_df, random_seed=42):
        self.agents_df = agents_df
        self.n_agents = len(agents_df)
        self.random_seed = random_seed
        np.random.seed(random_seed)
        
        # Parameters
        self.p_same_persona = 0.15
        self.p_diff_persona = 0.03
        self.p_bridge = 0.01
        self.min_degree = 2
        self.max_degree = 15
        
    def build_homophily_network(self):
        G = nx.Graph()
        
        # Add nodes
        for idx, agent in self.agents_df.iterrows():
            G.add_node(agent['agent_id'], persona=agent['persona'])
            
        # Edges
        for i in range(self.n_agents):
            for j in range(i + 1, self.n_agents):
                persona_i = self.agents_df.iloc[i]['persona']
                persona_j = self.agents_df.iloc[j]['persona']
                p_connect = self.p_same_persona if persona_i == persona_j else self.p_diff_persona
                
                if np.random.random() < p_connect:
                    G.add_edge(i, j)
                    
        # Bridges
        for i in range(self.n_agents):
            if np.random.random() < self.p_bridge:
                j = np.random.randint(0, self.n_agents)
                if i != j and not G.has_edge(i, j):
                    G.add_edge(i, j)
                    
        # Min degree enforcement
        for node in list(G.nodes()):
            while len(list(G.neighbors(node))) < self.min_degree:
                target = np.random.randint(0, self.n_agents)
                if target != node and not G.has_edge(node, target):
                    G.add_edge(node, target)
                    
        # Max degree enforcement
        for node in list(G.nodes()):
            while len(list(G.neighbors(node))) > self.max_degree:
                neighbors = list(G.neighbors(node))
                if neighbors:
                    remove = np.random.choice(neighbors)
                    G.remove_edge(node, remove)
                    
        return G

    def identify_influencers(self, G, top_k=5):
        degree_cent = nx.degree_centrality(G)
        betweenness_cent = nx.betweenness_centrality(G)
        eigenvector_cent = nx.eigenvector_centrality(G, max_iter=1000)
        
        scores = {}
        for node in G.nodes():
            scores[node] = (0.4 * degree_cent[node] + 0.3 * betweenness_cent[node] + 0.3 * eigenvector_cent[node])
            
        sorted_influencers = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_k]
        return [node for node, score in sorted_influencers]

# =============================================================================
# PHASE 5: TEMPORAL ENGINE
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
        
        # Unpack params
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
        
        # Apply modifiers to agent attributes
        resilience = agent['resilience'] * self.resilience_mod
        susceptibility = agent['susceptibility'] * self.susceptibility_mod
        variability = agent['variability'] * self.variability_mod
        
        # Always generate noise to maintain random stream synchronization
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
# GRADIO APP LOGIC
# =============================================================================

# Global State
from typing import Optional, Set

class SimulationState:
    def __init__(self):
        self.agents_df: Optional[pd.DataFrame] = None
        self.network: Optional[nx.Graph] = None
        self.influencers: Optional[Set[int]] = None
        self.baseline_results: Optional[pd.DataFrame] = None
        self.custom_results: Optional[pd.DataFrame] = None

state = SimulationState()

def initialize_system():
    """Load or create agents and network"""
    log = []
    try:
        # Try loading existing
        if AGENT_COHORT_PATH.exists() and NETWORK_PATH.exists():
            state.agents_df = pd.read_csv(AGENT_COHORT_PATH)
            network = nx.read_graphml(NETWORK_PATH)
            # Fix node types
            mapping = {node: int(node) for node in network.nodes()}
            state.network = nx.relabel_nodes(network, mapping)
            
            if INFLUENCERS_PATH.exists():
                with open(INFLUENCERS_PATH, 'r') as f:
                    data = json.load(f)
                    state.influencers = set(data['influencer_ids'])
            
            if state.agents_df is not None and state.network is not None:
                log.append(f"[OK] Loaded existing cohort: {len(state.agents_df)} agents")
                log.append(f"[OK] Loaded existing network: {state.network.number_of_edges()} edges")
        else:
            # Create new
            log.append("[INFO] Creating new agents and network...")
            factory = AgentFactory(PERSONA_FILE)
            state.agents_df = factory.create_agent_cohort()
            
            builder = NetworkBuilder(state.agents_df)
            state.network = builder.build_homophily_network()
            influencers = builder.identify_influencers(state.network)
            state.influencers = set(influencers)
            
            if state.agents_df is not None and state.network is not None:
                log.append(f"[OK] Created {len(state.agents_df)} agents")
                log.append(f"[OK] Created network with {state.network.number_of_edges()} edges")
            
        return "\n".join(log)
    except Exception as e:
        return f"[ERROR] Initialization failed: {str(e)}"

def run_simulation(alpha, beta, gamma, delta, res_mod, sus_mod, var_mod, int_day, apply_intervention):
    if state.agents_df is None or state.network is None:
        return "Please initialize the system first!", None, None, None

    params = {
        'alpha': alpha,
        'beta': beta,
        'gamma': gamma,
        'delta': delta,
        'resilience_mod': res_mod,
        'susceptibility_mod': sus_mod,
        'variability_mod': var_mod,
        'intervention_day': int_day,
        'intervention_usage_factor': 0.5,
        'intervention_peer_factor': 0.3
    }
    
    # Run Baseline (Default params, no intervention)
    engine_base = TemporalEngine(state.agents_df, state.network, params=DEFAULT_PARAMS)
    base_results = engine_base.simulate(intervention_day=None)
    
    # Run Custom (User params, intervention optional)
    engine_custom = TemporalEngine(state.agents_df, state.network, params=params)
    if apply_intervention:
        custom_results = engine_custom.simulate(intervention_day=int_day, intervention_agents=state.influencers)
    else:
        custom_results = engine_custom.simulate(intervention_day=None)
    
    # Generate Plots
    
    # Plot 1: Stress Comparison
    fig1, ax1 = plt.subplots(figsize=(10, 6))
    base_daily = base_results.groupby('day')['stress'].mean()
    custom_daily = custom_results.groupby('day')['stress'].mean()
    
    intervention_label = "With Intervention" if apply_intervention else "No Intervention"
    
    ax1.plot(base_daily.index+1, base_daily, label='Baseline (Default Params, No Intervention)', color='gray', linestyle='--', linewidth=2)
    ax1.plot(custom_daily.index +1, custom_daily, label=f'Custom Params ({intervention_label})', color='blue', linewidth=2)
    
    if apply_intervention:
        ax1.axvline(x=int_day, color='red', linestyle=':', alpha=0.5, label=f'Intervention Day {int_day}')
    
    ax1.set_title("Average Stress Level Comparison")
    ax1.set_xlabel("Day")
    ax1.set_ylabel("Stress (0-100)")
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Plot 2: Heatmap of Custom Run
    fig2, ax2 = plt.subplots(figsize=(12, 8))
    matrix = custom_results.pivot(index='agent_id', columns='day', values='stress')
    # Sort by final stress
    final_stress = matrix[30]
    matrix = matrix.loc[final_stress.sort_values(ascending=False).index]
    sns.heatmap(matrix, cmap='YlOrRd', vmin=0, vmax=100, ax=ax2)
    ax2.set_title("Custom Simulation Stress Heatmap")
    
    # Plot 3: Burnout Count
    fig3, ax3 = plt.subplots(figsize=(10, 6))
    base_burnout = base_results.groupby('day').apply(lambda x: (x['stress'] > 80).sum())
    custom_burnout = custom_results.groupby('day').apply(lambda x: (x['stress'] > 80).sum())
    
    ax3.plot(base_burnout.index, base_burnout, label='Baseline Burnout', color='gray', linestyle='--', linewidth=2)
    ax3.plot(custom_burnout.index, custom_burnout, label=f'Custom Burnout ({intervention_label})', color='red', linewidth=2)
    
    if apply_intervention:
        ax3.axvline(x=int_day, color='red', linestyle=':', alpha=0.5, label=f'Intervention Day {int_day}')
    
    ax3.set_title("Burnout Count (>80 Stress)")
    ax3.set_xlabel("Day")
    ax3.set_ylabel("Number of Agents")
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # Stats
    final_base = base_daily.iloc[-1]
    final_custom = custom_daily.iloc[-1]
    diff = final_custom - final_base
    pct_diff = (diff / final_base) * 100
    
    intervention_status = "✓ Applied" if apply_intervention else "✗ Not Applied"
    
    stats = f"""
    ### Simulation Results (Single Run, Seed=42)
    
    **Baseline (Default Parameters, No Intervention):**
    - Final Stress: {final_base:.2f}
    - Burnout Count: {base_burnout.iloc[-1]} agents
    
    **Custom Simulation (Your Parameters):**
    - Final Stress: {final_custom:.2f}
    - Burnout Count: {custom_burnout.iloc[-1]} agents
    - Intervention: {intervention_status}
    
    **Difference:**
    - Stress Change: {diff:+.2f} ({pct_diff:+.1f}%)
    - Burnout Change: {int(custom_burnout.iloc[-1] - base_burnout.iloc[-1]):+d} agents
    
    Note: Results from a single simulation run. Actual project results (40.09±0.73) are averaged over 5 runs with different random seeds for better accuracy.    """
    
    return stats, fig1, fig2, fig3

# =============================================================================
# GRADIO UI LAYOUT
# =============================================================================

with gr.Blocks(title="Digital Contagion Simulator - Interactive") as demo:
    gr.Markdown("#  Interactive Digital Contagion Simulator")
    gr.Markdown("Design your own simulation theory by adjusting the parameters below.")
    
    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("### 1. System Setup")
            init_btn = gr.Button("Initialize Agents & Network", variant="primary")
            init_log = gr.Textbox(label="System Status", value="Not Initialized", lines=4)
            
            gr.Markdown("### 2. Simulation Parameters")
            gr.Markdown("Adjust these sliders to test your theory.")
            
            with gr.Group():
                gr.Markdown("**Equation Weights**")
                s_alpha = gr.Slider(0.0, 1.0, value=0.6, label="Alpha (Usage Weight)", info="How much personal app usage causes stress.")
                s_beta = gr.Slider(0.0, 1.0, value=0.3, label="Beta (Peer Influence)", info="How much friends' stress affects you.")
                s_gamma = gr.Slider(0.0, 1.0, value=0.1, label="Gamma (Resilience)", info="How much natural resilience reduces stress.")
                s_delta = gr.Slider(0.0, 0.1, value=0.02, label="Delta (Feedback)", info="How much stress drives more app usage (loop).")
            
            with gr.Group():
                gr.Markdown("**Population Modifiers**")
                s_res = gr.Slider(0.5, 2.0, value=1.0, label="Resilience Modifier", info="Multiply population resilience (e.g., 1.5 = 50% more resilient).")
                s_sus = gr.Slider(0.5, 2.0, value=1.0, label="Susceptibility Modifier", info="Multiply population susceptibility to peers.")
                s_var = gr.Slider(0.5, 2.0, value=1.0, label="Variability Modifier", info="Multiply daily behavior randomness.")
            
            with gr.Group():
                gr.Markdown("**Intervention Policy**")
                apply_int = gr.Checkbox(value=False, label="Apply Intervention", info="Enable influencer quarantine (top 5 agents reduce usage by 50%)")
                s_day = gr.Slider(1, 30, value=10, step=1, label="Intervention Day", info="Day to start influencer quarantine (only if enabled).")
            
            run_btn = gr.Button("Run Simulation", variant="primary")
            
        with gr.Column(scale=2):
            gr.Markdown("### 3. Results & Comparison")
            stats_out = gr.Markdown("Run simulation to see results.")
            
            with gr.Tabs():
                with gr.TabItem("Stress Comparison"):
                    plot1 = gr.Plot(label="Stress Comparison")
                with gr.TabItem("Heatmap"):
                    plot2 = gr.Plot(label="Stress Heatmap")
                with gr.TabItem("Burnout"):
                    plot3 = gr.Plot(label="Burnout Analysis")

    # Event Handlers
    init_btn.click(initialize_system, outputs=[init_log])
    
    run_btn.click(
        run_simulation,
        inputs=[s_alpha, s_beta, s_gamma, s_delta, s_res, s_sus, s_var, s_day, apply_int],
        outputs=[stats_out, plot1, plot2, plot3]
    )

if __name__ == "__main__":
    demo.launch(server_name="127.0.0.1", share=False)
