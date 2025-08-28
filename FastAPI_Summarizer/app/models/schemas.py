from pydantic import Field, BaseModel 
from typing import List, Optional


class SummarizeRequest(BaseModel):
    incident_id: str = Field(..., description="Incident Correlation ID")
    logs: List[str] = Field(..., description="Raw log lines (pre-chunked)")
    max_tokens: int = 1024


class SummarizeResponse(BaseModel):
    incident_id: str
    summary: str
    model: str
    cached: bool = False