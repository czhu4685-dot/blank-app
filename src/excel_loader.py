"""Excel-only data access layer. It deliberately contains no Wind connectivity."""

from __future__ import annotations

from io import BytesIO
from pathlib import Path
from typing import BinaryIO

import pandas as pd

from config.assets import DEFAULT_WORKBOOK_PATH, SCHEMA
from src.metrics import prepare_etf_current, prepare_etf_history
from src.validation import ValidationResult, validate_workbook_frames


def _adapt_wind_workbook(frames: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    """Map the production Wind workbook's saved values to the app schema.

    The workbook has title rows above its headers and differs deliberately from
    the lightweight three-sheet interchange workbook. No Wind formulas are
    evaluated here; pandas reads only their last values saved by Excel.
    """
    wind = frames["WindData"].copy()
    indices = frames["GlobalIndices"].copy()

    current = wind.rename(columns={"as_of": "date", "fund_purchase_status": "purchase_status"})[
        ["date", "code", "name", "category", "close", "nav", "fund_scale", "amount", "pct_change", "purchase_status"]
    ].copy()
    current["category"] = current["category"].replace({"\u7eb3\u6307100": "\u7eb3\u6307", "\u6807\u666e500": "\u6807\u666e"})
    current["amount"] = pd.to_numeric(current["amount"], errors="coerce") / 100_000_000
    # WSS rt_pct_chg is stored as percentage points, such as 0.30 for 0.30%.
    current["pct_change"] = pd.to_numeric(current["pct_change"], errors="coerce") / 100

    global_index = indices.rename(columns={"latest": "close", "as_of": "date"})[
        ["date", "code", "name", "close", "pct_change", "pe_ttm"]
    ].copy()
    global_index["pct_change"] = pd.to_numeric(global_index["pct_change"], errors="coerce") / 100

    # This particular workbook's PremiumHistory only has a complete price
    # series at present, so its close/NAV history is not yet usable. A current
    # point preserves detail-page availability until the full history is saved.
    history = current[["date", "code", "close", "nav"]].copy()
    history["premium"] = current["close"] / current["nav"] - 1
    return {"ETF_Current": current, "ETF_History": history, "Global_Index": global_index}


def _read_workbook(source: str | Path | bytes | BinaryIO) -> dict[str, pd.DataFrame]:
    if isinstance(source, bytes):
        source = BytesIO(source)
    # data_only=True is essential: the website consumes cached values saved by
    # Excel after Wind refresh, never the formula text itself.
    workbook = pd.ExcelFile(source, engine="openpyxl", engine_kwargs={"data_only": True})
    if set(SCHEMA).issubset(workbook.sheet_names):
        return pd.read_excel(workbook, sheet_name=list(SCHEMA))
    if {"WindData", "GlobalIndices"}.issubset(workbook.sheet_names):
        production = pd.read_excel(workbook, sheet_name=["WindData", "GlobalIndices", "StrategyAnalysis"], header=3)
        production["WindData"] = production["WindData"].dropna(subset=["code", "close", "nav"])
        production["GlobalIndices"] = production["GlobalIndices"].dropna(subset=["code"])
        adapted = _adapt_wind_workbook(production)
        adapted["StrategyAnalysis"] = production["StrategyAnalysis"].dropna(subset=["code"])
        return adapted
    return pd.read_excel(workbook, sheet_name=list(SCHEMA))


def load_dashboard_data(source: str | Path | bytes | BinaryIO | None = None) -> tuple[dict[str, pd.DataFrame], ValidationResult]:
    """Read saved Excel values, validate them, and return presentation-ready frames."""
    frames = _read_workbook(source or DEFAULT_WORKBOOK_PATH)
    validation = validate_workbook_frames(frames)
    frames["ETF_Current"] = prepare_etf_current(frames["ETF_Current"])
    frames["ETF_History"] = prepare_etf_history(frames["ETF_History"])
    return frames, validation
