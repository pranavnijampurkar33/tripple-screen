"""Generate Ripple, Wave, and Tide chart PNGs for a symbol."""

from __future__ import annotations

from pathlib import Path

from layers.charts.ripple_layer_chart import render_ripple
from layers.charts.tide_layer_chart import render_tide
from layers.charts.wave_layer_chart import render_wave
from layers.config import RIPPLE, TIDE, WAVE, WAVE_SR
from layers.dates import AsOfDate
from layers.paths import chart_path, make_run_output_dir
from layers.symbols import resolve_ticker


def generate(
    symbol: str = "RELIANCE",
    ripple_tf: str = RIPPLE.default_interval,
    wave_tf: str = WAVE.default_interval,
    tide_tf: str = TIDE.default_interval,
    as_of_date: AsOfDate = None,
) -> Path:
    """
    Build three layer charts and save under data/out/{YYMMDDHHMM}_{SYMBOL}/.

    Returns the run output directory.
    """
    ticker = resolve_ticker(symbol)
    run_dir = make_run_output_dir(symbol, as_of_date=as_of_date)

    ripple_out = chart_path(run_dir, "ripple", ripple_tf, RIPPLE.lookback_days, RIPPLE.chart_bars)
    wave_out = chart_path(run_dir, "wave", wave_tf, WAVE.lookback_days, WAVE.chart_bars)
    wave_sr_out = chart_path(run_dir, "wave_sr", wave_tf, WAVE_SR.lookback_days, WAVE_SR.chart_bars)
    tide_out = chart_path(run_dir, "tide", tide_tf, TIDE.lookback_days, TIDE.chart_bars)

    _, macd_signal = render_tide(ticker, tide_tf, tide_out, lookback_days=TIDE.lookback_days, as_of_date=as_of_date)
    print(f"Wrote {tide_out}")

    render_ripple(ticker, ripple_tf, ripple_out, lookback_days=RIPPLE.lookback_days, as_of_date=as_of_date)
    print(f"Wrote {ripple_out}")

    render_wave(
        ticker,
        wave_tf,
        wave_out,
        lookback_days=WAVE.lookback_days,
        trend=macd_signal.trend,
        sr_output_path=wave_sr_out,
        sr_lookback_days=WAVE_SR.lookback_days,
        sr_sessions=WAVE_SR.chart_bars,
        as_of_date=as_of_date,
    )
    
    print(f"Wrote {wave_out}")
    print(f"Wrote {wave_sr_out}")

    return run_dir
