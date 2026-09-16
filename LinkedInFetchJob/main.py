import logging
import time
import random 
from urllib.parse import urlencode

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from bs4 import BeautifulSoup 


logger = logging.getLogger(__name__)



### Constants
LINKEDIN_HOST = "www.linkedin.com"

DATE_RANGES = {
    "past month": "r2592000",
    "past week": "r604800",
    "24hr": "r86400",
}

EXPERIENCE_LEVELS = {
    "internship": "1",
    "entry level": "2",
    "associate": "3",
    "senior": "4",
    "director": "5",
    "executive": "6",
}

JOB_TYPES = {
    "full time": "F",
    "full-time": "F",
    "part time": "P",
    "part-time": "P",
    "contract": "C",
    "temporary": "T",
    "volunteer": "V",
    "internship": "I",
}

REMOTE_FILTERS = {
    "on-site": "1",
    "on site": "1",
    "remote": "2",
    "hybrid": "3",
}

SALARY_RANGES = {
    "40000": "1",
    "60000": "2",
    "80000": "3",
    "100000": "4",
    "120000": "5",
}

def delay(ms: int):
    time.sleep(ms/ 1000.0)

class RateLimitError(Exception):
    def __init__(self, retry_after=None):
        self.retry_after = retry_after
        super().__init__(
            f"Rate limited. Retry-After={retry_after}"
        )

class JobCache:
    def __init__(self, ttl_seconds: int = 3600):
        self.cache = {}
        self.ttl = ttl_seconds

    def set(self, key, value):
        self.cache[key] = (
            value,
            time.monotonic(),
        )

    def get(self, key):
        item = self.cache.get(key)

        if item is None:
            return None

        value, created_at = item

        if time.monotonic() - created_at >= self.ttl:
            self.cache.pop(key, None)
            return None

        return value

    def clear_expired(self):
        now = time.monotonic()

        expired = [
            key
            for key, (_, created_at) in self.cache.items()
            if now - created_at >= self.ttl
        ]

        for key in expired:
            del self.cache[key]

    def clear(self):
        self.cache.clear()

    def __len__(self):
        return len(self.cache)

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
    BATCH_SIZE = 25
    MAX_CONSECUTIVE_ERRORS = 3
    
    def __init__(self, query_obj: dict):
        self.host = LINKEDIN_HOST

        def norm(s):
            return s.strip() if isinstance(s, str) else ""

        self.keyword = norm(query_obj.get("keyword", ""))
        self.location = norm(query_obj.get("location", ""))
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
        self.has_verification = bool(
            query_obj.get("has_verification", False)
        )
        self.under_10_applicants = bool(
            query_obj.get("under_10_applicants", False)
        )

        self.session = self._build_session()

    @staticmethod
    def _build_session():
        session = requests.Session()

        retry = Retry(
            total=3,
            connect=3,
            read=3,
            backoff_factor=1,
            status_forcelist=(500, 502, 503, 504),
            allowed_methods=("GET",),
            respect_retry_after_header=True,
        )

        adapter = HTTPAdapter(
            max_retries=retry,
            pool_connections=5,
            pool_maxsize=5,
        )

        session.mount("https://", adapter)

        session.headers.update({
            "User-Agent": random_user_agent(),
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://www.linkedin.com/jobs",
            "X-Requested-With": "XMLHttpRequest",
        })

        return session

    def get_date_since_posted(self) -> str:
        return DATE_RANGES.get(self.date_since_posted.lower(), "")
    
    def get_experience_level(self) -> str:
        return EXPERIENCE_LEVELS.get(
            self.experience_level.lower(),
            "",
        )
    
    def get_job_type(self) -> str:
        return JOB_TYPES.get(self.job_type.lower(), "")

    def get_remote_filter(self) -> str:
        return REMOTE_FILTERS.get(self.remote_filter.lower(), "")

    def get_salary(self) -> str:
        key = str(self.salary) if self.salary is not None else ""
        return SALARY_RANGES.get(key, "")

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
        cache_key = self.get_cache_key()

        cached_jobs = cache.get(cache_key)

        if cached_jobs is not None:
            logger.info("Returning cached results")
            return cached_jobs

        all_jobs = []
        start = 0
        consecutive_errors = 0

        while True:
            try:
                jobs = self.fetch_job_batch(start)

            except RateLimitError as exc:
                if exc.retry_after:
                    logger.warning(
                        "LinkedIn rate limited the request. Retry-After: %s",
                        exc.retry_after,
                    )
                else:
                    logger.warning(
                        "LinkedIn rate limited the request."
                    )

                # Don't immediately retry a 429
                break

            except requests.RequestException as exc:
                consecutive_errors += 1

                logger.warning(
                    "HTTP request failed (%d/%d): %s",
                    consecutive_errors,
                    self.MAX_CONSECUTIVE_ERRORS,
                    exc,
                )

                if consecutive_errors >= self.MAX_CONSECUTIVE_ERRORS:
                    break

                time.sleep(2 ** consecutive_errors)
                continue

            except Exception:
                logger.exception("Unexpected error")
                raise

            if not jobs:
                break

            all_jobs.extend(jobs)

            logger.info(
                "Fetched %d jobs. Total: %d",
                len(jobs),
                len(all_jobs),
            )

            if self.limit and len(all_jobs) >= self.limit:
                all_jobs = all_jobs[:self.limit]
                break

            consecutive_errors = 0
            start += self.BATCH_SIZE

            time.sleep(random.uniform(2.0, 3.0))

        if all_jobs:
            cache.set(cache_key, all_jobs)

        return all_jobs

    def fetch_job_batch(self, start: int):
        headers = {
            "User-Agent": random_user_agent(),
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://www.linkedin.com/jobs",
            "X-Requested-With": "XMLHttpRequest",
        }

        url = self.url(start)

        resp = self.session.get(
            url,
            headers=headers,
            timeout=(5, 15),
        )

        print("Status:", resp.status_code)
        print("Retry-After:", resp.headers.get("Retry-After"))

        if resp.status_code == 429:
            retry_after = resp.headers.get("Retry-After")
            raise RateLimitError(retry_after)

        resp.raise_for_status()

        return parse_job_list(resp.text)

def extract_text(element, selector: str) -> str:
    node = element.select_one(selector)
    return node.get_text(" ", strip=True) if node else ""

def parse_job_list(job_data: str):
    try:
        soup = BeautifulSoup(job_data, "html.parser")
        jobs = soup.select("li div.base-card")
        results = []

        for idx, element in enumerate(jobs):
            try:
                job = element

                position = extract_text(job, ".base-search-card__title")
                company = extract_text(job, ".base-search-card__subtitle")
                location = extract_text(job, ".job-search-card__location")

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
    

def query(query_object: dict):
    q = Query(query_object)
    return q.get_jobs()


def clear_cache():
    cache.clear()


def get_cache_size() -> int:
    return len(cache.cache)


if __name__ == "__main__":
    jobs = query({
        "keyword": "python developer",
        "location": "Spain",
        "limit": 50,
        "sortBy": "recent",
    })

    logger.info("Fetched %d jobs", len(jobs))
    logger.warning("Rate limited")
    logger.exception("Unexpected error")