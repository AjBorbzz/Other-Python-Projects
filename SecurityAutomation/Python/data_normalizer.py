import json
import re
from datetime import datetime
from ipaddress import ip_address

# Canonical field mapping
FIELD_MAP = {
    "source_ip": ["src_ip", "sourceip", "source_ip", "SourceIp", "SourceIP"],
    "destination_ip": ["dst_ip", "destinationip", "destination_ip", "DestinationIP"],
    "timestamp": ["timestamp", "time", "Time", "Timestamp"],
    "event_type": ["event_type", "EventType"],
    "username": ["user", "username", "User", "Username"],
    "port": ["port", "Port"]
}

def normalize_timestamp(value: str):
    formats = [
        "%Y/%m/%d %H:%M:%S",
        "%d-%m-%Y %I:%M%p",
        "%Y-%m-%dT%H:%M:%S",
    ]
    for fmt in formats:
        try:
            return datetime.strptime(value, fmt).isoformat()
        except Exception:
            continue
    return value  # if unrecognized, keep original

def normalize_ip(ip_str: str):
    try:
        return str(ip_address(ip_str))
    except Exception:
        # attempt to strip leading zeros
        clean_ip = re.sub(r'\b0+(\d)', r'\1', ip_str)
        try:
            return str(ip_address(clean_ip))
        except Exception:
            return ip_str

def normalize_record(record: dict):
    normalized = {}
    for canonical, variants in FIELD_MAP.items():
        for variant in variants:
            if variant in record:
                normalized[canonical] = record[variant]
                break

    # Clean field types
    if "timestamp" in normalized:
        normalized["timestamp"] = normalize_timestamp(str(normalized["timestamp"]))
    if "source_ip" in normalized:
        normalized["source_ip"] = normalize_ip(normalized["source_ip"])
    if "destination_ip" in normalized:
        normalized["destination_ip"] = normalize_ip(normalized["destination_ip"])
    if "port" in normalized:
        try:
            normalized["port"] = int(normalized["port"])
        except Exception:
            normalized["port"] = None

    return normalized

def normalize_logs(logs: list):
    return [normalize_record(log) for log in logs]

if __name__ == "__main__":
    with open("sample_logs.json", "r") as f:
        logs = json.load(f)

    normalized = normalize_logs(logs)

    with open("normalized_logs.json", "w") as f:
        json.dump(normalized, f, indent=4)

    print(f" Normalized {len(logs)} records. Saved to normalized_logs.json")
