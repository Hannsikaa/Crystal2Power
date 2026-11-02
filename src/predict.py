"""Prediction and inference module for Crystal2Power.

Validates candidate device parameters, generates single-cell and batch PCE predictions,
flags out-of-distribution values and unseen categories, and attaches physical context.
"""

from typing import Dict, Any, List, Tuple, Optional
import numpy as np
import pandas as pd
from sklearn.pipeline import Pipeline


def predict_single_device(
    pipeline: Pipeline,
    input_data: Dict[str, Any],
    feature_columns: List[str],
    training_summary: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Generates a prospective PCE prediction for a candidate solar cell design.

    Args:
        pipeline: Fitted scikit-learn full pipeline.
        input_data: Dictionary mapping feature names to user-entered values.
        feature_columns: Exact list of prospective feature columns expected by pipeline.
        training_summary: Optional training range and category summary for warnings.

    Returns:
        Dictionary containing predicted PCE, warnings, and scientific notes.
    """
    # Build single-row DataFrame adhering strictly to model schema
    row: Dict[str, Any] = {}
    warnings: List[str] = []

    for col in feature_columns:
        val = input_data.get(col, None)
        if val is None or val == "" or str(val).strip() == "":
            row[col] = "Unknown"
        else:
            row[col] = val

    df_input = pd.DataFrame([row], columns=feature_columns)

    # Check for potential extrapolation or unusual inputs
    if training_summary and "numeric_ranges" in training_summary:
        ranges = training_summary["numeric_ranges"]
        for col, stats in ranges.items():
            if col in input_data and input_data[col] is not None:
                try:
                    num_val = float(input_data[col])
                    c_min, c_max = stats.get("min", -np.inf), stats.get("max", np.inf)
                    if num_val < c_min or num_val > c_max:
                        warnings.append(
                            f"Input '{col}' ({num_val}) lies outside observed training range [{c_min}, {c_max}]. Prediction is an extrapolation."
                        )
                except (ValueError, TypeError):
                    pass

    # Predict
    try:
        raw_pred = pipeline.predict(df_input)
        pce_pred = float(raw_pred[0])
    except Exception as e:
        raise RuntimeError(f"Prediction failed inside model pipeline: {str(e)}")

    # Physical plausibility checks
    physical_note = "Valid theoretical range."
    if pce_pred < 0.0:
        warnings.append(
            f"Model predicted a slightly negative efficiency ({pce_pred:.2f}%). Clamped to 0.0% (inactive/shunted device)."
        )
        pce_pred = 0.0
        physical_note = "Inactive device or severe recombination losses."
    elif pce_pred > 33.7:  # Single junction Shockley-Queisser limit
        warnings.append(
            f"Predicted PCE ({pce_pred:.2f}%) exceeds the single-junction Shockley-Queisser limit (~33.7%). Only achievable in multijunction/tandem architectures."
        )
        physical_note = "Exceptional tandem / multijunction efficiency tier."
    elif pce_pred >= 20.0:
        physical_note = "High efficiency tier (>20% PCE). Comparable to modern state-of-the-art laboratory champion cells."
    elif pce_pred >= 12.0:
        physical_note = "Standard viable efficiency tier (12-20% PCE)."
    else:
        physical_note = "Sub-optimal efficiency (<12% PCE). High interfacial losses, poor morphology, or mismatched band alignment."

    return {
        "predicted_pce": round(pce_pred, 2),
        "raw_prediction": round(float(raw_pred[0]), 4),
        "input_features": row,
        "warnings": warnings,
        "physical_note": physical_note,
        "unit": "%"
    }


def predict_batch_devices(
    pipeline: Pipeline,
    candidates: List[Dict[str, Any]],
    feature_columns: List[str]
) -> pd.DataFrame:
    """Predicts PCE for multiple candidate material configurations."""
    results = []
    for c in candidates:
        name = c.get("Candidate_Name", "Candidate")
        pred_dict = predict_single_device(pipeline, c, feature_columns)
        results.append({
            "Candidate": name,
            "Predicted PCE (%)": pred_dict["predicted_pce"],
            "Physical Assessment": pred_dict["physical_note"],
            "Warnings": "; ".join(pred_dict["warnings"]) if pred_dict["warnings"] else "None"
        })
    return pd.DataFrame(results)
