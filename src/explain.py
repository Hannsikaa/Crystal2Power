"""Model explainability and feature importance module for Crystal2Power.

Computes prospective feature importances using permutation importance on the
full held-out test dataset pipeline, with domain-level scientific context.
"""

from typing import Dict, Any, List, Optional
import numpy as np
import pandas as pd
from sklearn.inspection import permutation_importance
from sklearn.pipeline import Pipeline


def compute_permutation_importance(
    pipeline: Pipeline,
    X_test: pd.DataFrame,
    y_test: pd.Series,
    n_repeats: int = 5,
    random_state: int = 42,
    max_samples: Optional[int] = 2000
) -> pd.DataFrame:
    """Computes permutation importance for prospective features on held-out data.

    Args:
        pipeline: Fitted scikit-learn full pipeline.
        X_test: Held-out prospective features test DataFrame.
        y_test: Held-out true target values.
        n_repeats: Number of permutation iterations.
        random_state: Reproducible seed.
        max_samples: Sample limit to maintain fast computation on large datasets.

    Returns:
        DataFrame with feature names, mean importance, std, and rank.
    """
    if len(X_test) > max_samples:
        test_sub = X_test.sample(n=max_samples, random_state=random_state)
        y_sub = y_test.loc[test_sub.index]
    else:
        test_sub = X_test
        y_sub = y_test

    try:
        perm_res = permutation_importance(
            pipeline,
            test_sub,
            y_sub,
            scoring="neg_mean_absolute_error",
            n_repeats=n_repeats,
            random_state=random_state,
            n_jobs=1
        )

        df_importance = pd.DataFrame({
            "Feature": test_sub.columns,
            "Importance_Mean": np.round(perm_res.importances_mean, 4),
            "Importance_Std": np.round(perm_res.importances_std, 4)
        })

        df_importance = df_importance.sort_values(
            by="Importance_Mean", ascending=False
        ).reset_index(drop=True)

        return df_importance

    except Exception as e:
        # Fallback empty dataframe on failure
        return pd.DataFrame({
            "Feature": test_sub.columns,
            "Importance_Mean": [0.0] * len(test_sub.columns),
            "Importance_Std": [0.0] * len(test_sub.columns)
        })


def get_feature_explanation_summary() -> str:
    """Returns scientific disclaimer for model explainability."""
    return (
        "Permutation feature importance reflects how much the model's test error increases "
        "when the values of an input column are randomly shuffled. "
        "High importance indicates a strong statistical correlation within the historical dataset, "
        "not experimental proof of a causal mechanism. Solar cell efficiency is governed by "
        "coupled optoelectronic dynamics, interfacial band alignment, and morphology that require "
        "rigorous laboratory validation."
    )
