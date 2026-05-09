"""
Version Delta: LFR-based Digital Stress Contagion Simulator
Implements plan2.md requirements for baseline vs targeted intervention.
"""

import json
import math
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd

ROOT = Path(__file__).parent.parent
DELTA_DIR = Path(__file__).parent
PERSONA_FILE = ROOT / "analysis" / "persona_definitions.json"

SIM_PARAMS = {
    "n_days": 30,
    "alpha": 0.6,
    "beta": 0.3,
    "gamma": 0.1,
    "delta": 0.02,
    "stress_cap": 100.0,
    "usage_min": 30.0,
    "usage_cap": 600.0,
    "intervention_day": 10,
    "intervention_factor": 0.5,
    "peer_reduction": 0.3,
    "resilience_min": 0.7,
    "resilience_max": 1.3,
    "susceptibility_min": 0.5,
    "susceptibility_max": 1.5,
    "variability_min": 0.8,
    "variability_max": 1.2,
}

NETWORK_CONFIGS = {
    "LFR_100": {
        "n": 100,
        "tau1": 3.0,
        "tau2": 1.5,
        "mu": 0.1,
        "average_degree": 5,
        "min_community": 10,
        "max_community": 20,
        "seed": 42,
        "n_runs": 30,
    },
    "LFR_1000": {
        "n": 1000,
        "tau1": 3.0,
        "tau2": 1.5,
        "mu": 0.1,
        "average_degree": 10,
        "min_community": 20,
        "max_community": 100,
        "seed": 42,
        "n_runs": 10,
    },
}


