"""ElevenLabs API client: list voices and text-to-speech."""

from __future__ import annotations

import httpx

BASE_URL = "https://api.elevenlabs.io"


def list_voices(api_key: str) -> list[dict]:
    """
    Fetch available voices from ElevenLabs (v2 API).
    Returns a list of voice objects (voice_id, name, etc.).
    """
    all_voices: list[dict] = []
    next_page_token: str | None = None
    with httpx.Client(timeout=30.0) as client:
        while True:
            params = {"page_size": 100}
            if next_page_token:
                params["next_page_token"] = next_page_token
            r = client.get(
                f"{BASE_URL}/v2/voices",
                headers={"xi-api-key": api_key},
                params=params,
            )
            r.raise_for_status()
            data = r.json()
            voices = data.get("voices", [])
            all_voices.extend(voices)
            if not data.get("has_more"):
                break
            next_page_token = data.get("next_page_token")
            if not next_page_token:
                break
    return all_voices


def text_to_speech(
    api_key: str,
    voice_id: str,
    text: str,
    *,
    model_id: str = "eleven_flash_v2_5",
) -> bytes:
    """
    Convert text to speech using ElevenLabs.
    Returns raw audio bytes (MP3 by default).
    """
    with httpx.Client(timeout=60.0) as client:
        r = client.post(
            f"{BASE_URL}/v1/text-to-speech/{voice_id}",
            headers={
                "xi-api-key": api_key,
                "Content-Type": "application/json",
                "Accept": "audio/mpeg",
            },
            json={
                "text": text,
                "model_id": model_id,
            },
        )
        r.raise_for_status()
    return r.content
