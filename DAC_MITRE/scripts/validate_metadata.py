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

