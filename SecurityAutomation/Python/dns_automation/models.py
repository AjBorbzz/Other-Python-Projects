from __future__ import annotations

from pydantic import BaseModel, Field
from typing import Any, Literal


class DnsQueryEvent(BaseModel):
    timestamp: str | None = None
    src_ip: str | None = None
    qname: str
    qtype: str = "A"
    rcode: str | None = None
    answer_count: int | None = None
    raw: dict[str, Any] | None = None 

class Features(BaseModel):
    qname_len: int
    label_count: int
    entropy: float
    has_digits: bool
    has_many_dashes: bool
    suspicious_tld: bool
    looks_like_dga: bool
    looks_like_tunnel: bool
    uses_txt: bool


class Enrichment(BaseModel):
    domain: str
    a_records: list[str] = Field(default_factory=list)
    aaaa_records: list[str] = Field(default_factory=list)
    cname_chain: list[str] = Field(default_factory=list)
    mx_records: list[str] = Field(default_factory=list)
    txt_records: list[str] = Field(default_factory=list)

    whois: dict[str, Any] | None = None
    reputation: dict[str, Any] | None = None
    passive_dns: dict[str, Any] | None = None
    certificate_transparency: dict[str, Any] | None = None


class ScoreResult(BaseModel):
    score: int = Field(ge=0, le=100)
    reasons: list[str] = Field(default_factory=list)
    disposition: Literal["allow", "review", "block"]


class BlockDecision(BaseModel):
    domain: str
    score: int
    disposition: str
    written_to_rpz: bool
