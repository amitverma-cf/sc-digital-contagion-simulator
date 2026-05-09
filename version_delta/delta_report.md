# Version Delta Report

This report is generated from Version Delta output files. All numeric results below are read from saved artifacts.

## How To Use This Report

Use this file as the source pack for writing a printable final report similar to `final_report_printable.html`.
Do not invent additional values, p-values, scenarios, or mechanisms. If a number is not in this report or one of the listed artifacts, it should not appear as a Delta result.

## Core Scope

- Topology: LFR benchmark graph, generated before persona assignment.
- Persona assignment: dataset-derived personas assigned after topology generation.
- Scenarios: Baseline and Targeted Intervention only.
- Targeting: top 5% by degree centrality.
- Simulation horizon: 30 days.
- Intervention starts on day 10.
- Burnout definition: stress greater than 80.
- Age is sampled and stored, but it is not used in topology or stress dynamics.
- No support-loss term, targeting paradox, universal intervention, random targeting, low-degree targeting, or conformity sensitivity is included in the Delta core run.

## Variables And Ranges

| Variable | Meaning | Value or range |
| --- | --- | --- |
| `n_days` | Simulation length | 30 days |
| `alpha` | Personal usage weight in stress pressure | 0.6 |
| `beta` | Peer stress weight in stress pressure | 0.3 |
| `gamma` | Multiplicative resilience dampening weight | 0.1 |
| `delta` | Stress-to-usage feedback rate | 0.02 |
| `stress` | Digital stress proxy | 0 to 100.0 |
| `usage` | App usage in minutes per day | 30.0 to 600.0 |
| `resilience` | Individual stress dampening trait | 0.7 to 1.3 |
| `susceptibility` | Individual peer-stress sensitivity | 0.5 to 1.5 |
| `variability` | Individual usage variability multiplier | 0.8 to 1.2 |
| `intervention_factor` | Target usage multiplier after intervention | 0.5 |
| `peer_reduction` | Target outgoing peer-stress multiplier after intervention | 0.3 |

## Updated Formulas

Usage update:

`U_next = clip(U_prev * (1 + delta * S_prev / 100) * variability * noise * intervention_usage_factor, usage_min, usage_cap)`

Stress update:

`S_next = clip((alpha * U_norm + beta * peer_stress * susceptibility) * (1 - gamma * resilience), 0, stress_cap)`

Definitions:

- `U_norm = (U_next / usage_cap) * 100`.
- `noise` is sampled from a normal distribution centered at 1.0 with standard deviation 0.1.
- `peer_stress` is the mean previous-day stress of direct neighbors.
- After intervention begins, an intervened target contributes only `peer_reduction` times its stress to neighbors' peer-stress calculation.
- The stress formula is identical in baseline and intervention; only the usage and peer-stress inputs change for intervention.

## Burnout Count Interpretation

Burnout count is an integer within each individual run because it counts agents with final-day stress greater than 80.
Decimal burnout values in summary tables are means across Monte Carlo runs, not fractional agents inside one simulation.
The `peak_burnout_count` metric includes day 0 initialization, so use day-30 burnout for final-outcome claims.

## results_100

### Topology Details

- Nodes: 100
- Edges: 174
- Mean degree: 3.480
- Degree range: 1 to 13
- Clustering coefficient: 0.197
- Connected components: 1
- LFR communities: 8
- Community size distribution: [17, 13, 12, 12, 12, 12, 12, 10]
- Target mixing parameter: 0.100
- Actual mixing parameter: 0.058
- Mixing tolerance met: True
- Persona assortativity: -0.044
- Accepted topology seed: 42
- Persona counts: {'Active User': 21, 'Digital Addict': 19, 'Heavy User': 20, 'Minimalist': 19, 'Moderate User': 21}
- Age range and mean: 18 to 59, mean 37.27

### Intervention Targets

- Number of targets: 5
- Target IDs: [57, 99, 71, 2, 10]
- Selection rule: top 5% by degree centrality.

