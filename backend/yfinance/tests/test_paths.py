from __future__ import annotations

import unittest
from pathlib import Path

from layers.paths import chart_path, make_run_output_dir


class ChartPathTests(unittest.TestCase):
    def test_chart_path_includes_interval_lookback_and_bars(self) -> None:
        path = chart_path(Path("out"), "wave", "1d", 120, 21)

        self.assertEqual(path, Path("out") / "wave_interval_1d_lookback_120_bars_21.png")

    def test_chart_path_sanitizes_interval_slashes(self) -> None:
        path = chart_path(Path("out"), "custom", "1/2d", 90, 30)

        self.assertEqual(path, Path("out") / "custom_interval_1-2d_lookback_90_bars_30.png")

    def test_run_output_dir_includes_as_of_date_when_given(self) -> None:
        path = make_run_output_dir("RELIANCE", as_of_date="2026-06-15")

        try:
            self.assertTrue(path.name.endswith("_RELIANCE_asof_2026-06-15"))
        finally:
            if path.exists() and not any(path.iterdir()):
                path.rmdir()


if __name__ == "__main__":
    unittest.main()
