import sys
import httpx


API_URL = "http://127.0.0.1:8000/summarize"

def main():
    log_blob = None 
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        try:
            with open(arg, "r", encoding="utf-8") as f:
                log_blob = f.read()
        except FileNotFoundError:
            log_blob = arg

    else:
        log_blob = """2025-09-01T03:22:11Z authsvc[4122]: Failed password for invalid user 'report' from 203.0.113.41 port 52544 ssh2
2025-09-01T03:22:13Z authsvc[4122]: Failed password for invalid user 'deploy' from 203.0.113.41 port 52544 ssh2
2025-09-01T03:22:15Z authsvc[4122]: Accepted publickey for admin from 198.51.100.77 port 60322 ssh2 key type rsa-sha2-512
"""

    payload = {
        "log": log_blob,
        "model": "llama3:8b",
        "max_tokens": 256,
        "temperature": 0.2,
        "suspected_threat": "Brute-force on SSH followed by possible lateral move",
        "known_iocs": ["203.0.113.41", "198.51.100.77"]
    }

    with httpx.Client(timeout=60) as client:
        r = client.post(API_URL, json=payload)
        r.raise_for_status()
        data = r.json()
        print("\n=== SUMMARY ===")
        print(data["summary"])
        print("\nModel:", data["model"])

if __name__ == "__main__":
    main()