# Functions to execute trading strategy
# 
# 1. Get user input indicating whether to use Simple Moving Average (SMA) or Exponential Moving Average (EMA)
# 2. Identify trades using a DataFrame with computed indicators and stores transactions in a DataFrame
# 3. Extracting the trades from the main Dataframe and storing them in a separate DataFrame
# 4. Calculate profits by looping through all executed trades, and comparing the total profits with the buy-hold strategy
# 5. Running the entire pipeline and printing the results

import pandas as pd

def get_strategy_choice():
    """
    This function is designed to be used in the main script with variable use_ema which stores Boolean value
    :return: Boolean value True which means EMA, or False which means SMA
    """
    strategy = input("Select strategy ('EMA' or 'SMA'): ").strip().upper()
    while True:
        if strategy in ['SMA', 'EMA']:
            return strategy
        else:
            print('Please enter a valid response.')
            strategy = input("Select strategy ('EMA' or 'SMA'): ").strip().upper()

def identify_trades(df, hist_col='Histogram_EMA'):
    """
    Annotates the main DataFrame with trade actions based on MACD histogram crossover by looping through series.
    Adds columns: 'trade_action', 'trade_price', 'entry_price', 'trade_id'
    Does not compute profit or advanced features (keeps it light for ML or visualization).
    """

    # Initialize trade annotation columns
    df['trade_action'] = None
    df['trade_price'] = None
    df['entry_price'] = None
    df['trade_id'] = None

    action = 'BUY'
    last_buy_price = None
    trade_id = 0

    for i in range(1, len(df)):
        prev = df[hist_col].iloc[i - 1]
        curr = df[hist_col].iloc[i]
        price = df['price'].iloc[i]
        index = df.index[i]

        if pd.isna(prev) or pd.isna(curr):
            continue  # Skip rows with missing data, used for the first few rows with no histogram data

        # Buy based on condition
        if action == 'BUY' and prev < 0 and curr > 0:
            df.loc[index, 'trade_action'] = 'BUY'
            df.loc[index, 'trade_price'] = price
            df.loc[index, 'entry_price'] = price
            df.loc[index, 'trade_id'] = trade_id
            last_buy_price = price
            action = 'SELL'
 
        # Sell based on condition
        elif action == 'SELL' and prev > 0 and curr < 0 and (price * 0.99875) > last_buy_price:
            df.loc[index, 'trade_action'] = 'SELL'
            df.loc[index, 'trade_price'] = price
            df.loc[index, 'entry_price'] = last_buy_price
            df.loc[index, 'trade_id'] = trade_id
            action = 'BUY'
            trade_id += 1

    # To close the last sale on the last available date if it ends on a BUY (even if not profitable)
    if action == 'SELL' and last_buy_price is not None:
        final_index = df.index[-1]
        final_price = df['price'].iloc[-1]

        # Make the last entry a SELL and add relevant details
        df.loc[final_index, 'trade_action'] = 'SELL'
        df.loc[final_index, 'trade_price'] = final_price
        df.loc[final_index, 'entry_price'] = last_buy_price
        df.loc[final_index, 'trade_id'] = trade_id

    return df

def get_executed_trades(df):
    """
    Extracts only rows where a trade was executed.
    Returns a DataFrame with columns: date, action, price, trade_id
    """
    trades = df[df['trade_action'].notna()][
        ['trade_action', 'trade_price', 'entry_price', 'trade_id']
    ].copy()

    # Renames columns
    trades = trades.rename(columns={
        'trade_action': 'action',
        'trade_price': 'price'
    })

    # Creates new column of date using the index (whch is the dates)
    trades['date'] = trades.index
    # Resets the index to numbers
    trades.reset_index(drop=True, inplace=True)

    return trades

def calculate_trade_profit(trades, df, fee=0.00125):
    """
    Calculates total profit from trade actions.
    Also calculates buy-hold profit.
    :param fee: Transaction fee for selling
    Returns: (buy_sell_profit, buy_hold_profit)
    """
    profit = 0
    net_sell = 0
    buy_price = None

    for i in range(len(trades)):
        if trades['action'].iloc[i] == 'BUY':
            buy_price = trades['price'].iloc[i]
            profit -= round(buy_price, 2)
        elif trades['action'].iloc[i] == 'SELL' and buy_price is not None:
            sell_price = trades['price'].iloc[i]
            net_sell = sell_price * (1 - fee)
            profit += round(net_sell, 2)
            buy_price = None

    # Buy-Hold: first price to last price
    first_price = df['price'].iloc[0]
    last_price = df['price'].iloc[-1]
    buy_hold_profit = round(((last_price * (1 - fee)) - first_price), 2)

    return profit, buy_hold_profit

def run_trading_strategy(df, fee=0.00125):
    """
    Runs the full strategy selection, trading simulation, and profit comparison.
    1. User selects SMA or EMA
    2. Trades are identified and annotated into the DataFrame
    3. Executed trades are extracted
    4. Profits from Buy-Sell vs Buy-Hold are compared
    5. Results are printed
    :returns: DataFrame of trades
    """
    from trading_strategy import (
        get_strategy_choice,
        identify_trades,
        get_executed_trades,
        calculate_trade_profit
    )

    # Step 1: User selects strategy
    strategy = get_strategy_choice()
    suffix = strategy.upper()
    hist_col = f'Histogram_{suffix}'

    print(f"\nRunning {strategy} strategy using '{hist_col}'...\n")

    # Step 2: Identify trades and annotate DataFrame
    df = identify_trades(df, hist_col=hist_col)

    # Step 3: Extract trades
    trades = get_executed_trades(df)

    # Step 4: Calculate profits
    profit, buy_hold = calculate_trade_profit(trades, df, fee=fee)

    # Step 5: Print results
    print("🛒 Trade Actions:")
    print(trades)

    print("\n📊 Profit Summary:")
    print(f"Buy-Sell strategy profit: {profit:.2f}")
    print(f"Buy-Hold strategy profit: {buy_hold:.2f}")

    if profit > buy_hold:
        print("✅ Buy-Sell strategy outperformed Buy-Hold.")
    elif profit < buy_hold:
        print("📉 Buy-Hold would have been better.")
    else:
        print("⚖️ Both strategies performed equally.")

    return trades   # Return DataFrame of trades to allow for export