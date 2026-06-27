"""Support/resistance levels for Wave charts."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class SupportResistanceLevel:
    label: str
    value: float
    color: str


@dataclass(frozen=True)
class SupportResistanceResult:
    levels: tuple[SupportResistanceLevel, ...]

    def hlines_dict(self) -> dict | None:
        if not self.levels:
            return None
        return {
            "hlines": [level.value for level in self.levels],
            "linewidths": 1.2,
            "linestyle": "--",
            "colors": [level.color for level in self.levels],
        }

    def console_text(self, *, prefix: str = "Wave S/R") -> str:
        if not self.levels:
            return f"{prefix}: no levels"
        parts = [f"{level.label}={level.value:.2f}" for level in self.levels]
        return f"{prefix}: " + " | ".join(parts)


def support_resistance_levels(
    df: pd.DataFrame,
    *,
    candles: int = 90,
    resistance_window: int | None = None,
    support_window: int | None = None,
) -> SupportResistanceResult:
    """Calculate recent pullback support/resistance levels from recent OHLC data."""
    if df.empty:
        return SupportResistanceResult(())

    required = {"High", "Low"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing OHLC columns for support/resistance: {missing}")

    if candles <= 0:
        raise ValueError("candles must be greater than zero")

    sr_df = df.tail(candles).copy()
    resistance_window = resistance_window or candles
    support_window = support_window or candles
    levels: list[SupportResistanceLevel] = []

    recent_resistance_df = sr_df.tail(min(resistance_window, len(sr_df)))
    recent_resistance_idx = recent_resistance_df["High"].idxmax()
    recent_resistance = float(recent_resistance_df.loc[recent_resistance_idx, "High"])
    after_resistance_df = sr_df.loc[recent_resistance_idx:].iloc[1:]
    if not after_resistance_df.empty:
        levels.append(
            SupportResistanceLevel(
                "Pullback Support After Resistance",
                float(after_resistance_df["Low"].min()),
                "blue",
            )
        )
    levels.append(SupportResistanceLevel("Recent Resistance", recent_resistance, "red"))

    recent_support_df = sr_df.tail(min(support_window, len(sr_df)))
    recent_support_idx = recent_support_df["Low"].idxmin()
    recent_support = float(recent_support_df.loc[recent_support_idx, "Low"])
    after_support_df = sr_df.loc[recent_support_idx:].iloc[1:]

    levels.append(SupportResistanceLevel("Recent Support", recent_support, "green"))
    if not after_support_df.empty:
        levels.append(
            SupportResistanceLevel(
                "Pullback Resistance After Support",
                float(after_support_df["High"].max()),
                "purple",
            )
        )

    return SupportResistanceResult(tuple(levels))
