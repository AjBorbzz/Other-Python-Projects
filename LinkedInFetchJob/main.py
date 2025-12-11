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