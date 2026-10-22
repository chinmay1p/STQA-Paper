"""
run_experiment.py: Single entry point to run the AI Regression Test Selection experiment.
Usage:
    python run_experiment.py
"""
import os
import sys
import shutil

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.experiment_runner import execute_full_experiment

if __name__ == "__main__":
    execute_full_experiment()
    # Copy dataset and main results for easy access
    shutil.copy2(
        os.path.join(BASE_DIR, "data", "processed", "regression_test_selection_dataset.csv"),
        os.path.join(BASE_DIR, "data", "dataset.csv")
    )
    shutil.copy2(
        os.path.join(BASE_DIR, "results", "tables", "main_comparison_table.csv"),
        os.path.join(BASE_DIR, "results", "results.csv")
    )
    print("\n" + "=" * 60)
    print("DONE! Your simplified outputs are ready:")
    print("  - Dataset:  data/dataset.csv")
    print("  - Results:  results/results.csv")
    print("  - Figures:  results/figures/")
    print("  - Report:   REPORT.md")
    print("=" * 60)
