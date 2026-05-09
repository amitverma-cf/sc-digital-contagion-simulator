"""
Ablation 04: Gamma 0.05 on 100-node network.
Uses existing Delta topology and target list; changes only gamma.
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

ROOT = Path(__file__).resolve().parents[3]
ABLATION_DIR = Path(__file__).parent

INPUT_GRAPH = ROOT / "version_delta" / "results_100" / "delta_network.graphml"
INPUT_TARGETS = ROOT / "version_delta" / "results_100" / "delta_targets.json"

SIM_PARAMS = {
    "n_days": 30,
    "alpha": 0.6,
    "beta": 0.3,
    "gamma": 0.05,
    "delta": 0.02,
    "stress_cap": 100.0,
    "usage_min": 30.0,
    "usage_cap": 600.0,
    "intervention_day": 10,
    "intervention_factor": 0.5,
    "peer_reduction": 0.3,
}

N_RUNS = 30


def load_graph():
    G = nx.read_graphml(INPUT_GRAPH)
    mapping = {node: int(node) for node in G.nodes()}
    G = nx.relabel_nodes(G, mapping)

    for node in G.nodes():
        for key in [
            "base_stress",
            "app_usage",
            "variability",
            "susceptibility",
            "resilience",
        ]:
            if key in G.nodes[node]:
                G.nodes[node][key] = float(G.nodes[node][key])
    return G


def load_targets():
    with open(INPUT_TARGETS, "r", encoding="utf-8") as f:
        data = json.load(f)
    return set(int(x) for x in data["target_ids"]), data


def simulate(G, params, seed, scenario, intervention_day=None, intervention_agents=None):
    rng = np.random.default_rng(seed)
    if intervention_agents is None:
        intervention_agents = set()

    node_ids = list(G.nodes())
    stress = {n: float(G.nodes[n]["base_stress"]) for n in node_ids}
    usage = {n: float(G.nodes[n]["app_usage"]) for n in node_ids}

    records = []

    for day in range(params["n_days"] + 1):
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

            records.append({
                "agent_id": int(n),
                "day": int(day),
                "stress": float(stress[n]),
                "usage": float(usage[n]),
                "peer_influence": float(peer_stress),
                "persona": G.nodes[n].get("persona", "Unknown"),
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

        if day < params["n_days"]:
            stress = new_stress
            usage = new_usage

    return pd.DataFrame(records)


def compute_run_metrics(df, n_days, run_id, seed, scenario):
    day_final = df[df["day"] == n_days]
    daily_burnout = df.groupby("day")["stress"].apply(lambda x: (x > 80).sum())
    daily_burnout_1_30 = df[df["day"] >= 1].groupby("day")["stress"].apply(lambda x: (x > 80).sum())

    metrics = {
        "run_id": int(run_id),
        "seed": int(seed),
        "scenario": scenario,
        "final_mean_stress": float(day_final["stress"].mean()),
        "final_max_stress": float(day_final["stress"].max()),
        "final_mean_usage": float(day_final["usage"].mean()),
        "burnout_count_day_30": int((day_final["stress"] > 80).sum()),
        "peak_burnout_count": int(daily_burnout.max()),
        "peak_burnout_count_1_30": int(daily_burnout_1_30.max()),
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
        "peak_burnout_count_1_30",
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
    plt.title("Ablation 04: Stress Trajectory (Mean ± SD)")
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
    plt.title("Ablation 04: Burnout Count (Mean ± SD)")
    plt.xlabel("Day")
    plt.ylabel("Burnout Count (Stress > 80)")
    plt.legend()
    plt.grid(True, alpha=0.1)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()


def main():
    G = load_graph()
    targets, target_meta = load_targets()

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
            intervention_agents=targets,
        )
        intervention_df["run_id"] = run_id
        all_records.append(intervention_df)
        all_metrics.append(compute_run_metrics(intervention_df, SIM_PARAMS["n_days"], run_id, seed, "Intervention"))

    records_df = pd.concat(all_records, ignore_index=True)
    metrics_df = pd.DataFrame(all_metrics)

    records_df.to_csv(ABLATION_DIR / "ablation04_simulation_records.csv", index=False)
    metrics_df.to_csv(ABLATION_DIR / "ablation04_run_metrics.csv", index=False)

    baseline_metrics = metrics_df[metrics_df["scenario"] == "Baseline"].sort_values("run_id")
    intervention_metrics = metrics_df[metrics_df["scenario"] == "Intervention"].sort_values("run_id")

    paired_diff = baseline_metrics[["run_id"]].copy()
    for col in [
        "final_mean_stress",
        "final_max_stress",
        "final_mean_usage",
        "burnout_count_day_30",
        "peak_burnout_count_1_30",
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
            "gamma": SIM_PARAMS["gamma"],
            "target_ids": sorted(list(targets)),
            "final_mean_stress_reduction_pct": None if reduction_pct is None else float(reduction_pct),
        },
    }

    with open(ABLATION_DIR / "ablation04_aggregated_metrics.json", "w", encoding="utf-8") as f:
        json.dump(aggregated_metrics, f, indent=2)

    with open(ABLATION_DIR / "ablation04_targets.json", "w", encoding="utf-8") as f:
        json.dump(target_meta, f, indent=2)

    daily_summary = build_daily_summary(records_df)
    daily_summary.to_csv(ABLATION_DIR / "ablation04_daily_summary.csv", index=False)

    plot_trajectory(daily_summary, ABLATION_DIR / "ablation04_trajectory.png")
    plot_burnout(daily_summary, ABLATION_DIR / "ablation04_burnout.png")


if __name__ == "__main__":
    main()
