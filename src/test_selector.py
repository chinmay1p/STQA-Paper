"""
test_selector.py: Implements Method D (AI-Based Selection) using Random Forest.
Predicts test relevance probabilities, ranks tests, and selects candidate subsets under configurable budgets.
"""
import time
from typing import Dict, List, Tuple, Any
import numpy as np
import pandas as pd
from src.feature_extractor import get_feature_matrix


def select_ai_tests(
    model: Any,
    scenario_features_df: pd.DataFrame,
    budget_pct: float,
    all_tests: List[str]
) -> Tuple[List[str], Dict[str, float], float]:
    """
    Ranks tests by ML predicted relevance and selects top-K according to budget.
    Returns:
        (selected_test_ids, score_dict, selection_overhead_sec)
    """
    start_time = time.perf_counter()

    # Pre-execution feature extraction
    X = get_feature_matrix(scenario_features_df)
    test_ids = scenario_features_df["test_id"].tolist()

    # Predict relevance probability (class 1)
    if hasattr(model, "predict_proba"):
        probs = model.predict_proba(X)[:, 1]
    else:
        probs = model.predict(X).astype(float)

    # Ranking score dictionary
    # Tie-break using negative test_execution_cost (prefer faster tests when relevance is identical)
    exec_costs = scenario_features_df.get("test_execution_cost", pd.Series(np.zeros(len(X)))).tolist()
    
    ranked_indices = sorted(
        range(len(test_ids)),
        key=lambda i: (probs[i], -exec_costs[i]),
        reverse=True
    )

    total_tests = len(all_tests)
    k = max(1, min(total_tests, int(round(total_tests * budget_pct))))
    selected_indices = ranked_indices[:k]
    selected_tests = [test_ids[i] for i in selected_indices]

    scores = {test_ids[i]: float(probs[i]) for i in range(len(test_ids))}
    overhead = time.perf_counter() - start_time

    return selected_tests, scores, overhead
