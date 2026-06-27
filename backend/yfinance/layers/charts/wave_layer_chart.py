"""Wave layer: daily candlesticks + Stochastic RSI."""

from __future__ import annotations

from pathlib import Path

from layers.charts._save import save_figure
from layers.config import WAVE, WAVE_SR
from layers.data.fetch import fetch_ohlc
from layers.dates import AsOfDate, as_of_label
from layers.indicators.stoch_rsi import (
    annotate_stoch_rsi_highlights,
    detect_stoch_rsi_crossovers,
    select_tide_gated_stoch_highlights,
    stoch_highlight_status_text,
    stochastic_rsi,
    stoch_rsi_addplots,
)
from layers.indicators.support_resistance import support_resistance_levels
from layers.plot.candle import plot_candlestick

def render_wave_sr(
    ticker: str,
    interval: str,
    output_path: Path,
    df,
    sr_result,
    *,
    sessions: int = WAVE_SR.chart_bars,
    right_pad_bars: float = 2.25,
    as_of_date: AsOfDate = None,
) -> Path:
    """Render the Wave S/R chart over the configured recent candles."""
    plot_df = df.tail(sessions).copy()
    as_of_title = f" — as of {label}" if (label := as_of_label(as_of_date)) else ""
    title = f"{ticker} — Wave S/R ({interval}) — last {sessions} bars{as_of_title}"
    fig, _axlist = plot_candlestick(
        plot_df,
        title=title,
        hlines=sr_result.hlines_dict(),
        right_pad_bars=right_pad_bars,
        panel_ratios=(5, 1.0),
        figscale=1.25,
    )
    save_figure(fig, output_path)
    return Path(output_path)


def render_wave(
    ticker: str,
    interval: str,
    output_path: Path,
    *,
    sessions: int = WAVE.sessions,
    lookback_days: int | None = None,
    show_band: bool = WAVE.show_stoch_band,
    right_pad_bars: float = 2.25,
    trend: str | None = None,
    sr_output_path: Path | None = None,
    sr_lookback_days: int = WAVE_SR.lookback_days,
    sr_sessions: int = WAVE_SR.chart_bars,
    as_of_date: AsOfDate = None,
) -> Path:
    wave_lb = lookback_days if lookback_days is not None else WAVE.lookback_days
    lb = max(wave_lb, sr_lookback_days)

    df = fetch_ohlc(ticker, lb, interval, as_of_date=as_of_date)
    plot_df = df.tail(sessions).copy()

    k, d = stochastic_rsi(df["Close"])
    plot_k = k.reindex(plot_df.index)
    plot_d = d.reindex(plot_df.index)
    sr_result = support_resistance_levels(df.tail(sr_lookback_days), candles=sr_sessions)
    crossovers = detect_stoch_rsi_crossovers(plot_k, plot_d)
    highlights = select_tide_gated_stoch_highlights(crossovers, trend)
    current_k = float(plot_k.dropna().iloc[-1]) if not plot_k.dropna().empty else None
    current_d = float(plot_d.dropna().iloc[-1]) if not plot_d.dropna().empty else None
    log_status_text = stoch_highlight_status_text(trend, highlights, current_k=current_k, current_d=current_d)
    chart_status_text = stoch_highlight_status_text(trend, highlights)
    print(log_status_text)
    print(sr_result.console_text())
    addplot = stoch_rsi_addplots(
        plot_df,
        plot_k,
        plot_d,
        show_band=show_band,
        highlights=highlights,
    )

    trend_title = f" — Tide {trend.upper()}" if trend else ""
    as_of_title = f" — as of {label}" if (label := as_of_label(as_of_date)) else ""
    title = f"{ticker} — Wave ({interval}) — last {sessions} bars{trend_title}{as_of_title}"
    fig, axlist = plot_candlestick(
        plot_df,
        title=title,
        addplot=addplot,
        hlines=sr_result.hlines_dict(),
        right_pad_bars=right_pad_bars,
        panel_ratios=WAVE.panel_ratios,
        figscale=1.25,
    )
    if highlights and len(axlist) > 4:
        annotate_stoch_rsi_highlights(axlist[4], plot_df, highlights, status_text=chart_status_text)
    elif len(axlist) > 4:
        annotate_stoch_rsi_highlights(axlist[4], plot_df, [], status_text=chart_status_text)
    save_figure(fig, output_path)

    if sr_output_path is not None:
        render_wave_sr(
            ticker,
            interval,
            sr_output_path,
            df,
            sr_result,
            sessions=sr_sessions,
            right_pad_bars=right_pad_bars,
            as_of_date=as_of_date,
        )
    return Path(output_path)
