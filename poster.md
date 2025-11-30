# Digital Contagion Simulator: Poster Content Guide

## Layout Structure

```
┌─────────────────────────────────┐
│     TITLE BANNER                │
├──────────────┬──────────────────┤
│  LEFT SIDE   │   RIGHT SIDE     │
│  (Graphics)  │   (Content)      │
│              │                  │
│  • Network   │  • Abstract      │
│    Graph     │  • Introduction  │
│  • Stress    │  • Model         │
│    Graph     │  • Intervention  │
│  • Results   │  • Results Table │
│    Chart     │  • Key Findings  │
│              │  • Conclusion    │
│              │  • References    │
└──────────────┴──────────────────┘
```

---

## TITLE BANNER

**Digital Contagion Simulator: How Stress Spreads Through Social Networks**

Agent-Based Modeling | [Your Name] | [Course/Institution] | November 2025

---

## LEFT SIDE: Graphics from Analysis Folder

### 1. Network Topology Graph
**Use existing:** `analysis/social_network.graphml` visualization  
**What it shows:** 100 nodes, 270 connections, 5 persona clusters, top influencers highlighted

### 2. Stress Trajectory Over Time
**Use existing:** Data from `analysis/simulation_baseline.csv` and intervention CSVs  
**What it shows:** Baseline vs Intervention lines, Day 10 intervention marker, stress reduction

### 3. Results Comparison Chart
**Create from existing:** `analysis/scenario_comparison.json` or metrics CSVs  
**What it shows:** Bar chart comparing final stress, burnout cases, stabilization day

---

## RIGHT SIDE: Content Blocks

### ABSTRACT

Digital stress propagates through social networks like an epidemic. We created 100 synthetic agents from a 700-user dataset and simulated 30 days of stress contagion through a homophilous network (270 connections). Targeting the top 5 influencers on Day 10 reduced network-wide stress by 5.9% and prevented 0.4 burnout cases.

---

### INTRODUCTION

**Research Question:**  
Does digital stress spread through social networks, and can targeted interventions reduce it?

**Hypothesis:**  
Targeting high-influence users reduces network-wide stress through contagion-breaking mechanisms.

**Approach:**
- 100 agents across 5 personas (Minimalist to Digital Addict)
- Homophilous network (assortativity = 0.426)
- 30-day simulation with Day 10 intervention on top 5 influencers

---

### MODEL EQUATIONS

**Stress Propagation:**
```
Stressₜ = α·Usage + β·PeerStress·Suscept - γ·Resilience·10
```

**Terms:**
- α = 0.6 (personal usage weight)
- β = 0.3 (peer influence weight)
- γ = 0.1 (resilience dampening)
- Suscept = 0.5-1.5 (peer sensitivity)
- Resilience = 0.7-1.3 (stress resistance)

**Usage Feedback:**
```
Usageₜ = Usageₜ₋₁ × (1 + δ·Stress/100) × Variability × Noise
```

**Terms:**
- δ = 0.02 (stress amplification)
- Variability = 0.8-1.2 (daily consistency)
- Noise = N(1, 0.1) (random fluctuation)

**Burnout:** Stress > 80

---

### INTERVENTION

**Day 10 Actions on Top 5 Influencers:**
1. Cut usage by 50% (digital detox)
2. Reduce stress transmission by 70% (less broadcasting)

**Duration:** Days 10-30

---

### RESULTS TABLE

| Metric | Baseline | Intervention | Change |
|--------|----------|--------------|--------|
| **Final Stress** | 42.61 ± 1.16 | 40.09 ± 0.73 | **-5.9%** |
| **Burnout Cases** | 5.8 ± 1.3 | 5.4 ± 1.1 | -0.4 agents |
| **Stabilization** | Day 23.4 | Day 21.8 | 1.6 days faster |

*Average across 5 simulation runs (seeds 42-46)*

---

### KEY FINDINGS (4 Facts)

**🎯 The Targeting Paradox**  
Influencers reduce average stress by 3.7% but cause 12.5% MORE burnout than random targeting.

**🔊 Echo Chamber Effect**  
When stress is 80% social, targeting influencers cuts stress by 65% and eliminates all burnout.

