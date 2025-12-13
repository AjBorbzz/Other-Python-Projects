from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import List


@dataclass(frozen=True)
class Finding:
    tool : str
    target: str
    severity : str
    description: str
    timestamp: datetime


class SecurityScanner:
    """
    Abstract base class defining the contract
    for all cybersecurity scanners.
    """