# Digital Contagion Simulator — Complete Project Context

## Project Overview

**Project Name:** Digital Contagion Simulator: Agent-Based Modeling of Stress Propagation

**Team:** Brainwave Storms
- Amit Verma (SE23UCSE020)
- Jayanth Reddy .Y (SE23UCSE080)
- Ishani Singh (SE23UCSE078)
- Tanvi Ganesh Borkar (SE23UCSE172)
- Yashika Gupta (SE23UCSE190)

**Date:** November 2025

**Repository:** github.com/amitverma-cf/sc-digital-contagion-simulator

---

## The Core Idea

We built a "Digital Twin" of a social network to study how stress spreads through peer interactions, similar to how diseases spread through populations. The fundamental hypothesis: if stress is contagious through social connections, can we reduce population-level stress by targeting interventions at highly connected individuals (influencers)?

---

## Why We Did This Project

### The Problem
Modern students face unprecedented levels of digital stress. Social media creates echo chambers where anxiety and stress spread rapidly through peer networks. Traditional mental health interventions treat individuals, but what if stress operates at the network level?

### Real-World Motivation
During exam seasons, we observed stress cascading through friend groups. One person's anxiety post triggers others, creating a feedback loop. We wanted to:
1. Quantify how stress spreads through networks
2. Test if targeted interventions on key individuals could reduce population-level stress
3. Understand trade-offs between different intervention strategies

### Academic Foundation
Our work builds on:
- **Epidemiology:** SIR models (Kermack & McKendrick, 1927)
- **Social Contagion:** Christakis & Fowler's happiness spread study (2008)
- **Digital Wellbeing:** Thomée et al.'s work on phone use and stress (2011)
- **Agent-Based Modeling:** Epstein & Axtell's artificial societies framework (1996)

---

## What We Built

### 1. Data Foundation
**Source:** Valakhorasani User Behavior Dataset (Kaggle, 2024)
- 700 real smartphone users
- Metrics: Screen time, app switches, notifications, battery drain

**Why this data?** We needed realistic behavioral patterns, not made-up numbers. This dataset captures actual human-device interaction patterns.

### 2. Agent Creation (K-Means Clustering)
We ran K-Means clustering (k=5) to identify natural user groups:

**The 5 Personas:**
- Minimalists (14%): 1.5 hrs/day, low app switching
- Moderate Users (21%): 3.0 hrs/day, balanced patterns
- Active Users (31%): 5.0 hrs/day, regular engagement
- Heavy Users (25%): 6.9 hrs/day, high daily usage
- Digital Addicts (9%): 10.1 hrs/day, extreme usage, frequent notifications

**Why clustering?** To find data-driven user types rather than arbitrary thresholds. Our synthetic agents match real data with <5% error.

### 3. Network Construction (Stochastic Block Model)
**Structure:**
- 100 nodes (agents)
- 270 edges (friendships)
- Assortativity: 0.426

**Connection Logic:**
- P(connection) = 0.15 if same persona
- P(connection) = 0.03 if different persona  
- P(connection) = 0.01 for random bridges

**Why this topology?** Enforces homophily ("birds of a feather flock together"). Addicts connect mostly with addicts, mimicking real social bubbles. The 0.426 assortativity proves strong clustering vs. random networks (~0.0).

### 4. The Mathematical Engine

**Stress Dynamics:**
```
Stress_t = α·Usage + β·PeerStress·Susceptibility − γ·Resilience
```

**Parameters:**
- α = 0.6 (Personal Usage): Individual behavior is primary driver
- β = 0.3 (Peer Influence): From Christakis & Fowler's 30% transmission rate
- γ = 0.1 (Resilience): Protective buffer scaled ×10 for meaningful impact

**Agent Heterogeneity:**
- Susceptibility: 0.5-1.5 (variation in peer sensitivity)
- Resilience: 0.7-1.3 (variation in stress resistance)
- Variability: 0.8-1.2 (behavioral consistency)

**Feedback Loop (Doomscrolling):**
```
Usage_t = Usage_(t-1) × (1 + δ·Stress/100) × Variability × Noise
```
- δ = 0.02: Stress increases usage by 2% (from Thomée et al.)
- Noise: N(1.0, 0.1) adds daily randomness

**Why these equations?** Linear combination allows us to isolate effects of personal vs. social factors. The feedback loop captures the vicious cycle we see in real doomscrolling behavior.

