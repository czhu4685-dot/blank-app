"""Homepage for the local QDII ETF monitoring prototype."""

import pandas as pd
import streamlit as st

from config.assets import HIGH_PREMIUM_THRESHOLD
from src.ui import get_data, render_source_uploader

st.set_page_config(page_title="QDII ETF Monitor", page_icon="📊", layout="wide")
render_source_uploader()
frames = get_data()
current = frames["ETF_Current"].copy()

st.title("QDII ETF Daily Monitor")
st.caption("Local Excel-reading prototype. Premium is always calculated as close / NAV - 1.")
data_date = current["date"].max()
metrics = st.columns(4)
metrics[0].metric("Data date", data_date.strftime("%Y-%m-%d"))
metrics[1].metric("ETFs monitored", len(current))
metrics[2].metric("Average premium", f"{current['premium'].mean():.2%}")
metrics[3].metric("High-premium ETFs", int((current["premium"] >= HIGH_PREMIUM_THRESHOLD).sum()))

categories = sorted(current["category"].dropna().unique())
selected_categories = st.multiselect("Filter by category", options=categories, default=categories)
view = current[current["category"].isin(selected_categories)].copy()
for column in ["premium", "pct_change"]:
    view[column] = view[column].map(lambda value: "—" if pd.isna(value) else f"{value:.2%}")

st.subheader("ETF overview")
st.dataframe(
    view[["code", "name", "category", "close", "nav", "premium", "fund_scale", "amount", "pct_change", "purchase_status"]],
    width="stretch",
    hide_index=True,
    column_config={
        "fund_scale": st.column_config.NumberColumn("Fund scale (RMB 100m)", format="%.2f"),
        "amount": st.column_config.NumberColumn("Turnover (RMB 100m)", format="%.2f"),
    },
)
st.info("Use the page navigation for ETF detail, global markets, and premium analysis. An uploaded Excel file is used across all pages in this session.")
