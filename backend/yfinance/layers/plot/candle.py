"""Candlestick plotting via mplfinance."""

from __future__ import annotations

import mplfinance as mpf
import numpy as np
import pandas as pd


def integer_index_xlim(n: int, *, right_pad_bars: float) -> tuple[float, float]:
    """Match mplfinance's integer x-axis with extra space on the right."""
    if n <= 0:
        return (-0.5, 0.5)
    if n == 1:
        return (-0.75, 0.75)
    idx = np.arange(n, dtype=float)
    avg = (idx[-1] - idx[0]) / float(n)
    minx = idx[0] - 0.45 * avg
    maxx = idx[-1] + (0.45 + right_pad_bars) * avg
    return (float(minx), float(maxx))


def spread_vertical_panel_gaps(axlist: list, gap_frac: float = 0.028) -> None:
    """Insert vertical gaps between mplfinance panels (primary + twinx move together)."""
    if len(axlist) < 2:
        return
    pairs = [(axlist[2 * i], axlist[2 * i + 1]) for i in range(len(axlist) // 2)]
    order = sorted(range(len(pairs)), key=lambda i: pairs[i][0].get_position().y0)
    positions = [pairs[i][0].get_position() for i in order]
    n = len(positions)
    if n < 2:
        return

    gap = gap_frac
    total_gap = gap * (n - 1)
    heights = [p.height for p in positions]
    scale = (sum(heights) - total_gap) / sum(heights)
    new_heights = [h * scale for h in heights]

    y = positions[0].y0
    for idx, panel_i in enumerate(order):
        h = new_heights[idx]
        for ax in pairs[panel_i]:
            pos = ax.get_position()
            ax.set_position([pos.x0, y, pos.width, h])
        y += h + gap


def plot_candlestick(
    ohlcv: pd.DataFrame,
    *,
    title: str,
    addplot: list | None = None,
    hlines: dict | None = None,
    volume: bool = True,
    right_pad_bars: float = 2.25,
    panel_ratios: tuple[float, ...] = (5, 1.0, 1.35, 1.25),
    panel_gap_frac: float = 0.032,
    figscale: float = 1.35,
):
    """Plot OHLC candles; optional volume and addplots on lower panels."""
    n = len(ohlcv)
    xlim = integer_index_xlim(n, right_pad_bars=right_pad_bars)
    plot_kwargs: dict = dict(
        type="candle",
        style="yahoo",
        title=title,
        volume=volume,
        panel_ratios=panel_ratios,
        figscale=figscale,
        addplot=addplot or [],
        tight_layout=True,
        xlim=xlim,
        scale_padding=dict(left=1.2, right=1.45, top=1.25, bottom=1.2),
        returnfig=True,
        warn_too_much_data=10_000,
    )
    if hlines:
        plot_kwargs["hlines"] = hlines
    if volume:
        plot_kwargs["volume_panel"] = 1
    fig, axlist = mpf.plot(ohlcv, **plot_kwargs)
    spread_vertical_panel_gaps(axlist, gap_frac=panel_gap_frac)
    return fig, axlist
