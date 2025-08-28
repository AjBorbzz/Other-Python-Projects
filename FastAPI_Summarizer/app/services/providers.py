from typing import Protocol
from app.core.config import settings
from app.services.llama import llama_chat
from app.services.openai import openai_chat

class ChatClient(Protocol):
    async def __call__(self, messages: list[dict]) -> str: ...

def get_chat_client(provider: str | None) -> ChatClient:
    p = (provider or settings.DEFAULT_PROVIDER).lower()
    return openai_chat if p == "openai" else llama_chat