### 5. Temporal Engine
**Simulation Duration:** 30 days (long enough for patterns to stabilize)
**Update Frequency:** Daily (matches real-world stress dynamics)
**Burnout Threshold:** Stress > 80 (based on clinical stress scales)

---

## The Intervention Experiment

### Design
**Timing:** Day 10 intervention start (allows baseline stress to build)
**Target:** Top 5 influencers by Degree Centrality
**Mechanism:**
1. Usage Clamp: Force screen time to 50% of baseline
2. Transmission Dampening: Reduce stress broadcast by 70%

**Why Day 10?** Real-world interventions have delayed response. Day 5 too early (no stress accumulation), Day 25 still works but less optimal.

**Why Degree Centrality?** Tested vs. betweenness, eigenvector, pagerank. Degree centrality most effective for our network topology (assortativity 0.426 favors local clustering).

### Control Measures
- 5 independent runs (seeds 42-46)
- Baseline scenario (no intervention)
- Statistical validation (paired t-test)
- Standard error calculation

**Why 5 runs?** Ensure results aren't statistical flukes from random noise. Low standard error (±0.73) confirms robustness.

---

## What We Found

### Primary Results
**Intervention Effect:**
- Final stress: 42.61 → 40.09 (−5.9%, p<0.05)
- Burnout cases: 5.8 → 5.4 (−0.4 agents)
- Stabilization: Day 23.4 → Day 21.8 (1.6 days faster)

### Discovery 1: The Targeting Paradox
**Finding:** Targeting influencers lowered average stress but increased burnout cases by 12.5%.

**Three Strategies Compared:**
| Strategy | Stress Reduction | Burnout Cases |
|----------|-----------------|---------------|
| Influencers | −3.7% (Best) | 3.60 (Worst) |
| Random | −2.2% | 3.40 |
| Isolated | −0.6% | 3.20 (Best) |

**Why?** Influencers are social support hubs. "Quarantining" them stops stress spread BUT their dependent friends lose social connection, causing localized stress spikes in vulnerable agents.

**Implication:** Optimizing for average stress ≠ optimizing for burnout prevention.

### Discovery 2: The Echo Chamber Effect
**Test:** Increased peer influence to β=0.8 (highly conformist environment)

**Result:**
- Stress reduction: −65%
- Burnout: 0 cases
- Targeting influencers became massively effective

**Why?** In highly conformist populations (think high school peer pressure), network structure dominates. Influencer interventions work when social conformity is high.

### Discovery 3: Collective Action Wins
**Test:** Universal "Digital Detox" where all 100 agents reduce usage 50%

**Result:** 5× better than targeting influencers

**Why?** Network leverage (β=0.3) isn't strong enough to beat universal behavior change. When contagion is weak, population-wide interventions outperform targeted strategies.

### Discovery 4: Intervention Timing
**Test:** Late intervention (Day 25 vs. Day 10)

**Result:** Still achieves 7% stress reduction, prevents 2 burnouts

**Why?** System exhibits path dependence. Early stress establishes network gradients that persist, but late action can still disrupt equilibrium.

---

## Technical Implementation

### Code Structure
```
src/
├── agent_factory.py          # Agent creation with personas
├── network_topology.py       # Stochastic Block Model
├── temporal_engine.py        # Simulation loop
├── persona_definition.py     # K-Means clustering
├── run_scenarios.py          # Experiment orchestration
└── create_visualizations.py  # Analysis & plotting
```

### Key Algorithms
1. **K-Means Clustering** (scikit-learn): User segmentation
2. **Stochastic Block Model** (NetworkX): Network generation
3. **Degree Centrality** (NetworkX): Influencer identification
4. **Paired t-test** (scipy.stats): Statistical validation

### Data Pipeline
1. Load Valakhorasani dataset (700 users)
2. Feature engineering (screen time, app switches, notifications)
3. K-Means clustering → 5 personas
4. Generate 100 agents from persona distributions
5. Build network with homophily
6. Run 30-day simulation
7. Apply intervention Day 10-30
8. Collect metrics & visualize

---

## Why Each Decision Was Made

### Why Agent-Based Modeling?
Traditional equation-based models can't capture emergent network effects. ABM lets us model heterogeneous agents with individual traits interacting in complex ways.

### Why 100 Agents?
Balance between computational efficiency and statistical power. Large enough for network effects, small enough to run thousands of simulations.

### Why 30 Days?
Stress dynamics stabilize around Day 23. 30 days captures full trajectory without unnecessary computation.

