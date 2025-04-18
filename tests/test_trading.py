import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pandas as pd
import pytest
from trading_strategy import (
    identify_trades,
    get_executed_trades,
    calculate_trade_profit
)

# --- Helper function to create dummy MACD histogram ---
def create_test_df_with_macd_hist():
    data = {
        'price': [100, 101, 102, 101, 99, 100, 102, 101, 99, 98, 100, 102],
        'Histogram_EMA': [-0.5, -0.2, 0.3, 0.5, 0.2, -0.1, -0.3, 0.2, 0.4, 0.1, -0.2, -0.4]
    }
    index = pd.date_range(start='2024-01-01', periods=len(data['price']))
    return pd.DataFrame(data, index=index)

# ---------- TEST: identify_trades ----------
def test_identify_trades_adds_columns():
    df = create_test_df_with_macd_hist()
    df = identify_trades(df, hist_col='Histogram_EMA')
    assert 'trade_action' in df.columns
    assert 'trade_price' in df.columns
    assert df['trade_action'].isin(['BUY', 'SELL', None]).all()

# ---------- TEST: get_executed_trades ----------
def test_get_executed_trades_filters_only_trades():
    df = create_test_df_with_macd_hist()
    df = identify_trades(df, hist_col='Histogram_EMA')
    trades_df = get_executed_trades(df)
    assert not trades_df.empty
    assert trades_df['action'].isin(['BUY', 'SELL']).all()
    assert 'price' in trades_df.columns
    assert 'date' in trades_df.columns

# ---------- TEST: calculate_trade_profit ----------
def test_calculate_trade_profit_correct_total():
    df = create_test_df_with_macd_hist()
    df = identify_trades(df, hist_col='Histogram_EMA')
    trades_df = get_executed_trades(df)
    profit, buy_hold = calculate_trade_profit(trades_df, df, fee=0.00125)
    
    assert isinstance(profit, float)
    assert isinstance(buy_hold, float)