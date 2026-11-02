"""Unit tests for training, evaluation, persistence, and prediction pipeline."""

import os
import shutil
import tempfile
import pytest
import numpy as np
import pandas as pd
from sklearn.pipeline import Pipeline
from src.train import (
    prepare_train_test_data,
    train_and_compare_models,
    save_trained_pipeline,
    load_saved_pipeline
)
from src.predict import predict_single_device, predict_batch_devices


@pytest.fixture
def synthetic_perovskite_df():
    """Generates a small valid synthetic dataset for automated testing."""
    np.random.seed(42)
    n = 60
    data = {
        "Cell_stack_sequence": ["SLG | FTO | TiO2 | Perovskite | Spiro | Au"] * n,
        "Cell_architecture": np.random.choice(["nip", "pin"], size=n),
        "Substrate_stack_sequence": ["SLG | FTO"] * n,
        "ETL_stack_sequence": np.random.choice(["TiO2", "SnO2"], size=n),
        "ETL_deposition_procedure": ["Spin-coating"] * n,
        "Perovskite_composition_a_ions": np.random.choice(["Cs", "MA", "FA"], size=n),
        "Perovskite_composition_b_ions": ["Pb"] * n,
        "Perovskite_composition_c_ions": np.random.choice(["I", "Br"], size=n),
        "Perovskite_composition_short_form": ["MAPbI3"] * n,
        "Perovskite_thickness": np.random.uniform(300, 600, size=n).astype(str),
        "Perovskite_deposition_number_of_deposition_steps": [1] * n,
        "Perovskite_deposition_procedure": ["Spin-coating"] * n,
        "Perovskite_deposition_solvents": ["DMF | DMSO"] * n,
        "Perovskite_deposition_quenching_induced_crystallisation": [True] * n,
        "Perovskite_deposition_thermal_annealing_temperature": ["100"] * n,
        "Perovskite_deposition_thermal_annealing_time": ["10.0"] * n,
        "HTL_stack_sequence": ["Spiro-MeOTAD"] * n,
        "HTL_deposition_procedure": ["Spin-coating"] * n,
        "Backcontact_stack_sequence": ["Au"] * n,
        "Backcontact_thickness_list": ["100.0"] * n,
        "Backcontact_deposition_procedure": ["Evaporation"] * n,
        "Encapsulation": [False] * n,
        "Encapsulation_stack_sequence": ["None"] * n,
        # Leakage fields
        "JV_measured": [True] * n,
        "JV_default_Voc": np.random.uniform(0.9, 1.2, size=n),
        "JV_default_Jsc": np.random.uniform(18.0, 24.0, size=n),
        "JV_default_FF": np.random.uniform(0.65, 0.80, size=n),
        # Target
        "JV_default_PCE": np.random.uniform(10.0, 22.0, size=n)
    }
    return pd.DataFrame(data)


def test_full_pipeline_train_and_predict(synthetic_perovskite_df):
    X_train, X_test, y_train, y_test, features, excluded, leakage_df = prepare_train_test_data(
        synthetic_perovskite_df, target_col="JV_default_PCE", test_size=0.25, random_state=42
    )

    assert len(X_train) == 45
    assert len(X_test) == 15
    assert "JV_default_PCE" not in features
    assert "JV_default_Voc" not in features

    best_pipeline, best_name, evaluations, cv_scores = train_and_compare_models(
        X_train, y_train, X_test, y_test, random_state=42, cv_folds=2
    )

    assert isinstance(best_pipeline, Pipeline)
    assert best_name in evaluations
    assert "DummyRegressor (Baseline)" in evaluations

    # Test persistence
    temp_dir = tempfile.mkdtemp()
    try:
        saved_path = save_trained_pipeline(
            best_pipeline,
            metadata={"best_model": best_name, "features": features},
            model_dir=temp_dir,
            filename="test_model.joblib"
        )
        assert os.path.exists(saved_path)

        reloaded_pipe, meta = load_saved_pipeline(saved_path)
        assert meta["best_model"] == best_name

        # Single prediction
        sample_input = {
            "Cell_architecture": "nip",
            "Perovskite_composition_a_ions": "Cs",
            "Perovskite_thickness": "450.0",
            "Perovskite_deposition_thermal_annealing_temperature": "100"
        }
        pred_res = predict_single_device(reloaded_pipe, sample_input, features)
        assert "predicted_pce" in pred_res
        assert isinstance(pred_res["predicted_pce"], float)
        assert pred_res["predicted_pce"] >= 0.0

        # Test incomplete input handling (empty input should gracefully impute and predict)
        empty_input = {}
        empty_pred = predict_single_device(reloaded_pipe, empty_input, features)
        assert "predicted_pce" in empty_pred
        assert isinstance(empty_pred["predicted_pce"], float)

        # Test extrapolation warning
        training_summary = {
            "numeric_ranges": {
                "Perovskite_thickness": {"min": 100.0, "max": 600.0}
            }
        }
        out_of_range_input = {"Perovskite_thickness": "9999.0"}
        warn_pred = predict_single_device(reloaded_pipe, out_of_range_input, features, training_summary=training_summary)
        assert any("lies outside observed training range" in w for w in warn_pred["warnings"])

    finally:
        shutil.rmtree(temp_dir)


def test_app_importable():
    """Verify that app.py can be imported without errors."""
    import app
    assert hasattr(app, "st")

