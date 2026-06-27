"""Output paths for layer chart PNGs."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from layers.symbols import folder_symbol
from layers.dates import AsOfDate, as_of_label

# yfinance/ project root (parent of layers/)
_PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUT_BASE = _PROJECT_ROOT / "data" / "out"


def make_run_output_dir(symbol: str, *, when: datetime | None = None, as_of_date: AsOfDate = None) -> Path:
    ts = (when or datetime.now()).strftime("%y%m%d%H%M")
    sym = folder_symbol(symbol)
    suffix = f"_asof_{label}" if (label := as_of_label(as_of_date)) else ""
    run_dir = OUT_BASE / f"{ts}_{sym}{suffix}"
    run_dir.mkdir(parents=True, exist_ok=True)
    return run_dir


def chart_path(run_dir: Path, layer: str, interval: str, lookback_days: int, chart_bars: int) -> Path:
    """e.g. ripple_interval_1h_lookback_90_bars_30.png"""
    safe_tf = interval.replace("/", "-")
    return run_dir / f"{layer}_interval_{safe_tf}_lookback_{lookback_days}_bars_{chart_bars}.png"
