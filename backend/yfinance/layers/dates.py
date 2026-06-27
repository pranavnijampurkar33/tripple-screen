"""Date helpers for as-of chart generation."""

from __future__ import annotations

from datetime import date, datetime, timedelta

import pandas as pd

AsOfDate = str | date | datetime | pd.Timestamp | None


def parse_as_of_date(as_of_date: AsOfDate) -> date | None:
    """Parse a public YYYY-MM-DD as-of date input."""
    if as_of_date is None:
        return None
    if isinstance(as_of_date, datetime):
        return as_of_date.date()
    if isinstance(as_of_date, date):
        return as_of_date

    parsed = pd.to_datetime(as_of_date, errors="raise")
    return parsed.date()


def as_of_label(as_of_date: AsOfDate) -> str | None:
    parsed = parse_as_of_date(as_of_date)
    return parsed.isoformat() if parsed else None


def as_of_download_window(as_of_date: AsOfDate, lookback_days: int) -> tuple[date, date] | None:
    """Return inclusive-style fetch window as yfinance start/end dates.

    yfinance treats end dates as exclusive, so the returned end is the day after
    the requested as-of date.
    """
    parsed = parse_as_of_date(as_of_date)
    if parsed is None:
        return None
    return parsed - timedelta(days=lookback_days), parsed + timedelta(days=1)


def filter_as_of(df: pd.DataFrame, as_of_date: AsOfDate) -> pd.DataFrame:
    """Keep rows whose index is on or before the as-of date end-of-day."""
    parsed = parse_as_of_date(as_of_date)
    if parsed is None:
        return df

    cutoff = pd.Timestamp(parsed) + pd.Timedelta(days=1) - pd.Timedelta(nanoseconds=1)
    index = pd.DatetimeIndex(df.index)
    if index.tz is not None:
        cutoff = cutoff.tz_localize(index.tz)
    return df.loc[index <= cutoff]
