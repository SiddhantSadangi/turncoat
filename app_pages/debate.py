"""Debate page: topic, model/voice selection, then 2×2 grid (LLM 1 | LLM 2) with one-by-one speech generation."""

from __future__ import annotations

import concurrent.futures

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
from lib import auth, debate_engine, elevenlabs_tts

NUM_SPEECHES = debate_engine.NUM_SPEECHES

INVALID_PLACEHOLDERS = ("(no models loaded)", "(no voices loaded)")
DEBATE_SPEECHES_KEY = "debate_speeches"
DEBATE_AUDIO_KEY = "debate_audio"  # {speech_index: bytes}

# Speech order: 0 = LLM1 for, 1 = LLM2 against, 2 = LLM2 for, 3 = LLM1 against.
# Grid: col 0 = LLM 1 (speeches 0, 3), col 1 = LLM 2 (speeches 1, 2).
SPEECH_LABELS = [
    "1. LLM 1 (for)",
    "2. LLM 2 (against)",
    "3. LLM 2 (for)",
    "4. LLM 1 (against)",
]
# (col, row) for each speech index: LLM1 row0, LLM2 row0, LLM2 row1, LLM1 row1
COL_FOR_INDEX = [0, 1, 1, 0]  # speech 0,1,2,3 -> col 0,1,1,0


def _speech_cell(
    speech_index: int,
    label: str,
    speech: dict | None,
    can_generate: bool,
    openrouter_key: str | None,
    elevenlabs_key: str | None,
    voice_id: str,
    topic: str,
    llm_1: str,
    llm_2: str,
    duration: int,
    previous_speeches: list[dict],
) -> None:
    st.subheader(label, anchor=False)
    if speech and speech.get("text") and speech["text"].strip():
        st.caption(speech.get("model_id", ""))
        # Audio above transcript
        audio_placeholder = st.container()
        with audio_placeholder:
            audio_cache = st.session_state.get(DEBATE_AUDIO_KEY) or {}
            if speech_index in audio_cache:
                st.audio(audio_cache[speech_index], format="audio/mpeg")
            elif elevenlabs_key and voice_id and voice_id not in INVALID_PLACEHOLDERS:
                if st.button(
                    "Play",
                    key=f"play_speech_{speech_index}",
                    icon=":material/play_circle:",
                ):
                    with st.spinner("Generating audio…"):
                        try:
                            audio_bytes = elevenlabs_tts.text_to_speech(
                                elevenlabs_key, voice_id, speech["text"]
                            )
                            if DEBATE_AUDIO_KEY not in st.session_state:
                                st.session_state[DEBATE_AUDIO_KEY] = {}
                            st.session_state[DEBATE_AUDIO_KEY][speech_index] = audio_bytes
                            st.rerun()
                        except Exception as e:
                            st.error(str(e))
            else:
                row = st.columns([3, 1])
                with row[0]:
                    st.button(
                        "Play",
                        key=f"play_speech_{speech_index}",
                        icon=":material/play_circle:",
                        disabled=True,
                    )
                with row[1]:
                    with st.popover(":material/info:", help="Why is Play disabled?"):
                        st.caption(
                            "Add your ElevenLabs API key in the sidebar to enable audio playback."
                        )
        st.write(speech["text"])
    else:
        if speech:
            st.caption("Previous attempt returned empty. You can retry below.")
        else:
            st.caption("Not generated yet.")
        can_retry = can_generate or (speech is not None)  # allow retry when slot exists but empty
        if openrouter_key and can_retry:
            if st.button(
                "Generate",
                key=f"gen_speech_{speech_index}",
                icon=":material/auto_awesome:",
            ):
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
        else:
            st.caption("Generate the previous speech(s) first.")


