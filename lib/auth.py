"""API key resolution: Streamlit secrets if present, else session state (UI)."""

from __future__ import annotations

import streamlit as st


def get_api_keys() -> tuple[str | None, str | None]:
    """Return (openrouter_key, elevenlabs_key). Uses secrets first, else sidebar/session."""
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
