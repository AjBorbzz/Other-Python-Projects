"""A collection of utilities for reuseable functions/methods."""
from datetime import datetime, timezone, timedelta 

def format_arrival_time(arrival_time: str) -> datetime:
    """Formats the arrival time value from the log (SIEM)"""
    dt = datetime.strptime(arrival_time.replace(" (UTC)", ""), "%d %b %Y %H:%M:%S.%f")
    dt = dt.replace(tzinfo=timezone.utc)
    return dt