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
    
    def get_job_type(self) -> str:
        job_type_range = {
            "full time": "F",
            "full-time": "F",
            "part time": "P",
            "part-time": "P",
            "contract": "C",
            "temporary": "T",
            "volunteer": "V",
            "internship": "I",
        }
        return job_type_range.get(self.job_type.lower(), "")

    def get_remote_filter(self) -> str:
        remote_filter_range = {
            "on-site": "1",
            "on site": "1",
            "remote": "2",
            "hybrid": "3",
        }
        return remote_filter_range.get(self.remote_filter.lower(), "")

    def get_salary(self) -> str:
        # Original JS uses object keys; support string or int input
        salary_range = {
            "40000": "1",
            "60000": "2",
            "80000": "3",
            "100000": "4",
            "120000": "5",
        }
        key = str(self.salary) if self.salary is not None else ""
        return salary_range.get(key, "")

    def get_has_verification(self) -> str:
        # Replicates JS: returns "true"/"false" string
        return "true" if self.has_verification else "false"

    def get_under_10_applicants(self) -> str:
        return "true" if self.under_10_applicants else "false"

    def get_page(self) -> int:
        return self.page * 25

    def url(self, start: int = 0) -> str:
        base = f"https://{self.host}/jobs-guest/jobs/api/seeMoreJobPostings/search?"
        params = {}

        if self.keyword:
            params["keywords"] = self.keyword
        if self.location:
            params["location"] = self.location

        tpr = self.get_date_since_posted()
        if tpr:
            params["f_TPR"] = tpr

        salary_code = self.get_salary()
        if salary_code:
            params["f_SB2"] = salary_code

        exp = self.get_experience_level()
        if exp:
            params["f_E"] = exp

        remote_code = self.get_remote_filter()
        if remote_code:
            params["f_WT"] = remote_code

        jt = self.get_job_type()
        if jt:
            params["f_JT"] = jt

        # To mirror JS behavior most closely, always send these flags
        params["f_VJ"] = self.get_has_verification()
        params["f_EA"] = self.get_under_10_applicants()

        params["start"] = start + self.get_page()

        if self.sort_by == "recent":
            params["sortBy"] = "DD"
        elif self.sort_by == "relevant":
            params["sortBy"] = "R"

        return base + urlencode(params)

    def get_cache_key(self) -> str:
        return f"{self.url(0)}_limit:{self.limit}"
    

    def get_jobs(self):
        all_jobs = []
        start = 0
        BATCH_SIZE = 25
        has_more = True
        consecutive_errors = 0
        MAX_CONSECUTIVE_ERRORS = 3

        print(self.url())
        print(self.get_cache_key())

        cache_key = self.get_cache_key()
        cached_jobs = cache.get(cache_key)
        if cached_jobs:
            print("Returning cached results")
            return cached_jobs

        try:
            while has_more:
                try:
                    jobs = self.fetch_job_batch(start)
                    if not jobs:
                        has_more = False
                        break

                    all_jobs.extend(jobs)
                    print(f"Fetched {len(jobs)} jobs. Total: {len(all_jobs)}")

                    if self.limit and len(all_jobs) >= self.limit:
                        all_jobs = all_jobs[: self.limit]
                        break

                    consecutive_errors = 0
                    start += BATCH_SIZE

                    # delay: 2000–3000ms
                    delay(2000 + random.randint(0, 1000))
                except Exception as e:
                    consecutive_errors += 1
                    print(f"Error fetching batch (attempt {consecutive_errors}): {e}")

                    if consecutive_errors >= MAX_CONSECUTIVE_ERRORS:
                        print("Max consecutive errors reached. Stopping.")
                        break

                    backoff_ms = (2 ** consecutive_errors) * 1000
                    delay(backoff_ms)

            if all_jobs:
                cache.set(cache_key, all_jobs)

            return all_jobs
        except Exception as e:
            print("Fatal error in job fetching:", e)
            raise

    def fetch_job_batch(self, start: int):
        headers = {
            "User-Agent": random_user_agent(),
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Referer": "https://www.linkedin.com/jobs",
            "X-Requested-With": "XMLHttpRequest",
            "Connection": "keep-alive",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
        }

        url = self.url(start)
        resp = requests.get(url, headers=headers, timeout=10)

        if resp.status_code == 429:
            raise RuntimeError("Rate limit reached")
        if resp.status_code != 200:
            raise RuntimeError(f"Unexpected status code: {resp.status_code}")

        return parse_job_list(resp.text)
    

def parse_job_list(job_data: str):
    try:
        soup = BeautifulSoup(job_data, "html.parser")
        jobs = soup.find_all("li")
        results = []

        for idx, element in enumerate(jobs):
            try:
                job = element

                def text_or_empty(selector):
                    node = job.select_one(selector)
                    return node.get_text(strip=True) if node else ""

                position = text_or_empty(".base-search-card__title")
                company = text_or_empty(".base-search-card__subtitle")
                location = text_or_empty(".job-search-card__location")

                date_element = job.find("time")
                date = date_element.get("datetime") if date_element else None

                salary_node = job.select_one(".job-search-card__salary-info")
                if salary_node:
                    salary = " ".join(salary_node.get_text(strip=True).split())
                else:
                    salary = "Not specified"

                job_link = job.select_one(".base-card__full-link")
                job_url = job_link.get("href") if job_link else ""

                logo_node = job.select_one(".artdeco-entity-image")
                company_logo = logo_node.get("data-delayed-url") if logo_node else ""

                ago_node = job.select_one(".job-search-card__listdate")
                ago_time = ago_node.get_text(strip=True) if ago_node else ""

                if not position or not company:
                    continue

                results.append(
                    {
                        "position": position,
                        "company": company,
                        "location": location,
                        "date": date,
                        "salary": salary or "Not specified",
                        "jobUrl": job_url,
                        "companyLogo": company_logo,
                        "agoTime": ago_time,
                    }
                )
            except Exception as e:
                print(f"Error parsing job at index {idx}: {e}")
                continue

        return results
    except Exception as e:
        print("Error parsing job list:", e)
        return []
    
# -------- Public API (mirroring module.exports) --------

def query(query_object: dict):
    q = Query(query_object)
    return q.get_jobs()


def clear_cache():
    cache.clear()


def get_cache_size() -> int:
    return len(cache.cache)

# Example usage:
jobs = query({
    "keyword": "python developer",
    "location": "Spain",
    "limit": 50,
    "sortBy": "recent",
})
print(len(jobs))