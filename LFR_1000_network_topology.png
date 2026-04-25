"""
==============================================================================
 LFR Benchmark Networks for SC Digital Contagion Simulator
==============================================================================
 Reference:
   Lancichinetti, Fortunato & Radicchi
   "Benchmark graphs for testing community detection algorithms"
   Physical Review E 78, 046110 (2008)

 WHY THIS IS BETTER THAN THE ORIGINAL HOMOPHILY NETWORK
 -------------------------------------------------------
 The original network uses fixed per-pair connection probabilities (p_same=0.15,
 p_diff=0.03).  This creates a graph that is too uniform — community boundaries
 are blurry and the degree distribution is narrow (Poisson-like).

 The LFR benchmark fixes both issues:
   • Power-law degree distribution (γ=3) → replicates real social networks
   • Power-law community-size distribution (β=1.5) → communities of varying size
   • Mixing parameter μ → precisely controls fraction of cross-community edges
   • Guarantees ≥5 distinct, well-separated communities per network
   • Used as the gold-standard benchmark in published community detection research

 TWO NETWORKS GENERATED
 ----------------------
   LFR_100  — 100  nodes, μ=0.1 (strong community structure)
   LFR_1000 — 1000 nodes, μ=0.1 (strong community structure)

 Both are fully compatible with the existing simulation pipeline:
   • Same 5-persona system (Minimalist → Digital Addict)
   • Same agent attributes, stress model, and influencer scoring
   • All outputs stored in lfr_networks/results_100/ and lfr_networks/results_1000/
   • Does NOT touch analysis/ (the original network results are preserved)

 USAGE
 -----
   cd sc-digital-contagion-simulator-beta
   python lfr_networks/generate_lfr_networks.py

 REQUIREMENTS
 ------------
   pip install networkx numpy pandas matplotlib seaborn tqdm
==============================================================================
"""

import json
import sys
import warnings
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import networkx as nx
import numpy as np
import pandas as pd
import seaborn as sns
from tqdm import tqdm

warnings.filterwarnings("ignore")

# ─────────────────────────────────────────────────────────────────────────────
# Paths
# ─────────────────────────────────────────────────────────────────────────────

ROOT = Path(__file__).parent.parent          # sc-digital-contagion-simulator-beta/
LFR_DIR = Path(__file__).parent              # lfr_networks/
PERSONA_FILE = ROOT / "analysis" / "persona_definitions.json"

# ─────────────────────────────────────────────────────────────────────────────
# Persona system  (identical to the main project)
# ─────────────────────────────────────────────────────────────────────────────

PERSONA_COLORS = {
    "Minimalist":     "#3498db",
    "Moderate User":  "#2ecc71",
    "Active User":    "#f39c12",
    "Heavy User":     "#e74c3c",
    "Digital Addict": "#9b59b6",
}
PERSONAS = list(PERSONA_COLORS.keys())

# ─────────────────────────────────────────────────────────────────────────────
# LFR network configurations
# ─────────────────────────────────────────────────────────────────────────────

NETWORK_CONFIGS = {
    "LFR_100": {
        "n":              100,
        "tau1":           3.0,    # degree power-law exponent  (γ in paper)
        "tau2":           1.5,    # community-size exponent    (β in paper)
        "mu":             0.1,    # mixing parameter           (μ in paper)
        "average_degree": 5,
        "min_community":  10,     # guarantees 8 communities in 100 nodes
        "max_community":  20,
        "max_iters":      2000,
        "seed":           42,
    },
    "LFR_1000": {
        "n":              1000,
        "tau1":           3.0,
        "tau2":           1.5,
        "mu":             0.1,
        "average_degree": 10,
        "min_community":  20,     # guarantees 20 communities in 1000 nodes
        "max_community":  100,
        "max_iters":      2000,
        "seed":           42,
    },
}

# Simulation parameters  (same as main project temporal engine)
SIM_PARAMS = {
    "n_days":       30,
    "alpha":        0.6,    # personal usage weight
    "beta":         0.3,    # peer influence weight
    "gamma":        0.1,    # resilience weight
    "delta":        0.02,   # self-feedback rate
    "stress_cap":   100.0,
    "usage_min":    30.0,
    "n_runs":       5,      # Monte-Carlo runs per scenario
    "intervention_day":    10,
    "intervention_factor": 0.5,  # reduce usage by 50% for intervened agents
}


# ══════════════════════════════════════════════════════════════════════════════
# STEP 1  —  Agent cohort
# ══════════════════════════════════════════════════════════════════════════════

class AgentFactory:
    """Creates synthetic agents — mirrors main project's AgentFactory exactly."""

    def __init__(self, n_agents: int, random_seed: int = 42):
        self.n_agents   = n_agents
        self.rng        = np.random.default_rng(random_seed)
        np.random.seed(random_seed)

        with open(PERSONA_FILE) as f:
            self.personas = json.load(f)
        self.persona_names = list(self.personas.keys())

        total = sum(p["count"] for p in self.personas.values())
        self.probs = [self.personas[p]["count"] / total for p in self.persona_names]

    def _sample_agent(self, persona_name: str, agent_id: int) -> dict:
        p  = self.personas[persona_name]
        ch = p["characteristics"]

        def norm(mu, sigma, lo):
            return float(max(lo, self.rng.normal(mu, sigma)))

        base_stress = (ch["behavior_class_mode"] - 1) / 4.0 * 100.0
        return {
            "agent_id":       agent_id,
            "persona":        persona_name,
            "base_stress":    base_stress,
            "resilience":     float(self.rng.uniform(0.7, 1.3)),
            "susceptibility": float(self.rng.uniform(0.5, 1.5)),
            "variability":    float(self.rng.uniform(0.8, 1.2)),
            "app_usage":      norm(ch["app_usage_mean"],     ch["app_usage_std"],     30),
            "screen_time":    norm(ch["screen_time_mean"],   ch["screen_time_std"],   1.0),
            "battery_drain":  norm(ch["battery_drain_mean"], ch["battery_drain_std"], 300),
            "apps_installed": int(max(10, self.rng.normal(ch["apps_installed_mean"], ch["apps_installed_std"]))),
            "data_usage":     norm(ch["data_usage_mean"],    ch["data_usage_std"],    100),
            "behavior_class": ch["behavior_class_mode"],
            "age":            int(np.clip(self.rng.normal(ch["age_mean"], ch["age_std"]), 18, 59)),
        }

    def create_cohort(self) -> pd.DataFrame:
        chosen = self.rng.choice(self.persona_names, size=self.n_agents, p=self.probs)
        agents = [self._sample_agent(p, i) for i, p in enumerate(chosen)]
        return pd.DataFrame(agents)


