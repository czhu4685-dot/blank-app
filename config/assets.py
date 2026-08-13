"""Static configuration shared by the dashboard pages."""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_WORKBOOK_PATH = PROJECT_ROOT / "data" / "mock_qdii_data.xlsx"

ETF_CATEGORIES = ["\u7eb3\u6307", "\u6807\u666e", "\u7279\u8272"]
HIGH_PREMIUM_THRESHOLD = 0.085
DISCLAIMER = "\u514d\u8d23\u58f0\u660e\uff1a\u7b56\u7565\u6807\u7b7e\u4ec5\u4e3a\u8bfe\u9898\u4efb\u52a1\u4e66\u4e2d\u7684\u91cf\u5316\u89c4\u5219\u5c55\u793a\uff0c\u4e0d\u6784\u6210\u4efb\u4f55\u6295\u8d44\u5efa\u8bae\u3002"
SCHEMA = {
    "ETF_Current": ["date", "code", "name", "category", "close", "nav", "fund_scale", "amount", "pct_change", "purchase_status"],
    "ETF_History": ["date", "code", "close", "nav", "premium"],
    "Global_Index": ["date", "code", "name", "close", "pct_change", "pe_ttm"],
}