def load_persona_definitions():
    with open(PERSONA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def compute_exact_persona_counts(n_agents, persona_defs):
    total = sum(p["count"] for p in persona_defs.values())
    raw = {name: n_agents * (p["count"] / total) for name, p in persona_defs.items()}
    floors = {name: int(math.floor(val)) for name, val in raw.items()}
    remainder = n_agents - sum(floors.values())
    if remainder > 0:
        frac = sorted(
            ((name, raw[name] - floors[name]) for name in raw),
            key=lambda x: (-x[1], x[0]),
        )
        for i in range(remainder):
            floors[frac[i][0]] += 1
    return floors


def sample_agent_attributes(persona_name, persona_defs, rng):
    char = persona_defs[persona_name]["characteristics"]
    app_usage = float(max(SIM_PARAMS["usage_min"], rng.normal(char["app_usage_mean"], char["app_usage_std"])))
    screen_time = float(max(1.0, rng.normal(char["screen_time_mean"], char["screen_time_std"])))
    battery_drain = float(max(300.0, rng.normal(char["battery_drain_mean"], char["battery_drain_std"])))
    apps_installed = int(max(10, rng.normal(char["apps_installed_mean"], char["apps_installed_std"])))
    data_usage = float(max(100.0, rng.normal(char["data_usage_mean"], char["data_usage_std"])))
    age = int(max(18, min(59, rng.normal(char["age_mean"], char["age_std"]))))

    base_stress = (char["behavior_class_mode"] - 1) / 4.0 * 100.0

    return {
        "persona": persona_name,
        "app_usage": app_usage,
        "screen_time": screen_time,
        "battery_drain": battery_drain,
        "apps_installed": apps_installed,
        "data_usage": data_usage,
        "behavior_class": char["behavior_class_mode"],
        "age": age,
        "base_stress": base_stress,
        "resilience": float(rng.uniform(SIM_PARAMS["resilience_min"], SIM_PARAMS["resilience_max"])),
        "susceptibility": float(rng.uniform(SIM_PARAMS["susceptibility_min"], SIM_PARAMS["susceptibility_max"])),
        "variability": float(rng.uniform(SIM_PARAMS["variability_min"], SIM_PARAMS["variability_max"])),
    }


def compute_mixing_parameter(G, community_id_by_node):
    ext_fracs = []
    for node in G.nodes():
        deg = G.degree(node)
        if deg == 0:
            continue
        own = community_id_by_node[node]
        ext = 0
        for nb in G.neighbors(node):
            if community_id_by_node[nb] != own:
                ext += 1
        ext_fracs.append(ext / deg)
    if not ext_fracs:
        return 0.0
    return float(np.mean(ext_fracs))


def build_lfr_graph(cfg, mu_tolerance=0.05, max_attempts=5):
    target_mu = cfg["mu"]
    last_graph = None
    last_mu = None
    last_seed = None
    last_comm_map = None
    last_error = None

    for attempt in range(max_attempts):
        seed = cfg["seed"] + attempt
        try:
            G = nx.LFR_benchmark_graph(
                n=cfg["n"],
                tau1=cfg["tau1"],
                tau2=cfg["tau2"],
                mu=cfg["mu"],
                average_degree=cfg["average_degree"],
                min_community=cfg["min_community"],
                max_community=cfg["max_community"],
                max_iters=5000,
                seed=seed,
            )
        except nx.ExceededMaxIterations as exc:
            last_error = exc
            continue
        G.remove_edges_from(list(nx.selfloop_edges(G)))

        communities = {frozenset(G.nodes[n]["community"]) for n in G.nodes()}
        comm_list = sorted(list(communities), key=len, reverse=True)
        comm_id_map = {comm: idx for idx, comm in enumerate(comm_list)}
        community_id_by_node = {n: comm_id_map[frozenset(G.nodes[n]["community"])] for n in G.nodes()}

        actual_mu = compute_mixing_parameter(G, community_id_by_node)

        last_graph = G
        last_mu = actual_mu
        last_seed = seed
        last_comm_map = community_id_by_node

        if abs(actual_mu - target_mu) <= mu_tolerance:
            break

    if last_graph is None:
        raise nx.ExceededMaxIterations("LFR generation failed after retries") from last_error

    return last_graph, last_mu, last_seed, last_comm_map


def assign_personas_and_attributes(G, community_id_by_node, persona_defs, seed):
    rng = np.random.default_rng(seed)
    counts = compute_exact_persona_counts(G.number_of_nodes(), persona_defs)
    persona_list = []
    for name, count in counts.items():
        persona_list.extend([name] * count)
    rng.shuffle(persona_list)

    nodes_sorted = sorted(G.nodes())
    for idx, node in enumerate(nodes_sorted):
        persona = persona_list[idx]
        attrs = sample_agent_attributes(persona, persona_defs, rng)
        attrs["agent_id"] = int(node)
        attrs["lfr_community_id"] = int(community_id_by_node[node])
        G.nodes[node].update(attrs)

    for node in G.nodes():
        if "community" in G.nodes[node]:
            G.nodes[node].pop("community", None)


def compute_node_centrality(G):
    degree_cent = nx.degree_centrality(G)
    betweenness = nx.betweenness_centrality(G)
    eigenvector = nx.eigenvector_centrality(G, max_iter=1000)

    for node in G.nodes():
        G.nodes[node]["degree"] = int(G.degree(node))
        G.nodes[node]["degree_centrality"] = float(degree_cent[node])
        G.nodes[node]["centrality_score"] = float(degree_cent[node])
        G.nodes[node]["betweenness_centrality"] = float(betweenness[node])
        G.nodes[node]["eigenvector_centrality"] = float(eigenvector[node])


def compute_topology_metrics(G, actual_mu, community_id_by_node, target_mu, mu_tolerance):
    degrees = [deg for _, deg in G.degree()]
    community_sizes = {}
    for node, cid in community_id_by_node.items():
        community_sizes[cid] = community_sizes.get(cid, 0) + 1

    persona_assort = nx.attribute_assortativity_coefficient(G, "persona") if G.number_of_nodes() > 1 else 0.0
    mu_distance = abs(actual_mu - target_mu)

    metrics = {
        "n_nodes": G.number_of_nodes(),
        "n_edges": G.number_of_edges(),
        "mean_degree": float(np.mean(degrees)) if degrees else 0.0,
        "clustering_coefficient": float(nx.average_clustering(G)) if G.number_of_nodes() > 1 else 0.0,
        "connected_components": int(nx.number_connected_components(G)),
        "n_communities": int(len(community_sizes)),
        "community_size_distribution": [int(sz) for sz in sorted(community_sizes.values(), reverse=True)],
        "actual_mixing_parameter": float(actual_mu),
        "target_mixing_parameter": float(target_mu),
        "mixing_parameter_distance": float(mu_distance),
        "mixing_tolerance": float(mu_tolerance),
        "mixing_tolerance_met": bool(mu_distance <= mu_tolerance),
        "persona_assortativity": float(persona_assort),
        "degree_distribution": [int(d) for d in degrees],
    }
    return metrics


def select_targets_by_degree(G):
    n_targets = max(5, int(0.05 * G.number_of_nodes()))
    sorted_nodes = sorted(G.nodes(), key=lambda n: G.nodes[n]["degree_centrality"], reverse=True)
    targets = sorted_nodes[:n_targets]
    return targets


def simulate(G, params, seed, scenario, intervention_day=None, intervention_agents=None):
    rng = np.random.default_rng(seed)
    if intervention_agents is None:
        intervention_agents = set()

    node_ids = list(G.nodes())
    stress = {n: float(G.nodes[n]["base_stress"]) for n in node_ids}
    usage = {n: float(G.nodes[n]["app_usage"]) for n in node_ids}

    records = []

    for day in range(params["n_days"] + 1):
        day_records = []
        new_stress = {}
        new_usage = {}
        intervention_active = intervention_day is not None and day >= intervention_day

        for n in node_ids:
            neighbors = list(G.neighbors(n))
            if neighbors:
                adjusted = []
                for nb in neighbors:
                    contrib = stress[nb]
                    if intervention_active and nb in intervention_agents:
                        contrib *= params["peer_reduction"]
                    adjusted.append(contrib)
                peer_stress = float(np.mean(adjusted)) if adjusted else 0.0
            else:
                peer_stress = 0.0

            is_intervened = intervention_active and n in intervention_agents

            day_records.append({
                "agent_id": int(n),
                "day": int(day),
                "stress": float(stress[n]),
                "usage": float(usage[n]),
                "peer_influence": float(peer_stress),
                "persona": G.nodes[n]["persona"],
                "intervention_active": bool(is_intervened),
                "scenario": scenario,
            })

            if day < params["n_days"]:
                u_factor = params["intervention_factor"] if is_intervened else 1.0
                noise = rng.normal(1.0, 0.1)
                s_factor = 1 + params["delta"] * (stress[n] / 100.0)
                u_next = usage[n] * s_factor * G.nodes[n]["variability"] * noise * u_factor
                u_next = float(np.clip(u_next, params["usage_min"], params["usage_cap"]))
                new_usage[n] = u_next

                usage_norm = (u_next / params["usage_cap"]) * 100.0
                p_contrib = peer_stress * G.nodes[n]["susceptibility"]
                resilience = G.nodes[n]["resilience"]
                s_next = (params["alpha"] * usage_norm + params["beta"] * p_contrib) * (1 - params["gamma"] * resilience)
                new_stress[n] = float(np.clip(s_next, 0, params["stress_cap"]))

        records.extend(day_records)
        if day < params["n_days"]:
            stress = new_stress
            usage = new_usage

    return pd.DataFrame(records)


def compute_run_metrics(df, n_days, run_id, seed, scenario):
    day_final = df[df["day"] == n_days]
    daily_burnout = df.groupby("day")["stress"].apply(lambda x: (x > 80).sum())

    metrics = {
        "run_id": int(run_id),
        "seed": int(seed),
        "scenario": scenario,
        "final_mean_stress": float(day_final["stress"].mean()),
        "final_max_stress": float(day_final["stress"].max()),
        "final_mean_usage": float(day_final["usage"].mean()),
        "burnout_count_day_30": int((day_final["stress"] > 80).sum()),
        "peak_burnout_count": int(daily_burnout.max()),
        "peak_stress": float(df["stress"].max()),
        "total_stress_auc": float(df.groupby("agent_id")["stress"].sum().sum()),
    }
    return metrics


def aggregate_metrics(metrics_df, paired_diff_df=None):
    summary = {}
    numeric_cols = [
        "final_mean_stress",
        "final_max_stress",
        "final_mean_usage",
        "burnout_count_day_30",
        "peak_burnout_count",
        "peak_stress",
        "total_stress_auc",
    ]

    for col in numeric_cols:
        values = metrics_df[col].values.astype(float)
        mean = float(np.mean(values))
        std = float(np.std(values, ddof=1)) if len(values) > 1 else 0.0
        stderr = float(std / math.sqrt(len(values))) if len(values) > 0 else 0.0
        ci_low = mean - 1.96 * stderr
        ci_high = mean + 1.96 * stderr
        summary[col] = {
            "mean": mean,
            "std": std,
            "stderr": stderr,
            "ci95_low": float(ci_low),
            "ci95_high": float(ci_high),
        }

    if paired_diff_df is not None:
        diff_summary = {}
        for col in numeric_cols:
            if col not in paired_diff_df.columns:
                continue
            values = paired_diff_df[col].values.astype(float)
            mean = float(np.mean(values))
            std = float(np.std(values, ddof=1)) if len(values) > 1 else 0.0
            stderr = float(std / math.sqrt(len(values))) if len(values) > 0 else 0.0
            ci_low = mean - 1.96 * stderr
            ci_high = mean + 1.96 * stderr
            diff_summary[col] = {
                "mean": mean,
                "std": std,
                "stderr": stderr,
                "ci95_low": float(ci_low),
                "ci95_high": float(ci_high),
            }
        summary["paired_difference"] = diff_summary

    return summary


def build_daily_summary(records_df):
    per_run_day = records_df.groupby(["scenario", "run_id", "day"]).agg(
        stress_mean=("stress", "mean"),
        usage_mean=("usage", "mean"),
        burnout_count=("stress", lambda x: (x > 80).sum()),
    ).reset_index()

    summary = per_run_day.groupby(["scenario", "day"]).agg(
        stress_mean=("stress_mean", "mean"),
        stress_std=("stress_mean", "std"),
        usage_mean=("usage_mean", "mean"),
        usage_std=("usage_mean", "std"),
        burnout_mean=("burnout_count", "mean"),
        burnout_std=("burnout_count", "std"),
    ).reset_index()

    summary["stress_std"] = summary["stress_std"].fillna(0.0)
    summary["usage_std"] = summary["usage_std"].fillna(0.0)
    summary["burnout_std"] = summary["burnout_std"].fillna(0.0)

    return summary


def plot_trajectory(summary_df, output_path):
    plt.figure(figsize=(10, 6))
    for scenario, color in [("Baseline", "#e74c3c"), ("Intervention", "#2ecc71")]:
        data = summary_df[summary_df["scenario"] == scenario]
        plt.plot(data["day"], data["stress_mean"], label=f"{scenario}", color=color, linewidth=2)
        plt.fill_between(
            data["day"],
            data["stress_mean"] - data["stress_std"],
            data["stress_mean"] + data["stress_std"],
            color=color,
            alpha=0.15,
        )
    plt.axvline(x=SIM_PARAMS["intervention_day"], color="black", linestyle="--", alpha=0.3)
    plt.title("Version Delta: Stress Trajectory (Mean ± SD)")
    plt.xlabel("Day")
    plt.ylabel("Mean Stress")
    plt.legend()
    plt.grid(True, alpha=0.1)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()


def plot_burnout(summary_df, output_path):
    plt.figure(figsize=(10, 6))
    for scenario, color in [("Baseline", "#e74c3c"), ("Intervention", "#2ecc71")]:
        data = summary_df[summary_df["scenario"] == scenario]
        plt.plot(data["day"], data["burnout_mean"], label=f"{scenario}", color=color, linewidth=2)
        plt.fill_between(
            data["day"],
            data["burnout_mean"] - data["burnout_std"],
            data["burnout_mean"] + data["burnout_std"],
            color=color,
            alpha=0.15,
        )
    plt.axvline(x=SIM_PARAMS["intervention_day"], color="black", linestyle="--", alpha=0.3)
    plt.title("Version Delta: Burnout Count (Mean ± SD)")
    plt.xlabel("Day")
    plt.ylabel("Burnout Count (Stress > 80)")
    plt.legend()
    plt.grid(True, alpha=0.1)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()


def describe_delta_file(filename):
    descriptions = {
        "plan.md": "Original delta plan draft (superseded by plan2.md).",
        "plan2.md": "Authoritative Version Delta implementation plan.",
        "generate_delta.py": "Main pipeline script that generates topology, runs simulations, and writes outputs.",
        "delta_report.md": "Generated report of Version Delta results and folder contents.",
    }
    return descriptions.get(filename, "File in Version Delta folder.")


def describe_result_file(filename):
    descriptions = {
        "delta_network.graphml": "LFR network with node attributes for the run.",
        "delta_topology_metrics.json": "Topology and assortativity metrics for the accepted LFR graph.",
        "delta_targets.json": "Target agent list (top 5% by degree centrality).",
        "delta_simulation_records.csv": "Raw daily simulation records with run id and scenario.",
        "delta_run_metrics.csv": "Run-level metrics for baseline and intervention.",
        "delta_aggregated_metrics.json": "Aggregated metrics with mean, std, stderr, and 95% CI.",
        "delta_daily_summary.csv": "Daily trajectory summary across runs with uncertainty.",
        "delta_trajectory.png": "Stress trajectory plot with uncertainty bands.",
        "delta_burnout.png": "Burnout count summary plot with uncertainty bands.",
    }
    return descriptions.get(filename, "Output file from Version Delta run.")


def write_delta_report(delta_root, results_dirs):
    report_path = delta_root / "delta_report.md"

    def metric_line(label, stats):
        return (
            f"| {label} | {stats['mean']:.3f} | {stats['std']:.3f} | "
            f"[{stats['ci95_low']:.3f}, {stats['ci95_high']:.3f}] |"
        )

    def value_counts_text(series):
        counts = series.value_counts().sort_index()
        return ", ".join(f"{int(k)} agents: {int(v)} runs" for k, v in counts.items())

    def summarize_graph(graph_path):
        G = nx.read_graphml(graph_path)
        personas = pd.Series([G.nodes[n].get("persona", "Unknown") for n in G.nodes()])
        ages = pd.Series([float(G.nodes[n].get("age", 0)) for n in G.nodes()])
        degrees = pd.Series([int(float(G.nodes[n].get("degree", G.degree(n)))) for n in G.nodes()])
        return {
            "persona_counts": personas.value_counts().sort_index().to_dict(),
            "age_min": int(ages.min()),
            "age_mean": float(ages.mean()),
            "age_max": int(ages.max()),
            "degree_min": int(degrees.min()),
            "degree_max": int(degrees.max()),
        }

    lines = []
    lines.append("# Version Delta Report")
    lines.append("")
    lines.append("This report is generated from Version Delta output files. All numeric results below are read from saved artifacts.")
    lines.append("")
    lines.append("## How To Use This Report")
    lines.append("")
    lines.append("Use this file as the source pack for writing a printable final report similar to `final_report_printable.html`.")
    lines.append("Do not invent additional values, p-values, scenarios, or mechanisms. If a number is not in this report or one of the listed artifacts, it should not appear as a Delta result.")
    lines.append("")
    lines.append("## Core Scope")
    lines.append("")
    lines.append("- Topology: LFR benchmark graph, generated before persona assignment.")
    lines.append("- Persona assignment: dataset-derived personas assigned after topology generation.")
    lines.append("- Scenarios: Baseline and Targeted Intervention only.")
    lines.append("- Targeting: top 5% by degree centrality.")
    lines.append("- Simulation horizon: 30 days.")
    lines.append("- Intervention starts on day 10.")
    lines.append("- Burnout definition: stress greater than 80.")
    lines.append("- Age is sampled and stored, but it is not used in topology or stress dynamics.")
    lines.append("- No support-loss term, targeting paradox, universal intervention, random targeting, low-degree targeting, or conformity sensitivity is included in the Delta core run.")
    lines.append("")
    lines.append("## Variables And Ranges")
    lines.append("")
    lines.append("| Variable | Meaning | Value or range |")
    lines.append("| --- | --- | --- |")
    lines.append(f"| `n_days` | Simulation length | {SIM_PARAMS['n_days']} days |")
    lines.append(f"| `alpha` | Personal usage weight in stress pressure | {SIM_PARAMS['alpha']} |")
    lines.append(f"| `beta` | Peer stress weight in stress pressure | {SIM_PARAMS['beta']} |")
    lines.append(f"| `gamma` | Multiplicative resilience dampening weight | {SIM_PARAMS['gamma']} |")
    lines.append(f"| `delta` | Stress-to-usage feedback rate | {SIM_PARAMS['delta']} |")
    lines.append(f"| `stress` | Digital stress proxy | 0 to {SIM_PARAMS['stress_cap']} |")
    lines.append(f"| `usage` | App usage in minutes per day | {SIM_PARAMS['usage_min']} to {SIM_PARAMS['usage_cap']} |")
    lines.append(f"| `resilience` | Individual stress dampening trait | {SIM_PARAMS['resilience_min']} to {SIM_PARAMS['resilience_max']} |")
    lines.append(f"| `susceptibility` | Individual peer-stress sensitivity | {SIM_PARAMS['susceptibility_min']} to {SIM_PARAMS['susceptibility_max']} |")
    lines.append(f"| `variability` | Individual usage variability multiplier | {SIM_PARAMS['variability_min']} to {SIM_PARAMS['variability_max']} |")
    lines.append(f"| `intervention_factor` | Target usage multiplier after intervention | {SIM_PARAMS['intervention_factor']} |")
    lines.append(f"| `peer_reduction` | Target outgoing peer-stress multiplier after intervention | {SIM_PARAMS['peer_reduction']} |")
    lines.append("")
    lines.append("## Updated Formulas")
    lines.append("")
    lines.append("Usage update:")
    lines.append("")
    lines.append("`U_next = clip(U_prev * (1 + delta * S_prev / 100) * variability * noise * intervention_usage_factor, usage_min, usage_cap)`")
    lines.append("")
    lines.append("Stress update:")
    lines.append("")
    lines.append("`S_next = clip((alpha * U_norm + beta * peer_stress * susceptibility) * (1 - gamma * resilience), 0, stress_cap)`")
    lines.append("")
    lines.append("Definitions:")
    lines.append("")
    lines.append("- `U_norm = (U_next / usage_cap) * 100`.")
    lines.append("- `noise` is sampled from a normal distribution centered at 1.0 with standard deviation 0.1.")
    lines.append("- `peer_stress` is the mean previous-day stress of direct neighbors.")
    lines.append("- After intervention begins, an intervened target contributes only `peer_reduction` times its stress to neighbors' peer-stress calculation.")
    lines.append("- The stress formula is identical in baseline and intervention; only the usage and peer-stress inputs change for intervention.")
    lines.append("")
    lines.append("## Burnout Count Interpretation")
    lines.append("")
    lines.append("Burnout count is an integer within each individual run because it counts agents with final-day stress greater than 80.")
    lines.append("Decimal burnout values in summary tables are means across Monte Carlo runs, not fractional agents inside one simulation.")
    lines.append("The `peak_burnout_count` metric includes day 0 initialization, so use day-30 burnout for final-outcome claims.")
    lines.append("")

    for res_dir in results_dirs:
        agg_path = res_dir / "delta_aggregated_metrics.json"
        topo_path = res_dir / "delta_topology_metrics.json"
        targets_path = res_dir / "delta_targets.json"
        run_metrics_path = res_dir / "delta_run_metrics.csv"
        graph_path = res_dir / "delta_network.graphml"

        if not agg_path.exists():
            lines.append(f"## {res_dir.name}")
            lines.append("No aggregated metrics file found.")
            lines.append("")
            continue

        with open(agg_path, "r", encoding="utf-8") as f:
            agg = json.load(f)
        with open(topo_path, "r", encoding="utf-8") as f:
            topo = json.load(f)
        with open(targets_path, "r", encoding="utf-8") as f:
            targets = json.load(f)
        run_metrics = pd.read_csv(run_metrics_path)
        graph_summary = summarize_graph(graph_path)

        lines.append(f"## {res_dir.name}")
        lines.append("")
        lines.append("### Topology Details")
        lines.append("")
        lines.append(f"- Nodes: {topo['n_nodes']}")
        lines.append(f"- Edges: {topo['n_edges']}")
        lines.append(f"- Mean degree: {topo['mean_degree']:.3f}")
        lines.append(f"- Degree range: {graph_summary['degree_min']} to {graph_summary['degree_max']}")
        lines.append(f"- Clustering coefficient: {topo['clustering_coefficient']:.3f}")
        lines.append(f"- Connected components: {topo['connected_components']}")
        lines.append(f"- LFR communities: {topo['n_communities']}")
        lines.append(f"- Community size distribution: {topo['community_size_distribution']}")
        lines.append(f"- Target mixing parameter: {topo['target_mixing_parameter']:.3f}")
        lines.append(f"- Actual mixing parameter: {topo['actual_mixing_parameter']:.3f}")
        lines.append(f"- Mixing tolerance met: {topo['mixing_tolerance_met']}")
        if not topo["mixing_tolerance_met"]:
            lines.append("- Warning: this graph did not meet the configured mixing tolerance. Use the actual mixing value in any report language.")
        lines.append(f"- Persona assortativity: {topo['persona_assortativity']:.3f}")
        lines.append(f"- Accepted topology seed: {topo.get('seed_used', agg.get('config', {}).get('seed_used'))}")
        lines.append(f"- Persona counts: {graph_summary['persona_counts']}")
        lines.append(f"- Age range and mean: {graph_summary['age_min']} to {graph_summary['age_max']}, mean {graph_summary['age_mean']:.2f}")
        lines.append("")
        lines.append("### Intervention Targets")
        lines.append("")
        lines.append(f"- Number of targets: {targets['n_targets']}")
        lines.append(f"- Target IDs: {targets['target_ids']}")
        lines.append("- Selection rule: top 5% by degree centrality.")
        lines.append("")
        lines.append("### Result Metrics")
        lines.append("")
        lines.append(f"- Monte Carlo runs: {agg['config']['n_runs']}")
        reduction_pct = agg["config"].get("final_mean_stress_reduction_pct")
        baseline_mean = agg.get("baseline", {}).get("final_mean_stress", {}).get("mean")
        intervention_mean = agg.get("intervention", {}).get("final_mean_stress", {}).get("mean")
        if baseline_mean is not None and intervention_mean is not None:
            diff_mean = baseline_mean - intervention_mean
            lines.append(f"- Final mean stress difference: {diff_mean:.3f} (baseline - intervention)")
        if reduction_pct is not None:
            lines.append(f"- Final mean stress reduction: {reduction_pct:.3f}%")
        lines.append("")
        lines.append("Baseline summary:")
        lines.append("")
        lines.append("| Metric | Mean | SD | 95% CI |")
        lines.append("| --- | ---: | ---: | --- |")
        baseline = agg.get("baseline", {})
        labels = {
            "final_mean_stress": "Final mean stress",
            "final_max_stress": "Final max stress",
            "final_mean_usage": "Final mean usage",
            "burnout_count_day_30": "Day-30 burnout count",
            "peak_burnout_count": "Peak burnout count, includes day 0",
            "total_stress_auc": "Total stress AUC",
        }
        for key in labels:
            if key in baseline:
                lines.append(metric_line(labels[key], baseline[key]))
        lines.append("")

        lines.append("Intervention summary:")
        lines.append("")
        lines.append("| Metric | Mean | SD | 95% CI |")
        lines.append("| --- | ---: | ---: | --- |")
        intervention = agg.get("intervention", {})
        for key in labels:
            if key in intervention:
                lines.append(metric_line(labels[key], intervention[key]))
        lines.append("")

        paired = agg.get("paired_difference", {})
        if paired:
            lines.append("Paired differences, baseline minus intervention:")
            lines.append("")
            lines.append("| Metric | Mean | SD | 95% CI |")
            lines.append("| --- | ---: | ---: | --- |")
            for key in labels:
                if key in paired:
                    lines.append(metric_line(labels[key], paired[key]))
            lines.append("")

        lines.append("Day-30 burnout count distribution by run:")
        lines.append("")
        for scenario in ["Baseline", "Intervention"]:
            vals = run_metrics.loc[run_metrics["scenario"] == scenario, "burnout_count_day_30"]
            lines.append(f"- {scenario}: {value_counts_text(vals)}.")
        lines.append("")

    lines.append("# Version Delta Folder Contents")
    lines.append("")
    for entry in sorted(delta_root.iterdir()):
        if entry.name == "__pycache__":
            continue
        if entry.is_dir():
            lines.append(f"- {entry.name}/: Output directory for a specific network size run.")
            for child in sorted(entry.iterdir()):
                if child.is_file():
                    lines.append(f"- {entry.name}/{child.name}: {describe_result_file(child.name)}")
        else:
            lines.append(f"- {entry.name}: {describe_delta_file(entry.name)}")

    if not any("delta_report.md" in line for line in lines):
        lines.append("- delta_report.md: Generated report of Version Delta results and folder contents.")

    report_path.write_text("\n".join(lines), encoding="utf-8")
    return report_path


def run_delta_for_config(cfg):
    out_dir = DELTA_DIR / f"results_{cfg['n']}"
    out_dir.mkdir(exist_ok=True)

    persona_defs = load_persona_definitions()

    G, actual_mu, seed_used, community_id_by_node = build_lfr_graph(cfg)
    assign_personas_and_attributes(G, community_id_by_node, persona_defs, seed_used)
    compute_node_centrality(G)

    metrics = compute_topology_metrics(G, actual_mu, community_id_by_node, cfg["mu"], 0.05)
    metrics["seed_used"] = seed_used

    nx.write_graphml(G, out_dir / "delta_network.graphml")
    with open(out_dir / "delta_topology_metrics.json", "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)

    targets = select_targets_by_degree(G)
    targets_json = {
        "n_targets": len(targets),
        "target_ids": [int(n) for n in targets],
        "target_degree_centrality": {str(n): float(G.nodes[n]["degree_centrality"]) for n in targets},
    }
    with open(out_dir / "delta_targets.json", "w", encoding="utf-8") as f:
        json.dump(targets_json, f, indent=2)

    all_records = []
    all_metrics = []

    for run_id in range(cfg["n_runs"]):
        seed = 100 + run_id
        baseline_df = simulate(G, SIM_PARAMS, seed, "Baseline")
        baseline_df["run_id"] = run_id
        all_records.append(baseline_df)
        all_metrics.append(compute_run_metrics(baseline_df, SIM_PARAMS["n_days"], run_id, seed, "Baseline"))

        intervention_df = simulate(
            G,
            SIM_PARAMS,
            seed,
            "Intervention",
            intervention_day=SIM_PARAMS["intervention_day"],
            intervention_agents=set(targets),
        )
        intervention_df["run_id"] = run_id
        all_records.append(intervention_df)
        all_metrics.append(compute_run_metrics(intervention_df, SIM_PARAMS["n_days"], run_id, seed, "Intervention"))

    records_df = pd.concat(all_records, ignore_index=True)
    metrics_df = pd.DataFrame(all_metrics)

    records_df.to_csv(out_dir / "delta_simulation_records.csv", index=False)
    metrics_df.to_csv(out_dir / "delta_run_metrics.csv", index=False)

    baseline_metrics = metrics_df[metrics_df["scenario"] == "Baseline"].sort_values("run_id")
    intervention_metrics = metrics_df[metrics_df["scenario"] == "Intervention"].sort_values("run_id")

    paired_diff = baseline_metrics[["run_id"]].copy()
    for col in [
        "final_mean_stress",
        "final_max_stress",
        "final_mean_usage",
        "burnout_count_day_30",
        "peak_burnout_count",
        "peak_stress",
        "total_stress_auc",
    ]:
        paired_diff[col] = baseline_metrics[col].values - intervention_metrics[col].values

    baseline_summary = aggregate_metrics(baseline_metrics)
    intervention_summary = aggregate_metrics(intervention_metrics)
    paired_summary = aggregate_metrics(baseline_metrics, paired_diff)["paired_difference"]

    reduction_pct = None
    if baseline_summary["final_mean_stress"]["mean"] != 0:
        reduction_pct = (
            (baseline_summary["final_mean_stress"]["mean"] - intervention_summary["final_mean_stress"]["mean"])
            / baseline_summary["final_mean_stress"]["mean"]
        ) * 100.0

    aggregated_metrics = {
        "baseline": baseline_summary,
        "intervention": intervention_summary,
        "paired_difference": paired_summary,
        "config": {
            "n_runs": cfg["n_runs"],
            "intervention_day": SIM_PARAMS["intervention_day"],
            "n_targets": len(targets),
            "seed_used": seed_used,
            "final_mean_stress_reduction_pct": None if reduction_pct is None else float(reduction_pct),
        },
    }

    with open(out_dir / "delta_aggregated_metrics.json", "w", encoding="utf-8") as f:
        json.dump(aggregated_metrics, f, indent=2)

    daily_summary = build_daily_summary(records_df)
    daily_summary.to_csv(out_dir / "delta_daily_summary.csv", index=False)

    plot_trajectory(daily_summary, out_dir / "delta_trajectory.png")
    plot_burnout(daily_summary, out_dir / "delta_burnout.png")

    return out_dir


def main():
    results_dirs = []
    for _, cfg in NETWORK_CONFIGS.items():
        results_dirs.append(run_delta_for_config(cfg))
    write_delta_report(DELTA_DIR, results_dirs)


if __name__ == "__main__":
    main()
