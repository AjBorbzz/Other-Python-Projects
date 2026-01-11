from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Tuple

import nmap


DEFAULT_PORTS = [
    21,   # FTP
    22,   # SSH
    23,   # Telnet
    25,   # SMTP
    53,   # DNS
    80,   # HTTP
    110,  # POP3
    135,  # MS RPC
    139,  # NetBIOS
    143,  # IMAP
    443,  # HTTPS
    445,  # SMB
    1433, # MSSQL
    1521, # Oracle
    3306, # MySQL
    3389, # RDP
    5432, # Postgres
    5900, # VNC
    6379, # Redis
    27017 # MongoDB
]


@dataclass(frozen=True)
class Finding:
    host: str
    port: int
    proto: str
    service: str
    state: str
    product: str | None = None
    version: str | None = None


def scan_targets(targets: str, ports: List[int], timeout: int) -> Dict[str, Any]:
    """
    Uses a TCP connect scan (-sT) to avoid requiring root (unlike SYN scan -sS).
    Includes service detection (-sV) and only returns open ports (--open).
    """
    nm = nmap.PortScanner()

    port_arg = ",".join(str(p) for p in sorted(set(ports)))
    # -n: no DNS, faster/cleaner. -sT: TCP connect. -sV: service version. --open: only open ports.
    arguments = f"-n -sT -sV --open -p {port_arg}"

    try:
        nm.scan(hosts=targets, arguments=arguments, timeout=timeout)
    except nmap.PortScannerError as e:
        raise RuntimeError(f"Nmap execution failed: {e}") from e
    except nmap.PortScannerTimeout as e:
        raise RuntimeError(f"Nmap timed out: {e}") from e

    # Raw structure includes scan metadata + per-host results.
    return nm._scan_result  # noqa: SLF001 (acceptable for PoC export)