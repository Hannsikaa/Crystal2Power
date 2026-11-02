"""Model training and selection module for Crystal2Power.

Trains and validates multiple regression algorithms (Dummy, HistGradientBoosting,
RandomForest, ExtraTrees), conducts cross-validation, selects the optimal model,
and persists the full fitted pipeline with metadata.
"""

import os
import sys
import time
from datetime import datetime
from typing import Dict, Any, Tuple, Optional, List
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split, KFold, cross_val_score, GroupKFold, GroupShuffleSplit
from sklearn.dummy import DummyRegressor
from sklearn.ensemble import HistGradientBoostingRegressor, RandomForestRegressor, ExtraTreesRegressor
from sklearn.pipeline import Pipeline
import sklearn

# Set environment variable to silence wmic lookup in joblib on modern Windows
os.environ["LOKY_MAX_CPU_COUNT"] = "4"

from src.leakage import audit_target_leakage
from src.preprocessing import identify_column_types, build_preprocessor_pipeline, create_full_pipeline
from src.evaluate import evaluate_predictions


MODEL_REGISTRY = {
    "HistGradientBoosting": lambda seed: HistGradientBoostingRegressor(
        random_state=seed, max_iter=100, max_leaf_nodes=31, learning_rate=0.1
    ),
    "RandomForest": lambda seed: RandomForestRegressor(
        n_estimators=35, max_depth=14, random_state=seed, n_jobs=1
    ),
    "ExtraTrees": lambda seed: ExtraTreesRegressor(
        n_estimators=35, max_depth=14, random_state=seed, n_jobs=1
    ),
    "DummyRegressor (Baseline)": lambda seed: DummyRegressor(strategy="mean")
}


def prepare_train_test_data(
    df: pd.DataFrame,
    target_col: str = "JV_default_PCE",
    test_size: float = 0.2,
    random_state: int = 42,
    group_col: Optional[str] = None
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series, List[str], List[str], pd.DataFrame]:
    """Prepares and splits dataset into train and test sets with strict leakage exclusion.

    Args:
        df: Raw input DataFrame.
        target_col: Target column name.
        test_size: Fraction of held-out test data.
        random_state: Random seed.
        group_col: Optional grouping column for GroupShuffleSplit.

    Returns:
        Tuple of (X_train, X_test, y_train, y_test, feature_cols, excluded_cols, leakage_audit_df).
    """
    if target_col not in df.columns:
        raise ValueError(f"Target column '{target_col}' not found in dataset columns.")

    # Convert target to numeric and drop invalid/missing target rows
    df_valid = df.copy()
    df_valid[target_col] = pd.to_numeric(df_valid[target_col], errors="coerce")
    valid_mask = df_valid[target_col].notna() & np.isfinite(df_valid[target_col])
    df_valid = df_valid[valid_mask]

    if len(df_valid) < 10:
        raise ValueError(
            f"Insufficient valid target rows ({len(df_valid)}). Minimum 10 rows required for training."
        )

    # Run leakage audit
    usable_features, excluded_cols, leakage_audit_df = audit_target_leakage(
        columns=list(df_valid.columns),
        target_col=target_col
    )

    if not usable_features:
        raise ValueError("No usable prospective features found after leakage quarantine.")

    X = df_valid[usable_features]
    y = df_valid[target_col]

    # Split
    if group_col and group_col in df_valid.columns and df_valid[group_col].nunique() > 1:
        groups = df_valid[group_col].fillna("Unknown").values
        gss = GroupShuffleSplit(n_splits=1, test_size=test_size, random_state=random_state)
        train_idx, test_idx = next(gss.split(X, y, groups=groups))
        X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
        y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]
    else:
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state
        )

    return X_train, X_test, y_train, y_test, usable_features, excluded_cols, leakage_audit_df


