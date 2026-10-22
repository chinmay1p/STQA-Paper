"""
metrics.py: Implements standard research metrics for Regression Test Selection:
- Test Reduction (%)
- Execution Time Saving (%)
- Total Workflow Time Saving (%) including selection overhead
- Fault Detection Effectiveness (%)
- Per-scenario and aggregate summary statistics
"""
from typing import Dict, List, Any
import numpy as np
import pandas as pd


def compute_test_reduction(n_full: int, n_selected: int) -> float:
    """Computes test suite reduction percentage."""
    if n_full <= 0:
        return 0.0
    return round(100.0 * (n_full - n_selected) / n_full, 2)


def compute_time_saving(t_full: float, t_selected: float) -> float:
    """Computes execution time saving percentage."""
    if t_full <= 0:
        return 0.0
    saving = 100.0 * (t_full - t_selected) / t_full
    return round(saving, 2)


def compute_fault_detection_rate(
    detected_faults_selected: int,
    detected_faults_full: int
) -> float:
    """
    Computes fault detection rate relative to full suite.
    If full suite detected 0 faults (clean scenario), returns NaN or None.
    """
    if detected_faults_full <= 0:
        return np.nan
    rate = 100.0 * (detected_faults_selected / detected_faults_full)
    return round(rate, 2)


def aggregate_scenario_metrics(scenario_df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregates scenario metrics across all evaluated test scenarios.
    Computes mean and standard deviation for each method and budget.
    """
    summary = []
    grouped = scenario_df.groupby(["method", "budget_pct"])

    for (method, budget_pct), group in grouped:
        n_selected_mean = group["n_selected"].mean()
        reduction_mean = group["test_reduction_pct"].mean()
        exec_time_mean = group["execution_time_sec"].mean()
        overhead_mean = group["selection_overhead_sec"].mean()
        total_time_mean = group["total_workflow_time_sec"].mean()
        time_saving_mean = group["execution_time_saving_pct"].mean()
        total_time_saving_mean = group["total_time_saving_pct"].mean()

        # Fault detection effectiveness on fault-bearing scenarios only
        fault_bearing = group.dropna(subset=["fault_detection_rate_pct"])
        if len(fault_bearing) > 0:
            fdr_mean = fault_bearing["fault_detection_rate_pct"].mean()
            fdr_std = fault_bearing["fault_detection_rate_pct"].std()
            total_faults_detected = fault_bearing["faults_detected"].sum()
            total_eligible_faults = fault_bearing["eligible_faults"].sum()
            aggregate_fdr = 100.0 * (total_faults_detected / total_eligible_faults) if total_eligible_faults > 0 else 100.0
        else:
            fdr_mean = np.nan
            fdr_std = np.nan
            total_faults_detected = 0
            total_eligible_faults = 0
            aggregate_fdr = np.nan

        summary.append({
            "method": method,
            "budget_pct": budget_pct,
            "mean_tests_selected": round(n_selected_mean, 1),
            "mean_test_reduction_pct": round(reduction_mean, 2),
            "mean_execution_time_sec": round(exec_time_mean, 4),
            "mean_selection_overhead_sec": round(overhead_mean, 6),
            "mean_total_workflow_time_sec": round(total_time_mean, 4),
            "mean_time_saving_pct": round(time_saving_mean, 2),
            "mean_total_time_saving_pct": round(total_time_saving_mean, 2),
            "mean_fault_detection_rate_pct": round(fdr_mean, 2) if not np.isnan(fdr_mean) else 100.0,
            "fault_detection_rate_std": round(fdr_std, 2) if not np.isnan(fdr_std) else 0.0,
            "total_faults_detected": int(total_faults_detected),
            "total_eligible_faults": int(total_eligible_faults),
            "aggregate_fault_detection_pct": round(aggregate_fdr, 2) if not np.isnan(aggregate_fdr) else 100.0
        })

    return pd.DataFrame(summary)
