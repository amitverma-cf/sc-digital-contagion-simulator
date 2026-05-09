"""
Ablation 06: Burnout meaningfulness (metric-only analysis).
Computes severe-stress exposure metrics from existing outputs without rerunning simulations.
"""

import json
import math
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
ABLATION_DIR = Path(__file__).parent

INPUTS = [
    {
        "label": "core_delta",
        "output_base": "core",
        "path": ROOT / "version_delta" / "results_100" / "delta_simulation_records.csv",
    },
    {
        "label": "gamma_005",
        "output_base": "gamma005",
        "path": ROOT / "version_delta" / "ablations" / "04_gamma_005_100" / "ablation04_simulation_records.csv",
    },
]

THRESHOLDS = [70, 75, 80, 85]


def load_records(path):
    df = pd.read_csv(path)
    return df


def compute_consecutive_burnout_count(df, threshold):
    count = 0
    for agent_id, group in df.groupby("agent_id"):
        days = group.loc[group["stress"] > threshold, "day"].sort_values().values
        if len(days) < 2:
            continue
        if np.any(np.diff(days) == 1):
            count += 1
    return count


def compute_metrics_for_run(run_df):
    day30 = run_df[run_df["day"] == 30]
    days_1_30 = run_df[run_df["day"] >= 1]

    metrics = {}
    metrics["day30_burnout_count"] = int((day30["stress"] > 80).sum())
    metrics["peak_burnout_count_days_1_30"] = int(days_1_30.groupby("day")["stress"].apply(lambda x: (x > 80).sum()).max())
    metrics["ever_burnout_count_days_1_30"] = int(days_1_30.loc[days_1_30["stress"] > 80, "agent_id"].nunique())
    metrics["severe_agent_days"] = int((days_1_30["stress"] > 80).sum())
    metrics["persistent_burnout_3day_count"] = int(
        days_1_30.loc[days_1_30["stress"] > 80].groupby("agent_id").size().ge(3).sum()
    )
    metrics["consecutive_burnout_2day_count"] = int(compute_consecutive_burnout_count(days_1_30, 80))
    metrics["severe_stress_burden"] = float((days_1_30.loc[days_1_30["stress"] > 80, "stress"] - 80).sum())
    metrics["day30_p90_stress"] = float(np.percentile(day30["stress"].values, 90))
    metrics["day30_p95_stress"] = float(np.percentile(day30["stress"].values, 95))
    top10 = day30["stress"].nlargest(max(1, int(len(day30) * 0.1)))
    metrics["day30_top10pct_mean_stress"] = float(top10.mean())
    metrics["days_1_30_p95_stress"] = float(np.percentile(days_1_30["stress"].values, 95))
    return metrics


def summarize_metrics(metrics_df):
    summary_rows = []
    for scenario, group in metrics_df.groupby("scenario"):
        row = {"scenario": scenario}
        for col in [c for c in metrics_df.columns if c not in ("run_id", "scenario")]:
            values = group[col].astype(float).values
            mean = float(np.mean(values))
            std = float(np.std(values, ddof=1)) if len(values) > 1 else 0.0
            stderr = float(std / math.sqrt(len(values))) if len(values) > 0 else 0.0
            ci_low = mean - 1.96 * stderr
            ci_high = mean + 1.96 * stderr
            row[f"{col}_mean"] = mean
            row[f"{col}_std"] = std
            row[f"{col}_ci95_low"] = float(ci_low)
            row[f"{col}_ci95_high"] = float(ci_high)
        summary_rows.append(row)
    return pd.DataFrame(summary_rows)


def paired_diff_summary(metrics_df):
    baseline = metrics_df[metrics_df["scenario"] == "Baseline"].sort_values("run_id")
    intervention = metrics_df[metrics_df["scenario"] == "Intervention"].sort_values("run_id")
    diff = pd.DataFrame({"run_id": baseline["run_id"].values})

    for col in [c for c in metrics_df.columns if c not in ("run_id", "scenario")]:
        diff[col] = baseline[col].values - intervention[col].values

    summary = {"metric": [], "mean": [], "std": [], "ci95_low": [], "ci95_high": []}
    for col in [c for c in diff.columns if c != "run_id"]:
        values = diff[col].astype(float).values
        mean = float(np.mean(values))
        std = float(np.std(values, ddof=1)) if len(values) > 1 else 0.0
        stderr = float(std / math.sqrt(len(values))) if len(values) > 0 else 0.0
        ci_low = mean - 1.96 * stderr
        ci_high = mean + 1.96 * stderr
        summary["metric"].append(col)
        summary["mean"].append(mean)
        summary["std"].append(std)
        summary["ci95_low"].append(float(ci_low))
        summary["ci95_high"].append(float(ci_high))

    return diff, pd.DataFrame(summary)


