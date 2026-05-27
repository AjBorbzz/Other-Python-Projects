from __future__ import annotations

import json
import re
import sys
from collections import defaultdict
from pathlib import Path

import yaml 

ATTACKK_TAG_RE = re.compile(r"^attack\.t(\d{4})(?:\.(\d{3}))?$", re.IGNORECASE)

def technique_id_from_tag(tag: str) -> str | None:
    m = ATTACKK_TAG_RE.match(tag)
    if not m:
        return None 
    
    base, sub = m.group(1), m.group(2)
    return f"T{base}.{sub}" if sub else f"T{base}"

