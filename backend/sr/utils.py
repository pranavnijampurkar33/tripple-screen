import yfinance as yf
import pandas as pd
import mplfinance as mpf
from datetime import datetime, timedelta
import numpy as np
import random


# ==============================
# Helper function to plot levels
# ==============================
def plot_chart(df, title, levels=None, hlines_dict=None):
    kwargs = dict(
        type="candle",
        style="yahoo",
        title=title,
        ylabel="Price",
        volume=True,
        figsize=(14, 8)
    )

    if hlines_dict:
        kwargs["hlines"] = hlines_dict
    elif levels:
        kwargs["hlines"] = dict(
            hlines=levels,
            linewidths=1.2,
            linestyle="--"
        )

    mpf.plot(df, **kwargs)


# Helper function to merge nearby levels
def merge_nearby_levels(levels, tolerance_pct=0.005):
    levels = sorted(levels)
    merged = []
    for level in levels:
        if not merged:
            merged.append([level])
        else:
            avg_level = np.mean(merged[-1])
            if abs(level - avg_level) / avg_level <= tolerance_pct:
                merged[-1].append(level)
            else:
                merged.append([level])
    return [np.mean(group) for group in merged]