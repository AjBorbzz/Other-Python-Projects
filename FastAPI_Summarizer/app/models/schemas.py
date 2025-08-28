from pydantic import Field, BaseModel 
from typing import List, Literal

Provider = Literal["llama3", "openai"]


class SummarizeRequest(BaseModel):
    incident_id: str = Field(..., description="Incident Correlation ID")
    logs: List[str] = Field(..., description="Raw log lines (pre-chunked)")
    provider: Provider | None = None
    max_tokens: int = 1024


class SummarizeResponse(BaseModel):
    incident_id: str
    summary: str
    provider: Provider
    model: str
    cached: bool = False