#!/usr/bin/env python3
"""
Timestamp Converter & Parser
A utility script for converting between different timestamp formats and timezones.
Essential for log correlation and forensic timeline analysis.

"""

import re
import sys
import argparse
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Tuple
import json


class TimestampConverter:
    """Convert and parse various timestamp formats."""
    
    # Common timestamp patterns
    PATTERNS = {
        'unix_seconds': r'^\d{10}$',
        'unix_milliseconds': r'^\d{13}$',
        'unix_microseconds': r'^\d{16}$',
        'unix_nanoseconds': r'^\d{19}$',
        'iso8601': r'^\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}',
        'rfc3339': r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})',
        'common_log': r'^\d{2}/[A-Za-z]{3}/\d{4}:\d{2}:\d{2}:\d{2}',  # Apache/Nginx
        'windows_filetime': r'^\d{18}$',  # 100-nanosecond intervals since 1601-01-01
        'syslog': r'^[A-Za-z]{3}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2}',  # Mar 10 10:14:23
        'mysql': r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}',
        'human_readable': r'^[A-Za-z]{3,9}\s+\d{1,2},?\s+\d{4}',  # December 25, 2024
    }
    
    # Common log format patterns with timestamps
    LOG_PATTERNS = {
        'apache_combined': r'\[(\d{2}/[A-Za-z]{3}/\d{4}:\d{2}:\d{2}:\d{2} [+-]\d{4})\]',
        'nginx_error': r'(\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2})',
        'syslog': r'^([A-Za-z]{3}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2})',
        'iso_in_text': r'(\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:?\d{2})?)',
        'windows_event': r'(\d{1,2}/\d{1,2}/\d{4}\s+\d{1,2}:\d{2}:\d{2}\s+(?:AM|PM))',
    }
    
    def __init__(self, default_timezone: str = 'UTC'):
        """
        Initialize the timestamp converter.
        
        Args:
            default_timezone: Default timezone for ambiguous timestamps
        """
        self.default_tz = timezone.utc if default_timezone == 'UTC' else None
    
    def identify_format(self, timestamp_str: str) -> Optional[str]:
        """
        Identify the format of a timestamp string.
        
        Args:
            timestamp_str: The timestamp string to identify
            
        Returns:
            Format name or None if unrecognized
        """
        timestamp_str = timestamp_str.strip()
        
        for format_name, pattern in self.PATTERNS.items():
            if re.match(pattern, timestamp_str):
                return format_name
        
        return None
    
    def parse(self, timestamp_str: str, format_hint: str = None) -> Optional[datetime]:
        """
        Parse a timestamp string to datetime object.
        
        Args:
            timestamp_str: The timestamp string to parse
            format_hint: Optional format hint to speed up parsing
            
        Returns:
            datetime object or None if parsing fails
        """
        timestamp_str = timestamp_str.strip()
        
        # If format hint provided, try that first
        if format_hint:
            try:
                return self._parse_format(timestamp_str, format_hint)
            except:
                pass
        
        # Auto-detect format
        detected_format = self.identify_format(timestamp_str)
        if detected_format:
            try:
                return self._parse_format(timestamp_str, detected_format)
            except Exception as e:
                pass
        
        # Try common formats as fallback
        for fmt in self.PATTERNS.keys():
            try:
                result = self._parse_format(timestamp_str, fmt)
                if result:
                    return result
            except:
                continue
        
        return None
    
    def _parse_format(self, timestamp_str: str, format_name: str) -> Optional[datetime]:
        """Parse timestamp based on specific format."""
        
        if format_name == 'unix_seconds':
            return datetime.fromtimestamp(int(timestamp_str), tz=timezone.utc)
        
        elif format_name == 'unix_milliseconds':
            return datetime.fromtimestamp(int(timestamp_str) / 1000, tz=timezone.utc)
        
        elif format_name == 'unix_microseconds':
            return datetime.fromtimestamp(int(timestamp_str) / 1_000_000, tz=timezone.utc)
        
        elif format_name == 'unix_nanoseconds':
            return datetime.fromtimestamp(int(timestamp_str) / 1_000_000_000, tz=timezone.utc)
        
        elif format_name == 'windows_filetime':
            # Windows FILETIME: 100-nanosecond intervals since 1601-01-01
            EPOCH_DIFF = 11644473600  # Seconds between 1601 and 1970
            timestamp = (int(timestamp_str) / 10_000_000) - EPOCH_DIFF
            return datetime.fromtimestamp(timestamp, tz=timezone.utc)
        
        elif format_name == 'iso8601' or format_name == 'rfc3339':
            # Handle various ISO8601/RFC3339 formats
            try:
                return datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            except:
                # Try without timezone
                dt = datetime.fromisoformat(timestamp_str.replace('Z', ''))
                return dt.replace(tzinfo=timezone.utc)
        
        elif format_name == 'common_log':
            # Apache/Nginx: 10/Oct/2000:13:55:36 -0700
            if ' ' in timestamp_str and ('+' in timestamp_str or '-' in timestamp_str):
                return datetime.strptime(timestamp_str, '%d/%b/%Y:%H:%M:%S %z')
            else:
                dt = datetime.strptime(timestamp_str.split()[0], '%d/%b/%Y:%H:%M:%S')
                return dt.replace(tzinfo=timezone.utc)
        
        elif format_name == 'syslog':
            # Syslog: Mar 10 10:14:23
            # Note: No year, assume current year
            current_year = datetime.now().year
            try:
                dt = datetime.strptime(f"{timestamp_str} {current_year}", '%b %d %H:%M:%S %Y')
                return dt.replace(tzinfo=timezone.utc)
            except:
                # Try with 2 digit day
                dt = datetime.strptime(f"{timestamp_str} {current_year}", '%b %d %H:%M:%S %Y')
                return dt.replace(tzinfo=timezone.utc)
        
        elif format_name == 'mysql':
            # MySQL: 2024-03-10 10:14:23
            dt = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
            return dt.replace(tzinfo=timezone.utc)
        
        elif format_name == 'human_readable':
            # Try various human-readable formats
            formats = [
                '%B %d, %Y',      # December 25, 2024
                '%b %d, %Y',      # Dec 25, 2024
                '%B %d %Y',       # December 25 2024
                '%b %d %Y',       # Dec 25 2024
            ]
            for fmt in formats:
                try:
                    dt = datetime.strptime(timestamp_str, fmt)
                    return dt.replace(tzinfo=timezone.utc)
                except:
                    continue
        
        return None
    
    def convert(self, timestamp_str: str, output_format: str = 'all', 
                timezone_name: str = None) -> Dict:
        """
        Convert a timestamp to various formats.
        
        Args:
            timestamp_str: Input timestamp string
            output_format: Desired output format or 'all' for all formats
            timezone_name: Target timezone (e.g., 'US/Eastern', 'Asia/Tokyo')
            
        Returns:
            Dictionary with converted timestamps
        """
        dt = self.parse(timestamp_str)
        
        if dt is None:
            return {'error': 'Could not parse timestamp', 'input': timestamp_str}
        
        # Convert timezone if requested
        if timezone_name and timezone_name != 'UTC':
            try:
                # Simple offset-based conversion
                if timezone_name.startswith('+') or timezone_name.startswith('-'):
                    hours = int(timezone_name[1:3])
                    minutes = int(timezone_name[3:5]) if len(timezone_name) > 3 else 0
                    offset = timedelta(hours=hours, minutes=minutes)
                    if timezone_name[0] == '-':
                        offset = -offset
                    tz = timezone(offset)
                    dt = dt.astimezone(tz)
            except:
                pass
        
        result = {
            'input': timestamp_str,
            'detected_format': self.identify_format(timestamp_str),
            'parsed': dt.isoformat()
        }
        
        if output_format == 'all' or output_format == 'unix':
            result['unix_seconds'] = int(dt.timestamp())
            result['unix_milliseconds'] = int(dt.timestamp() * 1000)
            result['unix_microseconds'] = int(dt.timestamp() * 1_000_000)
        
        if output_format == 'all' or output_format == 'iso':
            result['iso8601'] = dt.isoformat()
            result['iso8601_zulu'] = dt.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        
        if output_format == 'all' or output_format == 'human':
            result['human_readable'] = dt.strftime('%B %d, %Y %I:%M:%S %p %Z')
            result['date_only'] = dt.strftime('%Y-%m-%d')
            result['time_only'] = dt.strftime('%H:%M:%S')
        
        if output_format == 'all' or output_format == 'web':
            result['rfc2822'] = dt.strftime('%a, %d %b %Y %H:%M:%S %z')
            result['common_log'] = dt.strftime('%d/%b/%Y:%H:%M:%S %z')
        
        if output_format == 'all':
            result['day_of_week'] = dt.strftime('%A')
            result['day_of_year'] = dt.strftime('%j')
            result['week_number'] = dt.strftime('%W')
            result['timezone'] = dt.strftime('%Z') or 'UTC'
        
        return result
    
    def extract_from_log(self, log_line: str, log_format: str = None) -> List[Dict]:
        """
        Extract timestamps from a log line.
        
        Args:
            log_line: The log line to parse
            log_format: Optional log format hint
            
        Returns:
            List of extracted timestamps with context
        """
        results = []
        
        # If format specified, try that first
        if log_format and log_format in self.LOG_PATTERNS:
            pattern = self.LOG_PATTERNS[log_format]
            matches = re.finditer(pattern, log_line)
            for match in matches:
                timestamp_str = match.group(1)
                dt = self.parse(timestamp_str)
                if dt:
                    results.append({
                        'timestamp': timestamp_str,
                        'parsed': dt.isoformat(),
                        'position': match.span(),
                        'format': log_format
                    })
        
        # Try all patterns
        if not results:
            for format_name, pattern in self.LOG_PATTERNS.items():
                matches = re.finditer(pattern, log_line)
                for match in matches:
                    timestamp_str = match.group(1)
                    dt = self.parse(timestamp_str)
                    if dt:
                        results.append({
                            'timestamp': timestamp_str,
                            'parsed': dt.isoformat(),
                            'position': match.span(),
                            'format': format_name
                        })
        
        return results
    
    def calculate_time_difference(self, timestamp1: str, timestamp2: str) -> Dict:
        """
        Calculate the time difference between two timestamps.
        
        Args:
            timestamp1: First timestamp
            timestamp2: Second timestamp
            
        Returns:
            Dictionary with time difference information
        """
        dt1 = self.parse(timestamp1)
        dt2 = self.parse(timestamp2)
        
        if not dt1 or not dt2:
            return {'error': 'Could not parse one or both timestamps'}
        
        diff = abs(dt2 - dt1)
        total_seconds = diff.total_seconds()
        
        return {
            'timestamp1': dt1.isoformat(),
            'timestamp2': dt2.isoformat(),
            'difference': {
                'total_seconds': total_seconds,
                'total_minutes': total_seconds / 60,
                'total_hours': total_seconds / 3600,
                'total_days': total_seconds / 86400,
                'human_readable': self._format_timedelta(diff)
            },
            'earlier': dt1.isoformat() if dt1 < dt2 else dt2.isoformat(),
            'later': dt2.isoformat() if dt2 > dt1 else dt1.isoformat()
        }
    
    def _format_timedelta(self, td: timedelta) -> str:
        """Format a timedelta in human-readable form."""
        seconds = int(td.total_seconds())
        
        days = seconds // 86400
        seconds %= 86400
        hours = seconds // 3600
        seconds %= 3600
        minutes = seconds // 60
        seconds %= 60
        
        parts = []
        if days > 0:
            parts.append(f"{days} day{'s' if days != 1 else ''}")
        if hours > 0:
            parts.append(f"{hours} hour{'s' if hours != 1 else ''}")
        if minutes > 0:
            parts.append(f"{minutes} minute{'s' if minutes != 1 else ''}")
        if seconds > 0 or not parts:
            parts.append(f"{seconds} second{'s' if seconds != 1 else ''}")
        
        return ', '.join(parts)
    
    def batch_convert(self, timestamps: List[str], output_format: str = 'iso') -> List[Dict]:
        """
        Convert multiple timestamps at once.
        
        Args:
            timestamps: List of timestamp strings
            output_format: Desired output format
            
        Returns:
            List of conversion results
        """
        results = []
        for ts in timestamps:
            result = self.convert(ts, output_format)
            results.append(result)
        return results


