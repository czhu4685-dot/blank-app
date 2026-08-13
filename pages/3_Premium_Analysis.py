"""Premium statistics and task-book rule display."""

import math

import pandas as pd
import streamlit as st

from config.assets import DISCLAIMER
from src.metrics import premium_statistics
from src.signals import premium_signal
from src.ui import get_data, render_source_uploader


def pct(value: float, digits: int = 2) -> str:
    return "-" if value is None or math.isnan(value) else f"{value:.{digits}%}"


render_source_uploader()
frames = get_data()
current = frames["ETF_Current"]
history = frames["ETF_History"]
eligible = current[current["category"].isin(["\u7eb3\u6307", "\u6807\u666e"])]

st.title("Premium analysis")
st.caption("Premium uses close / NAV - 1. Statistics use the saved daily close/NAV history.")
options = {f"{row.code} | {row.name} ({row.category})": row for row in eligible.itertuples()}
selected = st.selectbox("Select Nasdaq or S&P ETF", list(options))
etf = options[selected]
stats = premium_statistics(history, etf.code)

# The production Wind workbook includes the Excel-calculated strategy table.
# Use it if its detailed NAV history has not yet been fully saved.
strategy = frames.get("StrategyAnalysis", pd.DataFrame())
if not strategy.empty and math.isnan(stats["std"]):
    row = strategy.loc[strategy["code"] == etf.code]
    if not row.empty:
        value = row.iloc[0]
        stats = {
            "current": float(value["premium"]), "percentile": float(value["pctile_1y"]),
            "mean": float(value["mean_1y"]), "std": float(value["std_1y"]),
            "plus_1": float(value["plus_1sigma"]), "plus_2": float(value["plus_2sigma"]),
            "minus_1": float(value["minus_1sigma"]), "minus_2": float(value["minus_2sigma"]),
        }

top = st.columns(4)
top[0].metric("Current premium", pct(stats["current"]))
top[1].metric("1-year percentile", pct(stats["percentile"], 1))
top[2].metric("Historical mean (mu)", pct(stats["mean"]))
top[3].metric("Standard deviation (sigma)", pct(stats["std"]))

bands = st.columns(4)
bands[0].metric("mu + 1 sigma", pct(stats["plus_1"]))
bands[1].metric("mu + 2 sigma", pct(stats["plus_2"]))
bands[2].metric("mu - 1 sigma", pct(stats["minus_1"]))
bands[3].metric("mu - 2 sigma", pct(stats["minus_2"]))

st.subheader("Task-book strategy label")
st.metric("Current label", premium_signal(etf.category, stats["current"]))
if etf.category == "\u7eb3\u6307":
    st.code("<3% Add | 3%-6% Hold / Buy | 6%-8.5% Cautious | 8.5%-10% Reduce | >10% Avoid")
else:
    st.code("<1.5% Add | 1.5%-4.5% Hold / Buy | 4.5%-7% Reduce | >7% Avoid")
st.warning(DISCLAIMER)
