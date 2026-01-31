"""
Turncoat – LLM turncoat debate app.
Phase 1: API clients and test page.
"""

import streamlit as st

from lib import elevenlabs_tts, openrouter


def _get_api_keys() -> tuple[str | None, str | None]:
    """Use Streamlit secrets if present, else session state (UI input)."""
    openrouter_key = None
    elevenlabs_key = None
    try:
        if hasattr(st, "secrets") and st.secrets:
            openrouter_key = st.secrets.get("OPENROUTER_API_KEY")
            elevenlabs_key = st.secrets.get("ELEVENLABS_API_KEY")
    except Exception:
        pass
    if not openrouter_key:
        openrouter_key = st.session_state.get("openrouter_api_key") or ""
    if not elevenlabs_key:
        elevenlabs_key = st.session_state.get("elevenlabs_api_key") or ""
    return openrouter_key or None, elevenlabs_key or None


def main() -> None:
    st.set_page_config(page_title="Turncoat", page_icon="🔄", layout="centered")
    st.title("Turncoat – Phase 1 test")
    st.caption("Test OpenRouter and ElevenLabs API clients.")

    # API keys in sidebar (used when secrets not set)
    with st.sidebar:
        st.subheader("API keys")
        st.session_state["openrouter_api_key"] = st.text_input(
            "OpenRouter API key",
            value=st.session_state.get("openrouter_api_key", ""),
            type="password",
            placeholder="sk-or-v1-...",
            help="Get your key: https://openrouter.ai/keys",
        )
        st.session_state["elevenlabs_api_key"] = st.text_input(
            "ElevenLabs API key",
            value=st.session_state.get("elevenlabs_api_key", ""),
            type="password",
            placeholder="sk_...",
            help="Get your key: https://elevenlabs.io/app/settings/api-keys",
        )

    openrouter_key, elevenlabs_key = _get_api_keys()

    st.divider()

    # ----- OpenRouter: list models -----
    st.subheader("OpenRouter – list models")
    if openrouter_key:
        if st.button("Fetch models", key="fetch_models"):
            with st.spinner("Fetching…"):
                try:
                    models = openrouter.list_models(openrouter_key)
                    st.session_state["openrouter_models"] = models
                    st.success(f"Loaded {len(models)} models.")
                except Exception as e:
                    st.error(str(e))
        if "openrouter_models" in st.session_state:
            models = st.session_state["openrouter_models"]
            ids = [m.get("id") or m.get("name", "") for m in models]
            st.selectbox(
                "Models (for test completion below)",
                options=ids,
                key="openrouter_model_choice",
                label_visibility="collapsed",
            )
    else:
        st.info("Set OpenRouter API key above to fetch models.")

    # ----- OpenRouter: one completion -----
    st.subheader("OpenRouter – one completion")
    if openrouter_key:
        test_prompt = st.text_input(
            "Prompt for test completion",
            value="Say hello in one short sentence.",
            key="test_prompt",
        )
        if st.button("Run completion", key="run_completion"):
            model = st.session_state.get("openrouter_model_choice")
            if not model and "openrouter_models" in st.session_state:
                model = st.session_state["openrouter_models"][0].get("id")
            if not model:
                st.warning("Fetch models first and pick one.")
            else:
                with st.spinner("Calling OpenRouter…"):
                    try:
                        out = openrouter.chat_completion(
                            openrouter_key,
                            model,
                            [{"role": "user", "content": test_prompt}],
                            max_tokens=100,
                        )
                        st.write("**Response:**")
                        st.write(out)
                    except Exception as e:
                        st.error(str(e))
    else:
        st.info("Set OpenRouter API key above.")

    st.divider()

    # ----- ElevenLabs: list voices -----
    st.subheader("ElevenLabs – list voices")
    if elevenlabs_key:
        if st.button("Fetch voices", key="fetch_voices"):
            with st.spinner("Fetching…"):
                try:
                    voices = elevenlabs_tts.list_voices(elevenlabs_key)
                    st.session_state["elevenlabs_voices"] = voices
                    st.success(f"Loaded {len(voices)} voices.")
                except Exception as e:
                    st.error(str(e))
        if "elevenlabs_voices" in st.session_state:
            voices = st.session_state["elevenlabs_voices"]
            options = [v.get("name", "") for v in voices]
            st.selectbox(
                "Voice (for TTS below)",
                range(len(options)),
                format_func=lambda i: options[i],
                key="elevenlabs_voice_choice",
                label_visibility="collapsed",
            )
    else:
        st.info("Set ElevenLabs API key above to fetch voices.")

    # ----- ElevenLabs: one TTS -----
    st.subheader("ElevenLabs – one TTS")
    if elevenlabs_key:
        tts_text = st.text_input(
            "Text to speak",
            value="Hello. This is a short test of text to speech.",
            key="tts_text",
        )
        if st.button("Generate and play", key="run_tts"):
            voice_id = None
            if "elevenlabs_voices" in st.session_state:
                idx = st.session_state.get("elevenlabs_voice_choice", 0)
                voices = st.session_state["elevenlabs_voices"]
                if 0 <= idx < len(voices):
                    voice_id = voices[idx].get("voice_id")
            if not voice_id:
                st.warning("Fetch voices first and pick one.")
            else:
                with st.spinner("Generating audio…"):
                    try:
                        audio_bytes = elevenlabs_tts.text_to_speech(
                            elevenlabs_key,
                            voice_id,
                            tts_text,
                        )
                        st.audio(audio_bytes, format="audio/mpeg")
                    except Exception as e:
                        st.error(str(e))
    else:
        st.info("Set ElevenLabs API key above.")


if __name__ == "__main__":
    main()
