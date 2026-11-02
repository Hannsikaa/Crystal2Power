"""Unit tests for target leakage audit."""

from src.leakage import audit_target_leakage


def test_leakage_exclusion_strict():
    columns = [
        "Cell_stack_sequence",
        "Cell_architecture",
        "Perovskite_composition_short_form",
        "JV_default_Voc",  # Must be excluded
        "JV_default_Jsc",  # Must be excluded
        "JV_default_FF",   # Must be excluded
        "JV_measured",     # Must be excluded
        "JV_default_PCE"   # Must be excluded (target)
    ]

    usable_features, excluded_cols, audit_df = audit_target_leakage(columns, target_col="JV_default_PCE")

    # Verify exclusions
    assert "JV_default_PCE" in excluded_cols
    assert "JV_default_Voc" in excluded_cols
    assert "JV_default_Jsc" in excluded_cols
    assert "JV_default_FF" in excluded_cols
    assert "JV_measured" in excluded_cols

    # Verify safe features are retained
    assert "Cell_stack_sequence" in usable_features
    assert "Cell_architecture" in usable_features
    assert "Perovskite_composition_short_form" in usable_features

    # Verify audit table rows
    assert len(audit_df) == len(columns)
    excluded_records = audit_df[audit_df["Status"] == "EXCLUDED"]
    assert len(excluded_records) == 5
