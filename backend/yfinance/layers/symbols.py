"""Ticker normalization for yfinance (NSE)."""

from __future__ import annotations


def resolve_ticker(symbol: str) -> str:
    s = symbol.strip().upper().replace(" ", "")
    if s.endswith(".NS") or s.endswith(".BO"):
        return s
    return f"{s}.NS"


def folder_symbol(symbol: str) -> str:
    """Folder-safe symbol label, e.g. RELIANCE.NS -> RELIANCE."""
    t = resolve_ticker(symbol)
    if t.endswith(".NS"):
        return t[:-3]
    if t.endswith(".BO"):
        return t[:-3]
    return t
