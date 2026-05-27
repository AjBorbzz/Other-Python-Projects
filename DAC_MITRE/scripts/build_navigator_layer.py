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

def build(root: Path) -> dict:
    technique_rules : dict[str, list[dict]] = defaultdict(list)

    for path in root.rglob("*.yml"):
        rule = yaml.safe_load(path.read_text())
        if rule.get("status") == "deprecated":
            continue
        for tag in rule.get("tags", []) or []:
            tid = technique_id_from_tag(tag)
            if tid:
                technique_rules[tid].append({
                    "title": rule.get("title"),
                    "id": rule.get("id"),
                    "status": rule.get("status"),
                    "level": rule.get("level"),
                    "file": str(path.relative_to(root.parent)),
                })

    techniques = []
    for tid, rules in sorted(technique_rules.items()):
        score = len(rules)
        comment = "\n".join(f"- {r['title']} [{r['status']}/{r['level']}]" for r in rules)
        techniques.append({
            "techniqueID": tid,
            "score": score,
            "comment": comment,
            "enabled": True,
            "color": "",
        })

    return {
        "name": "Detection-as-Code Lab Coverage",
        "versions": {"attack": "16", "navigator": "5.1.0", "layer": "4.5"},
        "domain": "enterprise-attack",
        "description": "Auto-generated from rules/tags. Score = active rule count per technique.",
        "techniques": techniques,
        "gradient": {
            "colors": ["#ffffff", "#66b1ff", "#0b3d91"],
            "minValue": 0,
            "maxValue": max((t["score"] for t in techniques), default=1),
        },
        "legendItems": [
            {"label": "1 rule", "color": "#cce0ff"},
            {"label": "2+ rules", "color": "#66b1ff"},
            {"label": "5+ rules (defense in depth)", "color": "#0b3d91"},
        ]
    }

if __name__ == "__main__":
    root = Path(sys.argv[1] if len(sys.argv) > 1 else "rules")
    print(json.dumps(build(root), indent=2))