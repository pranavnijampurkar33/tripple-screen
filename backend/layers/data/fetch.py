"""OHLCV download via the yfinance library (PyPI package)."""

from __future__ import annotations

import pandas as pd
import yfinance as yf

from layers.dates import AsOfDate, as_of_download_window, filter_as_of


def fetch_ohlc(ticker: str, lookback_days: int, interval: str, *, as_of_date: AsOfDate = None) -> pd.DataFrame:
    t = yf.Ticker(ticker)
    window = as_of_download_window(as_of_date, lookback_days)
    if window:
        start, end = window
        df = t.history(start=start, end=end, interval=interval, auto_adjust=True)
    else:
        df = t.history(period=f"{lookback_days}d", interval=interval, auto_adjust=True)
    if df is None or df.empty:
        raise SystemExit(f"No data returned for {ticker!r} (period={lookback_days}d interval={interval}).")
    df = filter_as_of(df, as_of_date)
    if df.empty:
        raise SystemExit(f"No data returned for {ticker!r} on or before as-of date {as_of_date!r}.")
    df = df.rename(columns=str.title).rename(columns={"Adj close": "Adj Close"})
    need = {"Open", "High", "Low", "Close", "Volume"}
    missing = need - set(df.columns)
    if missing:
        raise SystemExit(f"Unexpected columns for {ticker!r}: missing {missing}")
    return df
