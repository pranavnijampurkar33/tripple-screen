from __future__ import annotations

import unittest

import pandas as pd

from layers.indicators.support_resistance import support_resistance_levels


class SupportResistanceTests(unittest.TestCase):
    def test_calculates_recent_pullback_levels(self) -> None:
        df = pd.DataFrame(
            {
                "High": [10.0, 12.0, 15.0, 11.0, 13.0],
                "Low": [8.0, 9.0, 10.0, 7.0, 11.0],
            },
            index=pd.date_range("2026-01-01", periods=5),
        )

        result = support_resistance_levels(df, candles=5)

        self.assertEqual(
            [(level.label, level.value, level.color) for level in result.levels],
            [
                ("Pullback Support After Resistance", 7.0, "blue"),
                ("Recent Resistance", 15.0, "red"),
                ("Recent Support", 7.0, "green"),
                ("Pullback Resistance After Support", 13.0, "purple"),
            ],
        )

    def test_empty_dataframe_has_no_levels(self) -> None:
        result = support_resistance_levels(pd.DataFrame(columns=["High", "Low"]))

        self.assertEqual(result.levels, ())
        self.assertIsNone(result.hlines_dict())

    def test_uses_latest_candles_for_levels(self) -> None:
        df = pd.DataFrame(
            {
                "High": [1000.0] + [float(value) for value in range(10, 100)],
                "Low": [900.0] + [float(value) for value in range(9, 99)],
            },
            index=pd.date_range("2026-01-01", periods=91),
        )

        result = support_resistance_levels(df, candles=90)

        values = [level.value for level in result.levels]
        self.assertNotIn(1000.0, values)
        self.assertNotIn(900.0, values)


if __name__ == "__main__":
    unittest.main()
