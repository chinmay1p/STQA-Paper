"""
train_model.py: Trains Random Forest classifier (and optional Logistic Regression baseline)
on training scenarios and evaluates on held-out test scenarios with grouped splitting.
Saves model metrics, feature importances, and serialized models.
"""
import json
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import joblib
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
    classification_report
)
from src.feature_extractor import FEATURE_COLUMNS, get_feature_matrix, get_target_vector

DATASET_PATH = os.path.join(BASE_DIR, "data", "processed", "regression_test_selection_dataset.csv")
MODEL_METRICS_PATH = os.path.join(BASE_DIR, "results", "processed", "model_metrics.csv")
FEATURE_IMPORTANCE_PATH = os.path.join(BASE_DIR, "results", "processed", "feature_importance.csv")
RF_MODEL_PATH = os.path.join(BASE_DIR, "data", "processed", "random_forest_model.joblib")
LR_MODEL_PATH = os.path.join(BASE_DIR, "data", "processed", "logistic_regression_model.joblib")


def train_and_evaluate(random_state: int = 42):
    df = pd.read_csv(DATASET_PATH)

    train_df = df[df["split"] == "train"].copy()
    test_df = df[df["split"] == "test"].copy()

    X_train = get_feature_matrix(train_df)
    y_train = get_target_vector(train_df)

    X_test = get_feature_matrix(test_df)
    y_test = get_target_vector(test_df)

    print(f"Training on {len(X_train)} samples across {train_df['scenario_id'].nunique()} scenarios.")
    print(f"Testing on {len(X_test)} samples across {test_df['scenario_id'].nunique()} scenarios.")

    # 1. Random Forest Classifier
    rf_model = RandomForestClassifier(
        n_estimators=100,
        max_depth=5,
        min_samples_split=2,
        random_state=random_state
    )
    rf_model.fit(X_train, y_train)

    rf_pred = rf_model.predict(X_test)
    rf_proba = rf_model.predict_proba(X_test)[:, 1]

    rf_cm = confusion_matrix(y_test, rf_pred)
    rf_tn, rf_fp, rf_fn, rf_tp = rf_cm.ravel()

    rf_metrics = {
        "model": "Random Forest",
        "precision": round(precision_score(y_test, rf_pred, zero_division=0), 4),
        "recall": round(recall_score(y_test, rf_pred, zero_division=0), 4),
        "f1_score": round(f1_score(y_test, rf_pred, zero_division=0), 4),
        "roc_auc": round(roc_auc_score(y_test, rf_proba), 4),
        "true_positives": int(rf_tp),
        "false_positives": int(rf_fp),
        "true_negatives": int(rf_tn),
        "false_negatives": int(rf_fn)
    }

    # 2. Logistic Regression (Optional ML comparison)
    lr_model = LogisticRegression(random_state=random_state, max_iter=1000)
    lr_model.fit(X_train, y_train)

    lr_pred = lr_model.predict(X_test)
    lr_proba = lr_model.predict_proba(X_test)[:, 1]

    lr_cm = confusion_matrix(y_test, lr_pred)
    lr_tn, lr_fp, lr_fn, lr_tp = lr_cm.ravel()

    lr_metrics = {
        "model": "Logistic Regression",
        "precision": round(precision_score(y_test, lr_pred, zero_division=0), 4),
        "recall": round(recall_score(y_test, lr_pred, zero_division=0), 4),
        "f1_score": round(f1_score(y_test, lr_pred, zero_division=0), 4),
        "roc_auc": round(roc_auc_score(y_test, lr_proba), 4),
        "true_positives": int(lr_tp),
        "false_positives": int(lr_fp),
        "true_negatives": int(lr_tn),
        "false_negatives": int(lr_fn)
    }

    metrics_df = pd.DataFrame([rf_metrics, lr_metrics])
    os.makedirs(os.path.dirname(MODEL_METRICS_PATH), exist_ok=True)
    metrics_df.to_csv(MODEL_METRICS_PATH, index=False)

    # Feature Importance for Random Forest
    importances = rf_model.feature_importances_
    fi_df = pd.DataFrame({
        "feature": FEATURE_COLUMNS,
        "importance": [round(float(imp), 4) for imp in importances]
    }).sort_values(by="importance", ascending=False)
    fi_df.to_csv(FEATURE_IMPORTANCE_PATH, index=False)

    # Save models
    joblib.dump(rf_model, RF_MODEL_PATH)
    joblib.dump(lr_model, LR_MODEL_PATH)

    print("\n--- Model Evaluation on Held-Out Test Scenarios ---")
    print(metrics_df.to_string(index=False))
    print("\n--- Random Forest Feature Importance ---")
    print(fi_df.to_string(index=False))

    return rf_model, metrics_df, fi_df

if __name__ == "__main__":
    train_and_evaluate()
