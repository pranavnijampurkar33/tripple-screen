import yfinance as yf
import pandas as pd


def get_data(ticker, tf, start_date, end_date, market="nse"):
    """
    Downloads historical stock data using yfinance.

    Args:
        ticker (str): The stock ticker symbol.
        tf (str): The timeframe/interval for the data (e.g., '1d').
        start_date (datetime): The start date for data download.
        end_date (datetime): The end date for data download.

    Returns:
        pd.DataFrame: A DataFrame containing the historical stock data, or an empty DataFrame if no data is found.
    """
    if market == "nse":
        ticker = ticker + ".ns"
    print(f"Downloading data for {ticker} from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    df = yf.download(
        ticker,
        start=start_date,
        end=end_date,
        interval=tf,
        auto_adjust=False
    )

    df.dropna(inplace=True)

    # If yfinance returns multi-level columns, fix it
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    if df.empty:
        print(f"No data downloaded for {ticker}. Returning empty DataFrame.")

    return df


def get_nse_500():
    # URL for NSE 500 constituents (often found on NSE India's website or similar financial data portals)
    # This URL might change, so it's good to verify it if issues arise.
    url = "https://archives.nseindia.com/content/indices/ind_nifty500list.csv"
    nse500_symbols = []
    try:
        nse500_df = pd.read_csv(url)

        if 'Symbol' in nse500_df.columns:
            # Get the first 20 stock symbols
            nse500_symbols = nse500_df['Symbol'].tolist()
            print(f"Prepared the nse500_symbols and here is example {nse500_symbols[3]}")
        else:
            print("Error: 'Symbol' column not found in the downloaded data. Please check the CSV structure.")
            print("Available columns:", nse500_df.columns.tolist())

    except Exception as e:
        print(f"An error occurred while fetching or processing data: {e}")
        print("Please ensure the URL is correct and the website structure hasn't changed.")
    return nse500_symbols