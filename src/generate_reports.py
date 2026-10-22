"""
generate_reports.py: Generates publication-quality 300 DPI figures and academic tables (CSV and Markdown)
from actual experimental result records.
"""
import os
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIGURES_DIR = os.path.join(BASE_DIR, "results", "figures")
TABLES_DIR = os.path.join(BASE_DIR, "results", "tables")
PROCESSED_DIR = os.path.join(BASE_DIR, "results", "processed")

# Style configurations for academic figures
plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
plt.rcParams.update({
    "font.size": 11,
    "axes.labelsize": 12,
    "axes.titlesize": 13,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
    "legend.fontsize": 10,
    "figure.titlesize": 14,
    "font.family": "sans-serif"
})


def df_to_markdown_file(df: pd.DataFrame, filepath: str, title: str = ""):
    """Writes a DataFrame to a clean markdown table file."""
    with open(filepath, "w", encoding="utf-8") as f:
        if title:
            f.write(f"### {title}\n\n")
        f.write(df.to_markdown(index=False))
        f.write("\n")


def generate_all_figures_and_tables():
    os.makedirs(FIGURES_DIR, exist_ok=True)
    os.makedirs(TABLES_DIR, exist_ok=True)

    # Load computed metrics
    agg_df = pd.read_csv(os.path.join(PROCESSED_DIR, "aggregate_metrics.csv"))
    scen_df = pd.read_csv(os.path.join(PROCESSED_DIR, "scenario_metrics.csv"))
    rand_df = pd.read_csv(os.path.join(PROCESSED_DIR, "random_baseline_summary.csv"))
    model_df = pd.read_csv(os.path.join(PROCESSED_DIR, "model_metrics.csv"))
    fi_df = pd.read_csv(os.path.join(PROCESSED_DIR, "feature_importance.csv"))

    # -------------------------------------------------------------
    # Figure 1: Test Reduction Comparison
    # -------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(8, 5))
    plot_methods = [
        ("Full Suite", 1.0, "Full_Suite"),
        ("Change-Based", 1.0, "Change_Based"),
        ("Random (25%)", 0.25, "Random_Selection"),
        ("Random (50%)", 0.50, "Random_Selection"),
        ("Random (75%)", 0.75, "Random_Selection"),
        ("AI (25%)", 0.25, "AI_Selection"),
        ("AI (50%)", 0.50, "AI_Selection"),
        ("AI (75%)", 0.75, "AI_Selection"),
        ("AI (100%)", 1.00, "AI_Selection")
    ]

    labels = []
    reductions = []
    colors = []

    for label, budget, m_key in plot_methods:
        row = agg_df[(agg_df["method"] == m_key) & (agg_df["budget_pct"] == budget)]
        if len(row) > 0:
            labels.append(label)
            reductions.append(row["mean_test_reduction_pct"].values[0])
            if "AI" in label:
                colors.append("#1f77b4")  # Deep blue
            elif "Change" in label:
                colors.append("#2ca02c")  # Green
            elif "Random" in label:
                colors.append("#ff7f0e")  # Orange
            else:
                colors.append("#7f7f7f")  # Gray

    bars = ax.bar(labels, reductions, color=colors, edgecolor="black", linewidth=0.8, width=0.6)
    ax.set_ylabel("Test Reduction (%)")
    ax.set_title("Test Suite Reduction Across Selection Approaches")
    ax.set_ylim(0, 100)
    plt.xticks(rotation=35, ha="right")

    for bar in bars:
        h = bar.get_height()
        ax.annotate(f"{h:.1f}%",
                    xy=(bar.get_x() + bar.get_width() / 2, h),
                    xytext=(0, 3), textcoords="offset points",
                    ha="center", va="bottom", fontsize=9, fontweight="bold")

    plt.tight_layout()
    fig1_path = os.path.join(FIGURES_DIR, "test_reduction_comparison.png")
    plt.savefig(fig1_path, dpi=300)
    plt.close()

    # -------------------------------------------------------------
    # Figure 2: Execution Time and Total Workflow Time Comparison
    # -------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(9, 5))
    x = np.arange(len(labels))
    width = 0.35

    exec_times = []
    total_times = []
    for label, budget, m_key in plot_methods:
        row = agg_df[(agg_df["method"] == m_key) & (agg_df["budget_pct"] == budget)]
        if len(row) > 0:
            exec_times.append(row["mean_execution_time_sec"].values[0] * 1000)  # ms
            total_times.append(row["mean_total_workflow_time_sec"].values[0] * 1000)  # ms

    b1 = ax.bar(x - width/2, exec_times, width, label="Test Execution Time", color="#4575b4", edgecolor="black")
    b2 = ax.bar(x + width/2, total_times, width, label="Total Workflow Time (with overhead)", color="#d73027", edgecolor="black")

    ax.set_ylabel("Time (milliseconds)")
    ax.set_title("Execution Time and Total Workflow Time Comparison")
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=35, ha="right")
    ax.legend(frameon=True)
    plt.tight_layout()
    fig2_path = os.path.join(FIGURES_DIR, "execution_time_comparison.png")
    plt.savefig(fig2_path, dpi=300)
    plt.close()

    # -------------------------------------------------------------
    # Figure 3: Fault Detection Effectiveness Comparison
    # -------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(8, 5))
    fd_rates = []
    for label, budget, m_key in plot_methods:
        row = agg_df[(agg_df["method"] == m_key) & (agg_df["budget_pct"] == budget)]
        if len(row) > 0:
            fd_rates.append(row["mean_fault_detection_rate_pct"].values[0])

    bars = ax.bar(labels, fd_rates, color=colors, edgecolor="black", linewidth=0.8, width=0.6)
    ax.set_ylabel("Fault Detection Rate (%)")
    ax.set_title("Fault Detection Effectiveness Across Approaches (Test Scenarios)")
    ax.set_ylim(0, 115)
    plt.xticks(rotation=35, ha="right")

    for bar in bars:
        h = bar.get_height()
        ax.annotate(f"{h:.1f}%",
                    xy=(bar.get_x() + bar.get_width() / 2, h),
                    xytext=(0, 3), textcoords="offset points",
                    ha="center", va="bottom", fontsize=9, fontweight="bold")

    plt.tight_layout()
    fig3_path = os.path.join(FIGURES_DIR, "fault_detection_comparison.png")
    plt.savefig(fig3_path, dpi=300)
    plt.close()

    # -------------------------------------------------------------
    # Figure 4: Budget vs Fault Detection (Line plot)
    # -------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(7, 5))
    budgets_line = [0.25, 0.50, 0.75, 1.00]
    ai_fd = []
    rand_fd = []

    for b in budgets_line:
        ai_row = agg_df[(agg_df["method"] == "AI_Selection") & (agg_df["budget_pct"] == b)]
        ai_fd.append(ai_row["mean_fault_detection_rate_pct"].values[0] if len(ai_row) else 100.0)

        rand_row = agg_df[(agg_df["method"] == "Random_Selection") & (agg_df["budget_pct"] == b)]
        rand_fd.append(rand_row["mean_fault_detection_rate_pct"].values[0] if len(rand_row) else 100.0)

    budget_labels = ["25% (8 tests)", "50% (15 tests)", "75% (23 tests)", "100% (30 tests)"]
    ax.plot(budget_labels, ai_fd, marker="o", linewidth=2.5, color="#1f77b4", label="AI-Based Selection (Random Forest)")
    ax.plot(budget_labels, rand_fd, marker="s", linewidth=2.5, linestyle="--", color="#ff7f0e", label="Random Selection Baseline")

    ax.set_xlabel("Selection Budget")
    ax.set_ylabel("Fault Detection Rate (%)")
    ax.set_title("Selection Budget vs. Fault Detection Effectiveness")
    ax.set_ylim(0, 110)
    ax.legend(frameon=True, loc="lower right")
    plt.tight_layout()
    fig4_path = os.path.join(FIGURES_DIR, "budget_vs_fault_detection.png")
    plt.savefig(fig4_path, dpi=300)
    plt.close()

    # -------------------------------------------------------------
    # Figure 5: Random vs AI (with error bars)
    # -------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(7.5, 5))
    comp_budgets = [0.25, 0.50, 0.75]
    comp_labels = ["Budget 25%", "Budget 50%", "Budget 75%"]
    x = np.arange(len(comp_budgets))
    w = 0.35

    ai_vals = []
    rand_vals = []
    rand_errs = []

    for b in comp_budgets:
        ai_r = agg_df[(agg_df["method"] == "AI_Selection") & (agg_df["budget_pct"] == b)]
        ai_vals.append(ai_r["mean_fault_detection_rate_pct"].values[0])

        rand_r = agg_df[(agg_df["method"] == "Random_Selection") & (agg_df["budget_pct"] == b)]
        rand_vals.append(rand_r["mean_fault_detection_rate_pct"].values[0])
        rand_errs.append(rand_r["fault_detection_rate_std"].values[0])

    ax.bar(x - w/2, ai_vals, w, label="AI Selection", color="#1f77b4", edgecolor="black")
    ax.bar(x + w/2, rand_vals, w, yerr=rand_errs, capsize=5, label="Random (20 seeds, mean ± std)", color="#ff7f0e", edgecolor="black")

    ax.set_ylabel("Fault Detection Rate (%)")
    ax.set_title("AI Selection vs. Random Baseline (20 Repetitions)")
    ax.set_xticks(x)
    ax.set_xticklabels(comp_labels)
    ax.set_ylim(0, 115)
    ax.legend(frameon=True, loc="lower right")
    plt.tight_layout()
    fig5_path = os.path.join(FIGURES_DIR, "random_vs_ai.png")
    plt.savefig(fig5_path, dpi=300)
    plt.close()

    # -------------------------------------------------------------
    # Figure 6: Feature Importance Bar Chart
    # -------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(8, 4.5))
    sorted_fi = fi_df.sort_values(by="importance", ascending=True)
    y_pos = np.arange(len(sorted_fi))

    bars = ax.barh(y_pos, sorted_fi["importance"], color="#3182bd", edgecolor="black", height=0.6)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(sorted_fi["feature"])
    ax.set_xlabel("Gini Feature Importance")
    ax.set_title("Random Forest Feature Importance for Test Relevance")

    for bar in bars:
        w = bar.get_width()
        ax.annotate(f"{w:.4f}",
                    xy=(w, bar.get_y() + bar.get_height() / 2),
                    xytext=(5, 0), textcoords="offset points",
                    ha="left", va="center", fontsize=9)

    plt.tight_layout()
    fig6_path = os.path.join(FIGURES_DIR, "feature_importance.png")
    plt.savefig(fig6_path, dpi=300)
    plt.close()

    print("All 6 publication figures generated successfully at 300 DPI.")

    # -------------------------------------------------------------
    # Tables for the Paper
    # -------------------------------------------------------------

    # Table 1: Dataset & Test Suite Characteristics
    manifest = json.load(open(os.path.join(BASE_DIR, "scenarios", "scenario_manifest.json")))
    t1_data = [
        {"Characteristic": "Target Application", "Value": "sample_app (E-Commerce Logic)"},
        {"Characteristic": "Application Modules", "Value": "6 (discount, tax, auth, cart, orders, payment)"},
        {"Characteristic": "Total Regression Tests", "Value": "30 unit test cases (5 per module)"},
        {"Characteristic": "Total Change Scenarios", "Value": "16 controlled real-execution scenarios"},
        {"Characteristic": "Training Scenarios", "Value": "10 scenarios (SC-01 to SC-10)"},
        {"Characteristic": "Evaluation Test Scenarios", "Value": "6 held-out scenarios (SC-11 to SC-16)"},
        {"Characteristic": "Total Seeded Faults", "Value": "11 faults (6 in train, 5 in test)"},
        {"Characteristic": "Clean / Non-Faulty Scenarios", "Value": "5 scenarios (4 in train, 1 in test)"},
        {"Characteristic": "Total Matrix Records", "Value": "480 pairs (16 scenarios × 30 tests)"},
        {"Characteristic": "Train Dataset Records", "Value": "300 rows"},
        {"Characteristic": "Held-Out Test Records", "Value": "180 rows"},
    ]
    t1_df = pd.DataFrame(t1_data)
    t1_df.to_csv(os.path.join(TABLES_DIR, "dataset_characteristics.csv"), index=False)
    df_to_markdown_file(t1_df, os.path.join(TABLES_DIR, "dataset_characteristics.md"), "Table 1: Target Application and Dataset Characteristics")

    # Table 2: Experimental Environment
    import platform, sys, sklearn, pytest
    t2_data = [
        {"Item": "Operating System", "Specification": f"{platform.system()} {platform.release()} ({platform.version()})"},
        {"Item": "Python Runtime", "Specification": f"Python {platform.python_version()} (64-bit)"},
        {"Item": "Test Runner", "Specification": f"pytest {pytest.__version__}"},
        {"Item": "Machine Learning Library", "Specification": f"scikit-learn {sklearn.__version__}"},
        {"Item": "Data Handling", "Specification": f"pandas {pd.__version__}, numpy {np.__version__}"},
        {"Item": "Random Seed", "Specification": "42 (deterministic across all modules)"},
        {"Item": "Random Baseline Repetitions", "Specification": "20 iterations per scenario and budget"},
        {"Item": "Data Leakage Safeguard", "Specification": "Grouped scenario split; prior-only historical failure tracking"},
    ]
    t2_df = pd.DataFrame(t2_data)
    t2_df.to_csv(os.path.join(TABLES_DIR, "experimental_environment.csv"), index=False)
    df_to_markdown_file(t2_df, os.path.join(TABLES_DIR, "experimental_environment.md"), "Table 2: Experimental Environment and Configuration")

    # Table 3: Main Comparison Table across all Selection Methods
    main_rows = []
    for label, budget, m_key in plot_methods:
        row = agg_df[(agg_df["method"] == m_key) & (agg_df["budget_pct"] == budget)]
        if len(row) > 0:
            r = row.iloc[0]
            main_rows.append({
                "Selection Method": label,
                "Budget": f"{int(budget*100)}%",
                "Tests Selected": f"{r['mean_tests_selected']:.1f}",
                "Test Reduction (%)": f"{r['mean_test_reduction_pct']:.1f}%",
                "Execution Time (ms)": f"{r['mean_execution_time_sec']*1000:.2f}",
                "Selection Overhead (ms)": f"{r['mean_selection_overhead_sec']*1000:.3f}",
                "Total Workflow Time (ms)": f"{r['mean_total_workflow_time_sec']*1000:.2f}",
                "Time Saving (%)": f"{r['mean_time_saving_pct']:.1f}%",
                "Fault Detection Rate (%)": f"{r['mean_fault_detection_rate_pct']:.1f}%"
            })
    t3_df = pd.DataFrame(main_rows)
    t3_df.to_csv(os.path.join(TABLES_DIR, "main_comparison_table.csv"), index=False)
    df_to_markdown_file(t3_df, os.path.join(TABLES_DIR, "main_comparison_table.md"), "Table 3: Comprehensive Comparison of Regression Test Selection Approaches")

    # Table 4: Budget Comparison Table (AI vs Random)
    b_rows = []
    for b in [0.25, 0.50, 0.75, 1.00]:
        ai_r = agg_df[(agg_df["method"] == "AI_Selection") & (agg_df["budget_pct"] == b)].iloc[0]
        rand_match = agg_df[(agg_df["method"] == "Random_Selection") & (agg_df["budget_pct"] == b)]
        rand_r = rand_match.iloc[0] if len(rand_match) else None

        b_rows.append({
            "Budget": f"{int(b*100)}%",
            "Tests Selected": int(ai_r["mean_tests_selected"]),
            "AI Test Reduction (%)": f"{ai_r['mean_test_reduction_pct']:.1f}%",
            "AI Fault Detection (%)": f"{ai_r['mean_fault_detection_rate_pct']:.1f}%",
            "Random Fault Detection (%)": f"{rand_r['mean_fault_detection_rate_pct']:.1f}% ± {rand_r['fault_detection_rate_std']:.1f}%" if rand_r is not None else "100.0% ± 0.0%",
            "AI Time Saving (%)": f"{ai_r['mean_time_saving_pct']:.1f}%",
            "Random Time Saving (%)": f"{rand_r['mean_time_saving_pct']:.1f}%" if rand_r is not None else "0.0%"
        })
    t4_df = pd.DataFrame(b_rows)
    t4_df.to_csv(os.path.join(TABLES_DIR, "budget_comparison_table.csv"), index=False)
    df_to_markdown_file(t4_df, os.path.join(TABLES_DIR, "budget_comparison_table.md"), "Table 4: Comparative Performance across Configured Test Budgets")

    # Table 5: Random Baseline Summary
    rand_df.to_csv(os.path.join(TABLES_DIR, "random_baseline_summary.csv"), index=False)
    df_to_markdown_file(rand_df, os.path.join(TABLES_DIR, "random_baseline_summary.md"), "Table 5: Random Baseline Evaluation (20 Iterations per Scenario)")

    # Table 6: Model Performance Metrics
    model_df.to_csv(os.path.join(TABLES_DIR, "model_performance_table.csv"), index=False)
    df_to_markdown_file(model_df, os.path.join(TABLES_DIR, "model_performance_table.md"), "Table 6: Relevance Classifier Performance on Held-Out Test Scenarios")

    # Table 7: Feature Importance
    fi_df.to_csv(os.path.join(TABLES_DIR, "feature_importance_table.csv"), index=False)
    df_to_markdown_file(fi_df, os.path.join(TABLES_DIR, "feature_importance_table.md"), "Table 7: Random Forest Feature Importance for Test Selection")

    # Table 8: Per-Scenario Fault Detection Results
    scen_summary = scen_df[scen_df["eligible_faults"] > 0][[
        "scenario_id", "method", "budget_pct", "n_selected",
        "faults_detected", "eligible_faults", "fault_detection_rate_pct",
        "execution_time_sec"
    ]].copy()
    scen_summary.to_csv(os.path.join(TABLES_DIR, "per_scenario_fault_detection.csv"), index=False)
    df_to_markdown_file(scen_summary, os.path.join(TABLES_DIR, "per_scenario_fault_detection.md"), "Table 8: Scenario-Level Fault Detection Results")

    print("All 8 paper-ready tables (CSV and Markdown) generated successfully.")

if __name__ == "__main__":
    generate_all_figures_and_tables()
