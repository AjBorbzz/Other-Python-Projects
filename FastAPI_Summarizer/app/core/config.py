import os
from pydantic import BaseModel

class Settings(BaseModel):
    APP_NAME: str = os.get_env("APP_NAME", "siem-summarizer")
    APP_ENV: str = os.get_env("APP_ENV", "dev")
    APP_HOST: str = os.get_env("APP_HOST", "0.0.0.0")
    APP_PORT: int = int(os.get_env("APP_PORT", "8000"))

    LLM_API_BASE: str = os.get_env(("LLM_API_BASE", "http://ollama:11434/v1"))
    LLM_API_KEY: str = os.get_env("LLM_API_KEY", "")
    LLM_MODEL: str = os.get_env("LLM_MODEL", "llama3:8b-instruct")