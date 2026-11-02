"""Data loading module for Crystal2Power.

Provides robust loading of CSV and Excel datasets with multi-encoding fallback,
null-marker standardization, schema validation, and target verification.
"""

import os
from typing import Dict, Any, Optional, Tuple, Union
import pandas as pd
import numpy as np


TARGET_COLUMN = "JV_default_PCE"
COMMON_ENCODINGS = ["utf-8", "utf-8-sig", "latin1", "cp1252"]


def load_dataset(
    file_source: Union[str, Any],
    target_col: str = TARGET_COLUMN
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """Loads a tabular dataset from a file path or file-like buffer (e.g. Streamlit UploadedFile).

    Args:
        file_source: File path (str) or file buffer.
        target_col: Expected name of the target column.

    Returns:
        Tuple of (loaded DataFrame, metadata dictionary).

    Raises:
        ValueError: If file format is unsupported, file is empty, or data cannot be parsed.
    """
    metadata: Dict[str, Any] = {
        "filename": "uploaded_dataset",
        "file_format": "unknown",
        "total_rows": 0,
        "total_columns": 0,
        "target_col": target_col,
        "target_found": False,
        "valid_target_rows": 0,
        "invalid_target_rows": 0,
        "columns": [],
    }

    # Determine filename and extension
    if isinstance(file_source, str):
        metadata["filename"] = os.path.basename(file_source)
        ext = os.path.splitext(file_source)[1].lower()
    elif hasattr(file_source, "name"):
        metadata["filename"] = file_source.name
        ext = os.path.splitext(file_source.name)[1].lower()
    else:
        ext = ".csv"

    metadata["file_format"] = ext

    df: Optional[pd.DataFrame] = None
    last_error: Optional[Exception] = None

    if ext in [".csv", ".txt"]:
        for enc in COMMON_ENCODINGS:
            try:
                if hasattr(file_source, "seek"):
                    file_source.seek(0)
                df = pd.read_csv(
                    file_source,
                    encoding=enc,
                    low_memory=False,
                    na_values=["#N/A", "#NA", "NULL", "null", "NaN", "-1.#IND", "-1.#QNAN", ""]
                )
                break
            except (UnicodeDecodeError, pd.errors.ParserError) as e:
                last_error = e
                continue
    elif ext in [".xlsx", ".xls"]:
        try:
            if hasattr(file_source, "seek"):
                file_source.seek(0)
            df = pd.read_excel(file_source)
        except Exception as e:
            last_error = e
    elif ext == ".parquet":
        try:
            if hasattr(file_source, "seek"):
                file_source.seek(0)
            df = pd.read_parquet(file_source)
        except Exception as e:
            last_error = e
    else:
        raise ValueError(
            f"Unsupported file format '{ext}'. Crystal2Power supports .csv, .xlsx, .xls, and .parquet files."
        )

    if df is None:
        raise ValueError(
            f"Failed to read dataset '{metadata['filename']}'. Underlying error: {last_error}"
        )

    if df.empty or len(df.columns) == 0:
        raise ValueError(f"Dataset '{metadata['filename']}' is empty or contains no columns.")

    metadata["total_rows"] = int(len(df))
    metadata["total_columns"] = int(len(df.columns))
    metadata["columns"] = list(df.columns)

    # Validate target presence and numeric validity
    if target_col in df.columns:
        metadata["target_found"] = True
        num_target = pd.to_numeric(df[target_col], errors="coerce")
        valid_mask = num_target.notna() & np.isfinite(num_target)
        metadata["valid_target_rows"] = int(valid_mask.sum())
        metadata["invalid_target_rows"] = int((~valid_mask).sum())
    else:
        metadata["target_found"] = False
        metadata["valid_target_rows"] = 0
        metadata["invalid_target_rows"] = metadata["total_rows"]

    return df, metadata


def get_default_dataset_path() -> Optional[str]:
    """Finds the default CSV dataset in the local data directory if available."""
    candidates = [
        os.path.join("data", "Solar Cell data set.csv"),
        os.path.join("data", "solar_cell_dataset.csv"),
        os.path.join("data", "dataset.csv")
    ]
    for path in candidates:
        if os.path.exists(path):
            return path
    return None
