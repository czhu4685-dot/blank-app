"""ETF detail page."""

import plotly.express as px
import streamlit as st

from src.ui import get_data, render_source_uploader

render_source_uploader()
frames = get_data()
current = frames["ETF_Current"]
history = frames["ETF_History"]

st.title("ETF Monitor - 单品详情")
option_labels = {f"{row.code} | {row.name}": row.code for row in current.itertuples()}
selected_label = st.selectbox("选择 ETF", options=list(option_labels))
code = option_labels[selected_label]
record = current.loc[current["code"] == code].iloc[0]

cols = st.columns(4)
cols[0].metric("Close", f"{record['close']:.4f}")
cols[1].metric("NAV", f"{record['nav']:.4f}" if record["nav"] == record["nav"] else "—")
cols[2].metric("Premium", f"{record['premium']:.2%}" if record["premium"] == record["premium"] else "—")
cols[3].metric("Daily change", f"{record['pct_change']:.2%}")

series = history.loc[history["code"] == code].sort_values("date")
st.subheader("近一年溢价率")
if series.empty:
    st.warning("该 ETF 没有可展示的历史数据。")
else:
    chart = px.line(series, x="date", y="premium", title=f"{code} 溢价率（市价 / NAV - 1）")
    chart.update_yaxes(tickformat=".1%")
    chart.update_layout(margin=dict(l=10, r=10, t=45, b=10))
    st.plotly_chart(chart, width="stretch")
