"""Layer specs and env-backed defaults for Ripple / Wave / Tide charts."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parents[1]
_ENV_PATH = _PROJECT_ROOT / ".env"


def _read_env_file(path: Path = _ENV_PATH) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.exists():
        return values

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and value:
            values[key] = value
    return values


_ENV = _read_env_file()


def _env_str(name: str, default: str) -> str:
    return _ENV.get(name, default)


def _env_int(name: str, default: int) -> int:
    raw = _ENV.get(name)
    if raw is None:
        return default
    try:
        value = int(raw)
    except ValueError:
        return default
    return value if value > 0 else default


@dataclass(frozen=True)
class LayerSpec:
    name: str
    default_interval: str
    lookback_days: int
    chart_bars: int
    panel_ratios: tuple[float, ...]
    show_stoch_band: bool = True

    @property
    def sessions(self) -> int:
        return self.chart_bars


DEFAULT_RIPPLE_INTERVAL = "1h"
DEFAULT_RIPPLE_LOOK_BACK_DAYS = 90
DEFAULT_RIPPLE_CHART_BARS = 30

DEFAULT_WAVE_INTERVAL = "1d"
DEFAULT_WAVE_LOOK_BACK_DAYS = 120
DEFAULT_WAVE_CHART_BARS = 21

DEFAULT_TIDE_INTERVAL = "1wk"
DEFAULT_TIDE_LOOK_BACK_DAYS = 400
DEFAULT_TIDE_CHART_BARS = 15

DEFAULT_WAVE_SR_LOOKBACK_DAYS = 90
DEFAULT_WAVE_SR_CHART_BARS = 90


RIPPLE = LayerSpec(
    name="ripple",
    default_interval=_env_str("RIPPLE_INTERVAL", DEFAULT_RIPPLE_INTERVAL),
    lookback_days=_env_int("RIPPLE_LOOK_BACK_DAYS", DEFAULT_RIPPLE_LOOK_BACK_DAYS),
    chart_bars=_env_int("RIPPLE_CHART_BARS", DEFAULT_RIPPLE_CHART_BARS),
    panel_ratios=(5, 1.55),  # price + Stoch RSI (no volume)
)

WAVE = LayerSpec(
    name="wave",
    default_interval=_env_str("WAVE_INTERVAL", DEFAULT_WAVE_INTERVAL),
    lookback_days=_env_int("WAVE_LOOK_BACK_DAYS", DEFAULT_WAVE_LOOK_BACK_DAYS),
    chart_bars=_env_int("WAVE_CHART_BARS", DEFAULT_WAVE_CHART_BARS),
    panel_ratios=(5, 1.0, 1.55),
)

TIDE = LayerSpec(
    name="tide",
    default_interval=_env_str("TIDE_INTERVAL", DEFAULT_TIDE_INTERVAL),
    lookback_days=_env_int("TIDE_LOOK_BACK_DAYS", DEFAULT_TIDE_LOOK_BACK_DAYS),
    chart_bars=_env_int("TIDE_CHART_BARS", DEFAULT_TIDE_CHART_BARS),
    panel_ratios=(5, 1.25),  # price + MACD (no volume)
    show_stoch_band=False,
)

WAVE_SR = LayerSpec(
    name="wave_sr",
    default_interval=WAVE.default_interval,
    lookback_days=_env_int("WAVE_SR_LOOKBACK_DAYS", DEFAULT_WAVE_SR_LOOKBACK_DAYS),
    chart_bars=_env_int("WAVE_SR_CHART_BARS", DEFAULT_WAVE_SR_CHART_BARS),
    panel_ratios=(5, 1.0),
    show_stoch_band=False,
)


def lookback_days_for(interval: str, sessions: int, *, warmup: int = 60) -> int:
    """History length for yfinance download so indicators warm up before the visible window."""
    if interval == "1h":
        return max(90, (sessions + warmup) // 6 + 14)
    if interval == "1wk":
        return max(400, (sessions + warmup) * 7)
    return max(120, sessions + warmup + 30)
