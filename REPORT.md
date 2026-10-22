# Project Report: AI-Based Regression Test Selection

**Project Title**: AI-Based Regression Test Selection Using Machine Learning: A Comparative Study  
**Subject**: Software Testing and Quality Assurance (STQA)  

---

## 1. What Was Done

Continuous Integration (CI) pipelines run automated regression tests after every code change. As software grows, executing every test takes too much time and computational resources. 

In this project, we built a complete, working, and reproducible research experiment to evaluate whether **Machine Learning (AI)** can select a smaller subset of tests after a code change to save time while still catching seeded bugs.

### Summary of What Was Built:
1. **Target Software Application (`sample_app/`)**: A modular e-commerce Python application with 6 subsystems:
   - `discount.py`: Tier discounts, coupon codes, and bulk pricing.
   - `cart.py`: Cart items, quantity updates, and weight aggregation (depends on `discount`).
   - `tax.py`: State sales tax (CA, NY, TX, WA, DE), VAT, and exemptions.
   - `authentication.py`: Password validation, session tokens, and role permissions.
   - `orders.py`: Shipping fees, invoice totals, and state transitions (depends on `cart`, `tax`, `discount`, `authentication`).
   - `payment.py`: Credit card Luhn checksum validation and gateway fees (depends on `orders`).

2. **Regression Test Suite (`tests/`)**: 30 deterministic unit tests covering normal, boundary, and edge cases across the 6 modules using `pytest`.

3. **16 Controlled Change Scenarios (`scenarios/`)**:
   - 11 fault scenarios with real, seeded bugs (e.g. boundary off-by-one errors, regex omissions, incorrect tax rates, shipping calculation bugs, checksum parity errors).
   - 5 clean scenarios (refactoring, optimization) where all tests pass.

4. **Experiment Runner (`run_experiment.py`)**:
   - Executes **396 real test runs** via `pytest` subprocesses.
   - Measures real test execution time, selection overhead, test reduction, and fault detection.
   - Generates the dataset (`data/dataset.csv`), the results (`results/results.csv`), and 6 charts (`results/figures/`).

---

## 2. Algorithms and Methods Used

We compared four test selection approaches:

### Method A: Full Regression Test Suite (Reference Baseline)
- **Concept**: Execute all 30 tests on every code change.
- **Role**: Serves as the ground truth reference ($100\%$ fault detection, $0\%$ test reduction).

### Method B: Change-Based Selection (Rule-Based Dependency Graph)
- **Algorithm**: Inspects the modified module in the commit and traverses the static architectural dependency graph. It selects all tests belonging to the modified module plus all tests belonging to dependent modules.
- **Strengths**: Deterministic, zero overhead ($0.022\text{ ms}$).

### Method C: Random Selection (Stochastic Baseline)
- **Algorithm**: Randomly picks $K$ tests to match the test budget ($25\%$, $50\%$, $75\%$).
- **Methodology**: Repeated across **20 fixed random seeds** (`42` to `61`) per scenario and budget to obtain reliable mean and standard deviation numbers without flakiness.

### Method D: AI-Based Selection (Machine Learning)
- **Algorithm**: **Random Forest Classifier** (`n_estimators=100`, `max_depth=5`, `random_state=42`) trained via `scikit-learn`.
- **Workflow**:
  1. For any new commit, extract pre-execution features (module match, dependency overlap, code churn, historical failure rate, baseline duration).
  2. The Random Forest model predicts the probability of relevance for each candidate test.
  3. Tests are ranked in descending order of predicted relevance (faster tests prioritized on ties).
  4. Top $K$ tests are selected according to the configured budget ($25\%$, $50\%$, $75\%$, $100\%$) and executed.
- **Secondary Model**: **Logistic Regression** was also trained as a linear baseline comparison (achieved identical $1.00$ F1-score on held-out test scenarios).
- **Statistical Test**: **Wilcoxon signed-rank test** (one-tailed: AI > Random) was applied to compare paired fault detection effectiveness across test scenarios.

---

## 3. Dataset Used (`data/dataset.csv`)

The dataset contains **480 rows** ($16\text{ scenarios} \times 30\text{ tests}$) and **15 columns**:

| Feature / Column | Type | Meaning |
| :--- | :--- | :--- |
| `scenario_id` | Text | Scenario identifier (`SC-01` to `SC-16`). |
| `test_id` | Text | Test name (e.g., `tests/test_discount.py::test_discount_tier_rates`). |
| `test_module` | Text | Subsystem tested by this test (`discount`, `cart`, `tax`, `authentication`, `orders`, `payment`). |
| `changed_module` | Text | Subsystem modified in this scenario. |
| `module_match` | 0 or 1 | 1 if `test_module == changed_module`, else 0. |
| `dependency_overlap` | 0 or 1 | 1 if an architectural dependency exists between the two modules. |
| `code_churn` | Number | Lines of code changed in the commit. |
| `historical_failure_count` | Number | Times this test failed in strictly prior scenarios ($i < j$). |
| `historical_failure_rate` | Number | Past failure count divided by number of prior scenarios. |
| `average_test_duration` | Number | Baseline measured runtime on clean code (in seconds). |
| `test_execution_cost` | Number | Normalized execution duration cost ($0.0$ to $1.0$). |
| `is_relevant` | 0 or 1 | **Training Target**: 1 if test exercises the changed or dependent subsystem. |
| `detects_fault` | 0 or 1 | **Evaluation Target**: 1 if test catches the seeded bug in this scenario. (Never used as a training feature). |
| `execution_status` | Text | `PASSED` or `FAILED`. |
| `split` | Text | `train` (Scenarios `SC-01` to `SC-10`, 300 rows) or `test` (Scenarios `SC-11` to `SC-16`, 180 rows). |

