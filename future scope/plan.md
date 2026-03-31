# Future Scope & Upgrade Plan: Digital Contagion Simulator

This document outlines the roadmap to elevate the Digital Contagion Simulator from an academic project into a top-tier research paper suitable for conferences like AAAI, ICWSM, KDD, or journals like Nature Human Behaviour.

## 1. Core Innovations for the Research Paper

To publish at top venues, we need to move beyond simple linear threshold models and small-scale random graphs. The proposed core innovation is replacing the static, homogeneous mathematical contagion model (where peer influence is a fixed coefficient $\beta = 0.3$) with a **Graph Attention Network (GAT)**.

### Why Graph Attention Networks (GATs)?
*   **Dynamic Peer Influence:** Instead of all friends having equal influence ($1/\text{degree}$), GATs calculate an *attention coefficient* between users. A "Digital Addict" might pay 80% attention to another "Addict" but only 5% attention to a "Minimalist" in their network.
*   **State-Dependent Influence:** Attention weights can change based on current stress levels. If user $A$ is burning out, user $B$ might "doomscroll" more intensely in response to $A$'s posts.
*   **Non-linear Thresholds:** GNNs naturally model complex contagion where it takes specific combinations of influential peers to trigger burnout, rather than simple averaging.

---

## 2. Implementation Roadmap

### Phase 1: Engine Overhaul & Scaling (The GNN Upgrade)
Currently, simulations run on 100 agents using NumPy arrays. For a paper, we need $10,000+$ agents.
*   **Task:** Migrate from `networkx` + `numpy` to **PyTorch Geometric (PyG)** or **DGL**.
*   **Action Items:**
    *   Rewrite `agent_factory.py` to output dense node feature matrices (Persona, Base Stress, Daily Usage, Resilience, Susceptibility).
    *   Rewrite `network_topology.py` to generate PyG-compatible edge index formats spanning 10,000+ nodes using Kronecker Graph models or optimized Erdos-Renyi/SBM algorithms.
    *   Overhaul `temporal_engine.py`. Replace the equation:
        $Stress_t = \alpha \cdot Usage + \beta \cdot PeerStress - \gamma \cdot Resilience$
        *with a GAT Layer update:*
        $h_i^{(t)} = ReLU \left( \sum_{j \in \mathcal{N}(i) \cup \{i\}} \alpha_{ij}^{(t-1)} \mathbf{W} h_j^{(t-1)} \right)$
        Where $\alpha_{ij}$ is the attention score capturing how much agent $i$ is currently influenced by agent $j$.

### Phase 2: Real-World Validation
Reviewers will demand empirical validation to prove the GAT simulation mimics reality better than the baseline equation.
*   **Task:** Obtain and calibrate against longitudinal ground-truth data.
*   **Action Items:**
    *   **Acquire Data:** Look for Experience Sampling Method (ESM) datasets. The *StudentLife* dataset (Dartmouth) or *NetHealth* dataset are strong candidates as they contain Bluetooth proximity (network), usage data, and survey-based stress scores over time.
    *   **Supervised Calibration:** Train the GAT weights to minimize the Mean Squared Error (MSE) between the simulated stress trajectories and the real-world dataset's stress scores over a 30-60 day period.

### Phase 3: Advanced Interventions & Scenarios
Once the GAT model is calibrated and scaled, we will run the new experiments.
*   **Network Restructuring Interventions:** What happens if we dynamically break edges between high-stress nodes?
*   **Attention-Based Targeting:** The "Targeting Paradox" found in the initial project used Degree Centrality. In the GNN model, we can intervene by targeting agents with the highest **cumulative outward attention weights** (the true functional influencers, not just topological ones).

### Phase 4: Ablation Studies & Manuscript Generation
*   **Ablation List:**
    *   GAT Contagion vs. Mean-field Linear Contagion (proving the GNN is necessary).
    *   Targeting by Attention vs. Targeting by Degree (proving top-down heuristic targeting is flawed).
*   **Manuscript Structure:**
    *   Intro: Digital wellbeing as a network problem.
    *   Related Work: SIR Models $\rightarrow$ Complex Contagion $\rightarrow$ GNNs for Epidemiology.
    *   Methodology: The GAT architecture and dataset calibration.
    *   Results: The simulated cascades, targeting paradox resolution, and intervention optimizations.
    *   Discussion/Ethics: Policy implications for platform design (e.g., algorithmic feed dampening vs account bans).

---

## 3. Technology Stack & Dependencies

To execute this plan, update `pyproject.toml` with the following:
*   **PyTorch (`torch`)**: The underlying deep learning tensor framework.
*   **PyTorch Geometric (`torch_geometric`)**: For the GAT implementation and scalable message passing.
*   **GPU support (`cuda`)**: Critical for simulating the temporal loops of 10,000+ agent attention weights in a reasonable time.

## 4. Execution Checklist

### Phase 1: Planning and Setup
- [x] Refine the plan into a granular issue checklist.
- [x] Add PyTorch and PyTorch Geometric to `pyproject.toml` dependencies.
- [ ] Outline dataset requirements and search for ESM datasets (e.g., StudentLife).

### Phase 2: Refactoring & The GNN Upgrade
- [ ] Refactor `agent_factory.py` to output dense node feature matrices compatible with PyG (Persona, Base Stress, Daily Usage, Resilience, Susceptibility).
- [ ] Refactor `network_topology.py` to generate PyG-compatible edge index lists (for 10k nodes).
- [ ] Build a PyG proof of concept mapping the original formula to Graph tensor updates.
- [ ] Rebuild `temporal_engine.py` to use a Graph Attention Network (GAT) layer with custom state-dependent influences.

### Phase 3: Calibration and Simulation (10,000 Agents)
- [ ] Integrate a real-world ESM dataset to supervise/calibrate the GAT attention weights.
- [ ] Train the GNN model using MSE loss between simulated stress trajectories and the real data over 30 days.
- [ ] Run a baseline simulation at scale ($10,000+$ agents) predicting behavior and visualizing cascades.

### Phase 4: Scenarios and Evaluation
- [ ] Re-run the baseline linear contagion equation on the scaled infrastructure as a comparison.
- [ ] Implement targeting intervention scenario 1 (Target Top Centrality based on GAT attention scores).
- [ ] Compare GAT Contagion Targeting vs. Degree Centrality targeting to replicate the "Targeting Paradox".
- [ ] Assess the efficiency of the GAT Engine at simulating complex contagion cascades.

### Phase 5: Manuscript Preparation & Publishing
- [ ] Write the Methodology section outlining GAT usage and architectural differences.
- [ ] Write the Results, contrasting GNN performance & simulation accuracy with classical mean-field models.
- [ ] Finalize Discussion focusing on policy implications of attention contagion.

---

## 5. Next Steps
1.  **Literature Review Sprint:** Gather papers specifically on "GNNs for Contagion modeling" and "Social Media Stress ESM datasets".
2.  **Dataset Hunting:** Secure access to *StudentLife*, *NetHealth*, or a similar longitudinal cohort.
3.  **Proof of Concept:** Build a small GAT model using PyG on the existing 100-node network to verify the deep learning loops work before scaling.
