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
    def __init__(self, tool_name: str):
        self.tool_name = tool_name

    @abstractmethod
    def scan(self, target: str) -> List[Finding]:
        """
        Perform a security scan against a target.

        Args:
            target: Host, IP, URL, or resource identifier

        Returns:
            List of security findings
        """
        raise NotImplementedError