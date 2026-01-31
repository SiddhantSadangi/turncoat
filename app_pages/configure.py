"""Config form: topic, 2 LLMs, 2 voices, round duration. Used inside Debate page expander."""

from __future__ import annotations

import streamlit as st

from lib import auth, elevenlabs_tts, openrouter

# Session state keys for debate config
TOPIC_KEY = "topic"
LLM_1_KEY = "llm_1_id"
LLM_2_KEY = "llm_2_id"
VOICE_1_KEY = "voice_1_id"
VOICE_2_KEY = "voice_2_id"
ROUND_DURATION_KEY = "round_duration_sec"
DEFAULT_DURATION_SEC = 45
DEBATE_CONFIG_KEY = "debate_config"


def _load_models_and_voices() -> None:
    """Fetch OpenRouter models and ElevenLabs voices and store in session_state."""
    openrouter_key, elevenlabs_key = auth.get_api_keys()
    if openrouter_key:
        try:
            st.session_state["openrouter_models"] = openrouter.list_models(openrouter_key)
        except Exception:
            st.session_state["openrouter_models"] = []
    if elevenlabs_key:
        try:
            st.session_state["elevenlabs_voices"] = elevenlabs_tts.list_voices(
                elevenlabs_key
            )
        except Exception:
            st.session_state["elevenlabs_voices"] = []


def render_config_form() -> None:
    """Render config inside st.form; submit button saves to debate_config so config survives navigation."""
    openrouter_key, elevenlabs_key = auth.get_api_keys()
    if not openrouter_key or not elevenlabs_key:
        st.info("Set OpenRouter and ElevenLabs API keys in the sidebar to continue.")
        return

    # Restore saved config so form shows it after navigating back from History
    if DEBATE_CONFIG_KEY in st.session_state:
        for k, v in st.session_state[DEBATE_CONFIG_KEY].items():
            st.session_state[k] = v

    # Auto-load models and voices once per session
    if "openrouter_models" not in st.session_state or "elevenlabs_voices" not in st.session_state:
        with st.spinner("Loading models and voices…"):
            _load_models_and_voices()

    models = st.session_state.get("openrouter_models", [])
    voices = st.session_state.get("elevenlabs_voices", [])

    model_ids = [m.get("id") or m.get("name", "") for m in models]
    voice_id_to_name = {v.get("voice_id", ""): v.get("name", "") for v in voices}
    voice_ids = list(voice_id_to_name.keys())
    if not model_ids:
        model_ids = ["(no models loaded)"]
    if not voice_ids:
        voice_ids = ["(no voices loaded)"]
        voice_id_to_name["(no voices loaded)"] = "(no voices loaded)"

    # Defaults when no saved config
    if ROUND_DURATION_KEY not in st.session_state:
        st.session_state[ROUND_DURATION_KEY] = DEFAULT_DURATION_SEC
    if TOPIC_KEY not in st.session_state:
        st.session_state[TOPIC_KEY] = ""

    with st.form("debate_config_form"):
        topic = st.text_input(
            "Debate topic",
            placeholder="e.g. Universal basic income should be implemented.",
            key=TOPIC_KEY,
            help="The motion or statement the two LLMs will debate for and against.",
        )

        c1, c2 = st.columns(2)
        with c1:
            llm_1 = st.selectbox(
                "LLM 1",
                options=model_ids,
                key=LLM_1_KEY,
                help="First debater (OpenRouter model).",
            )
            voice_1 = st.selectbox(
                "Voice for LLM 1",
                options=voice_ids,
                format_func=lambda vid: voice_id_to_name.get(vid, vid),
                key=VOICE_1_KEY,
                help="ElevenLabs voice used to speak LLM 1's lines.",
            )
        with c2:
            llm_2 = st.selectbox(
                "LLM 2",
                options=model_ids,
                key=LLM_2_KEY,
                help="Second debater (OpenRouter model).",
            )
            voice_2 = st.selectbox(
                "Voice for LLM 2",
                options=voice_ids,
                format_func=lambda vid: voice_id_to_name.get(vid, vid),
                key=VOICE_2_KEY,
                help="ElevenLabs voice used to speak LLM 2's lines.",
            )

        duration = st.slider(
            "Round duration (seconds)",
            min_value=15,
            max_value=120,
            value=st.session_state.get(ROUND_DURATION_KEY, DEFAULT_DURATION_SEC),
            key=ROUND_DURATION_KEY,
            help="Target length of each speech when read aloud.",
        )

        st.caption(
            f"Each speech will be constrained to ~{int(duration * 150 / 60)} words "
            f"for {duration} s at ~150 wpm."
        )

        submitted = st.form_submit_button("Start debate")

    if submitted:
        # Persist config so it survives navigation to History and back.
        # Do not write to topic/llm_1_id/etc. — those keys are bound to form widgets.
        st.session_state[DEBATE_CONFIG_KEY] = {
            TOPIC_KEY: topic,
            LLM_1_KEY: llm_1,
            LLM_2_KEY: llm_2,
            VOICE_1_KEY: voice_1,
            VOICE_2_KEY: voice_2,
            ROUND_DURATION_KEY: duration,
        }
