"""Excel-only data access layer. It deliberately contains no Wind connectivity."""

from __future__ import annotations

from io import BytesIO
from pathlib import Path
from typing import BinaryIO

import pandas as pd

from config.assets import DEFAULT_WORKBOOK_PATH, SCHEMA
from src.metrics import prepare_etf_current, prepare_etf_history
from src.validation import ValidationResult, validate_workbook_frames


def _read_workbook(source: str | Path | bytes | BinaryIO) -> dict[str, pd.DataFrame]:
    if isinstance(source, bytes):
        source = BytesIO(source)
    return pd.read_excel(source, sheet_name=list(SCHEMA), engine="openpyxl")


def load_dashboard_data(source: str | Path | bytes | BinaryIO | None = None) -> tuple[dict[str, pd.DataFrame], ValidationResult]:
    """Read saved Excel values, validate them, and return presentation-ready frames."""
    frames = _read_workbook(source or DEFAULT_WORKBOOK_PATH)
    validation = validate_workbook_frames(frames)
    frames["ETF_Current"] = prepare_etf_current(frames["ETF_Current"])
    frames["ETF_History"] = prepare_etf_history(frames["ETF_History"])
    return frames, validation
