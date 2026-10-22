# AI-Based Regression Test Selection: Comparative Study

A clean, reproducible undergraduate research project evaluating **Machine Learning (Random Forest)** for **Regression Test Selection (RTS)** compared against Full Suite, Change-Based, and Random selection baselines.

---

## Quickstart

Run the complete experiment with one command:

```powershell
python run_experiment.py
```

This will automatically execute the tests, train the models, run all selection methods, and generate the results.

---

## Simplified Project Structure

```text
d:\STQA\
├── run_experiment.py        # Single script to run the entire experiment
├── requirements.txt         # Dependencies (pytest, scikit-learn, pandas, matplotlib)
├── REPORT.md                # Full project report: what was done, algorithms, results, and RQs
│
├── sample_app/              # Target application with 6 modules
│   ├── discount.py          # Discount and coupon logic
│   ├── cart.py              # Shopping cart
│   ├── tax.py               # Sales tax and VAT
│   ├── authentication.py    # Password and session security
│   ├── orders.py            # Orders and shipping calculation
│   └── payment.py           # Card verification and gateway fees
│
├── tests/                   # 30 unit tests (5 per module)
│   ├── test_discount.py
│   ├── test_cart.py
│   ├── test_tax.py
│   ├── test_authentication.py
│   ├── test_orders.py
│   └── test_payment.py
│
├── data/
│   └── dataset.csv          # 480-row experimental dataset (15 features/labels)
│
├── results/
│   ├── results.csv          # Main comparison results table
│   └── figures/             # 6 publication charts (300 DPI PNGs)
│       ├── test_reduction_comparison.png
│       ├── execution_time_comparison.png
│       ├── fault_detection_comparison.png
│       ├── budget_vs_fault_detection.png
│       ├── random_vs_ai.png
│       └── feature_importance.png
│
├── scenarios/               # 16 code-change scenarios (11 faults, 5 clean)
└── src/                     # Modular Python source files
    ├── dataset_builder.py   # Dataset builder
    ├── feature_extractor.py # Pre-execution feature extraction
    ├── train_model.py       # Random Forest & Logistic Regression trainer
    ├── test_selector.py     # AI selection & ranking
    ├── change_based_selector.py # Change-based selection
    ├── random_selector.py   # Random selection baseline
    ├── experiment_runner.py # Main execution engine
    ├── metrics.py           # Test reduction, time savings, fault detection
    ├── statistical_analysis.py # Wilcoxon statistical testing
    └── generate_reports.py  # Figures and tables generator
```

---

## Key Results Summary

| Selection Method | Budget | Tests Executed | Test Reduction | Total Time | Fault Detection Rate |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Full Regression Suite** | 100% | 30 / 30 | 0.0% | 552.0 ms | **100.0%** |
| **Change-Based Selection** | 100% | 15 / 30 | **50.0%** | 483.7 ms | **100.0%** |
| **Random Selection (50%)** | 50% | 15 / 30 | 50.0% | 501.3 ms | 50.0% ± 11.7% |
| **AI Selection (50% Budget)** | 50% | 15 / 30 | **50.0%** | 499.1 ms | **80.0%** (+30% vs Random) |
| **AI Selection (25% Budget)** | 25% | 8 / 30 | **73.3%** | 459.2 ms | **40.0%** (+18% vs Random) |

For complete details on methodology, features, and research question analyses, see **[`REPORT.md`](REPORT.md)**.
