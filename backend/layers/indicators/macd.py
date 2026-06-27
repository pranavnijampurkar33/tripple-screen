"""MACD (12, 26, 9) calculation and mplfinance addplot helpers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import numpy as np
import pandas as pd

MACD_PANEL = 1  # Tide: panel 0=price, 1=MACD (no volume)
MACD_FAST = 12
MACD_SLOW = 26
MACD_SIGNAL = 9
MACD_FLAT_TOLERANCE = 1e-6

MacdTrend = Literal["bullish", "bearish", "neutral"]


@dataclass(frozen=True)
class MacdTrendSignal:
    trend: MacdTrend
    reason: str
    context: str
    macd: float
    signal: float
    histogram: float

    @property
    def is_bullish(self) -> bool:
        return self.trend == "bullish"

    @property
    def is_bearish(self) -> bool:
        return self.trend == "bearish"

    def console_text(self, *, prefix: str = "Tide MACD") -> str:
        return (
            f"{prefix}: {self.trend.upper()} | {self.reason} | {self.context} | "
            f"MACD={self.macd:.2f} Signal={self.signal:.2f} Hist={self.histogram:.2f}"
        )


def macd(
    close: pd.Series,
    fast: int = MACD_FAST,
    slow: int = MACD_SLOW,
    signal: int = MACD_SIGNAL,
) -> tuple[pd.Series, pd.Series, pd.Series]:
    """Return MACD line, signal line, and histogram (MACD - signal)."""
    ema_fast = close.ewm(span=fast, adjust=False).mean()
    ema_slow = close.ewm(span=slow, adjust=False).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    histogram = macd_line - signal_line
    return macd_line, signal_line, histogram


def _direction(value: float, *, tolerance: float) -> int:
    if value > tolerance:
        return 1
    if value < -tolerance:
        return -1
    return 0


def classify_macd_trend(
    macd_line: pd.Series,
    signal_line: pd.Series,
    histogram: pd.Series,
    *,
    tolerance: float = MACD_FLAT_TOLERANCE,
) -> MacdTrendSignal:
    """Classify the latest Tide MACD as bullish, bearish, or neutral."""
    data = pd.concat(
        [macd_line.rename("macd"), signal_line.rename("signal"), histogram.rename("histogram")],
        axis=1,
    ).dropna()
    if len(data) < 4:
        return MacdTrendSignal("neutral", "insufficient history", "unconfirmed", np.nan, np.nan, np.nan)

    latest = data.iloc[-1]
    deltas = data["macd"].diff().iloc[-3:]
    hist_delta = float(data["histogram"].iloc[-1] - data["histogram"].iloc[-2])

    latest_dir = _direction(float(deltas.iloc[-1]), tolerance=tolerance)
    prev_dir = _direction(float(deltas.iloc[-2]), tolerance=tolerance)
    earlier_dir = _direction(float(deltas.iloc[-3]), tolerance=tolerance)
    hist_dir = _direction(hist_delta, tolerance=tolerance)

    macd_value = float(latest["macd"])
    signal_value = float(latest["signal"])
    hist_value = float(latest["histogram"])

    improving = hist_dir > 0 or hist_value > tolerance
    weakening = hist_dir < 0 or hist_value < -tolerance

    bullish_reason = ""
    bearish_reason = ""
    if latest_dir > 0:
        bullish_reason = "uptick" if prev_dir <= 0 else "up"
    elif latest_dir == 0 and prev_dir <= 0 and earlier_dir < 0:
        bullish_reason = "flat-after-down"

    if latest_dir < 0:
        bearish_reason = "downtick" if prev_dir >= 0 else "down"
    elif latest_dir == 0 and prev_dir >= 0 and earlier_dir > 0:
        bearish_reason = "flat-after-up"

    if bullish_reason and improving:
        context = "strong bullish" if macd_value >= 0 else "early bullish recovery"
        confirmation = "histogram positive" if hist_value > tolerance else "histogram rising"
        return MacdTrendSignal(
            "bullish",
            f"{bullish_reason} + {confirmation}",
            context,
            macd_value,
            signal_value,
            hist_value,
        )

    if bearish_reason and weakening:
        context = "strong bearish" if macd_value <= 0 else "early bearish weakening"
        confirmation = "histogram negative" if hist_value < -tolerance else "histogram falling"
        return MacdTrendSignal(
            "bearish",
            f"{bearish_reason} + {confirmation}",
            context,
            macd_value,
            signal_value,
            hist_value,
        )

    return MacdTrendSignal(
        "neutral",
        "mixed MACD slope and histogram confirmation",
        "unconfirmed",
        macd_value,
        signal_value,
        hist_value,
    )


def line_ylim(series: pd.Series, *, pad_frac: float = 0.15) -> tuple[float, float]:
    vals = series.dropna()
    if vals.empty:
        return (-1.0, 1.0)
    lo, hi = float(vals.min()), float(vals.max())
    span = hi - lo or 1.0
    pad = span * pad_frac
    lo -= pad
    hi += pad
    if lo < 0 < hi:
        margin = span * 0.05
        lo = min(lo, -margin)
        hi = max(hi, margin)
    return lo, hi


def macd_addplots(
    plot_df: pd.DataFrame,
    macd_line: pd.Series,
    *,
    trend_signal: MacdTrendSignal | None = None,
    panel: int = MACD_PANEL,
    fast: int = MACD_FAST,
    slow: int = MACD_SLOW,
    signal: int = MACD_SIGNAL,
) -> list:
    """MACD panel: MACD line only (EMA12 - EMA26), no histogram, no signal line."""
    import mplfinance as mpf

    line = macd_line.reindex(plot_df.index)
    ylim = line_ylim(line)
    addplots = [
        mpf.make_addplot(
            line,
            panel=panel,
            color="#2962ff",
            width=1.1,
            ylabel=f"MACD ({fast}, {slow}, close, {signal})",
            ylim=ylim,
        ),
    ]
    if trend_signal and trend_signal.trend in {"bullish", "bearish"} and not line.dropna().empty:
        marker = pd.Series(np.nan, index=plot_df.index)
        marker.iloc[-1] = line.dropna().iloc[-1]
        addplots.append(
            mpf.make_addplot(
                marker,
                panel=panel,
                type="scatter",
                marker="^" if trend_signal.is_bullish else "v",
                markersize=80,
                color="#1b9e5a" if trend_signal.is_bullish else "#d62728",
                ylim=ylim,
            )
        )
    return addplots