**🌍 Digital Detox Day**  
All 100 agents cutting usage 50% achieves 5× better results than targeting 5 influencers.

**⏰ Late Intervention Works**  
Intervening at Day 25 still reduces stress by 7% and saves 2 burnout cases.

---

### CONCLUSION

**Key Takeaways:**
- Network position matters: 5% intervention affects 100% of agents
- Timing flexibility: Late action still produces measurable effects
- Trade-offs exist: Lower average stress ≠ fewer burnout cases
- Collective > Targeted: Universal action beats influencer leverage 5×

---

### REFERENCES

1. Christakis & Fowler (2008). Dynamic spread of happiness. *BMJ*.
2. Thomée et al. (2011). Mobile phone use and stress. *BMC Public Health*.
3. Valakhorasani (2024). User Behavior Dataset. *Kaggle*.

**Contact:** [your.email@university.edu]

---

## Graphics You Already Have

**In analysis/ folder:**
- `social_network.graphml` → Network diagram
- `simulation_baseline.csv` → Baseline stress data
- `simulation_baseline_run0.csv` through `run4.csv` → Individual runs
- `simulation_intervention_run0.csv` through `run4.csv` → Intervention runs
- `scenario_comparison.json` → Results summary
- `metrics_baseline_all_runs.csv` → Baseline metrics
- `metrics_intervention_all_runs.csv` → Intervention metrics

**Use these files to create:**
1. Network visualization (from .graphml)
2. Stress trajectory line graph (from CSV files)
3. Results bar chart (from metrics or JSON)

### 1. TITLE BANNER (Full Width, Colored Background)

