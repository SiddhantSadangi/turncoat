# Turncoat app pages: Debate, History

import streamlit as st

from app_pages import debate, history

PAGES = [
    st.Page(debate.render, title="Debate", icon="🎤", url_path="debate"),
    st.Page(history.render, title="History", icon="📋", url_path="history"),
]
