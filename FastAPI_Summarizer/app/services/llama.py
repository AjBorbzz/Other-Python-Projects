import httpx
from app.core.config import Settings

_headers = {}
if Settings.LLM_API_KEY:
    _headers["Authorization"] = f"Bearer {Settings.LLM_API_KEY}"

async def llama_chat(messages: list[dict]) -> str:
    payload = {"model": Settings.LLM_MODEL, "messages": messages, "temperature": 0.2}
    async with httpx.AsyncClient(timeout=60) as client:
        r = await client.post(f"{Settings.LLM_API_BASE}/chat/completions", json=payload, headers=_headers)
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]
