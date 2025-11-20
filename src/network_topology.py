"""
Phase 4: Social Topology Blueprint
Generates friendship networks with homophily and assortativity
"""

import pandas as pd
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import json
from pathlib import Path

# Configuration
AGENT_COHORT_PATH = Path(__file__).parent.parent / "analysis" / "agent_cohort.csv"
OUTPUT_DIR = Path(__file__).parent.parent / "analysis"
OUTPUT_DIR.mkdir(exist_ok=True)

class NetworkBuilder:
    """Builds social network with homophily-based connections"""
    
    def __init__(self, agents_df, random_seed=42):
        """
        Initialize network builder
        
        Args:
            agents_df: DataFrame with agent attributes
            random_seed: Random seed for reproducibility
        """
        self.agents_df = agents_df
        self.n_agents = len(agents_df)
        self.random_seed = random_seed
        np.random.seed(random_seed)
        
        # Network parameters (based on social network research)
        self.p_same_persona = 0.15  # Probability of connection within same persona
        self.p_diff_persona = 0.03  # Probability of connection across personas
        self.p_bridge = 0.01        # Probability of random bridge connections
        self.min_degree = 2         # Minimum friends per agent
        self.max_degree = 15        # Maximum friends per agent
        self.target_avg_degree = 6  # Target average degree (typical for student networks)
        
        print("="*60)
        print("NETWORK BUILDER INITIALIZATION")
        print("="*60)
        print(f"✓ Loaded {self.n_agents} agents")
        print(f"✓ Random seed: {random_seed}")
        print(f"\nNetwork Parameters:")
        print(f"  • Same persona connection prob: {self.p_same_persona}")
        print(f"  • Different persona connection prob: {self.p_diff_persona}")
        print(f"  • Bridge connection prob: {self.p_bridge}")
        print(f"  • Degree range: [{self.min_degree}, {self.max_degree}]")
        print(f"  • Target avg degree: {self.target_avg_degree}")
    
    def build_homophily_network(self):
        """
        Build network with homophily (similar personas connect more)
        """
        print("\n" + "="*60)
        print("BUILDING HOMOPHILY-BASED NETWORK")
        print("="*60)
        
        G = nx.Graph()
        
        # Add nodes with attributes
        for idx, agent in self.agents_df.iterrows():
            G.add_node(
                agent['agent_id'],
                persona=agent['persona'],
                base_stress=agent['base_stress'],
                screen_time=agent['screen_time'],
                behavior_class=agent['behavior_class']
            )
        
        print(f"✓ Added {G.number_of_nodes()} nodes")
        
        # Phase 1: Homophily-based connections
        edges_added = 0
        for i in range(self.n_agents):
            for j in range(i + 1, self.n_agents):
                persona_i = self.agents_df.iloc[i]['persona']
                persona_j = self.agents_df.iloc[j]['persona']
                
                # Determine connection probability based on persona similarity
                if persona_i == persona_j:
                    p_connect = self.p_same_persona
                else:
                    p_connect = self.p_diff_persona
                
                # Probabilistic edge creation
                if np.random.random() < p_connect:
                    G.add_edge(i, j)
                    edges_added += 1
        
        print(f"✓ Added {edges_added} homophily-based edges")
        
        # Phase 2: Bridge connections (ensure connectivity)
        bridge_edges = 0
        for i in range(self.n_agents):
            # Add random bridges to prevent isolated clusters
            if np.random.random() < self.p_bridge:
                j = np.random.randint(0, self.n_agents)
                if i != j and not G.has_edge(i, j):
                    G.add_edge(i, j)
                    bridge_edges += 1
        
        print(f"✓ Added {bridge_edges} bridge edges")
        
        # Phase 3: Ensure minimum degree
        isolated_fixed = 0
        for node in G.nodes():
            degree = G.degree(node)
            if degree < self.min_degree:
                # Connect to random nodes until min degree met
                attempts = 0
                while G.degree(node) < self.min_degree and attempts < 20:
                    target = np.random.randint(0, self.n_agents)
                    if target != node and not G.has_edge(node, target):
                        G.add_edge(node, target)
                        isolated_fixed += 1
                    attempts += 1
        
        print(f"✓ Fixed {isolated_fixed} under-connected nodes")
        
        # Phase 4: Enforce maximum degree (trim excess connections)
        trimmed = 0
        for node in G.nodes():
            degree = G.degree(node)
            if degree > self.max_degree:
                # Remove random edges until max degree met
                neighbors = list(G.neighbors(node))
                to_remove = np.random.choice(neighbors, size=degree - self.max_degree, replace=False)
                for neighbor in to_remove:
                    G.remove_edge(node, neighbor)
                    trimmed += 1
        
        if trimmed > 0:
            print(f"✓ Trimmed {trimmed} excess edges")
        
        return G
    
    def compute_network_metrics(self, G):
        """Compute key network topology metrics"""
        print("\n" + "="*60)
        print("NETWORK TOPOLOGY METRICS")
        print("="*60)
        
        metrics = {}
        
        # Basic metrics
        metrics['n_nodes'] = G.number_of_nodes()
        metrics['n_edges'] = G.number_of_edges()
        metrics['density'] = nx.density(G)
        
        # Degree statistics
        degrees = [deg for node, deg in G.degree()]
        metrics['avg_degree'] = np.mean(degrees)
        metrics['std_degree'] = np.std(degrees)
        metrics['min_degree'] = np.min(degrees)
        metrics['max_degree'] = np.max(degrees)
        
        # Connectivity
        metrics['is_connected'] = nx.is_connected(G)
        if not metrics['is_connected']:
            metrics['n_components'] = nx.number_connected_components(G)
            largest_cc = max(nx.connected_components(G), key=len)
            metrics['largest_component_size'] = len(largest_cc)
        else:
            metrics['n_components'] = 1
            metrics['largest_component_size'] = metrics['n_nodes']
        
        # Clustering
        metrics['avg_clustering'] = nx.average_clustering(G)
        metrics['transitivity'] = nx.transitivity(G)
        
        # Path metrics (on largest component if disconnected)
        if metrics['is_connected']:
            metrics['diameter'] = nx.diameter(G)
            metrics['avg_shortest_path'] = nx.average_shortest_path_length(G)
        else:
            largest_cc = G.subgraph(max(nx.connected_components(G), key=len))
            metrics['diameter'] = nx.diameter(largest_cc)
            metrics['avg_shortest_path'] = nx.average_shortest_path_length(largest_cc)
        
        # Assortativity (do similar personas connect?)
        # Create numeric mapping for personas
        persona_to_int = {p: i for i, p in enumerate(self.agents_df['persona'].unique())}
        nx.set_node_attributes(G, {node: persona_to_int[G.nodes[node]['persona']] 
                                    for node in G.nodes()}, 'persona_int')
        metrics['assortativity_persona'] = nx.attribute_assortativity_coefficient(G, 'persona_int')
        
        # Print metrics
        print(f"\nBasic Structure:")
        print(f"  Nodes: {metrics['n_nodes']}")
        print(f"  Edges: {metrics['n_edges']}")
        print(f"  Density: {metrics['density']:.4f}")
        print(f"  Connected: {metrics['is_connected']}")
        
        print(f"\nDegree Distribution:")
        print(f"  Average: {metrics['avg_degree']:.2f} ± {metrics['std_degree']:.2f}")
        print(f"  Range: [{metrics['min_degree']}, {metrics['max_degree']}]")
        
        print(f"\nClustering:")
        print(f"  Avg Clustering Coefficient: {metrics['avg_clustering']:.3f}")
        print(f"  Transitivity: {metrics['transitivity']:.3f}")
        
        print(f"\nPath Metrics:")
        print(f"  Diameter: {metrics['diameter']}")
        print(f"  Avg Shortest Path: {metrics['avg_shortest_path']:.2f}")
        
        print(f"\nHomophily:")
        print(f"  Assortativity (persona): {metrics['assortativity_persona']:.3f}")
        if metrics['assortativity_persona'] > 0:
            print(f"  ✓ Positive assortativity detected (homophily present)")
        
        return metrics
    
    def identify_influencers(self, G, top_k=5):
        """Identify top influencers using centrality measures"""
        print("\n" + "="*60)
        print(f"IDENTIFYING TOP {top_k} INFLUENCERS")
        print("="*60)
        
        # Compute multiple centrality measures
        degree_cent = nx.degree_centrality(G)
        betweenness_cent = nx.betweenness_centrality(G)
        eigenvector_cent = nx.eigenvector_centrality(G, max_iter=1000)
        
        # Composite influence score (weighted average)
        influence_scores = {}
        for node in G.nodes():
            influence_scores[node] = (
                0.4 * degree_cent[node] +
                0.3 * betweenness_cent[node] +
                0.3 * eigenvector_cent[node]
            )
        
        # Sort by influence
        sorted_influencers = sorted(influence_scores.items(), key=lambda x: x[1], reverse=True)
        top_influencers = sorted_influencers[:top_k]
        
        print("\nTop Influencers:")
        for rank, (node, score) in enumerate(top_influencers, 1):
            persona = G.nodes[node]['persona']
            degree = G.degree(node)
            print(f"  {rank}. Agent {node} ({persona})")
            print(f"     Influence Score: {score:.3f}, Degree: {degree}")
        
        # Store influence scores in graph
        nx.set_node_attributes(G, influence_scores, 'influence_score')
        
        influencer_ids = [node for node, score in top_influencers]
        
        return influencer_ids, influence_scores
    
    def visualize_network(self, G, influencer_ids):
        """Create network visualization"""
        print("\n" + "="*60)
        print("GENERATING NETWORK VISUALIZATION")
        print("="*60)
        
        fig, axes = plt.subplots(1, 2, figsize=(20, 9))
        
        # Color map for personas
        persona_colors = {
            'Minimalist': '#3498db',
            'Moderate User': '#2ecc71',
            'Active User': '#f39c12',
            'Heavy User': '#e74c3c',
            'Digital Addict': '#9b59b6'
        }
        
        node_colors = [persona_colors[G.nodes[node]['persona']] for node in G.nodes()]
        
        # Layout
        pos = nx.spring_layout(G, k=0.5, iterations=50, seed=42)
        
        # Left plot: Color by persona
        ax = axes[0]
        nx.draw_networkx_edges(G, pos, alpha=0.2, width=0.5, ax=ax)
        nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=100, 
                               alpha=0.8, ax=ax, linewidths=0.5, edgecolors='black')
        
        # Highlight influencers
        nx.draw_networkx_nodes(G, pos, nodelist=influencer_ids, 
                               node_color='gold', node_size=300, 
                               alpha=1.0, ax=ax, linewidths=2, edgecolors='black')
        
        ax.set_title('Social Network (Colored by Persona)', fontsize=14, fontweight='bold')
        ax.axis('off')
        
        # Legend for personas
        from matplotlib.patches import Patch
        legend_elements = [Patch(facecolor=color, label=persona, edgecolor='black') 
                          for persona, color in persona_colors.items()]
        legend_elements.append(Patch(facecolor='gold', label='Top Influencers', edgecolor='black'))
        ax.legend(handles=legend_elements, loc='upper left', fontsize=9)
        
        # Right plot: Node size by influence
        ax = axes[1]
        influence_scores = nx.get_node_attributes(G, 'influence_score')
        node_sizes = [influence_scores[node] * 1000 for node in G.nodes()]
        
        nx.draw_networkx_edges(G, pos, alpha=0.2, width=0.5, ax=ax)
        nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=node_sizes, 
                               alpha=0.8, ax=ax, linewidths=0.5, edgecolors='black')
        
        ax.set_title('Social Network (Node Size = Influence)', fontsize=14, fontweight='bold')
        ax.axis('off')
        
        plt.tight_layout()
        output_path = OUTPUT_DIR / "network_topology.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"✓ Saved network visualization to {output_path}")
        plt.close()
        
        # Degree distribution plot
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))
        
        degrees = [deg for node, deg in G.degree()]
        
        ax = axes[0]
        ax.hist(degrees, bins=range(min(degrees), max(degrees) + 2), 
                edgecolor='black', alpha=0.7, color='steelblue')
        ax.set_xlabel('Degree (Number of Friends)', fontsize=11)
        ax.set_ylabel('Frequency', fontsize=11)
        ax.set_title('Degree Distribution', fontsize=12, fontweight='bold')
        ax.axvline(np.mean(degrees), color='red', linestyle='--', 
                   linewidth=2, label=f'Mean: {np.mean(degrees):.2f}')
        ax.legend()
        ax.grid(alpha=0.3)
        
        # Degree by persona
        ax = axes[1]
        persona_degrees = {persona: [] for persona in persona_colors.keys()}
        for node in G.nodes():
            persona = G.nodes[node]['persona']
            persona_degrees[persona].append(G.degree(node))
        
        positions = range(1, len(persona_colors) + 1)
        bp = ax.boxplot(persona_degrees.values(), labels=persona_colors.keys(), 
                        patch_artist=True, showmeans=True)
        
        for patch, persona in zip(bp['boxes'], persona_colors.keys()):
            patch.set_facecolor(persona_colors[persona])
            patch.set_alpha(0.7)
        
        ax.set_xlabel('Persona', fontsize=11)
        ax.set_ylabel('Degree', fontsize=11)
        ax.set_title('Degree Distribution by Persona', fontsize=12, fontweight='bold')
        ax.grid(axis='y', alpha=0.3)
        plt.xticks(rotation=45, ha='right')
        
        plt.tight_layout()
        output_path = OUTPUT_DIR / "degree_distribution.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"✓ Saved degree distribution to {output_path}")
        plt.close()
    
    def save_network(self, G, metrics, influencer_ids):
        """Save network data"""
        # Save as GraphML (preserves attributes)
        graphml_path = OUTPUT_DIR / "social_network.graphml"
        nx.write_graphml(G, graphml_path)
        print(f"\n✓ Saved network to {graphml_path}")
        
        # Save as edge list
        edgelist_path = OUTPUT_DIR / "network_edges.csv"
        edges_df = pd.DataFrame(G.edges(), columns=['source', 'target'])
        edges_df.to_csv(edgelist_path, index=False)
        print(f"✓ Saved edge list to {edgelist_path}")
        
        # Save metrics
        metrics_path = OUTPUT_DIR / "network_metrics.json"
        # Convert numpy types to native Python types
        metrics_serializable = {k: float(v) if isinstance(v, (np.floating, np.integer)) 
                                else v for k, v in metrics.items()}
        with open(metrics_path, 'w') as f:
            json.dump(metrics_serializable, f, indent=2)
        print(f"✓ Saved metrics to {metrics_path}")
        
        # Save influencers
        influencers_path = OUTPUT_DIR / "influencers.json"
        influencer_data = {
            'top_k': len(influencer_ids),
            'influencer_ids': [int(i) for i in influencer_ids],
            'influencers': [
                {
                    'agent_id': int(node),
                    'persona': G.nodes[node]['persona'],
                    'degree': int(G.degree(node)),
                    'influence_score': float(G.nodes[node]['influence_score'])
                }
                for node in influencer_ids
            ]
        }
        with open(influencers_path, 'w') as f:
            json.dump(influencer_data, f, indent=2)
        print(f"✓ Saved influencer data to {influencers_path}")
        
        # Save specification document
        spec_path = OUTPUT_DIR / "network_topology_specification.txt"
        with open(spec_path, 'w') as f:
            f.write("="*80 + "\n")
            f.write("NETWORK TOPOLOGY SPECIFICATION\n")
            f.write("="*80 + "\n\n")
            
            f.write("NETWORK MODEL: Homophily-Based Random Graph\n")
            f.write("-"*80 + "\n")
            f.write("Description: Stochastic graph where connection probability depends on\n")
            f.write("             persona similarity (homophily principle)\n\n")
            
            f.write("PARAMETERS:\n")
            f.write(f"  • Same persona connection probability: {self.p_same_persona}\n")
            f.write(f"  • Different persona connection probability: {self.p_diff_persona}\n")
            f.write(f"  • Bridge connection probability: {self.p_bridge}\n")
            f.write(f"  • Degree constraints: [{self.min_degree}, {self.max_degree}]\n\n")
            
            f.write("NETWORK METRICS:\n")
            f.write("-"*80 + "\n")
            for key, value in metrics_serializable.items():
                if isinstance(value, float):
                    f.write(f"  {key}: {value:.4f}\n")
                else:
                    f.write(f"  {key}: {value}\n")
        
        print(f"✓ Saved topology specification to {spec_path}")

def main():
    """Execute network topology pipeline"""
    print("\n" + "="*60)
    print("PHASE 4: SOCIAL TOPOLOGY BLUEPRINT")
    print("="*60 + "\n")
    
    # Load agents
    agents_df = pd.read_csv(AGENT_COHORT_PATH)
    
    # Initialize builder
    builder = NetworkBuilder(agents_df, random_seed=42)
    
    # Build network
    G = builder.build_homophily_network()
    
    # Compute metrics
    metrics = builder.compute_network_metrics(G)
    
    # Identify influencers
    influencer_ids, influence_scores = builder.identify_influencers(G, top_k=5)
    
    # Visualize
    builder.visualize_network(G, influencer_ids)
    
    # Save outputs
    builder.save_network(G, metrics, influencer_ids)
    
    print("\n" + "="*60)
    print("PHASE 4 COMPLETE ✓")
    print("="*60)
    print(f"\nOutputs saved to: {OUTPUT_DIR}")
    print("  - social_network.graphml")
    print("  - network_edges.csv")
    print("  - network_metrics.json")
    print("  - influencers.json")
    print("  - network_topology.png")
    print("  - degree_distribution.png")
    print("  - network_topology_specification.txt")

if __name__ == "__main__":
    main()
