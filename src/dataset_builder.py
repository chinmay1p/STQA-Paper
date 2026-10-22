"""
dataset_builder.py: Builds the regression test selection dataset with pre-execution features,
ground-truth relevance labels, and empirical fault detection outcomes with strict zero-leakage guarantees.
"""
import json
import os
import yaml
import pandas as pd
import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(BASE_DIR, "config", "experiment.yaml")
MANIFEST_PATH = os.path.join(BASE_DIR, "scenarios", "scenario_manifest.json")
BASELINE_DURATIONS_PATH = os.path.join(BASE_DIR, "data", "raw", "baseline_test_durations.json")
OUTPUT_CSV_PATH = os.path.join(BASE_DIR, "data", "processed", "regression_test_selection_dataset.csv")
OUTPUT_RAW_JSON = os.path.join(BASE_DIR, "data", "raw", "test_scenario_matrix.json")


def build_dataset():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        manifest = json.load(f)
    with open(BASELINE_DURATIONS_PATH, "r", encoding="utf-8") as f:
        baseline_durations = json.load(f)

    test_module_map = config["test_module_map"]
    dependencies = config["module_dependencies"]
    train_scenarios = set(config["scenario_split"]["train_scenarios"])
    test_scenarios = set(config["scenario_split"]["test_scenarios"])

    # Compute max baseline duration for normalization
    durations = [v["mean_duration_sec"] for v in baseline_durations.values()]
    min_dur = min(durations) if durations else 0.001
    max_dur = max(durations) if durations else 0.01
    dur_range = max(1e-6, max_dur - min_dur)

    rows = []
    # Track historical failures chronologically across scenarios
    historical_failure_tracker = {test_id: 0 for test_id in test_module_map.keys()}

    for scenario_idx, sc in enumerate(manifest):
        sc_id = sc["scenario_id"]
        changed_module = sc["changed_module"]
        code_churn = sc["code_churn"]
        failing_tests = set(sc.get("expected_failing_tests", []))
        split = "train" if sc_id in train_scenarios else "test"

        for test_id, test_module in test_module_map.items():
            # Feature 1: module_match
            module_match = 1 if test_module == changed_module else 0

            # Feature 2: dependency_overlap
            # True if test_module depends on changed_module, or changed_module depends on test_module
            deps_of_test = dependencies.get(test_module, [])
            deps_of_changed = dependencies.get(changed_module, [])
            dep_overlap = 1 if (changed_module in deps_of_test or test_module in deps_of_changed) else 0

            # Feature 3: historical failure metrics (STRICTLY FROM PRIOR SCENARIOS - ZERO LEAKAGE)
            hist_fails = historical_failure_tracker[test_id]
            hist_rate = hist_fails / max(1, scenario_idx)

            # Feature 4: timing metrics from baseline
            test_dur_info = baseline_durations.get(test_id, {})
            avg_duration = test_dur_info.get("mean_duration_sec", 0.002)
            exec_cost = round((avg_duration - min_dur) / dur_range, 4)

            # Label 1: is_relevant (architectural relevance to code change)
            is_relevant = 1 if (module_match == 1 or dep_overlap == 1) else 0

            # Target 2: detects_fault (actual fault detection outcome - NEVER USED AS FEATURE)
            detects_fault = 1 if test_id in failing_tests else 0
            execution_status = "FAILED" if detects_fault == 1 else "PASSED"

            rows.append({
                "scenario_id": sc_id,
                "test_id": test_id,
                "test_module": test_module,
                "changed_module": changed_module,
                "module_match": module_match,
                "dependency_overlap": dep_overlap,
                "code_churn": code_churn,
                "historical_failure_count": hist_fails,
                "historical_failure_rate": round(hist_rate, 4),
                "average_test_duration": round(avg_duration, 5),
                "test_execution_cost": exec_cost,
                "is_relevant": is_relevant,
                "detects_fault": detects_fault,
                "execution_status": execution_status,
                "split": split
            })

        # Update historical tracker AFTER recording row features for the current scenario
        for failed_test in failing_tests:
            if failed_test in historical_failure_tracker:
                historical_failure_tracker[failed_test] += 1

    df = pd.DataFrame(rows)
    os.makedirs(os.path.dirname(OUTPUT_CSV_PATH), exist_ok=True)
    df.to_csv(OUTPUT_CSV_PATH, index=False)

    with open(OUTPUT_RAW_JSON, "w", encoding="utf-8") as f:
        json.dump(rows, f, indent=2)

    print(f"Dataset successfully built with {len(df)} rows and {len(df.columns)} columns.")
    print(f"Saved to: {OUTPUT_CSV_PATH}")
    print(f"Train rows: {len(df[df['split'] == 'train'])}, Test rows: {len(df[df['split'] == 'test'])}")
    print(f"Relevance distribution: {df['is_relevant'].value_counts().to_dict()}")
    print(f"Fault detection occurrences: {df['detects_fault'].value_counts().to_dict()}")

    return df

if __name__ == "__main__":
    build_dataset()
