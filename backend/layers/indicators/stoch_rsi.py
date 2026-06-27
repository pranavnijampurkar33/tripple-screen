"""Stochastic RSI calculation and mplfinance addplot helpers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import numpy as np
import pandas as pd

STOCH_YLIM = (0, 110)
STOCH_PANEL = 2  # Wave: panel 0=price, 1=volume, 2=Stoch RSI
StochCrossoverType = Literal["PCR", "NCR"]
StochTrend = Literal["bullish", "bearish", "neutral"]


@dataclass(frozen=True)
class StochRsiCrossover:
    index: object
    type: StochCrossoverType
    y_value: float
    k_value: float = float("nan")
    d_value: float = float("nan")


@dataclass(frozen=True)
class StochRsiHighlight:
    crossover: StochRsiCrossover
    step: int

    @property
    def label(self) -> str:
        return f"Step {self.step} {self.crossover.type}"


def rsi_wilder(close: pd.Series, period: int = 14) -> pd.Series:
    delta = close.diff()
    gain = delta.clip(lower=0.0)
    loss = (-delta).clip(lower=0.0)
    avg_gain = gain.ewm(alpha=1.0 / period, min_periods=period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1.0 / period, min_periods=period, adjust=False).mean()
    rs = avg_gain / avg_loss.replace(0.0, 1e-12)
    return 100.0 - (100.0 / (1.0 + rs))


def stochastic_rsi(
    close: pd.Series,
    rsi_period: int = 14,
    stoch_period: int = 14,
    smooth_k: int = 3,
    smooth_d: int = 3,
) -> tuple[pd.Series, pd.Series]:
    r = rsi_wilder(close, rsi_period)
    lowest = r.rolling(stoch_period, min_periods=stoch_period).min()
    highest = r.rolling(stoch_period, min_periods=stoch_period).max()
    span = (highest - lowest).replace(0.0, 1e-12)
    stoch = (r - lowest) / span * 100.0
    k = stoch.rolling(smooth_k, min_periods=1).mean()
    d = k.rolling(smooth_d, min_periods=1).mean()
    return k, d


def detect_stoch_rsi_crossovers(k: pd.Series, d: pd.Series) -> list[StochRsiCrossover]:
    """Return ordered Stoch RSI %K/%D crossovers."""
    data = pd.concat([k.rename("k"), d.rename("d")], axis=1).dropna()
    if len(data) < 2:
        return []

    diff = data["k"] - data["d"]
    events: list[StochRsiCrossover] = []
    for i in range(1, len(data)):
        prev_diff = float(diff.iloc[i - 1])
        curr_diff = float(diff.iloc[i])
        if prev_diff <= 0.0 < curr_diff:
            crossover_type: StochCrossoverType = "PCR"
        elif prev_diff >= 0.0 > curr_diff:
            crossover_type = "NCR"
        else:
            continue

        row = data.iloc[i]
        events.append(
            StochRsiCrossover(
                index=data.index[i],
                type=crossover_type,
                y_value=float((row["k"] + row["d"]) / 2.0),
                k_value=float(row["k"]),
                d_value=float(row["d"]),
            )
        )
    return events


def select_tide_gated_stoch_highlights(
    crossovers: list[StochRsiCrossover],
    trend: str | None,
) -> list[StochRsiHighlight]:
    """Select staged Wave Stoch RSI highlights from Tide trend bias."""
    if not crossovers or trend not in {"bullish", "bearish"}:
        return []

    latest = crossovers[-1]
    if trend == "bullish":
        if latest.type == "NCR":
            return [StochRsiHighlight(latest, 1)]

        highlights = [
            StochRsiHighlight(prev, 1)
            for prev in reversed(crossovers[:-1])
            if prev.type == "NCR"
        ][:1]
        highlights.append(StochRsiHighlight(latest, 2))
        return highlights

    if latest.type == "PCR":
        return [StochRsiHighlight(latest, 1)]

    highlights = [
        StochRsiHighlight(prev, 1)
        for prev in reversed(crossovers[:-1])
        if prev.type == "PCR"
    ][:1]
    highlights.append(StochRsiHighlight(latest, 2))
    return highlights


def stoch_highlight_status_text(
    trend: str | None,
    highlights: list[StochRsiHighlight],
    *,
    prefix: str = "Wave Stoch RSI",
    current_k: float | None = None,
    current_d: float | None = None,
) -> str:
    """Format staged Wave Stoch RSI highlights for chart and console output."""
    trend_label = trend.upper() if trend else "UNKNOWN"
    current_text = ""
    if current_k is not None and current_d is not None:
        current_text = f" | Current K={current_k:.2f}, D={current_d:.2f}"

    if trend not in {"bullish", "bearish"}:
        return f"{prefix}: Tide {trend_label} | no staged PCR/NCR highlight{current_text}"
    if not highlights:
        return f"{prefix}: Tide {trend_label} | no PCR/NCR crossover in visible Wave window{current_text}"

    step_texts = []
    for highlight in highlights:
        text = f"Step {highlight.step} {highlight.crossover.type} completed"
        step_texts.append(text)
    completed = "; ".join(step_texts)
    if {highlight.step for highlight in highlights} == {1, 2}:
        completed += " | setup complete"
    return f"{prefix}: Tide {trend_label} | {completed}{current_text}"


def stoch_rsi_addplots(
    plot_df: pd.DataFrame,
    k: pd.Series,
    d: pd.Series,
    *,
    panel: int = STOCH_PANEL,
    ylim: tuple[float, float] = STOCH_YLIM,
    show_band: bool = True,
    highlights: list[StochRsiHighlight] | None = None,
) -> list:
    """Build mplfinance addplot list for the Stochastic RSI panel."""
    import mplfinance as mpf

    apds: list = []
    if show_band:
        apds.append(
            mpf.make_addplot(
                pd.Series(50.0, index=plot_df.index),
                panel=panel,
                type="line",
                color="white",
                alpha=0.0,
                width=0.1,
                fill_between=dict(y1=20.0, y2=80.0, alpha=0.14, color="#c8b8e8"),
            )
        )
    apds.extend(
        [
            mpf.make_addplot(
                k,
                panel=panel,
                color="#1f77b4",
                width=1.2,
                ylabel="Stoch RSI",
                ylim=ylim,
            ),
            mpf.make_addplot(d, panel=panel, color="#ff7f0e", width=1.0, ylim=ylim),
        ]
    )
    for y in (20, 80):
        apds.append(
            mpf.make_addplot(
                pd.Series(y, index=plot_df.index),
                panel=panel,
                color="#888888",
                linestyle="--",
                width=0.8,
                ylim=ylim,
            )
        )
    for highlight in highlights or []:
        marker = pd.Series(np.nan, index=plot_df.index)
        if highlight.crossover.index not in marker.index:
            continue
        marker.loc[highlight.crossover.index] = highlight.crossover.y_value
        apds.append(
            mpf.make_addplot(
                marker,
                panel=panel,
                type="scatter",
                marker="^" if highlight.crossover.type == "PCR" else "v",
                markersize=90,
                color="#1b9e5a" if highlight.crossover.type == "PCR" else "#d62728",
                ylim=ylim,
            )
        )
    return apds


def annotate_stoch_rsi_highlights(
    ax,
    plot_df: pd.DataFrame,
    highlights: list[StochRsiHighlight],
    *,
    status_text: str | None = None,
) -> None:
    """Add text labels for staged Stoch RSI highlights on an mplfinance panel."""
    if status_text:
        ax.text(
            0.01,
            0.97,
            status_text,
            transform=ax.transAxes,
            ha="left",
            va="top",
            fontsize=8,
            fontweight="bold",
            color="#222222",
            bbox=dict(boxstyle="round,pad=0.3", facecolor="white", edgecolor="#999999", alpha=0.82),
        )

    x_lookup = {idx: pos for pos, idx in enumerate(plot_df.index)}
    for highlight in highlights:
        x = x_lookup.get(highlight.crossover.index)
        if x is None:
            continue
        is_pcr = highlight.crossover.type == "PCR"
        y_offset = 8.0 if is_pcr else -10.0
        va = "bottom" if is_pcr else "top"
        ax.annotate(
            highlight.label,
            xy=(x, highlight.crossover.y_value),
            xytext=(x, highlight.crossover.y_value + y_offset),
            textcoords="data",
            ha="center",
            va=va,
            fontsize=8,
            fontweight="bold",
            color="#1b9e5a" if is_pcr else "#d62728",
            arrowprops=dict(
                arrowstyle="-",
                color="#1b9e5a" if is_pcr else "#d62728",
                linewidth=0.8,
            ),
            clip_on=True,
        )
