"""Data audit and exploratory analysis module for Crystal2Power.

Generates comprehensive data audits including missingness, unique counts,
target distribution, duplicate checks, and data quality warnings.
"""

import os
from typing import Dict, Any, List
import pandas as pd
import numpy as np


def generate_data_audit(
    df: pd.DataFrame,
    filename: str = "dataset.csv",
    target_col: str = "JV_default_PCE"
) -> Dict[str, Any]:
    """Performs an exhaustive audit on the tabular dataset.

    Args:
        df: Input pandas DataFrame.
        filename: Dataset filename.
        target_col: Expected target column name.

    Returns:
        Structured audit dictionary.
    """
    total_rows = len(df)
    total_cols = len(df.columns)
    duplicate_rows = int(df.duplicated().sum())

    # Column-level profile
    column_profiles: List[Dict[str, Any]] = []
    numeric_summaries: Dict[str, Dict[str, float]] = {}

    for col in df.columns:
        series = df[col]
        missing_count = int(series.isna().sum())
        missing_pct = round((missing_count / total_rows) * 100, 2) if total_rows > 0 else 0.0
        n_unique = int(series.nunique(dropna=True))
        dtype_str = str(series.dtype)

        # Test numeric convertibility
        num_converted = pd.to_numeric(series, errors="coerce")
        valid_num_count = int(num_converted.notna().sum())
        is_numeric = valid_num_count > 0 and (valid_num_count / (total_rows - missing_count) > 0.8) if (total_rows - missing_count) > 0 else False

        profile_entry = {
            "column": col,
            "dtype": dtype_str,
            "missing_count": missing_count,
            "missing_pct": missing_pct,
            "unique_count": n_unique,
            "is_numeric": is_numeric,
            "sample_value": str(series.dropna().iloc[0])[:50] if not series.dropna().empty else "N/A"
        }
        column_profiles.append(profile_entry)

        # If numeric (and not boolean), compute descriptive statistics
        if (pd.api.types.is_numeric_dtype(series) and not pd.api.types.is_bool_dtype(series)) or (is_numeric and valid_num_count > 10):
            valid_nums = num_converted.dropna().astype(float)
            if len(valid_nums) > 0:
                numeric_summaries[col] = {
                    "count": float(len(valid_nums)),
                    "mean": round(float(valid_nums.mean()), 3),
                    "std": round(float(valid_nums.std()), 3) if len(valid_nums) > 1 else 0.0,
                    "min": round(float(valid_nums.min()), 3),
                    "q25": round(float(valid_nums.quantile(0.25)), 3),
                    "median": round(float(valid_nums.median()), 3),
                    "q75": round(float(valid_nums.quantile(0.75)), 3),
                    "max": round(float(valid_nums.max()), 3),
                }

    # Target audit
    target_stats: Dict[str, Any] = {
        "target_col": target_col,
        "present": target_col in df.columns,
        "valid_count": 0,
        "missing_count": total_rows,
        "min": None,
        "max": None,
        "mean": None,
        "median": None,
        "std": None,
        "suspicious_values_count": 0,
        "quality_warnings": []
    }

    if target_col in df.columns:
        target_series = pd.to_numeric(df[target_col], errors="coerce")
        valid_targets = target_series.dropna()
        target_stats["valid_count"] = int(len(valid_targets))
        target_stats["missing_count"] = int(total_rows - len(valid_targets))

        if len(valid_targets) > 0:
            target_stats["min"] = float(valid_targets.min())
            target_stats["max"] = float(valid_targets.max())
            target_stats["mean"] = round(float(valid_targets.mean()), 3)
            target_stats["median"] = round(float(valid_targets.median()), 3)
            target_stats["std"] = round(float(valid_targets.std()), 3)

            # Check for suspicious or anomalous values
            neg_count = int((valid_targets < 0).sum())
            over_limit_count = int((valid_targets > 40).sum())  # Single junction theoretical limit is ~33%
            zero_count = int((valid_targets == 0).sum())

            if neg_count > 0:
                target_stats["suspicious_values_count"] += neg_count
                target_stats["quality_warnings"].append(
                    f"Found {neg_count} negative PCE values. Power Conversion Efficiency cannot physically be negative."
                )
            if over_limit_count > 0:
                target_stats["suspicious_values_count"] += over_limit_count
                target_stats["quality_warnings"].append(
                    f"Found {over_limit_count} PCE records > 40%, which exceeds typical single-junction physical limits."
                )
            if zero_count > 0:
                target_stats["quality_warnings"].append(
                    f"Found {zero_count} zero-efficiency (PCE = 0%) entries. These typically represent shunted or failed fabrication runs."
                )

    # General dataset warnings
    general_warnings = []
    if duplicate_rows > 0:
        general_warnings.append(
            f"Detected {duplicate_rows} duplicate rows ({round(duplicate_rows/total_rows*100, 2)}%). These may represent repeated fabrication experiments or duplicate literature records."
        )

    high_missing_cols = [c["column"] for c in column_profiles if c["missing_pct"] > 60]
    if high_missing_cols:
        general_warnings.append(
            f"{len(high_missing_cols)} columns have >60% missing values (e.g., {', '.join(high_missing_cols[:4])}). Imputation indicators or robust handling will be applied."
        )

    audit_result = {
        "filename": filename,
        "total_rows": total_rows,
        "total_columns": total_cols,
        "duplicate_rows": duplicate_rows,
        "column_profiles": column_profiles,
        "numeric_summaries": numeric_summaries,
        "target_stats": target_stats,
        "general_warnings": general_warnings
    }
    return audit_result


def save_audit_report(audit: Dict[str, Any], output_path: str = "reports/data_audit_report.md") -> str:
    """Exports the audit report as a comprehensive Markdown report file.

    Args:
        audit: Structured audit dictionary.
        output_path: Target markdown file path.

    Returns:
        Path to the saved report.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    t = audit["target_stats"]

    lines = [
        "# Crystal2Power — Dataset Audit Report",
        "",
        f"- **Dataset File**: `{audit['filename']}`",
        f"- **Total Rows**: {audit['total_rows']:,}",
        f"- **Total Columns**: {audit['total_columns']}",
        f"- **Duplicate Rows**: {audit['duplicate_rows']:,}",
        "",
        "## Target Column (`JV_default_PCE`) Analysis",
        f"- **Present**: {'Yes' if t['present'] else 'NO'}",
        f"- **Valid PCE Records**: {t['valid_count']:,} ({round(t['valid_count']/audit['total_rows']*100, 2) if audit['total_rows']>0 else 0}%)",
        f"- **Missing Target Records**: {t['missing_count']:,}",
        f"- **Observed Range**: [{t['min']}, {t['max']}] %",
        f"- **Mean**: {t['mean']} %",
        f"- **Median**: {t['median']} %",
        f"- **Std Dev**: {t['std']} %",
        "",
        "### Quality Warnings",
    ]

    all_warnings = audit["general_warnings"] + t["quality_warnings"]
    if all_warnings:
        for w in all_warnings:
            lines.append(f"- ⚠️ {w}")
    else:
        lines.append("- No critical data quality issues flagged.")

    lines.extend([
        "",
        "## Columns Profile",
        "| Column Name | Data Type | Missing Count | Missing % | Unique Count | Sample |",
        "| :--- | :--- | :--- | :--- | :--- | :--- |"
    ])

    for p in audit["column_profiles"]:
        lines.append(
            f"| `{p['column']}` | `{p['dtype']}` | {p['missing_count']} | {p['missing_pct']}% | {p['unique_count']} | {p['sample_value']} |"
        )

    report_text = "\n".join(lines)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(report_text)

    return output_path
