"""Debate page: topic, model/voice selection, then 2×2 grid (LLM 1 | LLM 2) with one-by-one speech generation."""

from __future__ import annotations

import streamlit as st

from app_pages.configure import (
    DEFAULT_DURATION_SEC,
    LLM_1_KEY,
    LLM_2_KEY,
    ROUND_DURATION_KEY,
    TOPIC_KEY,
    VOICE_1_KEY,
    VOICE_2_KEY,
    get_model_and_voice_options,
    render_config_form,
)
from lib import auth, debate_engine

NUM_SPEECHES = debate_engine.NUM_SPEECHES

INVALID_PLACEHOLDERS = ("(no models loaded)", "(no voices loaded)")
DEBATE_SPEECHES_KEY = "debate_speeches"

# Speech order: 0 = LLM1 for, 1 = LLM2 against, 2 = LLM2 for, 3 = LLM1 against.
# Grid: col 0 = LLM 1 (speeches 0, 3), col 1 = LLM 2 (speeches 1, 2).
SPEECH_LABELS = [
    "1 (for)",
    "2 (against)",
    "3 (for)",
    "4 (against)",
]
# (col, row) for each speech index: LLM1 row0, LLM2 row0, LLM2 row1, LLM1 row1
COL_FOR_INDEX = [0, 1, 1, 0]  # speech 0,1,2,3 -> col 0,1,1,0


def _speech_cell(
    speech_index: int,
    label: str,
    speech: dict | None,
    can_generate: bool,
    openrouter_key: str | None,
    topic: str,
    llm_1: str,
    llm_2: str,
    duration: int,
    previous_speeches: list[dict],
) -> None:
    st.subheader(label, anchor=False)
    if speech:
        st.caption(speech.get("model_id", ""))
        st.write(speech["text"])
    else:
        st.caption("Not generated yet.")
        if openrouter_key and can_generate:
            if st.button("Generate", key=f"gen_speech_{speech_index}"):
                with st.spinner("Generating…"):
                    try:
                        result = debate_engine.generate_single_speech(
                            api_key=openrouter_key,
                            topic=topic,
                            speech_index=speech_index,
                            previous_speeches=previous_speeches,
                            llm_1_id=llm_1,
                            llm_2_id=llm_2,
                            duration_sec=duration,
                        )
                        if DEBATE_SPEECHES_KEY not in st.session_state:
                            st.session_state[DEBATE_SPEECHES_KEY] = [None] * NUM_SPEECHES
                        st.session_state[DEBATE_SPEECHES_KEY][speech_index] = result
                        st.rerun()
                    except Exception as e:
                        st.error(str(e))
        elif not openrouter_key:
            st.caption("Set OpenRouter API key in the sidebar.")
        elif not can_generate:
            st.caption("Generate the previous speech(s) first.")


def render() -> None:
    st.title("Debate")

    st.text_input(
        "Topic",
        placeholder="e.g. Universal basic income should be implemented.",
        key=TOPIC_KEY,
        help="The motion or statement the two LLMs will debate for and against.",
    )

    # Load models/voices and set defaults when API keys are set (no expander)
    render_config_form()

    # Always show model/voice selectboxes (visible even without a topic)
    model_ids, voice_ids, voice_id_to_name = get_model_and_voice_options()
    sel_col1, sel_col2 = st.columns(2)
    with sel_col1:
        st.selectbox(
            "LLM 1",
            options=model_ids,
            key=LLM_1_KEY,
            help="First debater (OpenRouter model).",
        )
        st.selectbox(
            "Voice for LLM 1",
            options=voice_ids,
            format_func=lambda vid: voice_id_to_name.get(vid, vid),
            key=VOICE_1_KEY,
            help="ElevenLabs voice for LLM 1.",
        )
    with sel_col2:
        st.selectbox(
            "LLM 2",
            options=model_ids,
            key=LLM_2_KEY,
            help="Second debater (OpenRouter model).",
        )
        st.selectbox(
            "Voice for LLM 2",
            options=voice_ids,
            format_func=lambda vid: voice_id_to_name.get(vid, vid),
            key=VOICE_2_KEY,
            help="ElevenLabs voice for LLM 2.",
        )

    topic = (st.session_state.get(TOPIC_KEY) or "").strip()
    llm_1 = st.session_state.get(LLM_1_KEY)
    llm_2 = st.session_state.get(LLM_2_KEY)
    voice_1 = st.session_state.get(VOICE_1_KEY)
    voice_2 = st.session_state.get(VOICE_2_KEY)
    duration = st.session_state.get(ROUND_DURATION_KEY, DEFAULT_DURATION_SEC)

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
            "Enter a topic above, set round duration in the sidebar, and choose two LLMs and two voices above."
        )
        return

    st.divider()
    st.caption(f"Round duration: {duration} s (sidebar)")

    if DEBATE_SPEECHES_KEY not in st.session_state:
        st.session_state[DEBATE_SPEECHES_KEY] = [None] * NUM_SPEECHES
    speeches = st.session_state[DEBATE_SPEECHES_KEY]

    openrouter_key, _ = auth.get_api_keys()
    if not openrouter_key:
        st.warning("Set your OpenRouter API key in the sidebar to generate speeches.")

    # Clear button
    if any(speeches):
        if st.button("Clear all speeches"):
            st.session_state[DEBATE_SPEECHES_KEY] = [None] * NUM_SPEECHES
            st.rerun()

    # Two columns: LLM 1 (speeches 0, 3), LLM 2 (speeches 1, 2)
    col_llm1, col_llm2 = st.columns(2)
    cells_col0 = [(i, SPEECH_LABELS[i]) for i in range(NUM_SPEECHES) if COL_FOR_INDEX[i] == 0]
    cells_col1 = [(i, SPEECH_LABELS[i]) for i in range(NUM_SPEECHES) if COL_FOR_INDEX[i] == 1]

    with col_llm1:
        for speech_index, label in cells_col0:
            prev = [speeches[i] for i in range(speech_index) if speeches[i]]
            can_gen = all(speeches[i] is not None for i in range(speech_index))
            _speech_cell(
                speech_index=speech_index,
                label=label,
                speech=speeches[speech_index],
                can_generate=can_gen,
                openrouter_key=openrouter_key,
                topic=topic,
                llm_1=llm_1,
                llm_2=llm_2,
                duration=int(duration),
                previous_speeches=prev,
            )
            st.markdown("")

    with col_llm2:
        for speech_index, label in cells_col1:
            prev = [speeches[i] for i in range(speech_index) if speeches[i]]
            can_gen = all(speeches[i] is not None for i in range(speech_index))
            _speech_cell(
                speech_index=speech_index,
                label=label,
                speech=speeches[speech_index],
                can_generate=can_gen,
                openrouter_key=openrouter_key,
                topic=topic,
                llm_1=llm_1,
                llm_2=llm_2,
                duration=int(duration),
                previous_speeches=prev,
            )
            st.markdown("")