def render() -> None:
    st.title(":material/campaign: Debate")

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

    # Voices required only when ElevenLabs key is set (for audio)
    openrouter_key, elevenlabs_key = auth.get_api_keys()
    need_voices = bool(elevenlabs_key)
    invalid = (
        not topic
        or not llm_1
        or not llm_2
        or llm_1 in INVALID_PLACEHOLDERS
        or llm_2 in INVALID_PLACEHOLDERS
        or (
            need_voices
            and (
                not voice_1
                or not voice_2
                or voice_1 in INVALID_PLACEHOLDERS
                or voice_2 in INVALID_PLACEHOLDERS
            )
        )
    )

    if invalid:
        msg = (
            "Enter a topic above, set round duration in the sidebar, and choose two LLMs and two voices above."
            if need_voices
            else "Enter a topic above, set round duration in the sidebar, and choose two LLMs above."
        )
        st.info(msg)
        return

    st.divider()
    st.caption(f"Round duration: {duration} s (sidebar)")

    if DEBATE_SPEECHES_KEY not in st.session_state:
        st.session_state[DEBATE_SPEECHES_KEY] = [None] * NUM_SPEECHES
    speeches = st.session_state[DEBATE_SPEECHES_KEY]

    if not openrouter_key:
        st.warning("Set your OpenRouter API key in the sidebar to generate speeches.")

    # Row: Generate all speeches | Generate all audio | Clear all speeches
    audio_cache = st.session_state.get(DEBATE_AUDIO_KEY) or {}
    all_have_audio = all(i in audio_cache for i in range(NUM_SPEECHES))
    voices_ok = (
        voice_1
        and voice_2
        and voice_1 not in INVALID_PLACEHOLDERS
        and voice_2 not in INVALID_PLACEHOLDERS
    )
    all_have_speeches = all(speeches)
    btn_col1, btn_col2, btn_col3 = st.columns(3)
    with btn_col1:
        if (
            openrouter_key
            and not all_have_speeches
            and st.button(
                "Generate all speeches",
                key="gen_all_speeches",
                icon=":material/format_quote:",
            )
        ):
            progress = st.progress(0.0, text="Generating speeches…")
            try:
                for i in range(NUM_SPEECHES):
                    ss = st.session_state[DEBATE_SPEECHES_KEY]
                    if ss[i] is not None:
                        progress.progress((i + 1) / NUM_SPEECHES, text=f"Speech {i + 1} (cached)")
                        continue
                    prev = [ss[j] for j in range(i) if ss[j]]
                    progress.progress((i + 0.5) / NUM_SPEECHES, text=f"Generating speech {i + 1}…")
                    result = debate_engine.generate_single_speech(
                        api_key=openrouter_key,
                        topic=topic,
                        speech_index=i,
                        previous_speeches=prev,
                        llm_1_id=llm_1,
                        llm_2_id=llm_2,
                        duration_sec=int(duration),
                    )
                    st.session_state[DEBATE_SPEECHES_KEY][i] = result
                    progress.progress((i + 1) / NUM_SPEECHES, text=f"Speech {i + 1} done")
                progress.progress(1.0, text="Done")
                st.rerun()
            except Exception as e:
                st.error(str(e))
    with btn_col2:
        if all_have_speeches and not all_have_audio:
            if elevenlabs_key and voices_ok:
                if st.button(
                    "Generate all audio",
                    key="gen_all_audio",
                    icon=":material/record_voice_over:",
                ):
                    if DEBATE_AUDIO_KEY not in st.session_state:
                        st.session_state[DEBATE_AUDIO_KEY] = {}
                    progress = st.progress(0.0, text="Generating audio in parallel…")
                    try:
                        # Audio has no cross-dependency; generate in parallel
                        to_gen = [
                            (i, voice_1 if COL_FOR_INDEX[i] == 0 else voice_2, speeches[i]["text"])
                            for i in range(NUM_SPEECHES)
                            if i not in st.session_state[DEBATE_AUDIO_KEY]
                        ]
                        if not to_gen:
                            progress.progress(1.0, text="Done")
                            st.rerun()
                        else:

                            def do_tts(item: tuple) -> tuple[int, bytes]:
                                idx, vid, text = item
                                return idx, elevenlabs_tts.text_to_speech(elevenlabs_key, vid, text)

                            with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
                                futures = {
                                    executor.submit(do_tts, item): item[0] for item in to_gen
                                }
                                done = 0
                                for fut in concurrent.futures.as_completed(futures):
                                    idx, audio_bytes = fut.result()
                                    st.session_state[DEBATE_AUDIO_KEY][idx] = audio_bytes
                                    done += 1
                                    progress.progress(
                                        done / len(to_gen), text=f"Generated {done}/{len(to_gen)}"
                                    )
                            progress.progress(1.0, text="Done")
                            st.rerun()
                    except Exception as e:
                        st.error(str(e))
            else:
                sub_col1, sub_col2 = st.columns([3, 1])
                with sub_col1:
                    st.button(
                        "Generate all audio",
                        key="gen_all_audio",
                        icon=":material/record_voice_over:",
                        disabled=True,
                    )
                with sub_col2:
                    with st.popover(":material/info:", help="Why is this disabled?"):
                        st.caption(
                            "Add your ElevenLabs API key in the sidebar to enable audio generation."
                        )
    with btn_col3:
        if any(speeches) and st.button(
            "Clear all speeches",
            key="clear_all_speeches",
            icon=":material/delete_sweep:",
        ):
            st.session_state[DEBATE_SPEECHES_KEY] = [None] * NUM_SPEECHES
            st.session_state.pop(DEBATE_AUDIO_KEY, None)
            st.rerun()

    # Row-aligned grid: row 0 = speeches 0, 1; row 1 = speeches 3, 2 (LLM 1 | LLM 2)
    rows = [(0, 1), (3, 2)]  # (speech_index_left, speech_index_right) per row
    for speech_idx_left, speech_idx_right in rows:
        row_col1, row_col2 = st.columns(2)
        for col, speech_index in [(row_col1, speech_idx_left), (row_col2, speech_idx_right)]:
            with col:
                label = SPEECH_LABELS[speech_index]
                prev = [speeches[i] for i in range(speech_index) if speeches[i]]
                can_gen = all(speeches[i] is not None for i in range(speech_index))
                voice_id = voice_1 if COL_FOR_INDEX[speech_index] == 0 else voice_2
                _speech_cell(
                    speech_index=speech_index,
                    label=label,
                    speech=speeches[speech_index],
                    can_generate=can_gen,
                    openrouter_key=openrouter_key,
                    elevenlabs_key=elevenlabs_key,
                    voice_id=voice_id,
                    topic=topic,
                    llm_1=llm_1,
                    llm_2=llm_2,
                    duration=int(duration),
                    previous_speeches=prev,
                )
        st.markdown("")
