"""Unit tests for data loader."""

import os
import io
import pytest
import pandas as pd
from src.data_loader import load_dataset, get_default_dataset_path


def test_load_dataset_from_csv():
    csv_data = "Cell_architecture,Perovskite_thickness,JV_default_PCE\nnip,400.0,18.5\npin,350.0,15.2\n"
    buf = io.StringIO(csv_data)
    buf.name = "sample.csv"

    df, meta = load_dataset(buf, target_col="JV_default_PCE")
    assert len(df) == 2
    assert meta["total_rows"] == 2
    assert meta["target_found"] is True
    assert meta["valid_target_rows"] == 2
    assert "JV_default_PCE" in df.columns


def test_load_dataset_missing_target():
    csv_data = "Cell_architecture,Perovskite_thickness\nnip,400.0\npin,350.0\n"
    buf = io.StringIO(csv_data)
    buf.name = "sample.csv"

    df, meta = load_dataset(buf, target_col="JV_default_PCE")
    assert meta["target_found"] is False
    assert meta["valid_target_rows"] == 0


def test_load_dataset_invalid_format():
    buf = io.StringIO("some,data\n1,2\n")
    buf.name = "bad_file.xyz"
    with pytest.raises(ValueError, match="Unsupported file format"):
        load_dataset(buf)


def test_load_empty_dataset():
    buf = io.StringIO("")
    buf.name = "empty.csv"
    with pytest.raises(ValueError):
        load_dataset(buf)
