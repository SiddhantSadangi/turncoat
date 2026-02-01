"""Debate prompts: system and user messages for for/against speeches with max_words."""

from __future__ import annotations


def build_speech_messages(
    topic: str,
    side: str,
    previous_speeches: list[tuple[str, str]],
    max_words: int,
) -> list[dict]:
    """
    Build messages for one debate speech.
    side: "for" or "against"
    previous_speeches: list of (side_label, text) e.g. [("for", "First speech..."), ...]
    Returns list of {"role": "system"|"user", "content": "..."} for openrouter.
    """
    side_label = side.lower()
    if side_label not in ("for", "against"):
        raise ValueError('side must be "for" or "against"')

    context = ""
    if previous_speeches:
        context = "\n\n".join(
            f"Previous speech ({s}): {t}" for s, t in previous_speeches
        )
        context = (
            "\n\nHere are the previous speeches in this debate (you may respond to them):\n"
            + context
        )

    system = (
        f"You are a debater. The motion is: «{topic}».\n"
        f"You must argue **{side_label}** the motion.\n"
        f"Output only the speech transcript: the exact words to be read aloud. "
        f"At most {max_words} words. "
        "Do not use bullet points or headers; write in flowing prose. "
        "Do not repeat the motion verbatim. "
        "Do not add any preamble, introduction, or meta-commentary (e.g. no 'Here is my speech:', 'I will now argue...'). "
        "Your reply must start with the first sentence of the speech."
    )
    user = (
        f"Output only the transcript of your speech arguing {side_label} the motion (no intro, no meta)."
        + context
    )

    return [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]


def duration_sec_to_max_words(duration_sec: int) -> int:
    """Target word count for TTS at ~150 wpm. 45 s → ~112 words."""
    return max(30, int((duration_sec / 60) * 150))