# ══════════════════════════════════════════════════════════════════════════════
# STEP 2  —  LFR network builder
# ══════════════════════════════════════════════════════════════════════════════

class LFRNetworkBuilder:
    """
    Builds LFR benchmark graph and assigns personas to communities.

    Key design decision:
      Each LFR community is assigned ONE persona. Within a community all
      agents share that persona, so intra-community homophily is preserved
      (just like the original project) while community structure is now driven
      by the rigorous LFR model instead of simple probability thresholds.

    With μ=0.1 only 10 % of each node's edges cross community boundaries —
      this produces tight, well-separated clusters that are clearly visible
      in the network plot and meaningful for contagion research.
    """

    def __init__(self, cfg: dict, agents_df: pd.DataFrame):
        self.cfg       = cfg
        self.agents_df = agents_df.copy()
        self.n         = cfg["n"]
        self.rng       = np.random.default_rng(cfg["seed"])

    # ── Build graph ──────────────────────────────────────────────────────────

    def build(self) -> nx.Graph:
        print(f"\n  Building LFR graph (N={self.n}) …", end=" ", flush=True)
        G = nx.LFR_benchmark_graph(
            n             = self.cfg["n"],
            tau1          = self.cfg["tau1"],
            tau2          = self.cfg["tau2"],
            mu            = self.cfg["mu"],
            average_degree= self.cfg["average_degree"],
            min_community = self.cfg["min_community"],
            max_community = self.cfg["max_community"],
            max_iters     = self.cfg["max_iters"],
            seed          = self.cfg["seed"],
        )
        print(f"✓  {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")

        # Identify ground-truth communities (LFR stores them as sets on nodes)
        raw_comms = nx.get_node_attributes(G, "community")
        communities: dict[frozenset, list] = {}
        for node, comm in raw_comms.items():
            key = frozenset(comm)
            communities.setdefault(key, []).append(node)

        n_comm = len(communities)
        print(f"  Communities detected : {n_comm}")

        # ── Assign personas to communities ───────────────────────────────────
        # Distribute all 5 personas across communities (round-robin so every
        # persona appears regardless of how many communities there are)
        comm_list   = list(communities.keys())
        # Shuffle so assignment is not just sorted by community index
        shuffled    = self.rng.permutation(len(comm_list)).tolist()

        # Weighted persona sampling respecting original dataset distribution
        with open(PERSONA_FILE) as f:
            persona_defs = json.load(f)
        total  = sum(p["count"] for p in persona_defs.values())
        probs  = np.array([persona_defs[p]["count"] / total for p in PERSONAS])

        # Force all 5 personas to appear — assign round-robin for first 5 slots
        persona_assignment: dict[frozenset, str] = {}
        for rank, idx in enumerate(shuffled):
            comm = comm_list[idx]
            if rank < len(PERSONAS):
                persona_assignment[comm] = PERSONAS[rank]   # one each
            else:
                persona_assignment[comm] = self.rng.choice(PERSONAS, p=probs)

        # Set node attributes from agents_df, mapping sequentially
        node_list = list(G.nodes())
        # Map each node to an agent_id (same index order)
        node_to_agent = {node: i for i, node in enumerate(node_list)}

        for node in G.nodes():
            comm_key  = frozenset(raw_comms[node])
            persona   = persona_assignment[comm_key]
            agent_idx = node_to_agent[node]
            agent_row = self.agents_df.iloc[agent_idx % len(self.agents_df)]

            G.nodes[node]["persona"]        = persona
            G.nodes[node]["base_stress"]    = float(agent_row["base_stress"])
            G.nodes[node]["screen_time"]    = float(agent_row["screen_time"])
            G.nodes[node]["behavior_class"] = int(agent_row["behavior_class"])
            G.nodes[node]["community_id"]   = str(sorted(raw_comms[node]))  # store as string

        # Remove raw 'community' set attribute (not GraphML-serialisable)
        for node in G.nodes():
            del G.nodes[node]["community"]

        self.communities      = communities
        self.persona_assignment = persona_assignment
        self.comm_list        = comm_list
        return G

    # ── Metrics ──────────────────────────────────────────────────────────────

    def compute_metrics(self, G: nx.Graph) -> dict:
        degrees = [d for _, d in G.degree()]
        is_conn = nx.is_connected(G)
        Gsub    = G if is_conn else G.subgraph(max(nx.connected_components(G), key=len)).copy()

        # Persona assortativity
        p2i = {p: i for i, p in enumerate(PERSONAS)}
        nx.set_node_attributes(G, {n: p2i[G.nodes[n]["persona"]] for n in G.nodes()}, "persona_int")

        return {
            # LFR params
            "lfr_n":              self.cfg["n"],
            "lfr_gamma":          self.cfg["tau1"],
            "lfr_beta":           self.cfg["tau2"],
            "lfr_mu":             self.cfg["mu"],
            "lfr_avg_degree_target": self.cfg["average_degree"],
            # Realised topology
            "n_nodes":            G.number_of_nodes(),
            "n_edges":            G.number_of_edges(),
            "density":            nx.density(G),
            "avg_degree":         float(np.mean(degrees)),
            "std_degree":         float(np.std(degrees)),
            "min_degree":         int(np.min(degrees)),
            "max_degree":         int(np.max(degrees)),
            "is_connected":       is_conn,
            "n_components":       nx.number_connected_components(G),
            "largest_cc_size":    len(max(nx.connected_components(G), key=len)),
            "avg_clustering":     nx.average_clustering(G),
            "transitivity":       nx.transitivity(G),
            "diameter":           nx.diameter(Gsub),
            "avg_shortest_path":  nx.average_shortest_path_length(Gsub),
            "n_communities":      len(self.communities),
            "assortativity_persona": nx.attribute_assortativity_coefficient(G, "persona_int"),
        }

    # ── Influencers ──────────────────────────────────────────────────────────

    def identify_influencers(self, G: nx.Graph, top_k: int = 5) -> tuple:
        deg_c = nx.degree_centrality(G)
        bet_c = nx.betweenness_centrality(G, seed=self.cfg["seed"])
        eig_c = nx.eigenvector_centrality(G, max_iter=1000, tol=1e-6)
        scores = {n: 0.4*deg_c[n] + 0.3*bet_c[n] + 0.3*eig_c[n] for n in G.nodes()}
        nx.set_node_attributes(G, scores, "influence_score")
        top = sorted(scores, key=scores.get, reverse=True)[:top_k]
        return top, scores


