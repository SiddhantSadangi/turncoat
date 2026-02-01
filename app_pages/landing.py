"""Landing page: explain turncoat debate and what the app does."""

from __future__ import annotations

import streamlit as st


def render() -> None:
    st.title("Turncoat")
    st.caption("LLM debate app")

    st.markdown("")
    st.subheader("What is a turncoat debate?")
    st.write(
        "A **turncoat debate** is a format where each debater argues *both* sides of the motion. "
        "A speaker first argues for the motion, then “turns coat” and argues against it (or the other way around). "
        "The format highlights how well each side can make the case for and against a topic."
    )

    st.subheader("What does this app do?")
    st.write(
        "This app runs a **four-speech turncoat debate** between two AI models (via OpenRouter). "
        "You choose a topic (the motion), pick two LLMs and two voices (ElevenLabs). "
        "The debate order is:"
    )
    st.markdown(
        "- **Speech 1** — for the motion (LLM 1)  \n"
        "- **Speech 2** — against the motion (LLM 2)  \n"
        "- **Speech 3** — for the motion (LLM 2)  \n"
        "- **Speech 4** — against the motion (LLM 1)"
    )
    st.write(
        "So each model argues once for and once against, like two turncoats. "
        "You generate each speech one by one on the **Debate** page, and can play them with text-to-speech when that’s enabled."
    )

    st.markdown("")
    st.write("Use the **Debate** page in the sidebar to start a debate.")
