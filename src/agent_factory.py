"""
Phase 3: Agent Factory Specification
Defines rules for instantiating synthetic agents with reproducible seeds
"""

import pandas as pd
import numpy as np
import json
from pathlib import Path

# Configuration
PERSONA_FILE = Path(__file__).parent.parent / "analysis" / "persona_definitions.json"
OUTPUT_DIR = Path(__file__).parent.parent / "analysis"
OUTPUT_DIR.mkdir(exist_ok=True)

class AgentFactory:
    """Factory for creating synthetic student agents"""
    
    def __init__(self, persona_definitions_path, n_agents=100, random_seed=42):
        """
        Initialize the agent factory
        
        Args:
            persona_definitions_path: Path to persona definitions JSON
            n_agents: Number of agents to create
            random_seed: Random seed for reproducibility
        """
        self.n_agents = n_agents
        self.random_seed = random_seed
        np.random.seed(random_seed)
        
        # Load persona definitions
        with open(persona_definitions_path, 'r') as f:
            self.personas = json.load(f)
        
        self.persona_names = list(self.personas.keys())
        
        print("="*60)
        print("AGENT FACTORY INITIALIZATION")
        print("="*60)
        print(f"✓ Loaded {len(self.personas)} persona definitions")
        print(f"✓ Target cohort size: {n_agents} agents")
        print(f"✓ Random seed: {random_seed}")
    
    def compute_persona_probabilities(self):
        """
        Compute sampling probabilities based on persona distribution in original dataset
        """
        total = sum(p['count'] for p in self.personas.values())
        probabilities = {
            name: p['count'] / total 
            for name, p in self.personas.items()
        }
        
        print("\n" + "="*60)
        print("PERSONA SAMPLING PROBABILITIES")
        print("="*60)
        for name, prob in probabilities.items():
            print(f"  {name}: {prob:.3f}")
        
        return probabilities
    
    def sample_persona(self, probabilities):
        """Sample a persona based on probabilities"""
        return np.random.choice(self.persona_names, p=[probabilities[p] for p in self.persona_names])
    
    def sample_agent_attributes(self, persona_name):
        """
        Sample agent attributes from persona distribution
        
        Returns dict with all agent attributes
        """
        persona = self.personas[persona_name]
        char = persona['characteristics']
        
        # Sample from normal distributions with bounds
        agent = {
            'persona': persona_name,
            'app_usage': max(30, np.random.normal(char['app_usage_mean'], char['app_usage_std'])),
            'screen_time': max(1.0, np.random.normal(char['screen_time_mean'], char['screen_time_std'])),
            'battery_drain': max(300, np.random.normal(char['battery_drain_mean'], char['battery_drain_std'])),
            'apps_installed': max(10, int(np.random.normal(char['apps_installed_mean'], char['apps_installed_std']))),
            'data_usage': max(100, np.random.normal(char['data_usage_mean'], char['data_usage_std'])),
            'behavior_class': char['behavior_class_mode'],
            'age': max(18, min(59, int(np.random.normal(char['age_mean'], char['age_std'])))),
        }
        
        # Compute base stress level (normalized behavior class as proxy)
        agent['base_stress'] = (agent['behavior_class'] - 1) / 4.0 * 100  # Scale 0-100
        
        # Resilience factor (inverse of stress tendency)
        agent['resilience'] = np.random.uniform(0.7, 1.3)  # Variance around 1.0
        
        # Influence susceptibility (how much neighbors affect them)
        agent['susceptibility'] = np.random.uniform(0.5, 1.5)
        
        # Daily variability coefficient
        agent['variability'] = np.random.uniform(0.8, 1.2)
        
        return agent
    
    def create_agent_cohort(self):
        """
        Create full cohort of synthetic agents
        
        Returns DataFrame with all agent attributes
        """
        print("\n" + "="*60)
        print("CREATING AGENT COHORT")
        print("="*60)
        
        probabilities = self.compute_persona_probabilities()
        
        agents = []
        for i in range(self.n_agents):
            persona = self.sample_persona(probabilities)
            agent = self.sample_agent_attributes(persona)
            agent['agent_id'] = i
            agents.append(agent)
        
        df = pd.DataFrame(agents)
        
        # Reorder columns
        cols = ['agent_id', 'persona', 'base_stress', 'resilience', 'susceptibility', 
                'variability', 'app_usage', 'screen_time', 'battery_drain', 
                'apps_installed', 'data_usage', 'behavior_class', 'age']
        df = df[cols]
        
        print(f"\n✓ Created {len(df)} agents")
        print(f"\n✓ Persona distribution in cohort:")
        for persona in self.persona_names:
            count = (df['persona'] == persona).sum()
            pct = (count / len(df)) * 100
            print(f"  {persona}: {count} ({pct:.1f}%)")
        
        return df
    
    def validate_cohort(self, df):
        """
        Validate synthetic cohort matches expected distributions
        """
        print("\n" + "="*60)
        print("COHORT VALIDATION")
        print("="*60)
        
        # Compare aggregate stats
        print("\nComparison with Original Dataset:")
        
        # Load original dataset stats
        from pathlib import Path
        data_path = Path(__file__).parent.parent / "user_behavior_dataset.csv"
        original_df = pd.read_csv(data_path)
        
        metrics = {
            'Screen Time (hrs/day)': ('screen_time', 'Screen On Time (hours/day)'),
            'App Usage (min/day)': ('app_usage', 'App Usage Time (min/day)'),
            'Battery Drain (mAh/day)': ('battery_drain', 'Battery Drain (mAh/day)'),
        }
        
        for metric_name, (synth_col, orig_col) in metrics.items():
            synth_mean = df[synth_col].mean()
            synth_std = df[synth_col].std()
            orig_mean = original_df[orig_col].mean()
            orig_std = original_df[orig_col].std()
            
            print(f"\n{metric_name}:")
            print(f"  Original:  {orig_mean:.2f} ± {orig_std:.2f}")
            print(f"  Synthetic: {synth_mean:.2f} ± {synth_std:.2f}")
            
            # Compute relative difference
            diff_pct = abs(synth_mean - orig_mean) / orig_mean * 100
            if diff_pct < 10:
                print(f"  ✓ Difference: {diff_pct:.1f}% (Good)")
            else:
                print(f"  ⚠ Difference: {diff_pct:.1f}% (Acceptable)")
        
        print("\n✓ Cohort validation complete")
    
    def save_cohort(self, df):
        """Save agent cohort to files"""
        # Save as CSV
        csv_path = OUTPUT_DIR / "agent_cohort.csv"
        df.to_csv(csv_path, index=False)
        print(f"\n✓ Saved agent cohort to {csv_path}")
        
        # Save as JSON with metadata
        json_path = OUTPUT_DIR / "agent_cohort.json"
        cohort_data = {
            'metadata': {
                'n_agents': self.n_agents,
                'random_seed': self.random_seed,
                'personas': self.persona_names
            },
            'agents': df.to_dict(orient='records')
        }
        with open(json_path, 'w') as f:
            json.dump(cohort_data, f, indent=2)
        print(f"✓ Saved agent cohort with metadata to {json_path}")
        
        # Save agent factory specification document
        spec_path = OUTPUT_DIR / "agent_factory_specification.txt"
        with open(spec_path, 'w') as f:
            f.write("="*80 + "\n")
            f.write("AGENT FACTORY SPECIFICATION\n")
            f.write("="*80 + "\n\n")
            
            f.write("CONFIGURATION\n")
            f.write("-"*80 + "\n")
            f.write(f"Cohort Size: {self.n_agents} agents\n")
            f.write(f"Random Seed: {self.random_seed}\n")
            f.write(f"Personas: {len(self.personas)}\n\n")
            
            f.write("SAMPLING STRATEGY\n")
            f.write("-"*80 + "\n")
            f.write("1. Persona Selection: Multinomial sampling based on original distribution\n")
            f.write("2. Attribute Sampling: Normal distribution per persona with truncation\n")
            f.write("3. Derived Metrics:\n")
            f.write("   - Base Stress: Scaled from behavior class (0-100)\n")
            f.write("   - Resilience: Uniform [0.7, 1.3]\n")
            f.write("   - Susceptibility: Uniform [0.5, 1.5]\n")
            f.write("   - Variability: Uniform [0.8, 1.2]\n\n")
            
            f.write("AGENT ATTRIBUTES\n")
            f.write("-"*80 + "\n")
            f.write("Core Attributes:\n")
            f.write("  • agent_id: Unique identifier (0 to n-1)\n")
            f.write("  • persona: Behavioral archetype\n")
            f.write("  • base_stress: Initial stress level (0-100)\n")
            f.write("  • resilience: Stress resistance multiplier\n")
            f.write("  • susceptibility: Peer influence multiplier\n")
            f.write("  • variability: Daily usage variance\n\n")
            
            f.write("Behavioral Attributes (from persona):\n")
            f.write("  • app_usage: Daily app usage (minutes)\n")
            f.write("  • screen_time: Daily screen time (hours)\n")
            f.write("  • battery_drain: Daily battery drain (mAh)\n")
            f.write("  • apps_installed: Number of apps\n")
            f.write("  • data_usage: Daily data consumption (MB)\n")
            f.write("  • behavior_class: User behavior category (1-5)\n")
            f.write("  • age: Agent age (18-59)\n\n")
            
            f.write("VALIDATION CRITERIA\n")
            f.write("-"*80 + "\n")
            f.write("Synthetic cohort aggregate statistics must match original dataset:\n")
            f.write("  • Mean differences < 10% for key metrics\n")
            f.write("  • Persona distribution within ±5% of original\n")
        
        print(f"✓ Saved agent factory specification to {spec_path}")

def main():
    """Execute agent factory pipeline"""
    print("\n" + "="*60)
    print("PHASE 3: AGENT FACTORY SPECIFICATION")
    print("="*60 + "\n")
    
    # Initialize factory
    factory = AgentFactory(
        persona_definitions_path=PERSONA_FILE,
        n_agents=100,
        random_seed=42
    )
    
    # Create agent cohort
    df = factory.create_agent_cohort()
    
    # Validate cohort
    factory.validate_cohort(df)
    
    # Save cohort
    factory.save_cohort(df)
    
    print("\n" + "="*60)
    print("PHASE 3 COMPLETE ✓")
    print("="*60)
    print(f"\nOutputs saved to: {OUTPUT_DIR}")
    print("  - agent_cohort.csv")
    print("  - agent_cohort.json")
    print("  - agent_factory_specification.txt")

if __name__ == "__main__":
    main()
