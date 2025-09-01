import os
from pydantic import BaseModel

class Settings(BaseModel):
    DEFAULT_PROVIDER: str = os.getenv("DEFAULT_PROVIDER", "llama3")

    # LLaMA
    LLM_API_BASE: str = os.getenv("LLM_API_BASE", "http://ollama:11434/v1")
    LLM_API_KEY: str = os.getenv("LLM_API_KEY", "")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "llama3:8b-instruct")

    # OpenAI
    OPENAI_API_BASE: str = os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
