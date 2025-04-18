# 📈 StockCalc — Technical Indicator & Trading Strategy Simulator

StockCalc is a Python-based data pipeline for analyzing stock price data using classic technical indicators such as **SMA**, **EMA**, **MACD**, and **Signal Line (MACD9)**. It supports **automated trade signal detection**, **profit simulation**, and **data export**, making it ideal for finance learners, analysts, and machine learning preprocessing.

---

## 🚀 Features

- 📥 Import stock data from `.csv` or `.xlsx`
- 📅 Forward fills in missing market dates (e.g., weekends, holidays)
- 📊 Computes:
  - Simple Moving Average (SMA) with custom period
  - Exponential Moving Average (EMA) with custom period
  - MACD Line (SMA/EMA)
  - Signal Line (MACD9)
  - MACD Histogram
- 💰 Identifies **buy/sell trade signals** based on MACD crossovers
- 🔍 Simulates trading strategies and compares:
  - Buy-Hold strategy
  - Buy-Sell strategy with transaction fees
- 📤 Exports final results and trades to file
- 🧪 Includes unit tests and integration tests using `pytest`

---

## 📁 Folder Structure
```
project/
├── main.ipynb                  # Main notebook to run the strategy pipeline
├── indicators.py               # Technical indicators (SMA, EMA, MACD, etc.)
├── trading_strategy.py         # Trade identification and profit calculation
├── data_loader.py              # Data import, validation, export utilities
├── tests/                      # Unit & integration test suite
│   ├── test_loader.py
│   ├── test_indicators.py
│   └── test_trading.py
├── SP_2016_2021.xlsx           # Example input stock file (CSV/XLSX) Can organise in a folder for future
├── outputs/                    # Final results and trade logs
├── requirements.txt            # List of requirements
└── README.md                   # This file
```
---

## 🧪 How to Run the Tests

```bash
# Run all tests
pytest tests/
```

You’ll get instant feedback on every function and integration pipeline.

## 📦 Requirements
- Python 3.8+
- pandas
- openpyxl (for .xlsx support)
- pytest (for running tests)

Install with:
```bash
pip install -r requirements.txt
```

## ✅ Usage Example
In main.ipynb, the workflow includes:
```
from data_loader import import_stock_file, validate_and_prepare_data
from indicators import calc_sma, calc_ema, calc_macd, calc_macd9, compute_histogram
from trading_strategy import identify_trades, get_executed_trades, calculate_trade_profit

df = import_stock_file("data/sample_stock_data.csv")
df = validate_and_prepare_data(df)
df = calc_ema(df, 12)
df = calc_ema(df, 26)
df = calc_macd(df)
df = calc_macd9(df, 'MACD_EMA')
df = compute_histogram(df, 'MACD_EMA', 'MACD9_EMA')
df = identify_trades(df, hist_col='Histogram_EMA')
trades = get_executed_trades(df)
profit, buy_hold = calculate_trade_profit(trades, df)
```
Export results:
```
from data_loader import export_stock_file

export_stock_file(df, "outputs/final_data.csv")
export_stock_file(trades, "outputs/trades_log.csv")
```

## 📊 Sample Output
- outputs/final_stock_data.xlsx: All technical indicators + trade annotations
- outputs/trades_data.xlsx: List of all BUY/SELL transactions with dates and prices
- Profit comparison printed in console

## ✨ Future Ideas
- 📈 Chart with buy/sell markers
- 📤 Real-time API data import (e.g. Alpha Vantage, Yahoo Finance)
- 🤖 ML-ready feature set
- 📊 Portfolio equity curve plotting

## 👨‍💻 Author
Created by Jakin Tan<br>
For SC1003 – Intro to Computational Thinking & Programming<br>
AY2024 Semester 2<br>
Nanyang Technological Institute
