"""OpenRouter API client: list models and chat completion."""

from __future__ import annotations

import httpx

BASE_URL = "https://openrouter.ai/api/v1"
CHAT_COMPLETIONS_URL = f"{BASE_URL}/chat/completions"


def _normalize_key(key: str | None) -> str:
    """Strip whitespace; empty or None becomes empty string."""
    if key is None:
        return ""
    return (key or "").strip()


def _extract_message_content(raw: str | list | None) -> str:
    """
    Extract plain text from OpenRouter/OpenAI message content.
    content can be a string, or a list of parts (e.g. [{"type": "text", "text": "..."}]).
    Returns empty string if no text found (so truncated/empty responses don't abort the run).
    """
    if raw is None:
        return ""
    if isinstance(raw, str):
        return raw
    if isinstance(raw, list):
        parts = []
        for part in raw:
            if isinstance(part, dict):
                t = part.get("text")
                if t is not None:
                    parts.append(str(t))
                elif part.get("type") == "text" and "text" in part:
                    t = part["text"]
                    if t is not None:
                        parts.append(str(t))
            elif isinstance(part, str):
                parts.append(part)
        return "".join(parts)
    return ""


def _raise_with_body(response: httpx.Response) -> None:
    """Raise HTTPStatusError with response body in message for debugging."""
    try:
        body = response.text
    except Exception:
        body = ""
    msg = f"HTTP {response.status_code} for {response.url}"
    if body:
        msg += f" — {body[:500]}" + ("..." if len(body) > 500 else "")
    raise httpx.HTTPStatusError(msg, request=response.request, response=response) from None


def list_models(api_key: str) -> list[dict]:
    """
    Fetch all available models from OpenRouter.
    Returns a list of model objects (id, name, description, etc.).
    """
    key = _normalize_key(api_key)
    with httpx.Client(timeout=30.0) as client:
        r = client.get(
            f"{BASE_URL}/models",
            headers={
                "Authorization": f"Bearer {key}",
                "Content-Type": "application/json",
            },
        )
        if not r.is_success:
            _raise_with_body(r)
        data = r.json()
    return data.get("data", [])


def chat_completion(
    api_key: str,
    model: str,
    messages: list[dict],
    *,
    max_tokens: int = 256,
    temperature: float = 0.7,
) -> tuple[str, str]:
    """
    Send a chat completion request to OpenRouter.
    messages: list of {"role": "user"|"assistant"|"system", "content": "..."}
    Returns (content, model_used). model_used is from the response (e.g. for openrouter/free, the actual model that served the request).
    """
    key = _normalize_key(api_key)
    with httpx.Client(timeout=60.0) as client:
        r = client.post(
            CHAT_COMPLETIONS_URL,
            headers={
                "Authorization": f"Bearer {key}",
                "Content-Type": "application/json",
            },
            json={
                "model": model,
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": temperature,
            },
        )
        if not r.is_success:
            _raise_with_body(r)
        data = r.json()
    choices = data.get("choices", [])
    if not choices:
        raise ValueError("OpenRouter returned no choices")
    # Actual model used (e.g. for openrouter/free, the routed model)
    model_used = data.get("model") or model
    choice = choices[0]
    message = choice.get("message") or {}
    raw = message.get("content")
    text = _extract_message_content(raw)
    # Fallback: legacy "text" on choice (some providers when truncated)
    if not text and choice.get("text") is not None:
        text = str(choice["text"])
    return text.strip(), model_used
