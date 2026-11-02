"""Target leakage prevention and audit module for Crystal2Power.

Strictly identifies and quarantines target variables and post-measurement
electrical characterization metrics to enforce true prospective prediction.
"""

from typing import List, Dict, Tuple
import pandas as pd


# Explicitly known post-measurement and leakage column patterns
KNOWN_LEAKAGE_COLUMNS = {
    "JV_default_PCE": (
        "Target Variable",
        "Target variable to be predicted. Must never be used as an input feature."
    ),
    "JV_default_Voc": (
        "Post-Measurement Leakage",
        "Open-circuit voltage (Voc) is an electrical metric obtained only after solar cell fabrication and JV testing."
    ),
    "JV_default_Jsc": (
        "Post-Measurement Leakage",
        "Short-circuit current density (Jsc) is an electrical metric obtained only after solar cell testing."
    ),
    "JV_default_FF": (
        "Post-Measurement Leakage",
        "Fill Factor (FF) is derived directly from the illuminated JV curve after device measurement."
    ),
    "JV_measured": (
        "Measurement Status Leakage",
        "Indicates whether electrical measurement occurred; strongly correlates with device viability."
    )
}

# Any other identifiers or post-test metadata
IDENTIFIER_KEYWORDS = ["id", "doi", "ref", "author", "sample_id", "batch_number"]


def audit_target_leakage(
    columns: List[str],
    target_col: str = "JV_default_PCE"
) -> Tuple[List[str], List[str], pd.DataFrame]:
    """Audits dataset columns for prospective prediction safety.

    Args:
        columns: List of all column names in the dataset.
        target_col: Name of the target variable.

    Returns:
        Tuple of:
            - usable_features: list of safe prospective feature column names.
            - excluded_columns: list of excluded column names.
            - leakage_audit_df: detailed DataFrame explaining status and reasons.
    """
    audit_records = []
    usable_features = []
    excluded_columns = []

    for col in columns:
        col_lower = col.strip().lower()

        # Check target
        if col == target_col or col_lower == target_col.lower():
            audit_records.append({
                "Column": col,
                "Status": "EXCLUDED",
                "Category": "Prediction Target",
                "Scientific Reason": "The target variable itself. Including it causes 100% artificial target leakage."
            })
            excluded_columns.append(col)

        # Check explicit post-measurement electrical columns
        elif col in KNOWN_LEAKAGE_COLUMNS:
            category, reason = KNOWN_LEAKAGE_COLUMNS[col]
            audit_records.append({
                "Column": col,
                "Status": "EXCLUDED",
                "Category": category,
                "Scientific Reason": reason
            })
            excluded_columns.append(col)

        # Check for other potential JV electrical test metrics or post-testing columns
        elif any(col_lower.startswith(prefix) for prefix in ["jv_test", "jv_curve", "mpp_", "stabilized_pce"]):
            audit_records.append({
                "Column": col,
                "Status": "EXCLUDED",
                "Category": "Suspected Measurement Leakage",
                "Scientific Reason": "Column relates to post-measurement testing and is unavailable during prospective design."
            })
            excluded_columns.append(col)

        # Check for citation/ID metadata that could induce memorization
        elif any(col_lower == kw or col_lower.endswith(f"_{kw}") for kw in IDENTIFIER_KEYWORDS):
            audit_records.append({
                "Column": col,
                "Status": "EXCLUDED",
                "Category": "Identifier / Metadata",
                "Scientific Reason": "Record identifier or citation metadata risks memorization of individual publications."
            })
            excluded_columns.append(col)

        # Prospective candidate feature
        else:
            category = categorize_feature(col)
            audit_records.append({
                "Column": col,
                "Status": "INCLUDED",
                "Category": category,
                "Scientific Reason": "Prospective material, architectural, or fabrication parameter available prior to device testing."
            })
            usable_features.append(col)

    audit_df = pd.DataFrame(audit_records)
    return usable_features, excluded_columns, audit_df


def categorize_feature(column_name: str) -> str:
    """Classifies a prospective feature into a domain category."""
    name = column_name.lower()
    if "cell_architecture" in name or "stack_sequence" in name or "substrate" in name:
        return "Device Architecture"
    if "etl" in name:
        return "Electron Transport Layer (ETL)"
    if "htl" in name:
        return "Hole Transport Layer (HTL)"
    if "perovskite_composition" in name or "ions" in name:
        return "Perovskite Chemical Composition"
    if "additive" in name:
        return "Perovskite Additives"
    if "deposition" in name or "annealing" in name or "solvent" in name:
        return "Fabrication & Annealing Process"
    if "thickness" in name:
        return "Layer Thickness"
    if "backcontact" in name:
        return "Back Contact Electrode"
    if "encapsulation" in name:
        return "Device Encapsulation"
    return "Material / Fabrication Parameter"
