# Turncoat app pages: Landing, Debate

import streamlit as st

from app_pages import landing, debate

PAGES = [
    st.Page(landing.render, title="Home", icon="🔄", default=True),
    st.Page(debate.render, title="Debate", icon="🎤", url_path="debate"),
]
