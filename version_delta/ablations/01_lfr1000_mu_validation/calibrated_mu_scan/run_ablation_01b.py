"""
Ablation 01B: calibrated 1000-node LFR mu scan
Scans configured mu values to reach measured mixing near 0.10.
Runs simulations only if a valid graph is found.
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

ROOT = Path(__file__).resolve().parents[4]
ABLATION_DIR = Path(__file__).parent
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

LFR_BASE = {
    "n": 1000,
    "tau1": 3.0,
    "tau2": 1.5,
    "average_degree": 10,
    "min_community": 20,
    "max_community": 100,
    "seed_start": 42,
}

MU_VALUES = [0.065, 0.07, 0.075, 0.08, 0.085, 0.09]
MU_TARGET = 0.10
MU_TOLERANCE = 0.05
SEEDS_PER_MU = 10
N_RUNS = 10


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


def build_lfr_graph(mu_value, seed):
    G = nx.LFR_benchmark_graph(
        n=LFR_BASE["n"],
        tau1=LFR_BASE["tau1"],
        tau2=LFR_BASE["tau2"],
        mu=mu_value,
        average_degree=LFR_BASE["average_degree"],
        min_community=LFR_BASE["min_community"],
        max_community=LFR_BASE["max_community"],
        max_iters=5000,
        seed=seed,
    )
    G.remove_edges_from(list(nx.selfloop_edges(G)))

    communities = {frozenset(G.nodes[n]["community"]) for n in G.nodes()}
    comm_list = sorted(list(communities), key=len, reverse=True)
    comm_id_map = {comm: idx for idx, comm in enumerate(comm_list)}
    community_id_by_node = {n: comm_id_map[frozenset(G.nodes[n]["community"])] for n in G.nodes()}

    actual_mu = compute_mixing_parameter(G, community_id_by_node)
    return G, actual_mu, community_id_by_node


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


def compute_topology_metrics(G, actual_mu, community_id_by_node, configured_mu):
    degrees = [deg for _, deg in G.degree()]
    community_sizes = {}
    for node, cid in community_id_by_node.items():
        community_sizes[cid] = community_sizes.get(cid, 0) + 1

    persona_assort = nx.attribute_assortativity_coefficient(G, "persona") if G.number_of_nodes() > 1 else 0.0

    metrics = {
        "n_nodes": G.number_of_nodes(),
        "n_edges": G.number_of_edges(),
        "mean_degree": float(np.mean(degrees)) if degrees else 0.0,
        "clustering_coefficient": float(nx.average_clustering(G)) if G.number_of_nodes() > 1 else 0.0,
        "connected_components": int(nx.number_connected_components(G)),
        "n_communities": int(len(community_sizes)),
        "community_size_distribution": [int(sz) for sz in sorted(community_sizes.values(), reverse=True)],
        "actual_mixing_parameter": float(actual_mu),
        "configured_mu": float(configured_mu),
        "target_mixing_parameter": float(MU_TARGET),
        "mixing_parameter_distance": float(abs(actual_mu - MU_TARGET)),
        "mixing_tolerance": float(MU_TOLERANCE),
        "mixing_tolerance_met": bool(abs(actual_mu - MU_TARGET) <= MU_TOLERANCE),
        "persona_assortativity": float(persona_assort),
    }
    return metrics


def select_targets_by_degree(G):
    n_targets = max(5, int(0.05 * G.number_of_nodes()))
    sorted_nodes = sorted(G.nodes(), key=lambda n: G.nodes[n]["degree_centrality"], reverse=True)
    return sorted_nodes[:n_targets]


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
    plt.title("Ablation 01B: Stress Trajectory (Mean ± SD)")
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
    plt.title("Ablation 01B: Burnout Count (Mean ± SD)")
    plt.xlabel("Day")
    plt.ylabel("Burnout Count (Stress > 80)")
    plt.legend()
    plt.grid(True, alpha=0.1)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()


def main():
    persona_defs = load_persona_definitions()

    candidate_rows = []
    accepted = None

    for mu_value in MU_VALUES:
        for i in range(SEEDS_PER_MU):
            seed = LFR_BASE["seed_start"] + i
            try:
                G, actual_mu, community_id_by_node = build_lfr_graph(mu_value, seed)
            except nx.ExceededMaxIterations:
                candidate_rows.append({
                    "configured_mu": mu_value,
                    "seed": seed,
                    "status": "failed",
                    "actual_mu": None,
                    "mean_degree": None,
                    "n_edges": None,
                    "connected_components": None,
                    "n_communities": None,
                    "clustering_coefficient": None,
                })
                continue

            metrics = compute_topology_metrics(G, actual_mu, community_id_by_node, mu_value)
            candidate_rows.append({
                "configured_mu": mu_value,
                "seed": seed,
                "status": "accepted" if metrics["mixing_tolerance_met"] else "rejected",
                "actual_mu": metrics["actual_mixing_parameter"],
                "mean_degree": metrics["mean_degree"],
                "n_edges": metrics["n_edges"],
                "connected_components": metrics["connected_components"],
                "n_communities": metrics["n_communities"],
                "clustering_coefficient": metrics["clustering_coefficient"],
            })

            if metrics["mixing_tolerance_met"]:
                accepted = (G, metrics, community_id_by_node, seed, mu_value)
                break
        if accepted is not None:
            break

    candidates_df = pd.DataFrame(candidate_rows)
    candidates_df.to_csv(ABLATION_DIR / "ablation01b_candidates.csv", index=False)

    if accepted is None:
        return

    G, topo_metrics, community_id_by_node, seed_used, configured_mu = accepted

    assign_personas_and_attributes(G, community_id_by_node, persona_defs, seed_used)
    compute_node_centrality(G)

    topo_metrics["seed_used"] = seed_used
    topo_metrics["configured_mu"] = configured_mu

    nx.write_graphml(G, ABLATION_DIR / "ablation01b_network.graphml")
    with open(ABLATION_DIR / "ablation01b_topology_metrics.json", "w", encoding="utf-8") as f:
        json.dump(topo_metrics, f, indent=2)

    targets = select_targets_by_degree(G)
    targets_json = {
        "n_targets": len(targets),
        "target_ids": [int(n) for n in targets],
        "target_degree_centrality": {str(n): float(G.nodes[n]["degree_centrality"]) for n in targets},
    }
    with open(ABLATION_DIR / "ablation01b_targets.json", "w", encoding="utf-8") as f:
        json.dump(targets_json, f, indent=2)

    all_records = []
    all_metrics = []

    for run_id in range(N_RUNS):
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

    records_df.to_csv(ABLATION_DIR / "ablation01b_simulation_records.csv", index=False)
    metrics_df.to_csv(ABLATION_DIR / "ablation01b_run_metrics.csv", index=False)

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
            "n_runs": N_RUNS,
            "intervention_day": SIM_PARAMS["intervention_day"],
            "n_targets": len(targets),
            "seed_used": seed_used,
            "configured_mu": float(configured_mu),
            "target_mixing_parameter": float(MU_TARGET),
            "final_mean_stress_reduction_pct": None if reduction_pct is None else float(reduction_pct),
        },
    }

    with open(ABLATION_DIR / "ablation01b_aggregated_metrics.json", "w", encoding="utf-8") as f:
        json.dump(aggregated_metrics, f, indent=2)

    daily_summary = build_daily_summary(records_df)
    daily_summary.to_csv(ABLATION_DIR / "ablation01b_daily_summary.csv", index=False)

    plot_trajectory(daily_summary, ABLATION_DIR / "ablation01b_trajectory.png")
    plot_burnout(daily_summary, ABLATION_DIR / "ablation01b_burnout.png")


if __name__ == "__main__":
    main()
