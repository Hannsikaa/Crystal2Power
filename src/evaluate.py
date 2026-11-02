"""Model evaluation module for Crystal2Power.

Computes comprehensive regression metrics (MAE, RMSE, R²), residual distributions,
and diagnostic actual-vs-predicted data.
"""

from typing import Dict, Any, Union
import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, root_mean_squared_error, r2_score


def evaluate_predictions(
    y_true: Union[pd.Series, np.ndarray],
    y_pred: Union[pd.Series, np.ndarray],
    model_name: str = "Model"
) -> Dict[str, Any]:
    """Calculates regression evaluation metrics on test data.

    Args:
        y_true: True experimental values.
        y_pred: Model predictions.
        model_name: Human-readable algorithm identifier.

    Returns:
        Dictionary of performance metrics and diagnostic arrays.
    """
    y_true_arr = np.asarray(y_true, dtype=float)
    y_pred_arr = np.asarray(y_pred, dtype=float)

    # Filter out any non-finite pairs if present
    valid_mask = np.isfinite(y_true_arr) & np.isfinite(y_pred_arr)
    y_true_clean = y_true_arr[valid_mask]
    y_pred_clean = y_pred_arr[valid_mask]

    n_samples = len(y_true_clean)
    if n_samples == 0:
        return {
            "model_name": model_name,
            "n_samples": 0,
            "mae": np.nan,
            "rmse": np.nan,
            "r2": np.nan,
            "residuals": np.array([]),
            "r2_interpretation": "No valid samples to evaluate."
        }

    mae = float(mean_absolute_error(y_true_clean, y_pred_clean))
    rmse = float(root_mean_squared_error(y_true_clean, y_pred_clean))
    r2 = float(r2_score(y_true_clean, y_pred_clean))

    residuals = y_true_clean - y_pred_clean

    # Interpret R² honestly
    if r2 < 0:
        r2_interpretation = (
            "Negative R² indicates that the model performs worse than a simple baseline "
            "that always predicts the overall mean PCE of the training set. "
            "This highlights high residual variance or domain shifts."
        )
    elif r2 < 0.3:
        r2_interpretation = (
            "Weak predictive power (R² < 0.30). The model captures limited variance in PCE."
        )
    elif r2 < 0.6:
        r2_interpretation = (
            "Moderate predictive power (0.30 <= R² < 0.60). The model captures useful trends, "
            "though laboratory fabrication variance remains significant."
        )
    else:
        r2_interpretation = (
            f"Strong predictive power (R² = {r2:.3f}). The model captures the majority of variance "
            "in experimental solar cell efficiencies across the dataset."
        )

    return {
        "model_name": model_name,
        "n_samples": n_samples,
        "mae": round(mae, 4),
        "rmse": round(rmse, 4),
        "r2": round(r2, 4),
        "mean_residual": round(float(np.mean(residuals)), 4),
        "std_residual": round(float(np.std(residuals)), 4),
        "y_true": y_true_clean,
        "y_pred": y_pred_clean,
        "residuals": residuals,
        "r2_interpretation": r2_interpretation
    }


def format_metrics_table(results_dict: Dict[str, Dict[str, Any]]) -> pd.DataFrame:
    """Formats multiple evaluation results into a comparison DataFrame."""
    rows = []
    for name, res in results_dict.items():
        rows.append({
            "Model": name,
            "MAE (% PCE)": res.get("mae", np.nan),
            "RMSE (% PCE)": res.get("rmse", np.nan),
            "R² Score": res.get("r2", np.nan),
            "Test Samples": res.get("n_samples", 0)
        })
    df_metrics = pd.DataFrame(rows)
    return df_metrics.sort_values(by="MAE (% PCE)", ascending=True).reset_index(drop=True)
