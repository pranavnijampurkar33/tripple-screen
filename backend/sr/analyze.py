import pytz # Ensure pytz is imported for timezone handling
from sr.utils import plot_chart
import pandas as pd
import mplfinance as mpf
import pandas as pd
import matplotlib.pyplot as plt
from layers.indicators.support_resistance import support_resistance_levels


def get_sr_standard(df, ticker, window=25):
    print(f"\n--- Analyzing {ticker} ---")

    if df.empty:
        print(f"No data provided for {ticker}. Skipping analysis.")
        return

    current_price = df["Close"].iloc[-1]
    print(f"Current Price: {round(current_price, 2)}")
    # print(df.tail())

    sr_result = support_resistance_levels(df, candles=90, resistance_window=window)
    hlines_dict_support_strat = sr_result.hlines_dict()
    for level in sr_result.levels:
        print(f"{level.label}({level.color}):".ljust(40), round(level.value, 2))
    plot_chart(df, f"{ticker}: Recent Support + Pullback Resistance After Support", hlines_dict= hlines_dict_support_strat)
