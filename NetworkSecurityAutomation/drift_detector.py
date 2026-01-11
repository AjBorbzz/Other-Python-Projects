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


def extract_findings(scan_result: Dict[str, Any]) -> List[Finding]:
    findings: List[Finding] = []

    scan = scan_result.get("scan", {})
    for host, host_data in scan.items():
        status = (host_data.get("status") or {}).get("state")
        if status != "up":
            continue

        for proto in ("tcp", "udp"):
            ports = host_data.get(proto, {})
            for port_str, port_data in ports.items():
                try:
                    port = int(port_str)
                except Exception:
                    continue

                findings.append(
                    Finding(
                        host=host,
                        port=port,
                        proto=proto,
                        service=str(port_data.get("name") or ""),
                        state=str(port_data.get("state") or ""),
                        product=(port_data.get("product") or None),
                        version=(port_data.get("version") or None),
                    )
                )

    # Keep output stable for diffs
    findings.sort(key=lambda f: (f.host, f.proto, f.port))
    return findings


def to_keyset(findings: List[Finding]) -> set[Tuple[str, str, int]]:
    return {(f.host, f.proto, f.port) for f in findings if f.state == "open"}


def load_findings(path: Path) -> List[Finding]:
    data = json.loads(path.read_text(encoding="utf-8"))
    items = data.get("findings", [])
    out: List[Finding] = []
    for it in items:
        out.append(
            Finding(
                host=it["host"],
                port=int(it["port"]),
                proto=it["proto"],
                service=it.get("service", ""),
                state=it.get("state", ""),
                product=it.get("product"),
                version=it.get("version"),
            )
        )
    out.sort(key=lambda f: (f.host, f.proto, f.port))
    return out


def save_report(path: Path, targets: str, ports: List[int], raw_scan: Dict[str, Any], findings: List[Finding]) -> None:
    payload = {
        "targets": targets,
        "ports": sorted(set(ports)),
        "nmap_command_line": (raw_scan.get("nmap", {}) or {}).get("command_line"),
        "scanstats": (raw_scan.get("nmap", {}) or {}).get("scanstats"),
        "findings": [
            {
                "host": f.host,
                "port": f.port,
                "proto": f.proto,
                "service": f.service,
                "state": f.state,
                "product": f.product,
                "version": f.version,
            }
            for f in findings
        ],
    }
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description="Exposure Drift Detector (python-nmap PoC)")
    ap.add_argument("--targets", required=True, help="CIDR or target expression (e.g. 192.168.1.0/24 or 10.0.0.1-20)")
    ap.add_argument("--ports", default=",".join(map(str, DEFAULT_PORTS)), help="Comma-separated ports to check")
    ap.add_argument("--timeout", type=int, default=120, help="Overall nmap timeout seconds")
    ap.add_argument("--out", default="scan_current.json", help="Output JSON filename for this run")
    ap.add_argument("--baseline", default=None, help="Baseline JSON filename to diff against")
    args = ap.parse_args()

    ports = [int(p.strip()) for p in args.ports.split(",") if p.strip()]
    out_path = Path(args.out)

    raw = scan_targets(args.targets, ports, args.timeout)
    findings = extract_findings(raw)
    save_report(out_path, args.targets, ports, raw, findings)

    print(f"Wrote: {out_path} ({len(findings)} open-port findings)")

    if args.baseline:
        base_path = Path(args.baseline)
        if not base_path.exists():
            print(f"Baseline not found: {base_path}", file=sys.stderr)
            return 2

        old = load_findings(base_path)
        old_keys = to_keyset(old)
        new_keys = to_keyset(findings)

        newly_exposed = sorted(new_keys - old_keys)
        if not newly_exposed:
            print("Diff: no newly-open ports vs baseline")
            return 0

        print("Diff: NEWLY-OPEN exposures (host proto port):")
        for host, proto, port in newly_exposed:
            print(f"  {host} {proto} {port}")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())