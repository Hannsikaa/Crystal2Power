"""Data preprocessing and feature transformation module for Crystal2Power.

Provides scikit-learn transformers and pipelines to robustly clean, impute,
encode, and scale solar-cell features while guaranteeing zero data leakage.
"""

import re
from typing import List, Tuple, Dict, Any, Optional
import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder, StandardScaler


def extract_first_float(val: Any) -> float:
    """Extracts the first valid floating point number from a string, or returns NaN."""
    if pd.isna(val) or val is None:
        return np.nan
    val_str = str(val).strip()
    match = re.search(r"[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?", val_str)
    if match:
        try:
            return float(match.group(0))
        except ValueError:
            return np.nan
    return np.nan


def extract_max_float(val: Any) -> float:
    """Extracts the maximum floating point number from a multi-step string, or returns NaN."""
    if pd.isna(val) or val is None:
        return np.nan
    val_str = str(val).strip()
    matches = re.findall(r"[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?", val_str)
    if matches:
        nums = []
        for m in matches:
            try:
                nums.append(float(m))
            except ValueError:
                continue
        if nums:
            return float(max(nums))
    return np.nan


def extract_sum_float(val: Any) -> float:
    """Extracts and sums floating point numbers in a multi-layer stack string, or returns NaN."""
    if pd.isna(val) or val is None:
        return np.nan
    val_str = str(val).strip()
    matches = re.findall(r"[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?", val_str)
    if matches:
        nums = []
        for m in matches:
            try:
                nums.append(float(m))
            except ValueError:
                continue
        if nums:
            return float(sum(nums))
    return np.nan


class SolarCellFeatureCleaner(BaseEstimator, TransformerMixin):
    """Custom scikit-learn transformer to clean semi-structured and mixed solar cell strings.

    Converts strings with multi-step steps (e.g. '70 >> 100', '10 | 100') and booleans
    into standard numeric representation.
    """

    def __init__(self):
        self.num_cols_clean_: List[str] = []
        self.cat_cols_clean_: List[str] = []

    def fit(self, X: pd.DataFrame, y=None):
        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        """Transforms raw input DataFrame into clean tabular formats."""
        if not isinstance(X, pd.DataFrame):
            X_df = pd.DataFrame(X)
        else:
            X_df = X.copy()

        # Clean numeric thickness (e.g. '400.0', '500.0 | nan')
        if "Perovskite_thickness" in X_df.columns:
            X_df["Perovskite_thickness"] = X_df["Perovskite_thickness"].apply(extract_first_float)

        # Clean annealing temperature (e.g. '100', 'Unknown >> 100.0') -> max temp
        if "Perovskite_deposition_thermal_annealing_temperature" in X_df.columns:
            X_df["Perovskite_deposition_thermal_annealing_temperature"] = X_df[
                "Perovskite_deposition_thermal_annealing_temperature"
            ].apply(extract_max_float)

        # Clean annealing time (e.g. '10.0', '1.0; 2.0') -> max / total time
        if "Perovskite_deposition_thermal_annealing_time" in X_df.columns:
            X_df["Perovskite_deposition_thermal_annealing_time"] = X_df[
                "Perovskite_deposition_thermal_annealing_time"
            ].apply(extract_max_float)

        # Clean backcontact thickness (e.g. '10.0 | 100.0') -> sum
        if "Backcontact_thickness_list" in X_df.columns:
            X_df["Backcontact_thickness_list"] = X_df["Backcontact_thickness_list"].apply(extract_sum_float)

        # Clean boolean columns
        for b_col in ["Perovskite_deposition_quenching_induced_crystallisation", "Encapsulation"]:
            if b_col in X_df.columns:
                X_df[b_col] = (
                    X_df[b_col]
                    .astype(str)
                    .str.strip()
                    .str.lower()
                    .isin(["true", "1", "yes", "t"])
                    .astype(float)
                )

        # Clean integer steps
        if "Perovskite_deposition_number_of_deposition_steps" in X_df.columns:
            X_df["Perovskite_deposition_number_of_deposition_steps"] = pd.to_numeric(
                X_df["Perovskite_deposition_number_of_deposition_steps"], errors="coerce"
            )

        # Standardize string categories
        for col in X_df.columns:
            if X_df[col].dtype == object or pd.api.types.is_string_dtype(X_df[col]):
                X_df[col] = X_df[col].fillna("Unknown").astype(str).str.strip()

        return X_df


def identify_column_types(
    X: pd.DataFrame
) -> Tuple[List[str], List[str]]:
    """Identifies numeric and categorical column subsets from prospective features.

    Args:
        X: Feature DataFrame.

    Returns:
        Tuple of (numeric_columns, categorical_columns).
    """
    known_numeric = {
        "Perovskite_thickness",
        "Perovskite_deposition_number_of_deposition_steps",
        "Perovskite_deposition_quenching_induced_crystallisation",
        "Perovskite_deposition_thermal_annealing_temperature",
        "Perovskite_deposition_thermal_annealing_time",
        "Backcontact_thickness_list",
        "Encapsulation"
    }

    numeric_cols: List[str] = []
    categorical_cols: List[str] = []

    for col in X.columns:
        if col in known_numeric:
            numeric_cols.append(col)
        elif pd.api.types.is_numeric_dtype(X[col]):
            numeric_cols.append(col)
        else:
            categorical_cols.append(col)

    return numeric_cols, categorical_cols


def build_preprocessor_pipeline(
    numeric_cols: List[str],
    categorical_cols: List[str],
    max_categories: int = 40
) -> ColumnTransformer:
    """Builds a scikit-learn ColumnTransformer for prospective features.

    Features:
        - Median imputation + StandardScaler for numeric fields.
        - Constant 'Unknown' imputation + OneHotEncoder with handle_unknown='ignore'
          and max_categories for categorical fields.
    """
    num_pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler())
    ])

    cat_pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="constant", fill_value="Unknown")),
        ("ohe", OneHotEncoder(handle_unknown="ignore", max_categories=max_categories, sparse_output=False))
    ])

    transformers = []
    if numeric_cols:
        transformers.append(("num", num_pipeline, numeric_cols))
    if categorical_cols:
        transformers.append(("cat", cat_pipeline, categorical_cols))

    preprocessor = ColumnTransformer(transformers=transformers, remainder="drop")
    return preprocessor


def create_full_pipeline(
    preprocessor: ColumnTransformer,
    regressor: Any
) -> Pipeline:
    """Combines feature cleaning, ColumnTransformer, and regressor into an atomic Pipeline."""
    return Pipeline([
        ("cleaner", SolarCellFeatureCleaner()),
        ("preprocessor", preprocessor),
        ("regressor", regressor)
    ])
