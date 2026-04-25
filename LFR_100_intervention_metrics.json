# LFR Benchmark Networks — SC Digital Contagion Simulator

## What this folder contains

Two new social networks built using the **Lancichinetti-Fortunato-Radicchi (LFR)**
benchmark model, replacing the original homophily-based network for better research validity.

> **Original network is NOT touched.** All original results remain in `analysis/`.

---

## Why LFR is better for your research

| Property | Original (homophily) | LFR Benchmark |
|---|---|---|
| Degree distribution | Poisson (narrow, uniform) | **Power-law γ=3** (matches real social networks) |
| Community sizes | Roughly equal | **Power-law β=1.5** (varies like real communities) |
| Community separation | Blurry (probability-based) | **Sharp (μ=0.1 → only 10% cross-community edges)** |
| No. of communities | ~5 (persona groups) | **8 (100-node) / 22 (1000-node)** |
| Standard benchmark | No | **Yes — used in published literature** |

The low mixing parameter μ=0.1 means communities are tightly defined — essential
for meaningful digital stress contagion research (stress spreads fast within a
community, slowly across communities).

---

## Networks at a glance

| | LFR_100 | LFR_1000 |
|---|---|---|
| Nodes | 100 | 1000 |
| Edges | 189 | 5,629 |
| Communities | 8 | 22 |
| Avg degree ⟨k⟩ | 3.78 | 11.26 |
| Clustering | 0.197 | 0.206 |
| Diameter | 16 | 6 |
| Persona assortativity | 0.91 | 0.80 |
| Final mean stress (baseline) | 42.71 | 42.53 |

---

## How to run (from scratch)

```bash
# 1. Make sure you are in the project root
cd sc-digital-contagion-simulator-beta

# 2. Install dependencies (if not already installed)
pip install networkx numpy pandas matplotlib seaborn tqdm

# 3. Run the generator
python lfr_networks/generate_lfr_networks.py
```

That's it. All 15 output files per network are regenerated automatically.

---

## Output files (inside results_100/ and results_1000/)

| File | Description |
|---|---|
| `LFR_<n>_network_topology.png` | **4-panel publication figure** (persona, community, influence, degree dist.) |
| `LFR_<n>_temporal_heatmap.png` | **30-day stress contagion heatmap** |
| `LFR_<n>_intervention_comparison.png` | Baseline vs intervention stress over time |
| `LFR_<n>_community_stress_profile.png` | Per-community stress trajectories + persona violin plot |
| `LFR_<n>_network.graphml` | Full graph with all node attributes (load with `nx.read_graphml()`) |
| `LFR_<n>_edges.csv` | Edge list (source, target) |
| `LFR_<n>_nodes.csv` | Node table: agent_id, persona, degree, influence_score, community_id |
| `LFR_<n>_network_metrics.json` | All topology metrics |
| `LFR_<n>_influencers.json` | Top-5 influencer agents |
| `LFR_<n>_agent_cohort.csv` | Synthetic agents with all attributes |
| `LFR_<n>_simulation_baseline.csv` | 30-day simulation data (no intervention) |
| `LFR_<n>_simulation_intervention.csv` | 30-day simulation data (intervention at day 10) |
| `LFR_<n>_baseline_metrics.json` | KPIs averaged over 5 Monte-Carlo runs |
| `LFR_<n>_intervention_metrics.json` | Intervention KPIs averaged over 5 runs |
| `LFR_<n>_specification.txt` | Full parameter + result summary (human-readable) |

---

## Loading a network in your own script

```python
import networkx as nx
import pandas as pd

# Load graph
G = nx.read_graphml("lfr_networks/results_1000/LFR_1000_network.graphml")

# Load simulation results
df = pd.read_csv("lfr_networks/results_1000/LFR_1000_simulation_baseline.csv")
```

---

## Reference

Lancichinetti, A., Fortunato, S., & Radicchi, F. (2008).
*Benchmark graphs for testing community detection algorithms.*
**Physical Review E**, 78, 046110.
https://doi.org/10.1103/PhysRevE.78.046110
