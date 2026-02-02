# Turncoat app pages: Landing, Debate

import streamlit as st

from app_pages import debate, landing

PAGES = [
    st.Page(landing.render, title="Home", icon=":material/home:", default=True),
    st.Page(debate.render, title="Debate", icon=":material/campaign:", url_path="debate"),
]
