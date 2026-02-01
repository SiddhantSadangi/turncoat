"""Debate engine: speech order, 4 sequential LLM calls (no TTS)."""

from __future__ import annotations

import time

from lib import openrouter, prompts

MAX_EMPTY_RETRIES = 5
RETRY_DELAY_SEC = 1.0


def get_speech_order(llm_1_id: str, llm_2_id: str) -> list[tuple[str, str]]:
    """
    Return list of (model_id, side) for the 4 speeches.
    LLM 1 always starts for the motion: LLM1 (for) → LLM2 (against) → LLM2 (for) → LLM1 (against)
    """
    return [
        (llm_1_id, "for"),
        (llm_2_id, "against"),
        (llm_2_id, "for"),
        (llm_1_id, "against"),
    ]


NUM_SPEECHES = 4


def generate_single_speech(
    api_key: str,
    topic: str,
    speech_index: int,
    previous_speeches: list[dict],
    llm_1_id: str,
    llm_2_id: str,
    duration_sec: int,
) -> dict:
    """
    Generate one debate speech (0-indexed). Requires all previous speeches to exist.
    previous_speeches: list of {"side": str, "text": str} for speeches 0..speech_index-1.
    Returns {"model_id": str, "side": str, "text": str}.
    """
    if speech_index < 0 or speech_index >= NUM_SPEECHES:
        raise ValueError(f"speech_index must be 0..{NUM_SPEECHES - 1}")
    order = get_speech_order(llm_1_id, llm_2_id)
    model_id, side = order[speech_index]
    prev_as_tuples = [(s["side"], s["text"]) for s in previous_speeches]
    max_words = prompts.duration_sec_to_max_words(duration_sec)
    max_tokens = min(512, int(max_words * 1.35) + 50)

    messages = prompts.build_speech_messages(
        topic=topic,
        side=side,
        previous_speeches=prev_as_tuples,
        max_words=max_words,
    )
    text = ""
    model_used = model_id
    for attempt in range(MAX_EMPTY_RETRIES):
        text, model_used = openrouter.chat_completion(
            api_key=api_key,
            model=model_id,
            messages=messages,
            max_tokens=max_tokens,
            temperature=0.8,
        )
        if text.strip():
            break
        if attempt < MAX_EMPTY_RETRIES - 1:
            time.sleep(RETRY_DELAY_SEC)
    words = text.split()
    if len(words) > max_words:
        text = " ".join(words[:max_words])
    return {"model_id": model_used, "side": side, "text": text}
