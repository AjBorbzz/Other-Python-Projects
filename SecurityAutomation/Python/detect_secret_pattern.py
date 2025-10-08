"""
Secret Pattern Detector
A utility script for detecting hardcoded secrets, API keys, and sensitive information
in text files or strings.
"""

import re
import os
import sys
from typing import List, Dict, Tuple
from pathlib import Path
import argparse


class SecretDetector:


    def __init__(self):
        """Initialize the detector with pattern definitions."""
        self.patterns = {
            'AWS Access Key': r'(?:A3T[A-Z0-9]|AKIA|AGPA|AIDA|AROA|AIPA|ANPA|ANVA|ASIA)[A-Z0-9]{16}',
            'AWS Secret Key': r"(?i)aws(.{0,20})?['\"][0-9a-zA-Z\/+]{40}['\"]",
            'GitHub Token': r'ghp_[0-9a-zA-Z]{36}|gho_[0-9a-zA-Z]{36}|ghu_[0-9a-zA-Z]{36}|ghs_[0-9a-zA-Z]{36}|ghr_[0-9a-zA-Z]{36}',
            'Generic API Key': r'(?i)(api[_-]?key|apikey)[\s]*[=:]\s*[\'"][0-9a-zA-Z\-_]{20,}[\'"]',
            'Generic Secret': r'(?i)(secret|password|passwd|pwd)[\s]*[=:]\s*[\'"][^\'"]{8,}[\'"]',
            'Private Key': r'-----BEGIN (?:RSA |EC |DSA )?PRIVATE KEY-----',
            'JWT Token': r'eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}',
            'Slack Token': r'xox[pborsa]-[0-9]{12}-[0-9]{12}-[0-9]{12}-[a-z0-9]{32}',
            'Google API Key': r'AIza[0-9A-Za-z\-_]{35}',
            'Google OAuth': r'[0-9]+-[0-9A-Za-z_]{32}\.apps\.googleusercontent\.com',
            'Heroku API Key': r'[h|H][e|E][r|R][o|O][k|K][u|U].{0,30}[0-9A-F]{8}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{12}',
            'Stripe Key': r'(?:r|s)k_live_[0-9a-zA-Z]{24,}',
            'Slack Webhook': r'https://hooks\.slack\.com/services/T[a-zA-Z0-9_]{8}/B[a-zA-Z0-9_]{8}/[a-zA-Z0-9_]{24}',
            'Database Connection': r'(?i)(mongodb|mysql|postgresql|jdbc):\/\/[^\s]+',
            'IPv4 Private': r'(?:10\.|172\.(?:1[6-9]|2[0-9]|3[01])\.|192\.168\.)\d{1,3}\.\d{1,3}',
            'Email Address': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'Generic Password Pattern': r'(?i)password[\s]*=[\s]*[\'"][^\'"]{6,}[\'"]',
        }

        self.findings = []

    def scan_text(self, text: str, source: str ="input") -> List[Dict]:
        """
        Scan text for secrets and return findings.
        
        Args:
            text: The text content to scan
            source: Source identifier (filename or description)
            
        Returns:
            List of finding dictionaries
        """
        local_findings = []
        lines = text.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            for pattern_name, pattern in self.patterns.items():
                matches = re.finditer(pattern, line)
                for match in matches:
                    finding = {
                        'type': pattern_name,
                        'source': source,
                        'line': line_num,
                        'match': self._mask_secret(match.group(0)),
                        'full_match': match.group(0),
                        'context': line.strip()[:100]  # First 100 chars of line
                    }
                    local_findings.append(finding)
        
        self.findings.extend(local_findings)
        return local_findings
    
    def scan_file(self, filepath: str) -> List[Dict]:
        """
        Scan a file for secrets.
        
        Args:
            filepath: Path to the file to scan
            
        Returns:
            List of finding dictionaries
        """
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            return self.scan_text(content, filepath)
        except Exception as e:
            print(f"Error reading file {filepath}: {e}", file=sys.stderr)
            return []
    
    def scan_directory(self, directory: str, extensions: List[str] = None) -> List[Dict]:
        """
        Recursively scan a directory for secrets.
        
        Args:
            directory: Path to directory to scan
            extensions: List of file extensions to scan (e.g., ['.py', '.js'])
            
        Returns:
            List of finding dictionaries
        """
        if extensions is None:
            extensions = ['.py', '.js', '.json', '.yaml', '.yml', '.env', 
                         '.txt', '.md', '.sh', '.conf', '.config', '.xml']
        
        all_findings = []
        for root, _, files in os.walk(directory):
            for file in files:
                if any(file.endswith(ext) for ext in extensions):
                    filepath = os.path.join(root, file)
                    findings = self.scan_file(filepath)
                    all_findings.extend(findings)
        
        return all_findings

    def _mask_secret(self, secret: str) -> str:
        """
        Mask a secret for display purposes.
        
        Args:
            secret: The secret string to mask
            
        Returns:
            Masked version of the secret
        """
        if len(secret) <= 8:
            return '*' * len(secret)
        
        visible_chars = 4
        return secret[:visible_chars] + '*' * (len(secret) - visible_chars * 2) + secret[-visible_chars:]
    
    def generate_report(self, format: str = 'text') -> str:
        """
        Generate a report of all findings.
        
        Args:
            format: Output format ('text' or 'json')
            
        Returns:
            Formatted report string
        """
        if format == 'json':
            import json
            return json.dumps(self.findings, indent=2)
        
        # Text format
        report = []
        report.append("=" * 80)
        report.append("SECRET PATTERN DETECTION REPORT")
        report.append("=" * 80)
        report.append(f"\nTotal findings: {len(self.findings)}\n")
        
        if not self.findings:
            report.append("No secrets detected!")
            return '\n'.join(report)
        
        # Group by source
        by_source = {}
        for finding in self.findings:
            source = finding['source']
            if source not in by_source:
                by_source[source] = []
            by_source[source].append(finding)
        
        for source, findings in by_source.items():
            report.append(f"\n[{source}]")
            report.append("-" * 80)
            for f in findings:
                report.append(f"  Line {f['line']}: {f['type']}")
                report.append(f"    Match: {f['match']}")
                report.append(f"    Context: {f['context'][:80]}...")
                report.append("")
        
        # Summary by type
        report.append("\nSUMMARY BY TYPE:")
        report.append("-" * 80)
        type_counts = {}
        for f in self.findings:
            type_counts[f['type']] = type_counts.get(f['type'], 0) + 1
        
        for secret_type, count in sorted(type_counts.items(), key=lambda x: x[1], reverse=True):
            report.append(f"  {secret_type}: {count}")
        
        return '\n'.join(report)
    
    def get_summary(self) -> Dict:
        """
        Get a summary of findings.
        
        Returns:
            Dictionary with summary statistics
        """
        type_counts = {}
        for f in self.findings:
            type_counts[f['type']] = type_counts.get(f['type'], 0) + 1
        
        return {
            'total_findings': len(self.findings),
            'unique_sources': len(set(f['source'] for f in self.findings)),
            'findings_by_type': type_counts
        }


