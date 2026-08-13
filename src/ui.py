"""Small Streamlit-only helpers kept outside the data and metrics layers."""

from __future__ import annotations

import streamlit as st

from config.assets import DEFAULT_WORKBOOK_PATH
from src.excel_loader import load_dashboard_data
from src.validation import WorkbookValidationError


@st.cache_data(show_spinner=False)
def _load(source_bytes: bytes | None):
    return load_dashboard_data(source_bytes) if source_bytes else load_dashboard_data(DEFAULT_WORKBOOK_PATH)


def render_source_uploader() -> None:
    uploaded = st.sidebar.file_uploader("Upload saved Wind / test Excel", type=["xlsx"])
    if uploaded is not None:
        st.session_state["dashboard_source"] = uploaded.getvalue()
        st.session_state["dashboard_source_name"] = uploaded.name
    if st.sidebar.button("Use built-in mock Excel"):
        st.session_state.pop("dashboard_source", None)
        st.session_state.pop("dashboard_source_name", None)
    st.sidebar.caption(f"Data source: {st.session_state.get('dashboard_source_name', DEFAULT_WORKBOOK_PATH.name)}")


def get_data():
    try:
        frames, result = _load(st.session_state.get("dashboard_source"))
        for warning in result.warnings:
            st.warning(warning)
        return frames
    except (WorkbookValidationError, ValueError, FileNotFoundError) as exc:
        st.error(f"Excel data cannot be used:\n{exc}")
        st.stop()
