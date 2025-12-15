# Digital Contagion Simulator — Reference Guide

## The Mathematical Engine & Parameter Justification

### The Stress Contagion Equation

We modeled stress (S_t) as a linear combination of three forces:

Stress_t = α · Usage + β · PeerStress · Susceptibility − γ · Resilience

**Parameter Calibration:**

α = 0.6 (Personal Usage)
- Source: Calibrated weight from literature
- Why: Individual behavior is the primary predictor of digital stress. We assigned it 60% weight to ensure personal agency dominates over peer pressure.

β = 0.3 (Peer Influence)
- Source: Christakis & Fowler (2008)
- Why: Their study on social networks showed happiness/stress spreads with a transmission rate of ~30%. We directly adopted this coefficient.

γ = 0.1 (Resilience)
- Source: Calibrated buffer
- Why: Resilience acts as a dampener. We scaled it by ×10 in the equation so that a 0.1 weight provides a meaningful protective buffer (10-15 points).

### The Feedback Loop (Doomscrolling)

Usage_t = Usage_(t-1) × (1 + δ · Stress/100) × Variability × Noise

δ = 0.02 (The Spiral Factor)
- Source: Thomée et al. (2011)
- Why: Research indicates stressed young adults increase phone use by 2-3% as a coping mechanism. This creates the "vicious cycle" in our model.

**Variability vs. Noise:**
- Variability (0.8-1.2): A fixed "personality trait" for each agent. Some people are consistently erratic.
- Noise (N(1.0, 0.1)): A random daily fluctuation. Even consistent people have random bad days. 



---

## Constructing the "Digital Twin"

### From Real Data to Synthetic Agents

We did not invent the user behaviors. We used the Valakhorasani Dataset (700 users) and applied K-Means Clustering (k=5).

**Why K-Means?** We wanted to find natural groupings in the data rather than setting arbitrary thresholds (e.g., "anyone over 5 hours is an addict").

**The 5 Clusters Identified:**
- Minimalists (14%): 1.5 hrs/day
- Moderate (21%): 3.0 hrs/day
- Active (31%): 5.0 hrs/day
- Heavy (25%): 6.9 hrs/day
- Addicts (9%): 10.1 hrs/day

Validation: Our synthetic agents match the real dataset statistics with <5% error across all metrics (screen time, app usage, battery drain).

### Network Topology (The "Homophily" Graph)

We didn't just connect random people. We used a Stochastic Block Model to enforce "Homophily" (birds of a feather flock together).

**Connection Logic:**
- Probability 0.15: If two agents share the same persona (e.g., Addict ↔ Addict)
- Probability 0.03: If two agents have different personas
- Probability 0.01: Random "bridge" edges to ensure the network isn't totally disconnected

**Resulting Topology:**
- Nodes: 100
- Edges: 270
- Assortativity: 0.426 (This proves strong clustering; a random graph would be ~0.0) 



---

## Key Findings: Paradoxes & Trade-offs

### The Targeting Paradox

Why did targeting influencers increase burnout?

Strategy | Stress Reduction | Burnout Cases
---------|-----------------|---------------
Target Influencers | -3.7% (Best) | 3.60 (Worst)
Target Random | -2.2% | 3.40
Target Isolated | -0.6% | 3.20 (Best)

**Explanation:** Influencers act as "Social Support Hubs." When you quarantine them (reduce their usage):
- They stop spreading stress → Good for the average
- BUT their dependent friends lose a connection → This isolation causes localized stress spikes in vulnerable agents, pushing them over the edge into burnout

### The "Echo Chamber" Scenario

What if peer pressure was stronger?

We ran a simulation with β = 0.8 (Peer Influence dominates Personal Usage).

**Result:** Targeting influencers became massively effective.
- Stress: -65% reduction
- Burnout: 0 cases

**Insight:** Network interventions work best in highly conformist environments (like high schools with high peer pressure).

### Collective Action Wins

We tested a "Digital Detox Day" where all 100 agents reduced usage by 50% (instead of just 5 influencers).

**Result:** 5× better stress reduction than targeting influencers.

**Insight:** Network leverage (β=0.3) is not strong enough to beat universal behavior change. 



---

## Methodology & Reproducibility

### Experimental Rigor

We didn't just run the simulation once.

**5 Runs Per Scenario:** We used 5 different random seeds (42-46) for every experiment.

**Why?** To ensure our results (like the 5.9% reduction) weren't just a statistical fluke caused by random noise.

**Confidence:** The standard error was low (±0.73), confirming the effect is robust.

### Intervention Mechanics (The "Quarantine")

On Day 10, we targeted the top 5 agents (by Degree Centrality) and applied two specific clamps:

1. Usage Clamp: Capped screen time at 50% of their baseline
2. Transmission Dampening (70%): Reduced the stress they broadcast to neighbors

