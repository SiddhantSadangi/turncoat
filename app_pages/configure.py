"""Config: session state keys, load models/voices, defaults. Topic and duration are on Debate page and sidebar."""

from __future__ import annotations

import streamlit as st

from lib import auth, elevenlabs_tts, openrouter

# Session state keys
TOPIC_KEY = "topic"
LLM_1_KEY = "llm_1_id"
LLM_2_KEY = "llm_2_id"
VOICE_1_KEY = "voice_1_id"
VOICE_2_KEY = "voice_2_id"
ROUND_DURATION_KEY = "round_duration_sec"
DEFAULT_DURATION_SEC = 30


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
            st.session_state["elevenlabs_voices"] = elevenlabs_tts.list_voices(elevenlabs_key)
        except Exception:
            st.session_state["elevenlabs_voices"] = []


def ensure_models_and_voices_loaded() -> None:
    """
    Load models/voices when API keys are set (either or both). No UI.
    Call this before reading topic/llm_1/etc. so defaults are in session_state.
    """
    openrouter_key, elevenlabs_key = auth.get_api_keys()
    if not openrouter_key and not elevenlabs_key:
        return
    need_load = (openrouter_key and "openrouter_models" not in st.session_state) or (
        elevenlabs_key and "elevenlabs_voices" not in st.session_state
    )
    if need_load:
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
    if TOPIC_KEY not in st.session_state:
        st.session_state[TOPIC_KEY] = ""
    if "openrouter/free" in model_ids:
        if LLM_1_KEY not in st.session_state:
            st.session_state[LLM_1_KEY] = "openrouter/free"
        if LLM_2_KEY not in st.session_state:
            st.session_state[LLM_2_KEY] = "openrouter/free"
    if voice_ids and voice_ids[0] != "(no voices loaded)":
        if VOICE_1_KEY not in st.session_state:
            st.session_state[VOICE_1_KEY] = voice_ids[0]
        if VOICE_2_KEY not in st.session_state:
            st.session_state[VOICE_2_KEY] = voice_ids[0]


def render_config_form() -> None:
    """Show config UI (info or caption). Call ensure_models_and_voices_loaded() before reading config."""
    openrouter_key, elevenlabs_key = auth.get_api_keys()
    if not openrouter_key:
        st.info("Set your OpenRouter API key in the sidebar to continue.")
        return
    ensure_models_and_voices_loaded()
    if elevenlabs_key:
        st.caption("Topic below, duration in sidebar. Choose LLMs and voices below.")
    else:
        st.caption(
            "Topic below, duration in sidebar. Choose LLMs below. "
            "Add your ElevenLabs API key in the sidebar to enable voice selection and audio playback."
        )


def get_model_and_voice_options() -> tuple[list[str], list[str], dict[str, str]]:
    """
    Return (model_ids, voice_ids, voice_id_to_name) from session_state.
    Call after render_config_form() so models/voices are loaded.
    """
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
    return model_ids, voice_ids, voice_id_to_name
