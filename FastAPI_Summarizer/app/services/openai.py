import httpx
from app.core.config import settings

_headers = {"Authorization": f"Bearer {settings.OPENAI_API_KEY}"} if settings.OPENAI_API_KEY else {}

async def openai_chat(messages: list[dict]) -> str:
    payload = {"model": settings.OPENAI_MODEL, "messages": messages, "temperature": 0.2}
    async with httpx.AsyncClient(timeout=60) as client:
        r = await client.post(f"{settings.OPENAI_API_BASE}/chat/completions", json=payload, headers=_headers)
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]
