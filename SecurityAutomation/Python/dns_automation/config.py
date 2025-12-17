from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="DNSAUTO_", extra="ignore")

    host: str = "0.0.0.0"
    port: int = 8080
    log_level: str = "INFO"

    resolver_timeout_s: float = 2.5
    resolver_lifetime_s: float = 3.5

    rpz_origin: str = "rpz.local."
    rpz_output_path: str = "./output/rpz.zone"
    block_action: str = "CNAME ."  # “sinkhole” variant: CNAME sinkhole.local.
    allowlist_path: str = "./data/allowlist.txt"
    denylist_path: str = "./data/denylist.txt"
    feeds_path: str = "./data/feeds.txt"

    zone_snapshot_a: str = "./data/zone_snapshot_a.txt"
    zone_snapshot_b: str = "./data/zone_snapshot_b.txt"

    # Hygiene checks
    stale_a_records_report: str = "./output/stale_a_records.json"

    # Scoring thresholds
    score_block_threshold: int = Field(default=85, ge=0, le=100)

settings = Settings()
