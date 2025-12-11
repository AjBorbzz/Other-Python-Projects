from typing import Any, Dict, List, Optional, Tuple 
import re
from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI(title= "SIEM Log Normalizer and Data Masker")


class RawLog(BaseModel):
    log : Dict[str, Any] = Field(..., description="Raw SIEM Log as key-value JSON")
    source: Optional[str] = Field(None, description="Optional source identifier")


class NormalizedLog(BaseModel):
    normalized_log : Dict[str, Any]
    llm_payload: Dict[str, Any]
    masked_fields : List[str]
    redaction_notes: List[str]

class BatchRequest(BaseModel):
    records: List[RawLog]

class BatchResponse(BaseModel):
    results: List[NormalizedLog]

    