**Background:** Deep blue gradient (#1E3A8A to #3B82F6)  
**Text Color:** White  
**Height:** 60mm

**Title (Bold, 36pt):**  
Digital Contagion Simulator: How Stress Spreads Through Social Networks

**Subtitle (Regular, 14pt):**  
Agent-Based Modeling | [Your Name] | [Course/Institution] | November 2025

---

### 2. ABSTRACT (Right Column Top)

**Background:** Light blue box (#DBEAFE)

Digital stress propagates through social networks like an epidemic. We created 100 synthetic agents from a 700-user dataset and simulated 30 days of stress contagion through a homophilous network (270 connections). Targeting the top 5 influencers on Day 10 reduced network-wide stress by 5.9% and prevented 0.4 burnout cases.

---

### 3. INTRODUCTION

**Research Question:**  
Does digital stress spread through social networks, and can targeted interventions reduce it?

**Hypothesis:**  
Targeting high-influence users reduces network-wide stress through contagion-breaking mechanisms.

**Approach:**
- 100 agents across 5 personas (Minimalist to Addict)
- Homophilous network (assortativity = 0.426)
- 30-day simulation with Day 10 intervention

---

### 4. MODEL EQUATIONS (Gray Box)

**Background:** Light gray (#F3F4F6)

#### Stress Propagation

```
Stressₜ = α·Usage + β·PeerStress·Suscept - γ·Resilience·10
```

| Term | Value | Meaning |
|------|-------|---------|
| α | 0.6 | Personal usage weight |
| β | 0.3 | Peer influence weight |
| γ | 0.1 | Resilience dampening |
| Suscept | 0.5-1.5 | Peer sensitivity |
| Resilience | 0.7-1.3 | Stress resistance |

#### Usage Feedback

```
Usageₜ = Usageₜ₋₁ × (1 + δ·Stress/100) × Variability × Noise
```

| Term | Value | Meaning |
|------|-------|---------|
| δ | 0.02 | Stress amplification |
| Variability | 0.8-1.2 | Daily consistency |
| Noise | N(1,0.1) | Random fluctuation |

**Burnout:** Stress > 80

---

### 5. INTERVENTION

**Day 10 Actions on Top 5 Influencers:**
1. ✂️ Cut usage by 50% (digital detox)
2. 🔇 Reduce stress transmission by 70% (less broadcasting)

**Duration:** Days 10-30

---

### 6. RESULTS TABLE

| Metric | Baseline | Intervention | Change |
|--------|----------|--------------|--------|
| **Final Stress** | 42.61 ± 1.16 | 40.09 ± 0.73 | **-5.9%** ✓ |
| **Burnout Cases** | 5.8 ± 1.3 | 5.4 ± 1.1 | -0.4 agents |
| **Stabilization** | Day 23.4 | Day 21.8 | 1.6 days faster |

*Average across 5 simulation runs (seeds 42-46)*

---

### 7. KEY FINDINGS (4 Colored Boxes)

#### 🎯 Targeting Paradox
Influencers reduce avg stress by 3.7% but cause 12.5% MORE burnout than random targeting.

#### 🔊 Echo Chamber Effect
When stress is 80% social, targeting influencers cuts stress by 65% and eliminates all burnout.

#### 🌍 Digital Detox Day
All 100 agents cutting usage 50% achieves 5× better results than targeting 5 influencers.

#### ⏰ Late Intervention Works
Intervening at Day 25 still reduces stress by 7% and saves 2 burnout cases.

---

### 8. CONCLUSION

**Key Takeaways:**
- ✅ Network position matters: 5% intervention affects 100% of agents
- ✅ Timing flexibility: Late action still produces measurable effects
- ⚠️ Trade-offs exist: Lower avg stress ≠ fewer burnout cases
- 🌐 Collective > Targeted: Universal action beats influencer leverage 5×

---

### 9. REFERENCES (Small Font, 9pt)

1. Christakis & Fowler (2008). Dynamic spread of happiness. *BMJ*.
2. Thomée et al. (2011). Mobile phone use and stress. *BMC Public Health*.
3. Valakhorasani (2024). User Behavior Dataset. *Kaggle*.

**Contact:** [your.email@university.edu]

---

## 🎨 Canva Setup Instructions

### Step 1: Create Canvas (2 minutes)

1. Open Canva → "Create a design"
2. Select "Custom size" → **297mm × 420mm** (A3 Portrait)
3. Background: White

---

### Step 2: Build 2-Column Layout (10 minutes)

**LEFT COLUMN (Graphics - 120mm width):**

1. **Insert vertical space** for images aligned left
2. **Upload 3-4 PNG images** (create these first - see below):
   - Network diagram (top, 120mm × 110mm)
   - Stress trajectory graph (middle, 120mm × 100mm)
   - Results bar chart (bottom, 120mm × 90mm)
   - [Optional] Persona pie chart (if space, 120mm × 70mm)
3. **Add captions** below each image (9pt, gray text)

**RIGHT COLUMN (Content - 162mm width):**

1. **Insert text boxes** for sections 2-9
2. **Add colored boxes** for:
   - Abstract (light blue #DBEAFE)
   - Model equations (light gray #F3F4F6)
   - 4 Key findings (white with 8pt colored left border)

**Column Gap:** 15mm between columns

---

### Step 3: Typography & Colors

**Fonts in Canva:**
- Title: Montserrat Bold, 36pt
- Section headers: Montserrat Bold, 20pt
- Body: Open Sans Regular, 12pt
- Equations: Courier New, 11pt
- Captions: Open Sans Light, 9pt

**Color Palette:**
- Title banner: #1E3A8A (deep blue)
- Highlights: #EA580C (orange), #0D9488 (teal), #7C3AED (purple)
- Backgrounds: #DBEAFE (light blue), #F3F4F6 (light gray)

---

### Step 4: Export (2 minutes)

1. Click "Share" → "Download"
2. **File type:** PDF (Print) — High quality
3. Click "Download"

**Result:** `digital_contagion_poster.pdf` ready for A3 printing

---

## 📊 How to Generate Required PNGs

### PNG 1: Network Diagram (120mm × 110mm = 1417×1299 pixels @ 300 DPI)

**Create this visualization:**

```python
import networkx as nx
import matplotlib.pyplot as plt
import json

# Load network and agent data
G = nx.read_graphml('analysis/social_network.graphml')
with open('analysis/agent_cohort.json') as f:
    agents = json.load(f)

# Color map for personas
persona_colors = {
    'Minimalist': '#10B981',
    'Moderate User': '#3B82F6',
    'Active User': '#F59E0B',
    'Heavy User': '#EF4444',
    'Digital Addict': '#8B5CF6'
}

# Get node colors
node_colors = [persona_colors[agents[str(node)]['persona']] for node in G.nodes()]

# Identify top 5 influencers
influencers = [32, 59, 66, 78, 85]  # From report.md
node_sizes = [400 if node in influencers else 100 for node in G.nodes()]

# Draw
plt.figure(figsize=(4.72, 4.33), dpi=300)
pos = nx.spring_layout(G, seed=42, k=0.3)
nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=node_sizes, 
                       edgecolors=['red' if n in influencers else 'black' for n in G.nodes()],
                       linewidths=[3 if n in influencers else 0.5 for n in G.nodes()])
nx.draw_networkx_edges(G, pos, alpha=0.2, width=0.5)
plt.axis('off')
plt.tight_layout()
plt.savefig('network_diagram.png', dpi=300, bbox_inches='tight', facecolor='white')
plt.close()
```

**Caption:** Social Network (Assortativity = 0.426)

---

### PNG 2: Stress Trajectory (120mm × 100mm = 1417×1181 pixels @ 300 DPI)

**Create comparison line graph:**

```python
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Load simulation data (average across 5 runs)
baseline = pd.read_csv('analysis/simulation_baseline.csv')
intervention = pd.read_csv('analysis/simulation_intervention_run0.csv')  # Or average

# Calculate daily network stress
baseline_stress = baseline.groupby('day')['stress'].mean()
intervention_stress = intervention.groupby('day')['stress'].mean()

# Plot
fig, ax = plt.subplots(figsize=(4.72, 3.94), dpi=300)
ax.plot(baseline_stress.index, baseline_stress.values, 'o-', color='#3B82F6', linewidth=2, markersize=3, label='Baseline (42.61)')
ax.plot(intervention_stress.index, intervention_stress.values, 'o-', color='#EA580C', linewidth=2, markersize=3, label='Intervention (40.09)')

# Intervention marker
ax.axvline(x=10, color='gray', linestyle='--', linewidth=1.5, alpha=0.7)
ax.axvspan(10, 30, alpha=0.1, color='#EA580C')

# Labels
ax.set_xlabel('Day', fontsize=12)
ax.set_ylabel('Network Stress', fontsize=12)
ax.set_xlim(0, 30)
ax.set_ylim(25, 50)
ax.legend(fontsize=10, loc='upper right')
ax.grid(True, alpha=0.3, linestyle=':')
plt.tight_layout()
plt.savefig('stress_trajectory.png', dpi=300, bbox_inches='tight', facecolor='white')
plt.close()
```

**Caption:** Stress Reduction: -5.9% (42.61 → 40.09)

---

### PNG 3: Results Comparison Bar Chart (120mm × 90mm = 1417×1063 pixels @ 300 DPI)

**Create grouped bar chart:**

```python
import matplotlib.pyplot as plt
import numpy as np

# Data
metrics = ['Final\nStress', 'Burnout\nCases', 'Stabil.\nDay']
baseline = [42.61, 5.8, 23.4]
intervention = [40.09, 5.4, 21.8]
change_pct = [-5.9, -6.9, -6.8]

# Bar positions
x = np.arange(len(metrics))
width = 0.35

# Plot
fig, ax = plt.subplots(figsize=(4.72, 3.54), dpi=300)
bars1 = ax.bar(x - width/2, baseline, width, label='Baseline', color='#3B82F6', alpha=0.8)
bars2 = ax.bar(x + width/2, intervention, width, label='Intervention', color='#EA580C', alpha=0.8)

# Add change percentages on top
for i, pct in enumerate(change_pct):
    ax.text(i, max(baseline[i], intervention[i]) + 1.5, f'{pct:+.1f}%', 
            ha='center', fontsize=10, fontweight='bold', color='green' if pct < 0 else 'red')

# Labels
ax.set_ylabel('Value', fontsize=12)
ax.set_xticks(x)
ax.set_xticklabels(metrics, fontsize=10)
ax.legend(fontsize=10, loc='upper right')
ax.grid(True, alpha=0.3, linestyle=':', axis='y')
plt.tight_layout()
plt.savefig('results_comparison.png', dpi=300, bbox_inches='tight', facecolor='white')
plt.close()
```

**Caption:** Intervention Effectiveness Across Metrics

---

### [OPTIONAL] PNG 4: Persona Distribution (120mm × 70mm = 1417×827 pixels @ 300 DPI)

**Create pie chart:**

```python
import matplotlib.pyplot as plt

# Data from report
personas = ['Minimalist\n(14%)', 'Moderate\n(21%)', 'Active\n(31%)', 'Heavy\n(25%)', 'Addict\n(9%)']
sizes = [14, 21, 31, 25, 9]
colors = ['#10B981', '#3B82F6', '#F59E0B', '#EF4444', '#8B5CF6']

# Plot
fig, ax = plt.subplots(figsize=(4.72, 2.76), dpi=300)
ax.pie(sizes, labels=personas, colors=colors, autopct='', startangle=90, textprops={'fontsize': 9})
ax.axis('equal')
plt.tight_layout()
plt.savefig('persona_distribution.png', dpi=300, bbox_inches='tight', facecolor='white')
plt.close()
```

**Caption:** Agent Population by Persona

---

## ✅ Final Checklist

- [ ] Canvas set to 297mm × 420mm (A3 Portrait) in Canva
- [ ] 3-4 PNGs created and uploaded to left column
- [ ] Title banner (60mm height, blue gradient, 36pt)
- [ ] Both equations with term tables included
- [ ] Results table shows 3 metrics (42.61 → 40.09)
- [ ] 4 key findings with colored left borders
- [ ] All numbers match report.md
- [ ] References included (9pt font)
- [ ] PDF exported at high quality (Print mode)

---

## 📏 Final Dimensions

**Canva Canvas:** 297mm × 420mm (Portrait)  
**Left Column (Graphics):** 120mm width  
**Right Column (Content):** 162mm width  
**Print Cost:** ~$5-10 at university print center

This follows your template's left-graphics + right-content layout!

### 6️⃣ Primary Results (Table with green highlights)

| Metric | Baseline | Intervention | Change |
|--------|----------|-------------|--------|
| **Final Stress** | 42.61 ± 1.16 | 40.09 ± 0.73 | **-5.9%** ✓ |
| **Burnout Cases** | 5.8 ± 1.3 | 5.4 ± 1.1 | -0.4 agents |
| **Stabilization Day** | 23.4 | 21.8 | 1.6 days faster |

**Visual:** Line graph showing baseline vs intervention stress trajectories (Day 0-30)

### 7️⃣ Interesting Facts (4 boxes, colorful borders)

**Fact 1: The Targeting Paradox** 🎯  
Influencers reduce average stress by 3.7% but cause MORE burnout (+12.5%) than targeting random people.

**Fact 2: Echo Chamber Saves Lives** 🔊  
When stress is 80% social (not personal), targeting influencers cuts stress by **65%** and eliminates all burnout.

**Fact 3: Digital Detox Day Wins** 🌍  
All 100 agents reducing usage 50% for one day achieves **5× better results** than targeting 5 influencers for 20 days.

**Fact 4: Late Intervention Still Works** ⏰  
Intervening at Day 25 (5 days before end) still reduces stress by 7% and saves 2 burnout cases.

### 8️⃣ Key Takeaways (Bold bullet points)

✅ **Network position matters:** 5% intervention affects 100% of agents  
✅ **Timing flexibility:** Even late action (Day 25) produces measurable effects  
⚠️ **Trade-offs exist:** Lower average stress ≠ fewer burnout cases  
🌐 **Collective > Targeted:** Universal participation beats influencer leverage by 5×

---

## FOOTER

### References (9pt, two-column text)

1. Christakis & Fowler (2008). *Dynamic spread of happiness in social networks*. BMJ.
2. Thomée et al. (2011). *Mobile phone use and stress*. BMC Public Health.
3. Valakhorasani (2024). *User Behavior Dataset*. Kaggle.
4. Epstein & Axtell (1996). *Growing Artificial Societies*. MIT Press.

**QR Code:** Link to GitHub repository (bottom-right, 60mm × 60mm)

**Contact:** [your.email@university.edu]

---

## 🎨 Design Specifications

### Color Palette

- **Primary (Headers):** Deep Blue #1E3A8A
- **Secondary (Highlights):** Teal #0D9488
- **Accent (Important):** Orange #EA580C
- **Background:** White #FFFFFF
- **Box Backgrounds:** Light Gray #F3F4F6, Light Blue #DBEAFE
- **Text:** Dark Gray #1F2937

### Typography

- **Title:** Helvetica Bold, 72pt
- **Section Headers:** Helvetica Bold, 36pt
- **Subheaders:** Helvetica Bold, 24pt
- **Body Text:** Helvetica Regular, 18pt
- **Table/Math:** Courier New, 16pt
- **References:** Helvetica Light, 9pt

### Visual Elements

1. **Network Diagram (Column 1):** 5 colored node clusters showing homophily
2. **Stress Trajectory Graph (Column 3):** Dual lines (baseline vs intervention) with shaded intervention period (Day 10-30)
3. **Equation Boxes:** Light gray background with colored borders
4. **Fact Boxes:** White with thick colored left border (blue, teal, orange, purple)
5. **Result Table:** Alternating row colors, green highlights for improvements

---

## 🛠️ Tools & Production

### Recommended Software

**Option A: PowerPoint**
- Layout: Custom size (59.4 cm × 84.1 cm)
- Export: PDF (high quality, 300 DPI)

**Option B: LaTeX (Beamerposter)**
```latex
\documentclass[final,t]{beamer}
\usepackage[size=a1,scale=1.4]{beamerposter}
```

**Option C: Canva**
- Template: "Academic Research Poster"
- Custom dimensions: 594mm × 841mm

### Export Settings

- **Format:** PDF (preferred) or PNG
- **Resolution:** 300 DPI minimum
- **Color Mode:** RGB (for screens) or CMYK (for printing)
- **File Size:** Target < 20 MB for easy sharing

---

## ✅ Pre-Submission Checklist

- [ ] Title visible from 3 meters away
- [ ] No text smaller than 18pt (except references)
- [ ] Equations clearly labeled with term definitions
- [ ] All graphs have axis labels and legends
- [ ] Color-blind friendly palette (test with simulator)
- [ ] QR code tested and working
- [ ] Contact information visible
- [ ] References formatted consistently
- [ ] Grammar/spelling checked
- [ ] PDF exports correctly without blurriness

---

## 📊 Graph Details

### Stress Trajectory Graph (Column 3)

**Axes:**
- X-axis: Day 0-30 (labeled every 5 days)
- Y-axis: Network Stress 25-50 (labeled every 5 units)

**Lines:**
- Baseline: Solid blue line (thickness 3pt)
- Intervention: Solid orange line (thickness 3pt)
- Vertical line at Day 10: Dashed gray (intervention start)

**Shaded Region:** Light orange (Day 10-30, alpha=0.2)

**Data Points:** Show markers every 5 days (circles, 10pt)

**Legend:** Top-right corner
- Blue circle: Baseline (42.61 ± 1.16)
- Orange circle: Intervention (40.09 ± 0.73)

---

## 💡 Space-Saving Tips

1. **Use icons** instead of words where possible (📊 🎯 ⏰)
2. **Abbreviate units:** hours → hrs, minutes → min, agents → ag
3. **Combine related info:** Use tables instead of bullet lists
4. **Remove redundancy:** Don't repeat "stress" if header already says it
5. **Use subscripts:** Write equations compactly (Stressₜ not Stress_t)
6. **Smart highlighting:** Bold only the key number, not entire sentence
7. **Equation margins:** Tight spacing around math (10mm not 20mm)

---

## 📐 Printable Dimensions

**For A1 Poster Printing:**
- Width: 594mm (23.4 inches)
- Height: 841mm (33.1 inches)
- Safe zone: 30mm margin (avoid critical content)
- Bleed: Add 5mm if printer requires

**Cost Estimate:** $30-50 at university print shop

**Alternative:** A0 (larger) = 841mm × 1189mm if presenting at conference
