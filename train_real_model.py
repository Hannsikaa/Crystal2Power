"""Train and evaluate the production model on the real Perovskite Solar Cell dataset."""

import os
import sys
import time
import json
import pandas as pd
import numpy as np

sys.stdout.reconfigure(line_buffering=True)

from src.data_loader import load_dataset
from src.data_audit import generate_data_audit, save_audit_report
from src.train import (
    prepare_train_test_data,
    train_and_compare_models,
    save_trained_pipeline
)
from src.explain import compute_permutation_importance
from src.evaluate import format_metrics_table

print("=" * 60)
print("  Crystal2Power: Training Production Model on Real Data")
print("=" * 60)

csv_path = os.path.join("data", "Solar Cell data set.csv")
if not os.path.exists(csv_path):
    print(f"Error: Dataset not found at {csv_path}")
    exit(1)

# 1. Load dataset
print("\n[1/5] Loading real solar cell dataset...")
df, load_meta = load_dataset(csv_path, target_col="JV_default_PCE")
print(f"Loaded {load_meta['total_rows']:,} rows, {load_meta['total_columns']} columns.")
print(f"Valid PCE rows: {load_meta['valid_target_rows']:,} ({load_meta['valid_target_rows']/load_meta['total_rows']*100:.2f}%)")

# 2. Run and save data audit
print("\n[2/5] Performing comprehensive data audit...")
audit = generate_data_audit(df, filename="Solar Cell data set.csv", target_col="JV_default_PCE")
audit_file = save_audit_report(audit, output_path="reports/data_audit_report.md")
print(f"Audit report generated and saved to: {audit_file}")

# 3. Train/test split with leakage quarantine
print("\n[3/5] Applying target leakage safeguards and creating 80/20 train/test split...")
X_train, X_test, y_train, y_test, features, excluded, leakage_df = prepare_train_test_data(
    df, target_col="JV_default_PCE", test_size=0.20, random_state=42
)
print(f"Prospective Features: {len(features)}")
print(f"Quarantined Leakage Columns: {len(excluded)} ({', '.join(excluded)})")
print(f"Training Samples: {len(X_train):,}")
print(f"Held-out Test Samples: {len(X_test):,}")

# 4. Train and compare models
print("\n[4/5] Training candidate regressors with 2-fold cross-validation...")
t_start = time.time()

def progress_logger(fraction, message):
    print(f"  [{int(fraction*100)}%] {message}")

best_pipeline, best_name, evaluations, cv_scores = train_and_compare_models(
    X_train, y_train, X_test, y_test,
    random_state=42, cv_folds=2, progress_callback=progress_logger
)
total_train_time = round(time.time() - t_start, 2)
print(f"\nTraining completed in {total_train_time} seconds. Selected Model: {best_name}")

# Print evaluation results
metrics_df = format_metrics_table(evaluations)
print("\n=== HELD-OUT TEST EVALUATION COMPARISON ===")
print(metrics_df.to_string(index=False))

# 5. Compute Permutation Feature Importance
print("\n[5/5] Computing permutation feature importance on held-out test data...")
perm_df = compute_permutation_importance(
    best_pipeline, X_test, y_test, n_repeats=5, random_state=42, max_samples=1000
)
print("\nTop 10 Most Influential Features:")
print(perm_df.head(10).to_string(index=False))

# Compute numeric training ranges for prediction extrapolation checks
numeric_ranges = {}
for col in features:
    try:
        col_num = pd.to_numeric(X_train[col], errors="coerce").dropna()
        if len(col_num) > 10:
            numeric_ranges[col] = {
                "min": float(col_num.min()),
                "max": float(col_num.max()),
                "mean": float(col_num.mean()),
                "median": float(col_num.median())
            }
    except Exception:
        pass

# Model metadata
meta = {
    "target_col": "JV_default_PCE",
    "dataset_filename": "Solar Cell data set.csv",
    "total_rows": int(len(df)),
    "train_rows": int(len(X_train)),
    "test_rows": int(len(X_test)),
    "best_model": best_name,
    "feature_columns": features,
    "excluded_columns": excluded,
    "training_time_seconds": total_train_time,
    "training_timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
    "cv_scores_mae": cv_scores,
    "test_metrics": {
        m: {
            "mae": evaluations[m]["mae"],
            "rmse": evaluations[m]["rmse"],
            "r2": evaluations[m]["r2"]
        } for m in evaluations
    },
    "numeric_ranges": numeric_ranges,
    "top_features": perm_df.head(15).to_dict(orient="records"),
    "random_seed": 42
}

# Save trained pipeline
saved_model_path = save_trained_pipeline(
    best_pipeline,
    metadata=meta,
    model_dir="models",
    filename="crystal2power_best_model.joblib"
)
print(f"\nModel and metadata successfully saved to: {saved_model_path}")
print("Training process finished successfully!")