### Zero Data Leakage Safeguards:
- **Grouped Split**: Scenarios in the test set never appeared in the training set.
- **Past-Only History**: Historical failure rates for scenario $N$ were calculated only from scenarios $1$ to $N-1$.
- **Strict Separation of Labels**: The fault detection label `detects_fault` was **never** given to the model as an input feature.

---

## 4. Experimental Results and Answers to Research Questions

All numbers below were measured directly from real test executions on the held-out test scenarios (`SC-11` to `SC-16`):

### Main Comparison Table
| Selection Method | Budget | Tests Selected | Test Reduction (%) | Selection Overhead | Total Workflow Time | Time Saving (%) | Fault Detection Rate (%) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Full Suite** | 100% | 30.0 / 30 | 0.0% | 0.002 ms | 552.0 ms | 0.0% | **100.0%** (5/5) |
| **Change-Based** | 100% | 15.0 / 30 | **50.0%** | 0.022 ms | 483.7 ms | **12.1%** | **100.0%** (5/5) |
| **Random (25%)** | 25% | 8.0 / 30 | 73.3% | 0.037 ms | 476.4 ms | 13.7% | 22.0% ± 11.5% |
| **Random (50%)** | 50% | 15.0 / 30 | 50.0% | 0.039 ms | 501.3 ms | 9.2% | 50.0% ± 11.7% |
| **Random (75%)** | 75% | 22.0 / 30 | 26.7% | 0.039 ms | 504.4 ms | 8.7% | 70.0% ± 9.4% |
| **AI Selection (25%)** | 25% | 8.0 / 30 | **73.3%** | 5.851 ms | 459.2 ms | **16.4%** | **40.0%** (+18% vs Random) |
| **AI Selection (50%)** | 50% | 15.0 / 30 | **50.0%** | 5.758 ms | 499.1 ms | **9.3%** | **80.0%** (+30% vs Random) |
| **AI Selection (75%)** | 75% | 22.0 / 30 | **26.7%** | 5.791 ms | 505.0 ms | **8.3%** | **80.0%** (+10% vs Random) |
| **AI Selection (100%)**| 100% | 30.0 / 30 | 0.0% | 6.290 ms | 533.9 ms | 2.9% | **100.0%** (5/5) |

---

### Answering the 4 Research Questions:

#### RQ1: How much can each selection approach reduce the number of executed tests?
- **AI Selection at 25% Budget**: Executes only **8 tests**, achieving a **73.3% reduction**.
- **AI Selection at 50% Budget**: Executes **15 tests**, achieving a **50.0% reduction**.
- **Change-Based Selection**: Executes **15 tests** on average, achieving a **50.0% reduction**.

#### RQ2: How much execution time can each approach save?
- AI Selection saved up to **17.5%** in raw test execution time.
- The model overhead (extracting features + Random Forest prediction) took only **5.8 ms**.
- Even when adding model overhead to test execution time, total workflow savings remained positive (**16.4% net saving** at 25% budget).

#### RQ3: How does fault detection effectiveness change when fewer tests are executed?
- **AI beats Random Selection across every budget level**:
  - At 25% budget: AI caught **40.0%** of faults vs. **22.0%** for Random (+18% advantage).
  - At 50% budget: AI caught **80.0%** of faults vs. **50.0%** for Random (**+30% advantage**).
  - At 75% budget: AI caught **80.0%** of faults vs. **70.0%** for Random (+10% advantage).
- **Change-Based Selection** detected **100.0%** of faults because all injected defects occurred in modified or directly linked modules.
- *Statistical note*: In Wilcoxon signed-rank testing ($N=5$ fault scenarios, $W=10.0, p=0.3125$), AI showed a strong descriptive improvement (+30%), but the small sample size was underpowered to reach asymptotic significance at $\alpha=0.05$.

#### RQ4: Which test features contribute most to the Random Forest model's predictions?
Feature importance values from the trained Random Forest:
1. **`dependency_overlap` (52.97%)**: Whether the test exercises a dependent module.
2. **`module_match` (32.96%)**: Whether the test directly matches the changed file.
3. **`test_execution_cost` (5.99%)**: Normalized test duration.
4. **`average_test_duration` (3.94%)**: Raw test runtime.
5. **`code_churn` (2.67%)**: Number of lines modified.
6. **`historical_failure_rate` (1.08%)**: Past failure frequency.
7. **`historical_failure_count` (0.39%)**: Past failure count.

Structural architectural features (`dependency_overlap` + `module_match`) account for **85.9%** of the model's predictive decisions.

---

## 5. Generated Figures (`results/figures/`)

The following 300 DPI publication-quality charts are generated in `results/figures/`:
1. `test_reduction_comparison.png`: Bar chart comparing test reduction across methods.
2. `execution_time_comparison.png`: Test execution time vs total workflow time (with overhead).
3. `fault_detection_comparison.png`: Fault detection percentage across methods.
4. `budget_vs_fault_detection.png`: Curve showing fault detection as budget increases (25% to 100%).
5. `random_vs_ai.png`: Head-to-head bar chart comparing AI Selection against the 20-seed Random baseline with error bars.
6. `feature_importance.png`: Horizontal bar chart of Random Forest feature importance weights.

---

## 6. How to Run the Project

Running the entire experiment takes just one command:

```powershell
python run_experiment.py
```

### Outputs Created:
- **`data/dataset.csv`**: The complete 480-row experimental dataset.
- **`results/results.csv`**: The main comparative metrics table.
- **`results/figures/`**: All 6 research charts (PNG at 300 DPI).
- **`REPORT.md`**: This comprehensive summary report.
