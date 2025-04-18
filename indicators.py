# Functions for calculations of stock indicators
#
# 1. Simple Moving Average (SMA) for n number of days
# 2. Exponential Moving Average (EMA) for n number of days
# 3. MACD Line value
# 4. Signal Line values, which is the EMA of the MACD Line where n=9
# 5. MACD Histogram, which is the difference between the MACD Line and Signal Line

import pandas as pd

def calc_sma(df, period, price_col='price'):
    """
    Computes the SMA for a given period
    :param df: Pandas DataFrame with columns 'date' and 'price'
    :param period: Number of days, n, for SMA calculation
    :return: DataFrame with new SMA column added
    """
    df[f'SMA{period}'] = df[price_col].rolling(window=period).mean()
    return df

def calc_ema(df, period, price_col='price', output_col=None):
    """
    Computes the EMA for a given period
    :param df: Pandas DataFrame with columns 'date' and 'price'
    :param period: Number of days, n, for SMA calculation
    :param price_col: The name of the column containing the prices in DataFrame df
    :param output_col: The name of the column that will store the EMA values from this function
    :return: DataFrame with new EMA column added
    """
    # Default name of output column
    if output_col is None:
        output_col = f'EMA{period}'

    # Calculate first SMA value
    sma_val = df[price_col].iloc[:period].mean()
    # Create a series containing sma_val as the first value, but with index of (period-1) which will be a date
    ema_seed = pd.Series([sma_val], index=[df.index[period - 1]])
    # Create a series containing the rest of the prices after the SMA value with index (period) onwards
    remaining_prices = df[price_col].iloc[period:]

    # Create series combining sma_val with the rest of the prices. The indices will be appended in order
    seeded_series = pd.concat([ema_seed, remaining_prices])
    # Calculate EMA with the first value as the SMA, storing it in a series with indices of dates in order
    ema_series = seeded_series.ewm(span=period, adjust=False).mean()

    # Attributing the whole series to new column in the DataFrame
    df[output_col] = [None] * (period - 1) + list(ema_series)
    return df

def calc_macd(df, short_period=12, long_period=26, method='EMA'):
    """
    Computes the MACD values for each date
    MACD = MA12 - MA26 (MA can be either SMA or EMA)
    :param df: Pandas DataFrame with columns 'date' and MA
    :param short_period: n of MA, default value 12
    :param long_period: n of MA, default value 26
    :return: DataFrame with new MACD column added
    """
    short_key = f"{method}{short_period}"
    long_key = f"{method}{long_period}"
    macd_key = f"MACD_{method}"

    # Will need to do exception handling here if EMA/SMA 12 and 26 have not yet been calculated
    try:
        df[macd_key] = df[short_key] - df[long_key]
    except:
        print(f"Error, {method}{short_key} or {method}{long_key} has not yet been calculated")
    return df

def calc_macd9(df, period=9, macd_key=None):
    """
    Computes the 9-day EMA of the MACD line (MACD9 / Signal Line).
    :param df: Pandas DataFrame with columns 'date' and MACD_EMA or SMA
    :param macd_key: Name of MACD column (MACD_EMA or MACD_SMA)
    """
    try:
        macd9_key = macd_key.replace("MACD", "MACD9")
    except:
        print('Column selected is not a MACD column.')

    macd_sma_val = df[macd_key].iloc[:period].mean()

    macd9_seed = pd.Series([macd_sma_val], index=[df.index[period-1]])

    remaining_val = df[macd_key].iloc[period:]


    seeded_series = pd.concat([macd9_seed, remaining_val])
    macd9_series = seeded_series.ewm(span=period, adjust=False).mean()

    df[macd9_key] = [None] * (period - 1) + list(macd9_series)
    return df

def compute_histogram(df, macd_key):
    """
    Computes the MACD Histogram: MACD - MACD9
    :param df: Pandas DataFrame with columns 'date' and MACD_EMA or SMA and MACD9_EMA or SMA
    :param macd_key: Name of MACD column (MACD_EMA or MACD_SMA)
    """
    macd9_key = macd_key.replace("MACD", "MACD9")
    hist_key = macd_key.replace("MACD", "Histogram")
    df[hist_key] = df[macd_key] - df[macd9_key]
    return df