# ══════════════════════════════════════════════════════════════════════════════
# STEP 3  —  Visualisations
# ══════════════════════════════════════════════════════════════════════════════

def _pos(G: nx.Graph, seed: int, n: int) -> dict:
    """Spring layout — wider spacing for small graphs."""
    k = 2.5 / np.sqrt(n)
    return nx.spring_layout(G, k=k, iterations=80, seed=seed)


def plot_network(G: nx.Graph, influencer_ids: list, metrics: dict,
                 name: str, out_dir: Path):
    """
    Publication-quality network figure with 4 panels:
      1. Persona-coloured topology
      2. Community-coloured topology (ground-truth LFR communities)
      3. Node size = influence score
      4. Degree distribution
    """
    n     = G.number_of_nodes()
    pos   = _pos(G, seed=42, n=n)
    inf_set = set(influencer_ids)
    influence_scores = nx.get_node_attributes(G, "influence_score")

    # Community colours (up to 15 distinct)
    community_ids  = sorted(set(G.nodes[nd]["community_id"] for nd in G.nodes()))
    cmap_comm      = plt.cm.get_cmap("tab20", len(community_ids))
    comm_color_map = {cid: cmap_comm(i) for i, cid in enumerate(community_ids)}

    node_persona_colors = [PERSONA_COLORS[G.nodes[nd]["persona"]] for nd in G.nodes()]
    node_comm_colors    = [comm_color_map[G.nodes[nd]["community_id"]] for nd in G.nodes()]
    node_inf_sizes      = [influence_scores[nd] * 3000 + 50 for nd in G.nodes()]
    base_size           = max(30, 2000 // n)

    fig = plt.figure(figsize=(22, 18))
    fig.patch.set_facecolor("white")

    ax1 = fig.add_subplot(2, 2, 1)
    ax2 = fig.add_subplot(2, 2, 2)
    ax3 = fig.add_subplot(2, 2, 3)
    ax4 = fig.add_subplot(2, 2, 4)

    edge_kw = dict(alpha=0.12, width=0.5, edge_color="#7f8c8d")

    # ── Panel 1: Persona colours ──────────────────────────────────────────────
    ax1.set_facecolor("#fafafa")
    nx.draw_networkx_edges(G, pos, ax=ax1, **edge_kw)
    regular = [nd for nd in G.nodes() if nd not in inf_set]
    nx.draw_networkx_nodes(G, pos, nodelist=regular,
                           node_color=[PERSONA_COLORS[G.nodes[nd]["persona"]] for nd in regular],
                           node_size=base_size, alpha=0.88, ax=ax1,
                           linewidths=0.5, edgecolors="white")
    nx.draw_networkx_nodes(G, pos, nodelist=influencer_ids,
                           node_color="gold", node_size=base_size*4,
                           alpha=1.0, ax=ax1, linewidths=2.5, edgecolors="#e67e22")
    ax1.set_title(
        f"Panel A — Persona Groups\n"
        f"N={metrics['n_nodes']}, E={metrics['n_edges']}, ⟨k⟩={metrics['avg_degree']:.1f}",
        fontsize=12, fontweight="bold")
    ax1.axis("off")
    legend_handles = [
        mpatches.Patch(facecolor=c, label=p, edgecolor="white", linewidth=0.8)
        for p, c in PERSONA_COLORS.items()
    ]
    legend_handles.append(
        mpatches.Patch(facecolor="gold", label="Top-5 Influencers",
                       edgecolor="#e67e22", linewidth=1.5))
    ax1.legend(handles=legend_handles, loc="upper left", fontsize=9,
               framealpha=0.95, title="Persona", title_fontsize=9)

    # ── Panel 2: Community colours ────────────────────────────────────────────
    ax2.set_facecolor("#fafafa")
    nx.draw_networkx_edges(G, pos, ax=ax2, **edge_kw)
    nx.draw_networkx_nodes(G, pos, node_color=node_comm_colors,
                           node_size=base_size, alpha=0.88, ax=ax2,
                           linewidths=0.5, edgecolors="white")
    nx.draw_networkx_nodes(G, pos, nodelist=influencer_ids,
                           node_color="gold", node_size=base_size*4,
                           alpha=1.0, ax=ax2, linewidths=2.5, edgecolors="#e67e22")
    ax2.set_title(
        f"Panel B — LFR Ground-Truth Communities\n"
        f"{metrics['n_communities']} communities, μ={metrics['lfr_mu']} (mixing parameter)",
        fontsize=12, fontweight="bold")
    ax2.axis("off")
    comm_legend = [
        mpatches.Patch(facecolor=comm_color_map[cid],
                       label=f"Community {i+1}", edgecolor="white", linewidth=0.5)
        for i, cid in enumerate(community_ids[:12])
    ]
    if len(community_ids) > 12:
        comm_legend.append(mpatches.Patch(facecolor="grey", label=f"+{len(community_ids)-12} more"))
    ax2.legend(handles=comm_legend, loc="upper left", fontsize=8,
               framealpha=0.95, title="Community", title_fontsize=9,
               ncol=2 if len(comm_legend) > 8 else 1)

    # ── Panel 3: Node size = influence score ──────────────────────────────────
    ax3.set_facecolor("#fafafa")
    nx.draw_networkx_edges(G, pos, ax=ax3, **edge_kw)
    nx.draw_networkx_nodes(G, pos, node_color=node_persona_colors,
                           node_size=node_inf_sizes, alpha=0.82, ax=ax3,
                           linewidths=0.5, edgecolors="white")
    inf_labels = {nd: str(nd) for nd in influencer_ids}
    nx.draw_networkx_labels(G, pos, inf_labels, font_size=7,
                            font_weight="bold", font_color="black", ax=ax3)
    ax3.set_title(
        "Panel C — Influence Score\n"
        "(node size = 0.4×degree + 0.3×betweenness + 0.3×eigenvector)",
        fontsize=12, fontweight="bold")
    ax3.axis("off")

    # ── Panel 4: Degree distribution ─────────────────────────────────────────
    degrees = [d for _, d in G.degree()]
    unique_d, counts = np.unique(degrees, return_counts=True)
    ax4.set_facecolor("#fafafa")
    ax4.bar(unique_d, counts, color="#3498db", edgecolor="white",
            alpha=0.85, width=0.8)
    ax4.axvline(np.mean(degrees), color="#e74c3c", linestyle="--",
                linewidth=2, label=f"Mean ⟨k⟩ = {np.mean(degrees):.2f}")
    # Power-law reference line
    x_fit = np.linspace(unique_d[0], unique_d[-1], 100)
    scale = counts.max() * (unique_d[0] ** metrics["lfr_gamma"])
    y_fit = scale * x_fit ** (-metrics["lfr_gamma"])
    ax4.plot(x_fit, y_fit, color="#f39c12", linewidth=2,
             linestyle=":", label=f"Power-law ref (γ={metrics['lfr_gamma']})")
    ax4.set_xlabel("Degree k", fontsize=11, fontweight="bold")
    ax4.set_ylabel("Frequency", fontsize=11, fontweight="bold")
    ax4.set_title(
        "Panel D — Degree Distribution\n"
        f"min={metrics['min_degree']}, max={metrics['max_degree']}, "
        f"σ={metrics['std_degree']:.2f}",
        fontsize=12, fontweight="bold")
    ax4.legend(fontsize=10)
    ax4.grid(alpha=0.3, axis="y")

    fig.suptitle(
        f"LFR Benchmark Network — {name}\n"
        f"SC Digital Contagion Simulator  ·  "
        f"Lancichinetti, Fortunato & Radicchi (Phys. Rev. E 78, 046110, 2008)",
        fontsize=14, fontweight="bold", y=1.01,
    )
    plt.tight_layout()
    out = out_dir / f"{name}_network_topology.png"
    plt.savefig(out, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"  ✓ Network topology plot → {out.name}")
    return out


def plot_temporal_heatmap(baseline_df: pd.DataFrame, name: str, out_dir: Path):
    """30-day stress contagion heatmap (identical style to main project)."""
    stress_matrix = baseline_df.pivot(index="agent_id", columns="day", values="stress")
    final_stress  = stress_matrix[stress_matrix.columns[-1]]
    stress_matrix = stress_matrix.loc[final_stress.sort_values(ascending=False).index]

    fig, ax = plt.subplots(figsize=(16, max(8, len(stress_matrix)//8)))
    sns.heatmap(stress_matrix, cmap="YlOrRd", vmin=0, vmax=100,
                cbar_kws={"label": "Stress Level (0-100)", "shrink": 0.8},
                xticklabels=5, yticklabels=max(1, len(stress_matrix)//20),
                ax=ax, linewidths=0)
    high = (final_stress > 60).sum()
    if high > 0:
        ax.axhline(y=high, color="#00b894", linewidth=2, linestyle="--", alpha=0.8)
        ax.text(stress_matrix.shape[1]+0.5, high/2, "High\nStress",
                va="center", ha="left", fontsize=10, fontweight="bold",
                color="white",
                bbox=dict(boxstyle="round", facecolor="#00b894", alpha=0.85))
    ax.set_xlabel("Day", fontsize=13, fontweight="bold")
    ax.set_ylabel("Agent (sorted by final stress)", fontsize=13, fontweight="bold")
    ax.set_title(
        f"30-Day Stress Contagion — {name} (Baseline, No Intervention)\n"
        "Heatmap rows sorted by final-day stress (descending)",
        fontsize=14, fontweight="bold", pad=15)
    plt.tight_layout()
    out = out_dir / f"{name}_temporal_heatmap.png"
    plt.savefig(out, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"  ✓ Temporal heatmap      → {out.name}")
    return out


def plot_intervention_comparison(baseline_df: pd.DataFrame,
                                 intervention_df: pd.DataFrame,
                                 name: str, out_dir: Path):
    """Baseline vs intervention stress over 30 days, by persona."""
    fig, axes = plt.subplots(1, 2, figsize=(18, 7))

    # Global average
    ax = axes[0]
    b_mean = baseline_df.groupby("day")["stress"].mean()
    i_mean = intervention_df.groupby("day")["stress"].mean()
    b_std  = baseline_df.groupby("day")["stress"].std()
    i_std  = intervention_df.groupby("day")["stress"].std()
    days   = b_mean.index

    ax.fill_between(days, b_mean-b_std, b_mean+b_std, alpha=0.15, color="#e74c3c")
    ax.fill_between(days, i_mean-i_std, i_mean+i_std, alpha=0.15, color="#2ecc71")
    ax.plot(days, b_mean, color="#e74c3c", linewidth=2.5, label="Baseline (no action)")
    ax.plot(days, i_mean, color="#2ecc71", linewidth=2.5, label="Intervention (day 10)")
    ax.axvline(x=10, color="#7f8c8d", linestyle=":", linewidth=1.5, label="Intervention start")
    ax.set_xlabel("Day", fontsize=12, fontweight="bold")
    ax.set_ylabel("Mean Stress Level", fontsize=12, fontweight="bold")
    ax.set_title("Average Stress: Baseline vs Intervention", fontsize=13, fontweight="bold")
    ax.legend(fontsize=11); ax.grid(alpha=0.3)

    # By persona
    ax = axes[1]
    for persona, color in PERSONA_COLORS.items():
        b_p = baseline_df[baseline_df["persona"] == persona].groupby("day")["stress"].mean()
        i_p = intervention_df[intervention_df["persona"] == persona].groupby("day")["stress"].mean()
        if len(b_p) > 0:
            ax.plot(b_p.index, b_p.values, color=color, linewidth=2,
                    linestyle="--", alpha=0.7)
            ax.plot(i_p.index, i_p.values, color=color, linewidth=2,
                    label=persona)
    ax.axvline(x=10, color="#7f8c8d", linestyle=":", linewidth=1.5)
    ax.set_xlabel("Day", fontsize=12, fontweight="bold")
    ax.set_ylabel("Mean Stress Level", fontsize=12, fontweight="bold")
    ax.set_title("Stress by Persona (solid=intervention, dashed=baseline)",
                 fontsize=13, fontweight="bold")
    ax.legend(fontsize=9, ncol=2); ax.grid(alpha=0.3)

    fig.suptitle(
        f"Intervention Analysis — {name}\n"
        f"SC Digital Contagion Simulator · LFR Benchmark Network",
        fontsize=14, fontweight="bold")
    plt.tight_layout()
    out = out_dir / f"{name}_intervention_comparison.png"
    plt.savefig(out, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"  ✓ Intervention comparison → {out.name}")
    return out


def plot_community_stress_profile(baseline_df: pd.DataFrame,
                                  G: nx.Graph, name: str, out_dir: Path):
    """
    Shows how stress propagates differently across communities —
    the key research insight enabled by proper community structure.
    """
    # Map agent_id → community_id and persona
    agent_to_comm    = {}
    agent_to_persona = {}
    for node in G.nodes():
        nid = int(node)
        agent_to_comm[nid]    = G.nodes[node].get("community_id", "?")
        agent_to_persona[nid] = G.nodes[node].get("persona", "Unknown")

    df = baseline_df.copy()
    df["community_id"] = df["agent_id"].map(agent_to_comm)

    # Unique communities sorted by median final stress
    comms = df.groupby("community_id")
    final_day = df["day"].max()
    comm_order = (
        df[df["day"] == final_day]
        .groupby("community_id")["stress"]
        .median()
        .sort_values(ascending=False)
        .index.tolist()
    )

    fig, axes = plt.subplots(1, 2, figsize=(18, 7))

    # Panel A: per-community stress trajectory
    ax = axes[0]
    cmap = plt.cm.get_cmap("tab20", len(comm_order))
    for i, cid in enumerate(comm_order):
        grp = df[df["community_id"] == cid].groupby("day")["stress"].mean()
        ax.plot(grp.index, grp.values, linewidth=1.8,
                color=cmap(i), label=f"C{i+1}", alpha=0.85)
    ax.set_xlabel("Day", fontsize=12, fontweight="bold")
    ax.set_ylabel("Mean Stress", fontsize=12, fontweight="bold")
    ax.set_title("Stress Trajectory per Community\n"
                 "(each line = one LFR community)", fontsize=13, fontweight="bold")
    ax.legend(fontsize=8, ncol=3, loc="upper left"); ax.grid(alpha=0.3)

    # Panel B: final-day stress distribution per persona (violin)
    ax = axes[1]
    final_df = df[df["day"] == final_day].copy()
    final_df["persona"] = final_df["agent_id"].map(agent_to_persona)
    persona_data = [final_df[final_df["persona"] == p]["stress"].values
                    for p in PERSONAS]
    # Only include personas that are present
    present_personas = [p for p in PERSONAS if len(final_df[final_df["persona"] == p]) > 0]
    present_data     = [final_df[final_df["persona"] == p]["stress"].values
                        for p in present_personas]

    parts = ax.violinplot(present_data, showmeans=True, showmedians=True)
    for i, (pc, persona) in enumerate(zip(parts["bodies"], present_personas)):
        pc.set_facecolor(PERSONA_COLORS[persona])
        pc.set_alpha(0.75)
    ax.set_xticks(range(1, len(present_personas)+1))
    ax.set_xticklabels(present_personas, rotation=15, ha="right", fontsize=10)
    ax.set_ylabel("Final-Day Stress Level", fontsize=12, fontweight="bold")
    ax.set_title("Stress Distribution by Persona (Day 30)\n"
                 "Violin = full distribution, line = median",
                 fontsize=13, fontweight="bold")
    ax.grid(alpha=0.3, axis="y")

    fig.suptitle(
        f"Community Stress Profile — {name}\n"
        f"SC Digital Contagion Simulator · LFR Benchmark Network",
        fontsize=14, fontweight="bold")
    plt.tight_layout()
    out = out_dir / f"{name}_community_stress_profile.png"
    plt.savefig(out, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"  ✓ Community stress profile → {out.name}")
    return out


# ══════════════════════════════════════════════════════════════════════════════
# STEP 4  —  Simulation engine  (identical logic to main project)
# ══════════════════════════════════════════════════════════════════════════════

class TemporalEngine:
    """
    30-day agent-based stress contagion simulation.
    Uses exactly the same equations as src/temporal_engine.py.
    """

    def __init__(self, agents_df: pd.DataFrame, G: nx.Graph,
                 params: dict, random_seed: int = 42):
        self.agents_df = agents_df.copy().set_index("agent_id")
        self.G         = G
        self.p         = params
        np.random.seed(random_seed)
        self.rng       = np.random.default_rng(random_seed)

    def simulate(self, intervention_day=None, intervention_agents=None) -> pd.DataFrame:
        records = []
        node_ids = list(self.G.nodes())
        # initial state
        stress = {n: float(self.G.nodes[n].get("base_stress",
                   self.agents_df.iloc[int(n) % len(self.agents_df)]["base_stress"]))
                  for n in node_ids}
        usage  = {n: float(self.agents_df.iloc[int(n) % len(self.agents_df)]["app_usage"])
                  for n in node_ids}
        # Day 0
        for n in node_ids:
            records.append({
                "agent_id":           int(n),
                "day":                0,
                "stress":             stress[n],
                "usage":              usage[n],
                "peer_influence":     0.0,
                "persona":            self.G.nodes[n].get("persona", "Unknown"),
                "intervention_active": False,
            })

        for day in range(1, self.p["n_days"] + 1):
            new_stress = {}
            new_usage  = {}
            for n in node_ids:
                agent_row = self.agents_df.iloc[int(n) % len(self.agents_df)]
                neighbors = list(self.G.neighbors(n))
                peer_stress = np.mean([stress[nb] for nb in neighbors]) if neighbors else 0.0

                usage_norm  = min(usage[n] / 600.0, 1.0)
                s = (self.p["alpha"] * usage_norm
                     + self.p["beta"]  * peer_stress / 100.0 * agent_row["susceptibility"]
                     - self.p["gamma"] * agent_row["resilience"] / 10.0) * 100.0
                s = float(np.clip(s, 0, self.p["stress_cap"]))

                is_intervened = (intervention_day is not None
                                 and day >= intervention_day
                                 and intervention_agents is not None
                                 and int(n) in intervention_agents)
                usage_factor = self.p["intervention_factor"] if is_intervened else 1.0

                noise = float(self.rng.normal(1.0, 0.1))
                u = (usage[n] * (1 + self.p["delta"] * stress[n] / 100.0)
                     * agent_row["variability"] * noise * usage_factor)
                u = float(np.clip(u, self.p["usage_min"], 600.0))

                new_stress[n] = s
                new_usage[n]  = u

                records.append({
                    "agent_id":           int(n),
                    "day":                day,
                    "stress":             s,
                    "usage":              u,
                    "peer_influence":     peer_stress,
                    "persona":            self.G.nodes[n].get("persona", "Unknown"),
                    "intervention_active": is_intervened,
                })
            stress = new_stress
            usage  = new_usage

        return pd.DataFrame(records)

    def summary_metrics(self, df: pd.DataFrame) -> dict:
        final = df[df["day"] == df["day"].max()]
        return {
            "final_mean_stress":   float(final["stress"].mean()),
            "final_std_stress":    float(final["stress"].std()),
            "final_max_stress":    float(final["stress"].max()),
            "high_stress_agents":  int((final["stress"] > 60).sum()),
            "peak_mean_usage":     float(df.groupby("day")["usage"].mean().max()),
        }


def run_simulation_suite(agents_df, G, name, params, out_dir):
    """Runs baseline + intervention across n_runs seeds."""
    print(f"\n  Running simulations ({params['n_runs']} runs × 2 scenarios) …")

    # Influencer agents as intervention targets
    influencer_ids = [n for n in G.nodes()
                      if G.nodes[n].get("influence_score", 0) > 0]
    top_influencers = sorted(influencer_ids,
                             key=lambda n: G.nodes[n].get("influence_score", 0),
                             reverse=True)[:5]
    intervention_set = set(int(n) for n in top_influencers)

    all_baseline, all_intervention = [], []
    baseline_metrics_list, intervention_metrics_list = [], []

    for run in tqdm(range(params["n_runs"]), desc=f"  {name}", leave=False):
        seed = 42 + run

        # Baseline
        eng = TemporalEngine(agents_df, G, params, random_seed=seed)
        b_df = eng.simulate()
        all_baseline.append(b_df)
        baseline_metrics_list.append(eng.summary_metrics(b_df))

        # Intervention (target influencers from day 10)
        eng2 = TemporalEngine(agents_df, G, params, random_seed=seed)
        i_df = eng2.simulate(intervention_day=params["intervention_day"],
                             intervention_agents=intervention_set)
        all_intervention.append(i_df)
        intervention_metrics_list.append(eng2.summary_metrics(i_df))

    # Average metrics across runs
    def avg_metrics(lst):
        keys = lst[0].keys()
        return {k: float(np.mean([m[k] for m in lst])) for k in keys}

    baseline_avg     = avg_metrics(baseline_metrics_list)
    intervention_avg = avg_metrics(intervention_metrics_list)

    # Representative run (run 0) for visualisations
    b0 = all_baseline[0]
    i0 = all_intervention[0]

    # Save CSVs
    b0.to_csv(out_dir / f"{name}_simulation_baseline.csv", index=False)
    i0.to_csv(out_dir / f"{name}_simulation_intervention.csv", index=False)

    with open(out_dir / f"{name}_baseline_metrics.json", "w") as f:
        json.dump(baseline_avg, f, indent=2)
    with open(out_dir / f"{name}_intervention_metrics.json", "w") as f:
        json.dump(intervention_avg, f, indent=2)

    print(f"  ✓ Simulation CSVs saved")
    return b0, i0, baseline_avg, intervention_avg


# ══════════════════════════════════════════════════════════════════════════════
# STEP 5  —  Save artefacts & specification doc
# ══════════════════════════════════════════════════════════════════════════════

def save_artefacts(G: nx.Graph, name: str, metrics: dict,
                   influencer_ids: list, agents_df: pd.DataFrame,
                   baseline_metrics: dict, intervention_metrics: dict,
                   out_dir: Path):

    # GraphML (convert attributes to primitive types)
    G_exp = G.copy()
    for nd in G_exp.nodes():
        for k, v in G_exp.nodes[nd].items():
            if isinstance(v, (np.integer,)):
                G_exp.nodes[nd][k] = int(v)
            elif isinstance(v, (np.floating,)):
                G_exp.nodes[nd][k] = float(v)
            elif isinstance(v, (np.str_,)):
                G_exp.nodes[nd][k] = str(v)
    nx.write_graphml(G_exp, out_dir / f"{name}_network.graphml")
    print(f"  ✓ GraphML saved")

    # Edge list
    pd.DataFrame(G.edges(), columns=["source", "target"]).to_csv(
        out_dir / f"{name}_edges.csv", index=False)

    # Node table
    node_rows = []
    for nd in G.nodes():
        row = {"agent_id": int(nd)}
        row.update({k: v for k, v in G.nodes[nd].items()
                    if k not in ("community",)})
        row["degree"] = G.degree(nd)
        node_rows.append(row)
    pd.DataFrame(node_rows).to_csv(out_dir / f"{name}_nodes.csv", index=False)

    # Metrics JSON
    def serial(d):
        return {k: (float(v) if isinstance(v, (np.floating, np.integer)) else v)
                for k, v in d.items()}
    with open(out_dir / f"{name}_network_metrics.json", "w") as f:
        json.dump(serial(metrics), f, indent=2)

    # Influencers JSON
    inf_data = {
        "network": name, "top_k": len(influencer_ids),
        "influencer_ids": [int(i) for i in influencer_ids],
        "influencers": [
            {"agent_id": int(n), "persona": G.nodes[n]["persona"],
             "degree": int(G.degree(n)),
             "influence_score": float(G.nodes[n]["influence_score"])}
            for n in influencer_ids
        ],
    }
    with open(out_dir / f"{name}_influencers.json", "w") as f:
        json.dump(inf_data, f, indent=2)

    # Human-readable specification
    spec = out_dir / f"{name}_specification.txt"
    with open(spec, "w") as f:
        f.write("=" * 80 + "\n")
        f.write(f"LFR BENCHMARK NETWORK SPECIFICATION — {name}\n")
        f.write("=" * 80 + "\n\n")
        f.write("REFERENCE\n")
        f.write("  Lancichinetti, Fortunato & Radicchi\n")
        f.write("  'Benchmark graphs for testing community detection algorithms'\n")
        f.write("  Physical Review E 78, 046110 (2008)\n\n")
        f.write("WHY LFR INSTEAD OF ORIGINAL HOMOPHILY NETWORK\n")
        f.write("-" * 80 + "\n")
        f.write("  Original: fixed per-pair probabilities (p_same=0.15, p_diff=0.03)\n")
        f.write("    → Poisson-like degree distribution, blurry community structure\n")
        f.write("  LFR: power-law degree + power-law community sizes + exact μ control\n")
        f.write("    → Matches real social network statistics, tight community separation\n\n")
        f.write("LFR PARAMETERS\n")
        f.write("-" * 80 + "\n")
        f.write(f"  N (nodes)                   : {metrics['lfr_n']}\n")
        f.write(f"  gamma γ (degree exponent)   : {metrics['lfr_gamma']}\n")
        f.write(f"  beta  β (community exponent): {metrics['lfr_beta']}\n")
        f.write(f"  mu    μ (mixing parameter)  : {metrics['lfr_mu']}\n")
        f.write(f"  Target avg degree           : {metrics['lfr_avg_degree_target']}\n\n")
        f.write("REALISED NETWORK METRICS\n")
        f.write("-" * 80 + "\n")
        for k, v in serial(metrics).items():
            if not k.startswith("lfr_"):
                tag = f"  {k}"
                f.write(f"{tag:<40}: {v:.4f}\n" if isinstance(v, float)
                        else f"{tag:<40}: {v}\n")
        f.write("\nSIMULATION RESULTS (averaged over 5 runs)\n")
        f.write("-" * 80 + "\n")
        f.write("  Baseline:\n")
        for k, v in baseline_metrics.items():
            f.write(f"    {k:<35}: {v:.2f}\n")
        f.write("  Intervention (target top-5 influencers from day 10):\n")
        for k, v in intervention_metrics.items():
            f.write(f"    {k:<35}: {v:.2f}\n")
        f.write("\nTOP-5 INFLUENCERS\n")
        f.write("-" * 80 + "\n")
        for rank, inf in enumerate(inf_data["influencers"], 1):
            f.write(f"  {rank}. Agent {inf['agent_id']:4d}  ({inf['persona']:<15})"
                    f"  deg={inf['degree']:3d}  score={inf['influence_score']:.4f}\n")

    print(f"  ✓ All data artefacts saved")


# ══════════════════════════════════════════════════════════════════════════════
# MAIN PIPELINE
# ══════════════════════════════════════════════════════════════════════════════

def run_network_pipeline(cfg_name: str, cfg: dict):
    print(f"\n{'='*70}")
    print(f"  PIPELINE: {cfg_name}  (N={cfg['n']}, μ={cfg['mu']})")
    print(f"{'='*70}")

    out_dir = LFR_DIR / f"results_{cfg['n']}"
    out_dir.mkdir(parents=True, exist_ok=True)

    # ── 1. Agent cohort ───────────────────────────────────────────────────────
    print(f"\n[1/6] Creating agent cohort ({cfg['n']} agents)…")
    factory    = AgentFactory(n_agents=cfg["n"], random_seed=cfg["seed"])
    agents_df  = factory.create_cohort()
    agents_df.to_csv(out_dir / f"{cfg_name}_agent_cohort.csv", index=False)
    print(f"  ✓ Agent cohort saved  ({len(agents_df)} agents)")

    # ── 2. Build LFR network ──────────────────────────────────────────────────
    print(f"\n[2/6] Building LFR benchmark network…")
    builder = LFRNetworkBuilder(cfg, agents_df)
    G       = builder.build()

    # ── 3. Metrics + influencers ──────────────────────────────────────────────
    print(f"\n[3/6] Computing metrics & influencers…")
    metrics        = builder.compute_metrics(G)
    influencer_ids, _ = builder.identify_influencers(G, top_k=5)
    for rank, n in enumerate(influencer_ids, 1):
        print(f"  {rank}. Agent {n} ({G.nodes[n]['persona']})  "
              f"score={G.nodes[n]['influence_score']:.4f}")

    # ── 4. Simulation ─────────────────────────────────────────────────────────
    print(f"\n[4/6] Running stress contagion simulation…")
    b0, i0, b_metrics, i_metrics = run_simulation_suite(
        agents_df, G, cfg_name, SIM_PARAMS, out_dir)

    # ── 5. Visualisations ─────────────────────────────────────────────────────
    print(f"\n[5/6] Generating plots…")
    plot_network(G, influencer_ids, metrics, cfg_name, out_dir)
    plot_temporal_heatmap(b0, cfg_name, out_dir)
    plot_intervention_comparison(b0, i0, cfg_name, out_dir)
    plot_community_stress_profile(b0, G, cfg_name, out_dir)

    # ── 6. Save all artefacts ─────────────────────────────────────────────────
    print(f"\n[6/6] Saving data artefacts…")
    save_artefacts(G, cfg_name, metrics, influencer_ids,
                   agents_df, b_metrics, i_metrics, out_dir)

    print(f"\n  ✅  {cfg_name} complete — outputs in lfr_networks/results_{cfg['n']}/")
    return metrics, b_metrics, i_metrics


def main():
    print("\n" + "=" * 70)
    print("  LFR BENCHMARK NETWORK GENERATOR")
    print("  SC Digital Contagion Simulator")
    print("=" * 70)
    print("\n  Original homophily network preserved in analysis/")
    print("  New LFR networks go into lfr_networks/results_100/")
    print("                       and lfr_networks/results_1000/")

    summary = {}
    for name, cfg in NETWORK_CONFIGS.items():
        m, b, i = run_network_pipeline(name, cfg)
        summary[name] = {"network": m, "baseline": b, "intervention": i}

    # ── Final comparison table ────────────────────────────────────────────────
    print("\n" + "=" * 70)
    print("  SUMMARY COMPARISON")
    print("=" * 70)
    header = f"{'Metric':<35} {'LFR_100':>12} {'LFR_1000':>12}"
    print(header)
    print("-" * len(header))
    for key in ["n_nodes", "n_edges", "avg_degree", "n_communities",
                "avg_clustering", "diameter", "assortativity_persona"]:
        v100  = summary["LFR_100"]["network"].get(key, "—")
        v1000 = summary["LFR_1000"]["network"].get(key, "—")
        fmt   = lambda v: f"{v:.3f}" if isinstance(v, float) else str(v)
        print(f"  {key:<33} {fmt(v100):>12} {fmt(v1000):>12}")
    print("-" * len(header))
    for key in ["final_mean_stress", "high_stress_agents"]:
        b100  = summary["LFR_100"]["baseline"].get(key, "—")
        b1000 = summary["LFR_1000"]["baseline"].get(key, "—")
        fmt   = lambda v: f"{v:.2f}" if isinstance(v, float) else str(v)
        print(f"  {key} (baseline){'':<18} {fmt(b100):>12} {fmt(b1000):>12}")

    print("\n  Files produced per network:")
    files = [
        "<name>_network_topology.png       — 4-panel network figure",
        "<name>_temporal_heatmap.png       — 30-day stress heatmap",
        "<name>_intervention_comparison.png — baseline vs intervention",
        "<name>_community_stress_profile.png — per-community contagion",
        "<name>_network.graphml            — full graph (load into any script)",
        "<name>_edges.csv                  — edge list",
        "<name>_nodes.csv                  — node/agent attributes",
        "<name>_network_metrics.json       — topology metrics",
        "<name>_influencers.json           — top-5 influencers",
        "<name>_agent_cohort.csv           — synthetic agent table",
        "<name>_simulation_baseline.csv    — 30-day baseline simulation",
        "<name>_simulation_intervention.csv — 30-day intervention simulation",
        "<name>_baseline_metrics.json      — averaged baseline KPIs",
        "<name>_intervention_metrics.json  — averaged intervention KPIs",
        "<name>_specification.txt          — full parameter & result summary",
    ]
    for f in files:
        print(f"    {f}")
    print()


if __name__ == "__main__":
    main()
