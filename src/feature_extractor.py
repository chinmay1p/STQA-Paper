"""
feature_extractor.py: Defines feature set and extraction pipeline for ML-based regression test selection.
Guarantees strict absence of target leakage.
"""
from typing import List
import pandas as pd

FEATURE_COLUMNS = [
    "module_match",
    "dependency_overlap",
    "code_churn",
    "historical_failure_count",
    "historical_failure_rate",
    "average_test_duration",
    "test_execution_cost",
]

TARGET_COLUMN = "is_relevant"
EVALUATION_TARGET = "detects_fault"


def get_feature_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """Extracts pre-execution feature matrix from DataFrame."""
    missing = [col for col in FEATURE_COLUMNS if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required feature columns: {missing}")
    return df[FEATURE_COLUMNS].copy()


def get_target_vector(df: pd.DataFrame) -> pd.Series:
    """Extracts ground-truth relevance target vector."""
    if TARGET_COLUMN not in df.columns:
        raise ValueError(f"Missing target column: {TARGET_COLUMN}")
    return df[TARGET_COLUMN].copy()
