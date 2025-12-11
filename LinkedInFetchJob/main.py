import time
import random 
from urllib.parse import urlencode
import requests
from bs4 import BeautifulSoup 


def delay(ms: int):
    time.sleep(ms/ 1000.0)

class JobCache:
    def __init__(self, ttl_ms: int = 1000 * 60 * 60):
        self.cache = {}
        self.TTL = ttl_ms

    def set(self, key, value):
        self.cache[key] = {
            "data": value,
            "timestamp": time.time() * 1000,
        }

    def get(self, key):
        item = self.cache.get(key)
        if not item:
            return None
        now = time.time() * 1000
        if now - item["timestamp"] > self.TTL:
            self.cache.pop(key, None)
            return None
        return item["data"]
    

    def clear(self):
        now = time.time() * 1000
        keys_to_delete = []
        for key, val in self.cache.items():
            if now - val['timestamp']> self.TTL:
                keys_to_delete.append(key)
        
        for k in keys_to_delete:
            self.cache.pop(k, None)

cache = JobCache()



USER_AGENTS = [
    # A few common UA strings (extend if needed)y
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/605.1.15 (KHTML, like Gecko) "
    "Version/17.0 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36",
]

def random_user_agent() -> str:
    return random.choice(USER_AGENTS)


class Query:
    def __init__(self, query_obj: dict):
        self.host = query_obj.get("host", "www.linkedin.com")

        def norm(s):
            return s.strip().replace(" ", "+") if isinstance(s, str) else ""

        self.keyword = norm(query_obj.get("keyword", ""))
        self.location = norm(query_obj.get("location", ""))

        self.date_since_posted = query_obj.get("dateSincePosted", "") or ""
        self.job_type = query_obj.get("jobType", "") or ""
        self.remote_filter = query_obj.get("remoteFilter", "") or ""
        self.salary = query_obj.get("salary", "") or ""
        self.experience_level = query_obj.get("experienceLevel", "") or ""
        self.sort_by = query_obj.get("sortBy", "") or ""
        self.limit = int(query_obj.get("limit") or 0)
        self.page = int(query_obj.get("page") or 0)
        self.has_verification = bool(query_obj.get("has_verification", False))
        self.under_10_applicants = bool(query_obj.get("under_10_applicants", False))
        
    def get_date_since_posted(self) -> str:
        date_range = {
            "past month": "r2592000",
            "past week": "r604800",
            "24hr": "r86400",
        }
        return date_range.get(self.date_since_posted.lower(), "")
    
    def get_experience_level(self) -> str:
        experience_range = {
            "internship": "1",
            "entry level": "2",
            "associate": "3",
            "senior": "4",
            "director": "5",
            "executive": "6",
        }
        return experience_range.get(self.experience_level.lower(), "")