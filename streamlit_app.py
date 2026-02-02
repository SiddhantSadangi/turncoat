"""
Turncoat – LLM turncoat debate app.
Entrypoint: sidebar (API keys, round duration), navigation (Home, Debate).
"""

import streamlit as st

from app_pages import PAGES
from app_pages.configure import DEFAULT_DURATION_SEC, ROUND_DURATION_KEY


def main() -> None:
    st.set_page_config(page_title="Turncoat", page_icon="🔄", layout="centered")

    with st.sidebar:
        st.subheader("API keys")
        st.text_input(
            "OpenRouter API key",
            type="password",
            placeholder="sk-or-v1-...",
            help="Get your key: https://openrouter.ai/keys",
            key="openrouter_api_key",
        )
        st.text_input(
            "ElevenLabs API key",
            type="password",
            placeholder="sk_...",
            help="Get your key: https://elevenlabs.io/app/settings/api-keys",
            key="elevenlabs_api_key",
        )
        st.divider()
        st.subheader("Debate")
        st.slider(
            "Round duration (sec)",
            min_value=30,
            max_value=120,
            value=st.session_state.get(ROUND_DURATION_KEY, DEFAULT_DURATION_SEC),
            key=ROUND_DURATION_KEY,
            help="Target length of each speech when read aloud.",
        )

    pg = st.navigation(PAGES)
    pg.run()


if __name__ == "__main__":
    main()
