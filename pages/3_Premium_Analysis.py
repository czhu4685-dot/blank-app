"""Premium statistics and task-book rule display."""

import math

import streamlit as st

from src.ui import get_data, render_source_uploader
from config.assets import DISCLAIMER
from src.metrics import premium_statistics
from src.signals import premium_signal

render_source_uploader()
frames = get_data()
current = frames["ETF_Current"]
history = frames["ETF_History"]
eligible = current[current["category"].isin(["\u7eb3\u6307", "\u6807\u666e"])]

st.title("Premium Analysis")
st.caption("统计基于上传 Excel 中该 ETF 的近一年历史记录；标准差使用总体标准差 σ。")
options = {f"{row.code} | {row.name}（{row.category}）": row for row in eligible.itertuples()}
selected = st.selectbox("选择纳指或标普 ETF", list(options))
etf = options[selected]
stats = premium_statistics(history, etf.code)

top = st.columns(4)
top[0].metric("当前溢价率", "—" if math.isnan(stats["current"]) else f"{stats['current']:.2%}")
top[1].metric("近 1 年历史分位", "—" if math.isnan(stats["percentile"]) else f"{stats['percentile']:.1%}")
top[2].metric("历史均值 μ", "—" if math.isnan(stats["mean"]) else f"{stats['mean']:.2%}")
top[3].metric("标准差 σ", "—" if math.isnan(stats["std"]) else f"{stats['std']:.2%}")

bands = st.columns(4)
bands[0].metric("μ + 1σ", f"{stats['plus_1']:.2%}")
bands[1].metric("μ + 2σ", f"{stats['plus_2']:.2%}")
bands[2].metric("μ - 1σ", f"{stats['minus_1']:.2%}")
bands[3].metric("μ - 2σ", f"{stats['minus_2']:.2%}")

st.subheader("任务书策略标签")
st.metric("当前标签", premium_signal(etf.category, stats["current"]))
if etf.category == "纳指":
    st.code("<3% 加仓 ｜ 3%-6% 持有/可买 ｜ 6%-8.5% 谨慎/少买 ｜ 8.5%-10% 减仓 ｜ >10% 回避")
else:
    st.code("<1.5% 加仓 ｜ 1.5%-4.5% 持有/可买 ｜ 4.5%-7% 减仓 ｜ >7% 回避")
st.warning(DISCLAIMER)