**Justification:** If you post less, you broadcast less stress. Christakis & Fowler (2008) suggest contagion attenuates by ~60-70% per hop; we modeled this as a direct reduction in transmission.

### Key References

- Epidemics: Kermack & McKendrick (1927) — The SIR Model basis
- Social Contagion: Christakis & Fowler (2008) — Happiness spreads in networks
- Phone Stress: Thomée et al. (2011) — Mobile use correlates with stress/depression
- ABM Framework: Epstein & Axtell (1996) — Sugarscape/Artificial Societies



---

## The "Targeting Paradox" — Deep Dive

### The Experiment

To validate our findings, we tested three distinct targeting strategies. In each case, we intervened on exactly 5 agents (5% of population).

Strategy | Who are they? | Avg. Connections (Degree)
---------|--------------|---------------------------
Top Influencers | The "Popular Kids" | 10.8 friends/agent
Random Agents | Random selection | 5.4 friends/agent
Isolates | Least connected | 2.0 friends/agent

### The Results (The Paradox)

Targeting influencers was best for the average person, but dangerous for the vulnerable few.

Metric | Target Influencers | Target Random | Target Isolates
-------|-------------------|--------------|----------------
Final Network Stress | 40.09 (Lowest) | 41.00 | 41.62 (Highest)
Burnout Cases | 3.60 (Highest) | 3.40 | 3.20 (Lowest)

### The Explanation

**Network Effect:** Influencers act as hubs. When you "quarantine" them (reduce their usage), you successfully stop them from spreading stress to their 10+ friends. This lowers the average stress.

**The Cost:** Those 10+ friends also rely on the influencer for social connection. When the influencer "goes dark," the network structure fractures. Highly dependent neighbors lose their social buffer, causing localized stress spikes that push them into burnout.



---

## Simulation Logic & Algorithm Flow

### The Daily Loop (Repeated for 30 Days)

**Step 1: Usage Update (The Feedback)**
- First, the agent decides how much to use the phone based on yesterday's stress
- Mechanism: If stress was high yesterday, usage goes up today (Doomscrolling factor δ=0.02)
- Noise: We add random Gaussian noise (N(1.0, 0.1)) so agents don't act robotically perfect

**Step 2: Stress Update (The Contagion)**
- Now we calculate the new stress level
- Personal Factor: We calculate stress from their new usage time (α=0.6)
- Social Factor: We look at all the agent's neighbors. We average their stress levels and multiply by the peer influence weight (β=0.3)
- Buffering: We subtract the agent's resilience score (γ=0.1)

**Step 3: Intervention Check (Days 10-30)**

If the agent is one of the Top 5 Influencers:
1. Usage Clamp: We force their Usage variable to 50% of its calculated value
2. Transmission Block: When their neighbors look at them (in Step 2), we multiply the stress transmission by 0.3 (blocking 70%)



---

## Limitations & Future Work

### Current Limitations

**Single Topology (The "Seed 42" Issue):** All 10 simulation runs used the exact same social network structure (Seed 42). While we varied the temporal noise (seeds 42-46), we have not yet tested if this works on a completely different network shape.

**Linear Transmission:** We modeled stress transmission as linear. In reality, contagion might be "complex" (requiring multiple reinforcements before spreading), which we didn't model.

**Binary Burnout:** We defined burnout as strictly Stress > 80. Real clinical burnout is a spectrum, not a binary switch.

### Proposed Future Work

**Sensitivity Analysis:** We plan to sweep the parameters (α, β, γ) to see which one matters most. For example, if we raise resilience training, does that beat usage reduction?

**Real-World Validation:** We want to compare our synthetic curves against Experience Sampling Method (ESM) data from real students to calibrate the β (peer influence) parameter.



---

## Annotated Bibliography

### Christakis, N. A., & Fowler, J. H. (2008). Dynamic spread of happiness... BMJ.

This is the foundational paper for social contagion. They found happiness spreads up to 3 degrees of separation with a ~25-30% transmission rate. We used this to set our Peer Influence Weight (β = 0.3) and our Transmission Dampening (70%).

### Thomée, S., et al. (2011). Mobile phone use and stress... BMC Public Health.

They established the link between high usage and stress/depression. Crucially, they described the feedback loop where stressed users use their phones more. We used this to justify our Self-Feedback Rate (δ = 0.02).

### Valakhorasani, R. (2024). User Behavior Dataset. Kaggle.

This provided the raw data (700 users). We ran K-Means Clustering on this data to create our 5 Agent Personas (Minimalist, Addict, etc.) ensuring our agents are statistically realistic, not random.

### Epstein, J. M., & Axtell, R. (1996). Growing Artificial Societies.

The "Bible" of Agent-Based Modeling. We followed their guidelines for assigning heterogeneous traits (giving each agent a unique resilience score between 0.7-1.3) rather than making everyone identical.