def threshold_metrics(metrics_df, threshold):
    day30 = metrics_df[metrics_df["day"] == 30]
    days_1_30 = metrics_df[metrics_df["day"] >= 1]

    rows = []
    for (scenario, run_id), group in metrics_df.groupby(["scenario", "run_id"]):
        day30_run = day30[(day30["scenario"] == scenario) & (day30["run_id"] == run_id)]
        days_run = days_1_30[(days_1_30["scenario"] == scenario) & (days_1_30["run_id"] == run_id)]

        row = {
            "scenario": scenario,
            "run_id": run_id,
            "threshold": threshold,
            "day30_threshold_count": int((day30_run["stress"] > threshold).sum()),
            "ever_threshold_count_days_1_30": int(days_run.loc[days_run["stress"] > threshold, "agent_id"].nunique()),
            "threshold_agent_days": int((days_run["stress"] > threshold).sum()),
            "threshold_burden": float((days_run.loc[days_run["stress"] > threshold, "stress"] - threshold).sum()),
        }
        rows.append(row)

    return pd.DataFrame(rows)


def should_run_threshold(metrics_df):
    cols = [
        "day30_burnout_count",
        "ever_burnout_count_days_1_30",
        "severe_agent_days",
        "severe_stress_burden",
    ]
    baseline = metrics_df[metrics_df["scenario"] == "Baseline"]
    intervention = metrics_df[metrics_df["scenario"] == "Intervention"]

    for col in cols:
        if baseline[col].mean() > 0 or intervention[col].mean() > 0:
            return False
    return True


def run_dataset(label, output_base, path):
    df = load_records(path)

    metrics_rows = []
    for (scenario, run_id), run_df in df.groupby(["scenario", "run_id"]):
        run_metrics = compute_metrics_for_run(run_df)
        run_metrics["scenario"] = scenario
        run_metrics["run_id"] = run_id
        metrics_rows.append(run_metrics)

    metrics_df = pd.DataFrame(metrics_rows)
    summary_df = summarize_metrics(metrics_df)
    diff_df, diff_summary_df = paired_diff_summary(metrics_df)

    metrics_name = f"ablation06_{output_base}_burnout_metrics.csv"
    summary_name = f"ablation06_{output_base}_summary.csv"
    diff_name = f"ablation06_{output_base}_paired_differences.csv"
    diff_summary_name = f"ablation06_{output_base}_paired_summary.csv"

    metrics_df.to_csv(ABLATION_DIR / metrics_name, index=False)
    summary_df.to_csv(ABLATION_DIR / summary_name, index=False)
    diff_df.to_csv(ABLATION_DIR / diff_name, index=False)
    diff_summary_df.to_csv(ABLATION_DIR / diff_summary_name, index=False)

    threshold_df = None
    threshold_summary = None
    threshold_computed = should_run_threshold(metrics_df)
    if threshold_computed:
        threshold_rows = []
        for threshold in THRESHOLDS:
            threshold_rows.append(threshold_metrics(df, threshold))
        threshold_df = pd.concat(threshold_rows, ignore_index=True)
        threshold_df.to_csv(ABLATION_DIR / f"ablation06_{output_base}_threshold_sensitivity.csv", index=False)
    else:
        threshold_df = pd.DataFrame([
            {
                "dataset": label,
                "threshold": None,
                "computed": False,
                "reason": "threshold-80 metrics are nonzero; sensitivity not required",
            }
        ])
        threshold_df.to_csv(ABLATION_DIR / f"ablation06_{output_base}_threshold_sensitivity.csv", index=False)

    result = {
        "label": label,
        "output_base": output_base,
        "summary": summary_df.to_dict(orient="records"),
        "paired_difference_summary": diff_summary_df.to_dict(orient="records"),
        "threshold_sensitivity": "computed" if threshold_computed else "skipped",
    }

    return result


def main():
    outputs = []
    for item in INPUTS:
        outputs.append(run_dataset(item["label"], item["output_base"], item["path"]))

    with open(ABLATION_DIR / "ablation06_summary.json", "w", encoding="utf-8") as f:
        json.dump(outputs, f, indent=2)

    combined_thresholds = []
    for item in INPUTS:
        per_label = ABLATION_DIR / f"ablation06_{item['output_base']}_threshold_sensitivity.csv"
        if per_label.exists():
            df = pd.read_csv(per_label)
            if "dataset" not in df.columns:
                df.insert(0, "dataset", item["label"])
            combined_thresholds.append(df)

    if combined_thresholds:
        combined_df = pd.concat(combined_thresholds, ignore_index=True)
        combined_df.to_csv(ABLATION_DIR / "ablation06_threshold_sensitivity.csv", index=False)


if __name__ == "__main__":
    main()
