"""Tide layer: weekly candlesticks + MACD line."""

from __future__ import annotations

from pathlib import Path

from layers.charts._save import save_figure
from layers.config import TIDE
from layers.data.fetch import fetch_ohlc
from layers.dates import AsOfDate, as_of_label
from layers.indicators.macd import MACD_PANEL, classify_macd_trend, macd, macd_addplots
from layers.plot.candle import plot_candlestick


def render_tide(
    ticker: str,
    interval: str,
    output_path: Path,
    *,
    sessions: int = TIDE.sessions,
    lookback_days: int | None = None,
    right_pad_bars: float = 2.25,
    as_of_date: AsOfDate = None,
) -> tuple[Path, object]:
    lb = lookback_days if lookback_days is not None else TIDE.lookback_days

    df = fetch_ohlc(ticker, lb, interval, as_of_date=as_of_date)
    plot_df = df.tail(sessions).copy()

    macd_line, signal_line, hist = macd(df["Close"])
    macd_signal = classify_macd_trend(macd_line, signal_line, hist)
    print(f"MACD trend: {macd_signal.trend.upper()}")
    print(macd_signal.console_text())
    addplot = macd_addplots(plot_df, macd_line, trend_signal=macd_signal, panel=MACD_PANEL)

    as_of_title = f" — as of {label}" if (label := as_of_label(as_of_date)) else ""
    title = f"{ticker} — Tide ({interval}) — last {sessions} bars — MACD {macd_signal.trend.upper()}{as_of_title}"
    fig, _axlist = plot_candlestick(
        plot_df,
        title=title,
        addplot=addplot,
        volume=False,
        right_pad_bars=right_pad_bars,
        panel_ratios=TIDE.panel_ratios,
        figscale=1.25,
    )
    save_figure(fig, output_path)
    return Path(output_path), macd_signal
