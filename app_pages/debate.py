"""Debate page: config expander at top, then run turncoat debate (Phase 3–4)."""

from __future__ import annotations

import streamlit as st

from app_pages.configure import (
    DEBATE_CONFIG_KEY,
    DEFAULT_DURATION_SEC,
    LLM_1_KEY,
    LLM_2_KEY,
    ROUND_DURATION_KEY,
    TOPIC_KEY,
    VOICE_1_KEY,
    VOICE_2_KEY,
    render_config_form,
)

INVALID_PLACEHOLDERS = ("(no models loaded)", "(no voices loaded)")


def render() -> None:
    st.title("Debate")
    st.caption("Configure the debate in the expander and submit to start.")

    # Config in collapsible expander; collapse after "Start debate" (when debate_config is saved)
    with st.expander("Configure debate", expanded=not st.session_state.get(DEBATE_CONFIG_KEY)):
        render_config_form()

    # Read config from saved debate_config (persists after History) or session_state
    config = st.session_state.get(DEBATE_CONFIG_KEY, {})
    topic = (config.get(TOPIC_KEY) or st.session_state.get(TOPIC_KEY) or "").strip()
    llm_1 = config.get(LLM_1_KEY) or st.session_state.get(LLM_1_KEY)
    llm_2 = config.get(LLM_2_KEY) or st.session_state.get(LLM_2_KEY)
    voice_1 = config.get(VOICE_1_KEY) or st.session_state.get(VOICE_1_KEY)
    voice_2 = config.get(VOICE_2_KEY) or st.session_state.get(VOICE_2_KEY)
    duration = config.get(ROUND_DURATION_KEY) or st.session_state.get(
        ROUND_DURATION_KEY, DEFAULT_DURATION_SEC
    )

    invalid = (
        not topic
        or not llm_1
        or not llm_2
        or not voice_1
        or not voice_2
        or llm_1 in INVALID_PLACEHOLDERS
        or llm_2 in INVALID_PLACEHOLDERS
        or voice_1 in INVALID_PLACEHOLDERS
        or voice_2 in INVALID_PLACEHOLDERS
    )
    if invalid:
        st.info(
            "Set a topic, choose two LLMs and two voices in the **Configure debate** expander above, then click **Start debate**."
        )
        return

    st.divider()

    st.write("**Topic:** ", topic)
    st.write("**LLM 1:** ", llm_1, " · **LLM 2:** ", llm_2)
    st.write("**Round duration:** ", duration, " s")

    st.caption("Phase 3–4 will add the debate engine and TTS playback here.")
