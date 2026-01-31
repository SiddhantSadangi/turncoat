"""
Turncoat – LLM turncoat debate app.
Entrypoint: sidebar (API keys), navigation (Configure, Debate, History).
"""

import streamlit as st

from app_pages import PAGES


def main() -> None:
    st.set_page_config(page_title="Turncoat", page_icon="🔄", layout="centered")

    # API keys in sidebar (used when secrets not set)
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

    pg = st.navigation(PAGES)
    pg.run()


if __name__ == "__main__":
    main()