### Result Metrics

- Monte Carlo runs: 30
- Final mean stress difference: 2.293 (baseline - intervention)
- Final mean stress reduction: 6.509%

Baseline summary:

| Metric | Mean | SD | 95% CI |
| --- | ---: | ---: | --- |
| Final mean stress | 35.229 | 0.778 | [34.951, 35.508] |
| Final max stress | 78.968 | 1.854 | [78.304, 79.631] |
| Final mean usage | 287.847 | 6.255 | [285.608, 290.085] |
| Day-30 burnout count | 0.167 | 0.379 | [0.031, 0.302] |
| Peak burnout count, includes day 0 | 19.000 | 0.000 | [19.000, 19.000] |
| Total stress AUC | 105388.402 | 1815.502 | [104738.733, 106038.071] |

Intervention summary:

| Metric | Mean | SD | 95% CI |
| --- | ---: | ---: | --- |
| Final mean stress | 32.936 | 0.768 | [32.661, 33.211] |
| Final max stress | 78.941 | 1.885 | [78.266, 79.615] |
| Final mean usage | 275.284 | 6.398 | [272.995, 277.574] |
| Day-30 burnout count | 0.133 | 0.346 | [0.010, 0.257] |
| Peak burnout count, includes day 0 | 19.000 | 0.000 | [19.000, 19.000] |
| Total stress AUC | 101059.708 | 1710.496 | [100447.615, 101671.801] |

Paired differences, baseline minus intervention:

| Metric | Mean | SD | 95% CI |
| --- | ---: | ---: | --- |
| Final mean stress | 2.293 | 0.265 | [2.198, 2.388] |
| Final max stress | 0.027 | 0.037 | [0.014, 0.040] |
| Final mean usage | 12.562 | 1.541 | [12.011, 13.114] |
| Day-30 burnout count | 0.033 | 0.183 | [-0.032, 0.099] |
| Peak burnout count, includes day 0 | 0.000 | 0.000 | [0.000, 0.000] |
| Total stress AUC | 4328.694 | 443.330 | [4170.050, 4487.338] |

Day-30 burnout count distribution by run:

- Baseline: 0 agents: 25 runs, 1 agents: 5 runs.
- Intervention: 0 agents: 26 runs, 1 agents: 4 runs.

## results_1000

### Topology Details

- Nodes: 1000
- Edges: 5497
- Mean degree: 10.994
- Degree range: 4 to 98
- Clustering coefficient: 0.187
- Connected components: 1
- LFR communities: 19
- Community size distribution: [96, 81, 79, 79, 72, 71, 68, 67, 60, 55, 51, 44, 33, 28, 27, 25, 22, 21, 21]
- Target mixing parameter: 0.100
- Actual mixing parameter: 0.199
- Mixing tolerance met: False
- Warning: this graph did not meet the configured mixing tolerance. Use the actual mixing value in any report language.
- Persona assortativity: -0.005
- Accepted topology seed: 46
- Persona counts: {'Active User': 204, 'Digital Addict': 194, 'Heavy User': 199, 'Minimalist': 194, 'Moderate User': 209}
- Age range and mean: 18 to 59, mean 38.07

### Intervention Targets

- Number of targets: 50
- Target IDs: [772, 667, 968, 853, 268, 201, 712, 835, 200, 76, 409, 376, 764, 803, 792, 370, 44, 194, 26, 840, 872, 460, 585, 115, 393, 334, 907, 664, 819, 69, 939, 303, 910, 337, 578, 18, 245, 246, 279, 614, 760, 75, 400, 419, 618, 952, 67, 224, 260, 762]
- Selection rule: top 5% by degree centrality.

### Result Metrics

- Monte Carlo runs: 10
- Final mean stress difference: 3.589 (baseline - intervention)
- Final mean stress reduction: 10.009%

Baseline summary:

