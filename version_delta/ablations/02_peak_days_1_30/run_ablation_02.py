"""
Ablation 02: Recompute peak metrics for days 1-30.
Uses existing Delta simulation records and writes outputs in this folder only.
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
ABLATION_DIR = Path(__file__).parent

INPUTS = {
    "results_100": ROOT / "version_delta" / "results_100" / "delta_simulation_records.csv",
    "results_1000": ROOT / "version_delta" / "results_1000" / "delta_simulation_records.csv",
}


def compute_peaks(df):
    df = df[df["day"] >= 1].copy()

    def burnout_count(series):
        return (series > 80).sum()

    per_run_day = df.groupby(["scenario", "run_id", "day"]).agg(
        peak_stress_day=("stress", "max"),
        burnout_day=("stress", burnout_count),
    ).reset_index()

    peaks = per_run_day.groupby(["scenario", "run_id"]).agg(
        peak_stress_1_30=("peak_stress_day", "max"),
        peak_burnout_1_30=("burnout_day", "max"),
    ).reset_index()

    peak_stress_day = per_run_day.loc[
        per_run_day.groupby(["scenario", "run_id"])["peak_stress_day"].idxmax(),
        ["scenario", "run_id", "day"],
    ].rename(columns={"day": "day_of_peak_stress_1_30"})

    peak_burnout_day = per_run_day.loc[
        per_run_day.groupby(["scenario", "run_id"])["burnout_day"].idxmax(),
        ["scenario", "run_id", "day"],
    ].rename(columns={"day": "day_of_peak_burnout_1_30"})

    peaks = peaks.merge(peak_stress_day, on=["scenario", "run_id"]).merge(
        peak_burnout_day, on=["scenario", "run_id"]
    )

    return peaks


def summarize(peaks):
    summary = peaks.groupby("scenario").agg(
        peak_stress_1_30_mean=("peak_stress_1_30", "mean"),
        peak_stress_1_30_std=("peak_stress_1_30", "std"),
        peak_burnout_1_30_mean=("peak_burnout_1_30", "mean"),
        peak_burnout_1_30_std=("peak_burnout_1_30", "std"),
    ).reset_index()

    summary["peak_stress_1_30_std"] = summary["peak_stress_1_30_std"].fillna(0.0)
    summary["peak_burnout_1_30_std"] = summary["peak_burnout_1_30_std"].fillna(0.0)

    return summary


def paired_difference(peaks):
    baseline = peaks[peaks["scenario"] == "Baseline"].sort_values("run_id")
    intervention = peaks[peaks["scenario"] == "Intervention"].sort_values("run_id")

    diff = pd.DataFrame({
        "run_id": baseline["run_id"].values,
        "peak_stress_1_30_diff": baseline["peak_stress_1_30"].values - intervention["peak_stress_1_30"].values,
        "peak_burnout_1_30_diff": baseline["peak_burnout_1_30"].values - intervention["peak_burnout_1_30"].values,
        "day_of_peak_stress_1_30_diff": baseline["day_of_peak_stress_1_30"].values - intervention["day_of_peak_stress_1_30"].values,
        "day_of_peak_burnout_1_30_diff": baseline["day_of_peak_burnout_1_30"].values - intervention["day_of_peak_burnout_1_30"].values,
    })

    summary = {
        "peak_stress_1_30_diff_mean": float(diff["peak_stress_1_30_diff"].mean()),
        "peak_stress_1_30_diff_std": float(diff["peak_stress_1_30_diff"].std(ddof=1)) if len(diff) > 1 else 0.0,
        "peak_burnout_1_30_diff_mean": float(diff["peak_burnout_1_30_diff"].mean()),
        "peak_burnout_1_30_diff_std": float(diff["peak_burnout_1_30_diff"].std(ddof=1)) if len(diff) > 1 else 0.0,
        "day_of_peak_stress_1_30_diff_mean": float(diff["day_of_peak_stress_1_30_diff"].mean()),
        "day_of_peak_burnout_1_30_diff_mean": float(diff["day_of_peak_burnout_1_30_diff"].mean()),
    }

    return diff, summary


def run_for_path(label, path):
    df = pd.read_csv(path)
    peaks = compute_peaks(df)
    summary = summarize(peaks)
    diff_df, diff_summary = paired_difference(peaks)

    peaks.to_csv(ABLATION_DIR / f"ablation02_{label}_peaks_by_run.csv", index=False)
    summary.to_csv(ABLATION_DIR / f"ablation02_{label}_summary.csv", index=False)
    diff_df.to_csv(ABLATION_DIR / f"ablation02_{label}_paired_differences.csv", index=False)

    result = {
        "label": label,
        "summary": summary.to_dict(orient="records"),
        "paired_difference_summary": diff_summary,
    }
    return result


def main():
    outputs = []
    for label, path in INPUTS.items():
        outputs.append(run_for_path(label, path))

    with open(ABLATION_DIR / "ablation02_results.json", "w", encoding="utf-8") as f:
        json.dump(outputs, f, indent=2)


if __name__ == "__main__":
    main()