def train_and_compare_models(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    X_test: pd.DataFrame,
    y_test: pd.Series,
    random_state: int = 42,
    cv_folds: int = 3,
    progress_callback: Optional[Any] = None
) -> Tuple[Pipeline, str, Dict[str, Any], Dict[str, Any]]:
    """Trains candidate models, compares cross-validation MAE on training data,

    and evaluates all candidates on the held-out test data.

    Returns:
        Tuple of:
            - best_pipeline: Fitted Pipeline of the best-performing model.
            - best_model_name: Name of selected model.
            - test_evaluations: Dictionary of evaluation metrics for all candidates.
            - cv_scores: Cross-validation MAE scores on training set.
    """
    numeric_cols, categorical_cols = identify_column_types(X_train)
    preprocessor = build_preprocessor_pipeline(numeric_cols, categorical_cols)

    test_evaluations: Dict[str, Any] = {}
    cv_scores: Dict[str, float] = {}
    fitted_pipelines: Dict[str, Pipeline] = {}

    total_models = len(MODEL_REGISTRY)
    for idx, (m_name, model_fn) in enumerate(MODEL_REGISTRY.items()):
        if progress_callback:
            progress_callback(
                (idx + 0.1) / total_models,
                f"Validating {m_name} with {cv_folds}-fold cross validation..."
            )

        regressor = model_fn(random_state)
        pipeline = create_full_pipeline(preprocessor, regressor)

        # Cross-validation on training data only for fair model selection
        kf = KFold(n_splits=cv_folds, shuffle=True, random_state=random_state)
        try:
            scores = cross_val_score(
                pipeline, X_train, y_train,
                cv=kf, scoring="neg_mean_absolute_error",
                n_jobs=1
            )
            mean_cv_mae = float(-np.mean(scores))
        except Exception:
            mean_cv_mae = 999.0

        cv_scores[m_name] = round(mean_cv_mae, 4)

        if progress_callback:
            progress_callback(
                (idx + 0.8) / total_models,
                f"Fitting final {m_name} on complete training set..."
            )

        # Fit on full training data
        pipeline.fit(X_train, y_train)
        fitted_pipelines[m_name] = pipeline

        # Predict once on held-out test set
        y_test_pred = pipeline.predict(X_test)
        eval_metrics = evaluate_predictions(y_test, y_test_pred, model_name=m_name)
        test_evaluations[m_name] = eval_metrics

    # Select best model based on training cross-validation MAE (excluding dummy)
    valid_candidates = {k: v for k, v in cv_scores.items() if "Dummy" not in k}
    if valid_candidates:
        best_model_name = min(valid_candidates, key=valid_candidates.get)
    else:
        best_model_name = "HistGradientBoosting"

    best_pipeline = fitted_pipelines[best_model_name]

    if progress_callback:
        progress_callback(1.0, f"Completed training. Best model selected: {best_model_name}")

    return best_pipeline, best_model_name, test_evaluations, cv_scores


def save_trained_pipeline(
    pipeline: Pipeline,
    metadata: Dict[str, Any],
    model_dir: str = "models",
    filename: str = "crystal2power_best_model.joblib"
) -> str:
    """Saves the fitted pipeline and metadata atomically to disk."""
    os.makedirs(model_dir, exist_ok=True)
    target_path = os.path.join(model_dir, filename)
    meta_path = os.path.join(model_dir, f"{os.path.splitext(filename)[0]}_metadata.json")

    # Atomic write to temporary file then replace
    temp_target = target_path + ".tmp"
    joblib.dump(pipeline, temp_target)
    if os.path.exists(target_path):
        os.remove(target_path)
    os.rename(temp_target, target_path)

    # Save metadata
    import json
    def json_default(obj):
        if isinstance(obj, (np.floating, np.float32, np.float64)):
            return float(obj)
        if isinstance(obj, (np.integer, np.int32, np.int64)):
            return int(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return str(obj)

    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, default=json_default, indent=2)

    return target_path


def load_saved_pipeline(
    model_path: str = "models/crystal2power_best_model.joblib"
) -> Tuple[Pipeline, Dict[str, Any]]:
    """Loads a previously trained pipeline and its metadata."""
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model file not found at: {model_path}")

    pipeline = joblib.load(model_path)
    meta_path = os.path.join(
        os.path.dirname(model_path),
        f"{os.path.splitext(os.path.basename(model_path))[0]}_metadata.json"
    )

    metadata: Dict[str, Any] = {}
    if os.path.exists(meta_path):
        import json
        with open(meta_path, "r", encoding="utf-8") as f:
            metadata = json.load(f)

    return pipeline, metadata