| Metric | Mean | SD | 95% CI |
| --- | ---: | ---: | --- |
| Final mean stress | 35.857 | 0.235 | [35.711, 36.003] |
| Final max stress | 75.705 | 0.679 | [75.284, 76.126] |
| Final mean usage | 289.954 | 1.917 | [288.766, 291.142] |
| Day-30 burnout count | 0.000 | 0.000 | [0.000, 0.000] |
| Peak burnout count, includes day 0 | 194.000 | 0.000 | [194.000, 194.000] |
| Total stress AUC | 1085273.894 | 7050.182 | [1080904.146, 1089643.642] |

Intervention summary:

| Metric | Mean | SD | 95% CI |
| --- | ---: | ---: | --- |
| Final mean stress | 32.268 | 0.182 | [32.156, 32.381] |
| Final max stress | 74.075 | 1.013 | [73.447, 74.703] |
| Final mean usage | 273.906 | 1.619 | [272.902, 274.909] |
| Day-30 burnout count | 0.000 | 0.000 | [0.000, 0.000] |
| Peak burnout count, includes day 0 | 194.000 | 0.000 | [194.000, 194.000] |
| Total stress AUC | 1018902.826 | 5895.160 | [1015248.968, 1022556.684] |

Paired differences, baseline minus intervention:

| Metric | Mean | SD | 95% CI |
| --- | ---: | ---: | --- |
| Final mean stress | 3.589 | 0.070 | [3.546, 3.632] |
| Final max stress | 1.630 | 0.581 | [1.270, 1.990] |
| Final mean usage | 16.048 | 0.393 | [15.804, 16.292] |
| Day-30 burnout count | 0.000 | 0.000 | [0.000, 0.000] |
| Peak burnout count, includes day 0 | 0.000 | 0.000 | [0.000, 0.000] |
| Total stress AUC | 66371.068 | 1399.935 | [65503.380, 67238.757] |

Day-30 burnout count distribution by run:

- Baseline: 0 agents: 10 runs.
- Intervention: 0 agents: 10 runs.

# Version Delta Folder Contents

- delta_report.md: Generated report of Version Delta results and folder contents.
- generate_delta.py: Main pipeline script that generates topology, runs simulations, and writes outputs.
- plan.md: Original delta plan draft (superseded by plan2.md).
- plan2.md: Authoritative Version Delta implementation plan.
- results_100/: Output directory for a specific network size run.
- results_100/delta_aggregated_metrics.json: Aggregated metrics with mean, std, stderr, and 95% CI.
- results_100/delta_burnout.png: Burnout count summary plot with uncertainty bands.
- results_100/delta_daily_summary.csv: Daily trajectory summary across runs with uncertainty.
- results_100/delta_network.graphml: LFR network with node attributes for the run.
- results_100/delta_run_metrics.csv: Run-level metrics for baseline and intervention.
- results_100/delta_simulation_records.csv: Raw daily simulation records with run id and scenario.
- results_100/delta_targets.json: Target agent list (top 5% by degree centrality).
- results_100/delta_topology_metrics.json: Topology and assortativity metrics for the accepted LFR graph.
- results_100/delta_trajectory.png: Stress trajectory plot with uncertainty bands.
- results_1000/: Output directory for a specific network size run.
- results_1000/delta_aggregated_metrics.json: Aggregated metrics with mean, std, stderr, and 95% CI.
- results_1000/delta_burnout.png: Burnout count summary plot with uncertainty bands.
- results_1000/delta_daily_summary.csv: Daily trajectory summary across runs with uncertainty.
- results_1000/delta_network.graphml: LFR network with node attributes for the run.
- results_1000/delta_run_metrics.csv: Run-level metrics for baseline and intervention.
- results_1000/delta_simulation_records.csv: Raw daily simulation records with run id and scenario.
- results_1000/delta_targets.json: Target agent list (top 5% by degree centrality).
- results_1000/delta_topology_metrics.json: Topology and assortativity metrics for the accepted LFR graph.
- results_1000/delta_trajectory.png: Stress trajectory plot with uncertainty bands.