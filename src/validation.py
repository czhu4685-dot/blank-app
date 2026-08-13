"""Validation for the Excel interchange contract."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

import pandas as pd

from config.assets import SCHEMA


class WorkbookValidationError(Exception):
    """Raised when an uploaded workbook does not meet the dashboard schema."""


@dataclass(frozen=True)
class ValidationResult:
    warnings: list[str]


def validate_workbook_frames(frames: Mapping[str, pd.DataFrame]) -> ValidationResult:
    """Validate required sheets, columns, types, and non-empty source data."""
    errors: list[str] = []
    warnings: list[str] = []

    for sheet, columns in SCHEMA.items():
        if sheet not in frames:
            errors.append(f"缺少必需 Sheet：{sheet}")
            continue
        frame = frames[sheet]
        if frame.empty:
            errors.append(f"Sheet {sheet} 没有数据行。")
            continue
        missing = [column for column in columns if column not in frame.columns]
        if missing:
            errors.append(f"Sheet {sheet} 缺少字段：{', '.join(missing)}")

    if errors:
        raise WorkbookValidationError("\n".join(errors))

    for sheet in SCHEMA:
        frame = frames[sheet]
        parsed_dates = pd.to_datetime(frame["date"], errors="coerce")
        if parsed_dates.isna().any():
            errors.append(f"Sheet {sheet} 的 date 含无法识别的日期。")
        frames[sheet] = frame.copy()
        frames[sheet]["date"] = parsed_dates

    current = frames["ETF_Current"]
    if current[["code", "name", "category"]].isna().any().any():
        errors.append("Sheet ETF_Current 的代码、简称或类别不能为空。")

    for sheet, numeric_columns in {
        "ETF_Current": ["close", "nav", "fund_scale", "amount", "pct_change"],
        "ETF_History": ["close", "nav", "premium"],
        "Global_Index": ["close", "pct_change", "pe_ttm"],
    }.items():
        for column in numeric_columns:
            converted = pd.to_numeric(frames[sheet][column], errors="coerce")
            if converted.isna().all():
                errors.append(f"Sheet {sheet} 的 {column} 没有有效数值。")
            frames[sheet][column] = converted

    if frames["ETF_Current"]["nav"].isna().any():
        warnings.append("ETF_Current 中存在 NAV 为空的记录；该记录的溢价率会显示为不可用。")
    if frames["ETF_History"]["nav"].isna().any():
        warnings.append("ETF_History 中存在 NAV 为空的记录；对应历史溢价率会被忽略。")

    if errors:
        raise WorkbookValidationError("\n".join(errors))
    return ValidationResult(warnings=warnings)
