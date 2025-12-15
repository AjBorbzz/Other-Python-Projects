from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import List
import random


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
    
    @abstractmethod
    def supported_targets(self) -> List[str]:
        """
        Describe what this scanner can scan
        (e.g., ip, hostname, url).
        """
        raise NotImplementedError
    

# implementation:
class PortScanner(SecurityScanner):
    def __init__(self):
        super().__init__(tool_name="PortScanner")

    def supported_targets(self) -> List[str]:
        return ["ip", "hostname"]

    def scan(self, target: str) -> List[Finding]:
        findings = []

        open_ports = random.sample([22, 80, 443, 3306], k=2) 

        for port in open_ports:
            findings.append(
                Finding(
                    tool=self.tool_name,
                    target=target,
                    severity="MEDIUM",
                    description=f"Port {port} is open",
                    timestamp=datetime.now(),
                )
            )

        return findings
    

# Core Implementation:
class VulnerabilityScanner(SecurityScanner):
    def __init__(self):
        super().__init__(tool_name="VulnScanner")

    def supported_targets(self) -> List[str]:
        return ["ip", "hostname", "url"]

    def scan(self, target: str) -> List[Finding]:
        return [
            Finding(
                tool=self.tool_name,
                target=target,
                severity="HIGH",
                description="Outdated software detected (CVE-2023-XXXX)",
                timestamp=datetime.now(),
            )
        ]
    
class ScanOrchestrator:
    """
    Coordinates multiple scanners without knowing
    their concrete implementations.
    """

    def __init__(self, scanners: List[SecurityScanner]):
        self.scanners = scanners

    def run(self, target: str, target_type: str) -> List[Finding]:
        results: List[Finding] = []

        for scanner in self.scanners:
            if target_type in scanner.supported_targets():
                results.extend(scanner.scan(target))

        return results


if __name__ == "__main__":
    scanners = [
        PortScanner(),
        VulnerabilityScanner(),
    ]

    orchestrator = ScanOrchestrator(scanners)

    findings = orchestrator.run(
        target="192.168.1.10",
        target_type="ip",
    )

    for f in findings:
        print(
            f"[{f.severity}] {f.tool} | {f.target} | {f.description} | {f.timestamp}"
        )
