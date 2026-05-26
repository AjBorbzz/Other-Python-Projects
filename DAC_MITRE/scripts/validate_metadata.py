from __future__ import annotations

import re
import sys 
from pathlib import Path 

import yaml 


REQUIRED_TOP = {
    "title", "id", "status", "description", "tags", "logsource", "detection", "falsepositives", 
    "level", "author", "date", "version","references"
}

ALLOWED_STATUS = {"experimental", "test","stable","deprecated"}
ALLOWED_LEVEL = {"low","medium","high","critical"}

UUID_RE = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
    re.IGNORECASE
)

ATTACK_TECHNIQUE_RE = re.compile(r"^attack\.t\d{4}(\.\d{3})?$", re.IGNORECASE)
SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+$")


def validate(path: Path) -> list[str]:
    errs: list[str] = []
    try:
        rule = yaml.safe_load(path.read_text())
    except yaml.YAMLError as exc:
        return [f"{path} : YAML Parse error: {exc}"]
    
    missing = REQUIRED_TOP - rule.keys()
    if missing:
        errs.append(f"{path}: missing required fields: {sorted(missing)}")

    if "id" in rule and not UUID_RE.match(str(rule["id"])):
        errs.append(f"{path}: id must be UUID v4")
    
    if rule.get("status") not in ALLOWED_STATUS:
        errs.append(f"{path} : status must be one of {ALLOWED_STATUS}")

    if rule.get("level") not in ALLOWED_LEVEL:
        errs.append(f"{path} : status must be one of {ALLOWED_LEVEL}")

    if "version" in rule and not SEMVER_RE.match(str(rule["version"])):
        errs.append(f"{path} : version must be semver (eg: 1.0.0)")

    tags = rule.get("tags") or []
    technique_tags = [t for t in tags if ATTACK_TECHNIQUE_RE.match(t)]

    if not technique_tags:
        errs.append(f"{path}: must declare at least one attack.tXXXX[.YYY] tag")

    