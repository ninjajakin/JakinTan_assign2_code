import pandas as pd
import pytest
import sys
import os
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from data_loader import (
    import_stock_file,
    validate_and_prepare_data,
    fill_missing_dates,
    export_stock_file
)

# ---------- TEST: import_stock_file ----------
def test_import_stock_file_csv(tmp_path):
    # Create a temporary CSV
    path = tmp_path / "test.csv"
    data = "date,price\n2024-01-01,100\n2024-01-02,101"
    path.write_text(data)

    df = import_stock_file(str(path))
    assert isinstance(df, pd.DataFrame)
    assert df.shape == (2, 2)

# ---------- TEST: validate_and_prepare_data ----------
def test_validate_and_prepare_with_explicit_columns():
    raw = pd.DataFrame({
        'my_date': ['2024-01-01', '2024-01-02', '2024-01-03'],
        'my_price': [100, 101.5, 103]
    })
    result = validate_and_prepare_data(raw, date_col='my_date', price_col='my_price')

    assert 'price' in result.columns
    assert result.index.name == 'date'
    assert result.shape == (3, 1)
    assert result['price'].iloc[0] == 100

def test_validate_and_prepare_with_autodetection():
    raw = pd.DataFrame({
        'Date': ['2024-01-01', '2024-01-02', '2024-01-03'],
        'Close': [100, 101, 102]
    })
    result = validate_and_prepare_data(raw)

    assert result.index.name == 'date'
    assert 'price' in result.columns
    assert result['price'].iloc[-1] == 102

def test_invalid_date_and_price_rows_are_removed():
    raw = pd.DataFrame({
        'Date': ['2024-01-01', 'not a date', '2024-01-03'],
        'Close': ['100', 'bad', '105']
    })
    result = validate_and_prepare_data(raw)

    assert result.shape[0] == 2  # One row with bad date and price should be removed
    assert result['price'].dtype in [float, int]

def test_error_when_no_valid_columns():
    raw = pd.DataFrame({
        'random': [1, 2, 3],
        'numbers': [4, 5, 6]
    })

    with pytest.raises(ValueError):
        validate_and_prepare_data(raw)

# ---------- TEST: fill_missing_dates ----------
def test_fill_missing_dates():
    dates = pd.to_datetime(['2024-01-01', '2024-01-03'])
    df = pd.DataFrame({'price': [100, 102]}, index=dates)

    df_filled = fill_missing_dates(df)

    assert df_filled.shape[0] == 3
    assert df_filled['price'].iloc[1] == 100
    assert pd.Timestamp('2024-01-02') in df_filled.index

# ---------- TEST: export_stock_file ----------
def test_export_stock_file_creates_file(tmp_path):
    df = pd.DataFrame({'price': [100, 101]}, index=pd.to_datetime(['2024-01-01', '2024-01-02']))

    out_path = tmp_path / "output_dir/test_output.csv"
    export_stock_file(df, str(out_path))

    assert os.path.exists(out_path)

def test_export_stock_file_versions(tmp_path):
    df = pd.DataFrame({'price': [100, 101]}, index=pd.to_datetime(['2024-01-01', '2024-01-02']))

    base_path = tmp_path / "test_output.csv"
    export_stock_file(df, str(base_path))
    export_stock_file(df, str(base_path))  # should version as test_output_1.csv

    assert os.path.exists(base_path)
    versioned_path = tmp_path / "test_output_1.csv"
    assert os.path.exists(versioned_path)