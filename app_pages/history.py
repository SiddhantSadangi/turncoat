"""History page: list and replay saved debates (Phase 6)."""

from __future__ import annotations

import streamlit as st


def render() -> None:
    st.title("History")
    st.caption("Past debates will appear here once persistence is added (Phase 6).")

    st.info("No saved debates yet. Run a debate on the **Debate** page to save one.")
