"""Global index monitoring page."""

import pandas as pd
import streamlit as st

from src.ui import get_data, render_source_uploader

render_source_uploader()
indices = get_data()["Global_Index"].copy()
latest = indices.sort_values("date").groupby("code", as_index=False).tail(1).sort_values("code")

st.title("Global Markets")
st.caption(f"数据日期：{latest['date'].max():%Y-%m-%d}")
display = latest.copy()
display["pct_change"] = display["pct_change"].map(lambda value: "—" if pd.isna(value) else f"{value:.2%}")
display["pe_ttm"] = display["pe_ttm"].map(lambda value: "—" if pd.isna(value) else f"{value:.2f}")
st.dataframe(display[["code", "name", "close", "pct_change", "pe_ttm", "date"]], width="stretch", hide_index=True)
st.caption("PE(TTM) 仅展示 Excel 已保存的数值；字段可用性与口径等真实 Wind Excel 后验证。")
