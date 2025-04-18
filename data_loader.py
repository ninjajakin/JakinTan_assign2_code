# Functions for file selection and data importing
# 
# 1. Select the file and format you want to use
# 2. Importing the data into a Pandas DataFrame and validating it, ensuring data is in correct format
# 3. Filling in missing dates (forward fill) for non-trading days like weekends
# 4. Exporting the DataFrame with the added column into a new file

import pandas as pd
import os

def import_stock_file(filepath):
    """
    Imports a stock data file (CSV, XLS, XLSX).
    :param filepath: Path to the file
    :return: Pandas DataFrame
    """
    # Separate the extension of the file
    ext = os.path.splitext(filepath)[1].lower()

    if ext == '.csv':
        df = pd.read_csv(filepath)
    elif ext in ['.xls', '.xlsx']:
        df = pd.read_excel(filepath)
    else:
        raise ValueError(f"Unsupported file format: {ext}")
    
    return df

def validate_and_prepare_data(df, date_col=None, price_col=None):
    """
    Validates and prepares the stock data DataFrame for analysis.
    :param df: Raw DataFrame
    :param date_col: Name of the column containing dates
    :param price_col: Name of the column containing prices
    :return: Cleaned DataFrame with datetime index
    """
    df = df.copy()

    # Try to auto-detect columns if not given
    if date_col is None or price_col is None:
        date_candidates = ['date', 'datetime', 'timestamp']
        price_candidates = ['price', 'close', 'closing price', 'last']

        # Match best-guess columns
        date_col = next((col for col in df.columns if col.lower() in date_candidates), None)
        price_col = next((col for col in df.columns if col.lower() in price_candidates), None)

    if not date_col or not price_col:
        raise ValueError("Could not find suitable 'date' and 'price' columns.")

    # Rename to 'date' and 'price' for standardization
    df.rename(columns={date_col: 'date', price_col: 'price'}, inplace=True)

    # Convert to datetime
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df.dropna(subset=['date'], inplace=True)

    # Sort and set index
    df.sort_values(by='date', inplace=True)
    df.set_index('date', inplace=True)

    # Ensure price is numeric
    df['price'] = pd.to_numeric(df['price'], errors='coerce')
    df.dropna(subset=['price'], inplace=True)

    # Let user know what columns were mapped
    print(f"Using '{date_col}' as date column and '{price_col}' as price column.")

    return df

def fill_missing_dates(df, price_col='price'):
    """
    Fills missing dates in the stock price DataFrame and forward-fills missing prices.
    :param df: DataFrame with datetime index
    :param price_col: Name of the price column
    :return: DataFrame with filled dates
    """
    df = df.asfreq('D')  # daily frequency (includes weekends)
    df[price_col] = df[price_col].ffill()
    return df

def export_stock_file(df, filepath, overwrite=False):
    """
    Exports the DataFrame to a CSV or Excel file.
    If the file already exists, automatically appends a version number (_1, _2, etc.).
    
    :param df: DataFrame to export
    :param filepath: Desired filename (with .csv or .xlsx)
    """
    base, ext = os.path.splitext(filepath)
    ext = ext.lower()

    # Validate supported formats
    if ext not in ['.csv', '.xlsx']:
        raise ValueError(f"Unsupported export format: {ext}. Use .csv or .xlsx.")

    # Ensure parent folder exists
    folder = os.path.dirname(filepath)
    if folder and not os.path.exists(folder):
        os.makedirs(folder)
        print(f"📁 Created folder: {folder}")
        
    # Version control: check if file exists
    if not overwrite:
        version = 0
        new_filepath = filepath
        while os.path.exists(new_filepath):
            version += 1
            new_filepath = f"{base}_{version}{ext}"

    # Export based on file type
    if ext == '.csv':
        df.to_csv(new_filepath, index=True)
    else:  # .xlsx
        df.to_excel(new_filepath, index=True)

    print(f"✅ Data exported: {new_filepath}")