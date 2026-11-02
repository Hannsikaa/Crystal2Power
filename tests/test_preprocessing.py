"""Unit tests for preprocessing and feature cleaning."""

import numpy as np
import pandas as pd
from src.preprocessing import (
    extract_first_float,
    extract_max_float,
    extract_sum_float,
    SolarCellFeatureCleaner,
    build_preprocessor_pipeline,
    identify_column_types
)


def test_float_extractors():
    # extract_first_float
    assert extract_first_float("400.0 nm") == 400.0
    assert extract_first_float("500.0 | nan") == 500.0
    assert np.isnan(extract_first_float("Unknown"))
    assert np.isnan(extract_first_float(None))

    # extract_max_float
    assert extract_max_float("70.0 >> 100.0") == 100.0
    assert extract_max_float("Unknown >> 120") == 120.0
    assert extract_max_float("60; 100") == 100.0
    assert np.isnan(extract_max_float("Unknown"))

    # extract_sum_float
    assert extract_sum_float("10.0 | 100.0") == 110.0
    assert extract_sum_float("80.0") == 80.0
    assert np.isnan(extract_sum_float("Unknown"))


def test_feature_cleaner():
    df = pd.DataFrame({
        "Perovskite_thickness": ["400.0", "500.0 | nan", "nan"],
        "Perovskite_deposition_thermal_annealing_temperature": ["100", "70.0 >> 100.0", "Unknown"],
        "Perovskite_deposition_thermal_annealing_time": ["10.0", "1.0; 2.0", "Unknown"],
        "Backcontact_thickness_list": ["90.0", "10.0 | 100.0", "nan"],
        "Perovskite_deposition_quenching_induced_crystallisation": ["True", "False", "1"],
        "Encapsulation": [True, False, "yes"],
        "Cell_architecture": ["nip", "pin", None]
    })

    cleaner = SolarCellFeatureCleaner()
    df_clean = cleaner.transform(df)

    assert df_clean["Perovskite_thickness"].iloc[0] == 400.0
    assert df_clean["Perovskite_thickness"].iloc[1] == 500.0
    assert df_clean["Perovskite_deposition_thermal_annealing_temperature"].iloc[1] == 100.0
    assert df_clean["Backcontact_thickness_list"].iloc[1] == 110.0
    assert df_clean["Perovskite_deposition_quenching_induced_crystallisation"].iloc[0] == 1.0
    assert df_clean["Encapsulation"].iloc[2] == 1.0
    assert df_clean["Cell_architecture"].iloc[2] == "Unknown"


def test_unseen_category_at_inference():
    # Train data
    df_train = pd.DataFrame({
        "Cell_architecture": ["nip", "pin", "nip"],
        "Perovskite_composition_a_ions": ["Cs", "MA", "FA"],
        "Perovskite_thickness": [400.0, 350.0, 420.0]
    })

    num_cols, cat_cols = identify_column_types(df_train)
    preprocessor = build_preprocessor_pipeline(num_cols, cat_cols)
    preprocessor.fit(df_train)

    # Test data with unseen category 'bi-facial' and 'Rb'
    df_test = pd.DataFrame({
        "Cell_architecture": ["bi-facial"],  # Unseen!
        "Perovskite_composition_a_ions": ["Rb"],  # Unseen!
        "Perovskite_thickness": [380.0]
    })

    transformed = preprocessor.transform(df_test)
    assert transformed.shape[0] == 1
    assert not np.isnan(transformed).any()