def main():
    """Main function for CLI usage."""
    parser = argparse.ArgumentParser(
        description='Convert and parse timestamps between various formats',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Convert Unix timestamp
  python timestamp_converter.py -t 1699564800
  
  # Convert ISO8601 timestamp
  python timestamp_converter.py -t "2024-03-10T10:14:23Z"
  
  # Convert to specific format
  python timestamp_converter.py -t 1699564800 -f unix
  
  # Convert with timezone
  python timestamp_converter.py -t "2024-03-10 10:14:23" -z "+0800"
  
  # Extract timestamps from log line
  python timestamp_converter.py -l "2024-03-10 10:14:23 ERROR: Connection failed"
  
  # Calculate time difference
  python timestamp_converter.py -d "2024-03-10 10:14:23" "2024-03-10 15:30:45"
  
  # Get current timestamp in all formats
  python timestamp_converter.py --now
  
  # Batch convert from file
  python timestamp_converter.py -b timestamps.txt
        """
    )
    
    parser.add_argument('-t', '--timestamp', help='Timestamp to convert')
    parser.add_argument('-f', '--format', 
                       choices=['all', 'unix', 'iso', 'human', 'web'],
                       default='all',
                       help='Output format (default: all)')
    parser.add_argument('-z', '--timezone', help='Target timezone (e.g., +0800, -0500)')
    parser.add_argument('-l', '--log', help='Extract timestamp from log line')
    parser.add_argument('-d', '--diff', nargs=2, metavar=('TS1', 'TS2'),
                       help='Calculate difference between two timestamps')
    parser.add_argument('-b', '--batch', help='Batch convert from file (one timestamp per line)')
    parser.add_argument('--now', action='store_true', 
                       help='Show current timestamp in all formats')
    parser.add_argument('-j', '--json', action='store_true',
                       help='Output in JSON format')
    parser.add_argument('--identify', help='Just identify the timestamp format')
    
    args = parser.parse_args()
    
    converter = TimestampConverter()
    
    try:
        # Current timestamp
        if args.now:
            now = datetime.now(timezone.utc)
            result = converter.convert(str(int(now.timestamp())), args.format)
            
            if args.json:
                print(json.dumps(result, indent=2))
            else:
                print("\n=== CURRENT TIMESTAMP ===\n")
                for key, value in result.items():
                    if key not in ['input', 'detected_format']:
                        print(f"{key:20s}: {value}")
        
        # Identify format only
        elif args.identify:
            format_name = converter.identify_format(args.identify)
            print(f"Detected format: {format_name or 'Unknown'}")
        
        # Time difference calculation
        elif args.diff:
            result = converter.calculate_time_difference(args.diff[0], args.diff[1])
            
            if args.json:
                print(json.dumps(result, indent=2))
            else:
                if 'error' in result:
                    print(f"Error: {result['error']}", file=sys.stderr)
                    sys.exit(1)
                
                print("\n=== TIME DIFFERENCE ===\n")
                print(f"Timestamp 1: {result['timestamp1']}")
                print(f"Timestamp 2: {result['timestamp2']}")
                print(f"\nDifference: {result['difference']['human_readable']}")
                print(f"Total seconds: {result['difference']['total_seconds']:,.0f}")
                print(f"Total hours: {result['difference']['total_hours']:,.2f}")
                print(f"Total days: {result['difference']['total_days']:,.2f}")
        
        # Extract from log line
        elif args.log:
            results = converter.extract_from_log(args.log)
            
            if args.json:
                print(json.dumps(results, indent=2))
            else:
                print(f"\n=== EXTRACTED TIMESTAMPS ({len(results)}) ===\n")
                for i, result in enumerate(results, 1):
                    print(f"[{i}] {result['timestamp']}")
                    print(f"    Format: {result['format']}")
                    print(f"    Parsed: {result['parsed']}")
                    print()
        
        # Batch conversion
        elif args.batch:
            with open(args.batch, 'r') as f:
                timestamps = [line.strip() for line in f if line.strip()]
            
            results = converter.batch_convert(timestamps, args.format)
            
            if args.json:
                print(json.dumps(results, indent=2))
            else:
                for result in results:
                    print(f"\nInput: {result['input']}")
                    if 'error' in result:
                        print(f"  Error: {result['error']}")
                    else:
                        for key, value in result.items():
                            if key not in ['input', 'detected_format']:
                                print(f"  {key}: {value}")
        
        # Single timestamp conversion
        elif args.timestamp:
            result = converter.convert(args.timestamp, args.format, args.timezone)
            
            if args.json:
                print(json.dumps(result, indent=2))
            else:
                if 'error' in result:
                    print(f"Error: {result['error']}", file=sys.stderr)
                    sys.exit(1)
                
                print(f"\n=== TIMESTAMP CONVERSION ===\n")
                print(f"Input: {result['input']}")
                print(f"Detected format: {result.get('detected_format', 'Unknown')}")
                print()
                
                for key, value in result.items():
                    if key not in ['input', 'detected_format']:
                        print(f"{key:20s}: {value}")
        
        else:
            parser.print_help()
            sys.exit(1)
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()