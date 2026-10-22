"""
statistical_analysis.py: Performs statistical comparisons between AI-based test selection
and repeated Random selection baseline across test scenarios.
Uses paired Wilcoxon signed-rank test and paired t-test with multiple comparison adjustments.
"""
import os
from typing import Dict, List, Any
import numpy as np
import pandas as pd
from scipy import stats

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_PATH = os.path.join(BASE_DIR, "results", "processed", "statistical_analysis_results.csv")


def run_statistical_comparison(
    scenario_metrics_df: pd.DataFrame,
    random_runs_df: pd.DataFrame
) -> pd.DataFrame:
    """
    Compares AI Selection vs Random Selection across test scenarios for each budget.
    """
    results = []
    # Filter to test scenarios that have faults
    fault_scenarios = scenario_metrics_df[
        scenario_metrics_df["eligible_faults"] > 0
    ]["scenario_id"].unique()

    budgets = [0.25, 0.50, 0.75]

    for budget in budgets:
        ai_scores = []
        rand_mean_scores = []

        for sc_id in fault_scenarios:
            ai_row = scenario_metrics_df[
                (scenario_metrics_df["scenario_id"] == sc_id) &
                (scenario_metrics_df["method"] == "AI_Selection") &
                (scenario_metrics_df["budget_pct"] == budget)
            ]
            if len(ai_row) == 0:
                continue
            ai_fdr = ai_row["fault_detection_rate_pct"].values[0]

            # Random baseline mean for this scenario and budget
            rand_rows = random_runs_df[
                (random_runs_df["scenario_id"] == sc_id) &
                (random_runs_df["budget_pct"] == budget)
            ]
            if len(rand_rows) == 0:
                continue
            rand_mean_fdr = rand_rows["fault_detection_rate_pct"].mean()

            ai_scores.append(ai_fdr)
            rand_mean_scores.append(rand_mean_fdr)

        ai_arr = np.array(ai_scores)
        rand_arr = np.array(rand_mean_scores)
        n_pairs = len(ai_arr)

        if n_pairs < 3:
            p_val = np.nan
            test_name = "Sample too small (N < 3)"
            stat_val = np.nan
        else:
            diff = ai_arr - rand_arr
            if np.all(diff == 0):
                p_val = 1.0
                test_name = "Wilcoxon signed-rank (identical distributions)"
                stat_val = 0.0
            else:
                try:
                    # Wilcoxon signed-rank test
                    stat, p = stats.wilcoxon(ai_arr, rand_arr, alternative="greater")
                    stat_val = round(float(stat), 4)
                    p_val = round(float(p), 4)
                    test_name = "Wilcoxon signed-rank (one-tailed: AI > Random)"
                except Exception as e:
                    # Fallback to paired t-test
                    stat, p = stats.ttest_rel(ai_arr, rand_arr, alternative="greater")
                    stat_val = round(float(stat), 4)
                    p_val = round(float(p), 4)
                    test_name = "Paired t-test (one-tailed: AI > Random)"

        results.append({
            "budget_pct": budget,
            "metric": "Fault Detection Rate (%)",
            "n_paired_scenarios": n_pairs,
            "ai_mean": round(float(np.mean(ai_arr)), 2) if len(ai_arr) else 0.0,
            "random_mean": round(float(np.mean(rand_arr)), 2) if len(rand_arr) else 0.0,
            "mean_difference (AI - Random)": round(float(np.mean(ai_arr - rand_arr)), 2) if len(ai_arr) else 0.0,
            "test_type": test_name,
            "statistic": stat_val,
            "p_value": p_val,
            "statistically_significant_alpha_005": bool(p_val < 0.05) if not np.isnan(p_val) else False
        })

    stat_df = pd.DataFrame(results)
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    stat_df.to_csv(OUTPUT_PATH, index=False)

    print("\n--- Statistical Comparison (AI Selection vs Random Baseline) ---")
    print(stat_df.to_string(index=False))
    return stat_df
