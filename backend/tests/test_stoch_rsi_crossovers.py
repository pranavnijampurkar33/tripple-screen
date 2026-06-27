from __future__ import annotations

import unittest

import pandas as pd

from layers.indicators.stoch_rsi import (
    StochRsiCrossover,
    detect_stoch_rsi_crossovers,
    select_tide_gated_stoch_highlights,
    stoch_highlight_status_text,
)


def series(values: list[float]) -> pd.Series:
    return pd.Series(values, dtype="float64")


class StochRsiCrossoverTests(unittest.TestCase):
    def test_detects_positive_crossover_from_below_or_equal_to_above(self) -> None:
        events = detect_stoch_rsi_crossovers(
            series([10.0, 20.0, 35.0]),
            series([15.0, 20.0, 25.0]),
        )

        self.assertEqual([event.type for event in events], ["PCR"])
        self.assertEqual(events[0].index, 2)
        self.assertEqual(events[0].k_value, 35.0)
        self.assertEqual(events[0].d_value, 25.0)

    def test_detects_negative_crossover_from_above_or_equal_to_below(self) -> None:
        events = detect_stoch_rsi_crossovers(
            series([40.0, 30.0, 15.0]),
            series([35.0, 30.0, 25.0]),
        )

        self.assertEqual([event.type for event in events], ["NCR"])
        self.assertEqual(events[0].index, 2)

    def test_ignores_nan_warmup_values(self) -> None:
        events = detect_stoch_rsi_crossovers(
            series([float("nan"), 10.0, 30.0]),
            series([float("nan"), 20.0, 20.0]),
        )

        self.assertEqual([event.type for event in events], ["PCR"])


class TideGatedStochHighlightTests(unittest.TestCase):
    def test_bullish_latest_ncr_is_step_1(self) -> None:
        highlights = select_tide_gated_stoch_highlights(
            [StochRsiCrossover(1, "NCR", 45.0)],
            "bullish",
        )

        self.assertEqual([(h.step, h.crossover.type) for h in highlights], [(1, "NCR")])

    def test_bullish_latest_pcr_marks_prior_ncr_and_step_2(self) -> None:
        highlights = select_tide_gated_stoch_highlights(
            [
                StochRsiCrossover(1, "NCR", 35.0),
                StochRsiCrossover(2, "PCR", 55.0),
            ],
            "bullish",
        )

        self.assertEqual([(h.step, h.crossover.type) for h in highlights], [(1, "NCR"), (2, "PCR")])

    def test_bearish_latest_pcr_is_step_1(self) -> None:
        highlights = select_tide_gated_stoch_highlights(
            [StochRsiCrossover(1, "PCR", 55.0)],
            "bearish",
        )

        self.assertEqual([(h.step, h.crossover.type) for h in highlights], [(1, "PCR")])

    def test_bearish_latest_ncr_marks_prior_pcr_and_step_2(self) -> None:
        highlights = select_tide_gated_stoch_highlights(
            [
                StochRsiCrossover(1, "PCR", 65.0),
                StochRsiCrossover(2, "NCR", 45.0),
            ],
            "bearish",
        )

        self.assertEqual([(h.step, h.crossover.type) for h in highlights], [(1, "PCR"), (2, "NCR")])

    def test_neutral_trend_has_no_highlights(self) -> None:
        highlights = select_tide_gated_stoch_highlights(
            [StochRsiCrossover(1, "PCR", 55.0)],
            "neutral",
        )

        self.assertEqual(highlights, [])

    def test_status_text_says_step_1_only_completed(self) -> None:
        highlights = select_tide_gated_stoch_highlights(
            [StochRsiCrossover(1, "NCR", 45.0)],
            "bullish",
        )

        self.assertEqual(
            stoch_highlight_status_text("bullish", highlights),
            "Wave Stoch RSI: Tide BULLISH | Step 1 NCR completed",
        )

    def test_status_text_says_both_steps_completed(self) -> None:
        highlights = select_tide_gated_stoch_highlights(
            [
                StochRsiCrossover(1, "PCR", 65.0, 70.0, 60.0),
                StochRsiCrossover(2, "NCR", 45.0, 40.0, 50.0),
            ],
            "bearish",
        )

        self.assertEqual(
            stoch_highlight_status_text("bearish", highlights),
            "Wave Stoch RSI: Tide BEARISH | Step 1 PCR completed; Step 2 NCR completed | setup complete",
        )

    def test_status_text_can_include_current_stoch_rsi_values(self) -> None:
        highlights = select_tide_gated_stoch_highlights(
            [
                StochRsiCrossover(1, "NCR", 35.0, 30.25, 39.75),
                StochRsiCrossover(2, "PCR", 55.0, 61.5, 48.0),
            ],
            "bullish",
        )

        self.assertEqual(
            stoch_highlight_status_text("bullish", highlights, current_k=72.125, current_d=64.5),
            (
                "Wave Stoch RSI: Tide BULLISH | "
                "Step 1 NCR completed; Step 2 PCR completed | setup complete | "
                "Current K=72.12, D=64.50"
            ),
        )


if __name__ == "__main__":
    unittest.main()