def main():
    """Main function for CLI usage."""
    parser = argparse.ArgumentParser(
        description='Detect hardcoded secrets and sensitive information in files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Scan a single file
  python secret_detector.py -f config.py
  
  # Scan a directory
  python secret_detector.py -d ./src
  
  # Scan with JSON output
  python secret_detector.py -f config.py -o json
  
  # Scan from stdin
  echo "api_key = 'sk_live_abcd1234efgh5678'" | python secret_detector.py -s
        """
    )
    
    parser.add_argument('-f', '--file', help='Scan a single file')
    parser.add_argument('-d', '--directory', help='Scan a directory recursively')
    parser.add_argument('-s', '--stdin', action='store_true', help='Read from stdin')
    parser.add_argument('-o', '--output', choices=['text', 'json'], default='text',
                       help='Output format (default: text)')
    parser.add_argument('-e', '--extensions', nargs='+', 
                       help='File extensions to scan (e.g., .py .js)')
    
    args = parser.parse_args()
    
    # Initialize detector
    detector = SecretDetector()
    
    # Determine scan mode
    if args.stdin:
        text = sys.stdin.read()
        detector.scan_text(text, "stdin")
    elif args.file:
        if not os.path.exists(args.file):
            print(f"Error: File '{args.file}' not found", file=sys.stderr)
            sys.exit(1)
        detector.scan_file(args.file)
    elif args.directory:
        if not os.path.isdir(args.directory):
            print(f"Error: Directory '{args.directory}' not found", file=sys.stderr)
            sys.exit(1)
        detector.scan_directory(args.directory, args.extensions)
    else:
        parser.print_help()
        sys.exit(1)
    
    # Generate and print report
    print(detector.generate_report(args.output))
    
    # Exit with error code if secrets found
    sys.exit(1 if detector.findings else 0)


if __name__ == '__main__':
    main()