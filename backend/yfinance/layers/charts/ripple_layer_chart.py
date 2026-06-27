"""Ripple layer: hourly candlesticks + Stochastic RSI."""

from __future__ import annotations

from pathlib import Path

from layers.charts._save import save_figure
from layers.config import RIPPLE
from layers.data.fetch import fetch_ohlc
from layers.dates import AsOfDate, as_of_label
from layers.indicators.stoch_rsi import stochastic_rsi, stoch_rsi_addplots
from layers.plot.candle import plot_candlestick


def render_ripple(
    ticker: str,
    interval: str,
    output_path: Path,
    *,
    sessions: int = RIPPLE.sessions,
    lookback_days: int | None = None,
    show_band: bool = RIPPLE.show_stoch_band,
    right_pad_bars: float = 2.25,
    as_of_date: AsOfDate = None,
) -> Path:
    lb = lookback_days if lookback_days is not None else RIPPLE.lookback_days

    df = fetch_ohlc(ticker, lb, interval, as_of_date=as_of_date)
    plot_df = df.tail(sessions).copy()

    k, d = stochastic_rsi(df["Close"])
    addplot = stoch_rsi_addplots(
        plot_df,
        k.reindex(plot_df.index),
        d.reindex(plot_df.index),
        panel=1,
        show_band=show_band,
    )

    as_of_title = f" — as of {label}" if (label := as_of_label(as_of_date)) else ""
    title = f"{ticker} — Ripple ({interval}) — last {sessions} bars{as_of_title}"
    fig, _axlist = plot_candlestick(
        plot_df,
        title=title,
        addplot=addplot,
        volume=False,
        right_pad_bars=right_pad_bars,
        panel_ratios=RIPPLE.panel_ratios,
        figscale=1.25,
    )
    save_figure(fig, output_path)
    return Path(output_path)
