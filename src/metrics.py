"""Pure business calculations used by the Streamlit presentation layer."""

from __future__ import annotations

import numpy as np
import pandas as pd


def calculate_premium(close: pd.Series, nav: pd.Series) -> pd.Series:
    """Return the agreed premium convention: close / nav - 1."""
    safe_nav = nav.where(nav.notna() & (nav != 0))
    return close / safe_nav - 1


def prepare_etf_current(current: pd.DataFrame) -> pd.DataFrame:
    result = current.copy()
    result["premium"] = calculate_premium(result["close"], result["nav"])
    return result


def prepare_etf_history(history: pd.DataFrame) -> pd.DataFrame:
    result = history.copy()
    calculated = calculate_premium(result["close"], result["nav"])
    # Always calculate from close/NAV; workbook premium is retained only for source audit.
    result["premium"] = calculated.where(calculated.notna(), result["premium"])
    return result.sort_values(["code", "date"])


def premium_statistics(history: pd.DataFrame, code: str) -> dict[str, float]:
    series = history.loc[history["code"] == code, "premium"].dropna()
    if len(series) < 2:
        return {key: np.nan for key in ("current", "percentile", "mean", "std", "plus_1", "plus_2", "minus_1", "minus_2")}

    current = series.iloc[-1]
    mean = series.mean()
    std = series.std(ddof=0)
    return {
        "current": current,
        "percentile": series.rank(pct=True).iloc[-1],
        "mean": mean,
        "std": std,
        "plus_1": mean + std,
        "plus_2": mean + 2 * std,
        "minus_1": mean - std,
        "minus_2": mean - 2 * std,
    }
