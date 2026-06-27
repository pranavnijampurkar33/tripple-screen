from __future__ import annotations

import unittest

import pandas as pd

from layers.dates import as_of_download_window, as_of_label, filter_as_of


class AsOfDateTests(unittest.TestCase):
    def test_as_of_label_uses_iso_date(self) -> None:
        self.assertEqual(as_of_label("2026-06-15"), "2026-06-15")

    def test_download_window_uses_exclusive_next_day_end(self) -> None:
        start, end = as_of_download_window("2026-06-15", 90)

        self.assertEqual(start.isoformat(), "2026-03-17")
        self.assertEqual(end.isoformat(), "2026-06-16")

    def test_filter_as_of_keeps_rows_through_requested_date(self) -> None:
        df = pd.DataFrame(
            {"Close": [1.0, 2.0, 3.0]},
            index=pd.to_datetime(["2026-06-14 15:30", "2026-06-15 15:30", "2026-06-16 09:15"]),
        )

        filtered = filter_as_of(df, "2026-06-15")

        self.assertEqual(filtered["Close"].tolist(), [1.0, 2.0])


if __name__ == "__main__":
    unittest.main()
