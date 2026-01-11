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