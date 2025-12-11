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

FIELD_MAP = {
    "time": "timestamp",
    "@timestamp": "timestamp",
    "event_time": "timestamp",
    "eventtime": "timestamp",

    "src": "src_ip",
    "src_ip": "src_ip",
    "source_ip": "src_ip",
    "SourceIP": "src_ip",

    "dst": "dst_ip",
    "dst_ip": "dst_ip",
    "destination_ip": "dst_ip",
    "DestinationIP": "dst_ip",

    "user": "username",
    "user_name": "username",
    "username": "username",
    "account_name": "username",

    "message": "message",
    "msg": "message",
    "log_message": "message",
    "description": "message",
}

FULLY_SENSITIVE_FIELDS = {
    "password",
    "passwd",
    "pwd",
    "api_key",
    "apikey",
    "token",
    "access_token",
    "refresh_token",
    "secret",
    "client_secret",
    "private_key",
    "auth_header",
    "authorization",
    "session_id",
    "cookie",
    "csrf_token",
}

IDENTIFIER_FIELDS = {
    "username",
    "user",
    "user_id",
    "email",
    "src_ip",
    "dst_ip",
    "ip",
    "host",
    "hostname",
    "device_id",
    "computer_name",
    "account",
}

IPV4_RE = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")
EMAIL_RE = re.compile(r"\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[A-Za-z]{2,}\b")
URL_RE = re.compile(r"\bhttps?://[^\s]+")
TOKEN_RE = re.compile(r"\b[a-zA-Z0-9_\-]{20,}\b")

def normalize_key(key: str) -> str:
    base = key.strip().lower()
    base = base.replace(" ", "_").replace(".", "_")
    return FIELD_MAP.get(base, base)

def mask_string_value(value: str) -> Tuple[str, bool]:
    original = value
    masked = value 

    masked = IPV4_RE.sub("[IP]", masked)
    masked = EMAIL_RE.sub("[EMAIL]", masked)
    masked = URL_RE.sub("[URL]", masked)
    masked = TOKEN_RE.sub("[TOKEN]", masked)

    return masked, masked != original