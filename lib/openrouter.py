"""OpenRouter API client: list models and chat completion."""

from __future__ import annotations

import httpx

BASE_URL = "https://openrouter.ai/api/v1"


def list_models(api_key: str) -> list[dict]:
    """
    Fetch all available models from OpenRouter.
    Returns a list of model objects (id, name, description, etc.).
    """
    with httpx.Client(timeout=30.0) as client:
        r = client.get(
            f"{BASE_URL}/models",
            headers={"Authorization": f"Bearer {api_key}"},
        )
        r.raise_for_status()
        data = r.json()
    return data.get("data", [])


def chat_completion(
    api_key: str,
    model: str,
    messages: list[dict],
    *,
    max_tokens: int = 256,
    temperature: float = 0.7,
) -> str:
    """
    Send a chat completion request to OpenRouter.
    messages: list of {"role": "user"|"assistant"|"system", "content": "..."}
    Returns the assistant message content (single string).
    """
    with httpx.Client(timeout=60.0) as client:
        r = client.post(
            f"{BASE_URL}/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": model,
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": temperature,
            },
        )
        r.raise_for_status()
        data = r.json()
    choices = data.get("choices", [])
    if not choices:
        raise ValueError("OpenRouter returned no choices")
    content = choices[0].get("message", {}).get("content")
    if content is None:
        raise ValueError("OpenRouter choice has no message content")
    return content.strip()
