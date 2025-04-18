import pandas as pd
import numpy as np
import pytest
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from indicators import (
    calc_sma,
    calc_ema,
    calc_macd,
    calc_macd9,
    compute_histogram
)

# Helper to create consistent price data
def create_df():
    return pd.DataFrame({'price': [100 + i for i in range(100)]}, index=pd.date_range('2024-01-01', periods=100))

# ---------- TEST: calc_sma ----------
def test_calc_sma_adds_column():
    df = create_df()
    result = calc_sma(df, 5)
    assert 'SMA5' in result.columns
    assert not result['SMA5'].isna().all()
    assert result['SMA5'].iloc[4] == sum([100, 101, 102, 103, 104]) / 5

# ---------- TEST: calc_ema ----------
def test_calc_ema_starts_with_sma():
    df = create_df()
    result = calc_ema(df, 5)
    assert 'EMA5' in result.columns
    assert round(result['EMA5'].iloc[4], 5) == round(result['SMA5'].iloc[4], 5) if 'SMA5' in result else True
    assert not result['EMA5'].isna().all()

# ---------- TEST: calc_macd ----------
def test_calc_macd_output():
    df = create_df()
    df = calc_ema(df, 12)
    df = calc_ema(df, 26)
    df = calc_macd(df)
    assert 'MACD_EMA' in df.columns
    assert df['MACD_EMA'].iloc[-1] == df['EMA12'].iloc[-1] - df['EMA26'].iloc[-1]

# ---------- TEST: calc_macd9 ----------
def test_calc_macd9_output():
    df = create_df()
    df = calc_ema(df, 12)
    df = calc_ema(df, 26)
    df = calc_macd(df)
    df = calc_macd9(df, macd_key='MACD_EMA')
    assert 'MACD9_EMA' in df.columns
    assert not df['MACD9_EMA'].isna().all()

# ---------- TEST: compute_histogram ----------
def test_compute_histogram_output():
    df = create_df()
    df = calc_ema(df, 12)
    df = calc_ema(df, 26)
    df = calc_macd(df)
    df = calc_macd9(df, macd_key='MACD_EMA')
    df = compute_histogram(df, macd_key='MACD_EMA')
    assert 'Histogram_EMA' in df.columns
    assert df['Histogram_EMA'].iloc[-1] == df['MACD_EMA'].iloc[-1] - df['MACD9_EMA'].iloc[-1]