### Why Linear Stress Model?
Starting point for analysis. We acknowledge limitation—future work will test non-linear thresholds (complex contagion).

### Why Degree Centrality?
Most interpretable metric ("number of friends"). We tested alternatives; degree worked best for our assortativity pattern.

### Why Top 5 Influencers?
5% intervention coverage is realistic for resource-constrained programs. Tested 10%, 20%—diminishing returns beyond 5%.

---

## Validation & Rigor

### Data Validation
- Synthetic agents match real data: <5% error across all metrics
- Screen time distribution preserved
- App usage patterns replicated
- Network statistics align with social network research

### Statistical Validation
- Multiple runs (n=5) for each scenario
- Paired t-tests for significance
- Standard error calculation
- Confidence intervals reported

### Model Validation
- Parameter values from peer-reviewed research
- Network structure matches real social networks
- Behavior patterns match smartphone usage studies

---

## Limitations & Future Work

### Current Limitations
1. **Static Network:** Friendships don't change over 30 days
2. **Linear Transmission:** Real contagion may have thresholds
3. **Binary Burnout:** Real burnout is a spectrum, not switch
4. **Single Topology:** All runs used same network structure (Seed 42)
5. **Synthetic Data:** Needs validation with real student longitudinal data

### Proposed Future Work
1. **Sensitivity Analysis:** Sweep α, β, γ to find key parameters
2. **Non-linear Models:** Test complex contagion thresholds
3. **Dynamic Networks:** Add friendship formation/dissolution
4. **Combined Interventions:** Test detox + resilience training
5. **Real-world Calibration:** Validate with Experience Sampling Method data
6. **Multi-network Analysis:** Test across different network structures

---

## Real-World Applications

### Campus Wellness Programs
**Recommendation:** Hybrid strategies
- Use network analysis to identify influencers
- Combine with population-wide policies (screen-free hours)
- Don't rely solely on targeting "super-spreaders"

### Corporate Mental Health
**Insight:** Manager stress spreads to teams. Address both individual managers and team-wide policies.

### Public Health Policy
**Framework:** Network-aware intervention design. Understand trade-offs between average outcomes and vulnerable populations.

---

## Key Takeaways

1. **Stress is contagious:** Spreads measurably through social networks
2. **Targeting works but has trade-offs:** Influencer interventions reduce average stress but may increase burnout in vulnerable individuals
3. **Network structure matters:** Intervention effectiveness depends on assortativity and conformity levels
4. **Collective action beats targeted leverage:** When contagion is weak (β=0.3), universal interventions outperform
5. **It's never too late:** Even late interventions show measurable effects

---

## Technical Achievements

1. Built realistic agent-based model from real smartphone data
2. Implemented mathematical stress contagion framework
3. Discovered non-intuitive targeting paradox
4. Validated results with statistical rigor (5 runs, t-tests)
5. Created comprehensive visualization suite
6. Open-sourced entire codebase for reproducibility

---

## References

**Core Literature:**
- Christakis & Fowler (2008) — Social contagion (β parameter)
- Thomée et al. (2011) — Phone use & stress (δ parameter)
- Kermack & McKendrick (1927) — SIR epidemic model
- Epstein & Axtell (1996) — Agent-based modeling framework

**Data Source:**
- Valakhorasani (2024) — User Behavior Dataset (Kaggle)

**Full Bibliography:** See handout_printable.md

---

## Project Files

**Analysis:**
- `analysis/` — All simulation results, graphs, metrics
- `report.md` — Comprehensive technical report
- `interestingFacts.md` — Key discoveries summary

**Documentation:**
- `handout_printable.md` — Print-ready reference guide
- `presentation_script.md` — 5-minute presentation script
- `poster.html` — A3 research poster

**Code:**
- `src/` — All simulation code
- `main.py` — Main simulation runner
- `pyproject.toml` — Dependencies

---

## Impact Statement

This project demonstrates that mental health interventions can be optimized using network science. By understanding how stress spreads through social connections, we can design more effective, targeted, and equitable wellness programs. Our findings challenge the assumption that targeting "influencers" is always optimal—sometimes, collective action is the answer.

The open-source nature of this work enables others to:
- Validate our findings
- Test different scenarios
- Apply the framework to other contexts
- Build upon our methodology

We hope this work contributes to more evidence-based, network-aware approaches to digital wellbeing and mental health support in educational settings.
