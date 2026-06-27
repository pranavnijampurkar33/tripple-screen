from __future__ import annotations

import unittest

import pandas as pd

from layers.indicators.macd import classify_macd_trend


def series(values: list[float]) -> pd.Series:
    return pd.Series(values, dtype="float64")


class MacdTrendSignalTests(unittest.TestCase):
    def test_rising_macd_with_improving_histogram_is_bullish(self) -> None:
        result = classify_macd_trend(
            series([1.00, 1.10, 1.20, 1.40]),
            series([0.90, 1.00, 1.05, 1.10]),
            series([0.10, 0.10, 0.15, 0.30]),
        )

        self.assertEqual(result.trend, "bullish")
        self.assertIn("up", result.reason)

    def test_falling_macd_with_weakening_histogram_is_bearish(self) -> None:
        result = classify_macd_trend(
            series([1.40, 1.30, 1.20, 1.00]),
            series([1.10, 1.10, 1.10, 1.10]),
            series([0.30, 0.20, 0.10, -0.10]),
        )

        self.assertEqual(result.trend, "bearish")
        self.assertIn("down", result.reason)

    def test_flat_after_down_is_bullish_when_histogram_improves(self) -> None:
        result = classify_macd_trend(
            series([1.00, 0.80, 0.70, 0.70]),
            series([1.30, 1.05, 0.85, 0.75]),
            series([-0.30, -0.25, -0.15, -0.05]),
        )

        self.assertEqual(result.trend, "bullish")
        self.assertIn("flat-after-down", result.reason)

    def test_flat_after_down_without_confirmation_is_neutral(self) -> None:
        result = classify_macd_trend(
            series([1.00, 0.80, 0.70, 0.70]),
            series([1.20, 0.98, 0.85, 0.90]),
            series([-0.20, -0.18, -0.15, -0.20]),
        )

        self.assertEqual(result.trend, "neutral")

    def test_flat_after_up_is_bearish_when_histogram_weakens(self) -> None:
        result = classify_macd_trend(
            series([0.00, 0.20, 0.30, 0.30]),
            series([-0.10, 0.00, 0.15, 0.35]),
            series([0.10, 0.20, 0.15, -0.05]),
        )

        self.assertEqual(result.trend, "bearish")
        self.assertIn("flat-after-up", result.reason)

    def test_insufficient_history_is_neutral(self) -> None:
        result = classify_macd_trend(
            series([1.00, 1.10, 1.20]),
            series([0.90, 1.00, 1.05]),
            series([0.10, 0.10, 0.15]),
        )

        self.assertEqual(result.trend, "neutral")


if __name__ == "__main__":
    unittest.main()
