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
            'AWS Secret Key': r'(?i)aws(.{0,20})?['\"][0-9a-zA-Z\/+]{40}['\"]',
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