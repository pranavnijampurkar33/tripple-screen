#!/usr/bin/env python3
"""CLI: generate Ripple / Wave / Tide layer charts for a symbol."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from layers.config import RIPPLE, TIDE, WAVE
from layers.orchestrator import generate


def main() -> None:
    p = argparse.ArgumentParser(
        description="Generate Ripple (1h+Stoch), Wave (1d+Stoch), and Tide (1wk+MACD) charts."
    )
    p.add_argument(
        "symbol",
        nargs="?",
        default="RELIANCE",
        help="Symbol (default: RELIANCE → RELIANCE.NS)",
    )
    p.add_argument(
        "--ripple-tf",
        default=RIPPLE.default_interval,
        help=f"Ripple interval (default: {RIPPLE.default_interval})",
    )
    p.add_argument(
        "--wave-tf",
        default=WAVE.default_interval,
        help=f"Wave interval (default: {WAVE.default_interval})",
    )
    p.add_argument(
        "--tide-tf",
        default=TIDE.default_interval,
        help=f"Tide interval (default: {TIDE.default_interval})",
    )
    p.add_argument(
        "--as-of-date",
        default=None,
        help="Generate charts using data on or before this date (YYYY-MM-DD).",
    )
    args = p.parse_args()

    run_dir = generate(
        args.symbol,
        ripple_tf=args.ripple_tf,
        wave_tf=args.wave_tf,
        tide_tf=args.tide_tf,
        as_of_date=args.as_of_date,
    )
    print(f"\nOutput folder: {run_dir}")


if __name__ == "__main__":
    main()
