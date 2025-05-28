import os
import time
import requests
from datetime import datetime, timedelta, timezone
from collections import Counter
from dotenv import load_dotenv
import re

load_dotenv()

# ——— Configuration ———
TOKEN = os.getenv("GITHUB_TOKEN")
if not TOKEN:
    raise RuntimeError("Please set GITHUB_TOKEN environment variable")

HEADERS = {
    "Authorization": f"token {TOKEN}",
    "Accept": "application/vnd.github+json"
}

# each search can return up to 100 items/page, up to 10 pages (1 000 items max)
PER_PAGE = 100
MAX_PAGES = 10
RATE_BUFFER = 5  # seconds extra padding

LANG_TEST_PATTERNS = {
    "Python": {"dirs": ["test", "tests"], "files": [r"test_.*\.py", r".*_test\.py"]},
    "JavaScript": {"dirs": ["test", "tests", "__tests__"], "files": [r".*\.test\.js", r".*\.spec\.js"]},
    "Java": {"dirs": ["test", "tests", "src/test"], "files": [r"Test.*\.java", r".*Test\.java"]},
    "TypeScript": {"dirs": ["test", "tests", "__tests__"], "files": [r".*\.test\.ts", r".*\.spec\.ts"]},
    "C++": {"dirs": ["test", "tests"], "files": [r"test_.*\.cpp", r".*_test\.cpp"]},
    "C#": {"dirs": ["test", "tests", "UnitTest"], "files": [r".*Tests\.cs", r"Test.*\.cs"]},
    "PHP": {"dirs": ["test", "tests"], "files": [r"Test.*\.php", r".*_test\.php"]},
    "Go": {"dirs": [], "files": [r".*_test\.go"]},
    "Ruby": {"dirs": ["test", "tests", "spec"], "files": [r"test_.*\.rb", r".*_spec\.rb"]},
    "Kotlin": {"dirs": ["test", "tests", "src/test"], "files": [r"Test.*\.kt", r".*Test\.kt"]},
    "Swift": {"dirs": ["Tests"], "files": [r".*Tests\.swift", r"test.*\.swift"]},
    "Rust": {"dirs": ["tests"], "files": [r".*\.rs"]},
    "Dart": {"dirs": ["test"], "files": [r".*_test\.dart"]},
    "Scala": {"dirs": ["test", "tests"], "files": [r".*Spec\.scala", r".*Test\.scala"]},
    "Shell": {"dirs": ["test", "tests"], "files": [r"test_.*\.sh"]},
    "Objective-C": {"dirs": ["Tests", "Test"], "files": [r".*Tests\.m", r"test_.*\.m"]},
    "R": {"dirs": ["tests", "testthat"], "files": [r"test_.*\.R"]},
    "Elixir": {"dirs": ["test"], "files": [r".*_test\.exs"]},
    "Haskell": {"dirs": ["test", "tests"], "files": [r".*Spec\.hs", r"test_.*\.hs"]},
    "Perl": {"dirs": ["t", "test"], "files": [r".*\.t"]},
    "Other": {"dirs": ["test", "tests"], "files": [r".*test.*"]}  # Fallback for unknown languages
}

CI_INDICATORS = [
    ".github/workflows",
    ".travis.yml",
    ".circleci",
    "jenkinsfile",
    ".gitlab-ci.yml",
    "azure-pipelines.yml"
]

def github_get(url, params=None, max_retries=1):
    for _ in range(max_retries + 1):
        resp = requests.get(url, headers=HEADERS, params=params)
        if resp.status_code == 403 and "X-RateLimit-Reset" in resp.headers:
            reset_ts = int(resp.headers["X-RateLimit-Reset"])
            wait = max(0, reset_ts - time.time()) + RATE_BUFFER
            print(f"Rate limit hit. Sleeping {wait:.0f} seconds.")
            time.sleep(wait)
            continue  # retry after sleep
        return resp
    raise RuntimeError(f"Rate limit not lifted after {max_retries} retries.")

def has_unit_tests(repo_full_name: str, language: str = "Unknown") -> bool:
    url = f"https://api.github.com/repos/{repo_full_name}/contents"
    try:
        # resp = requests.get(url, headers=HEADERS)
        resp = github_get(url)
        if resp.status_code != 200:
            return False
        items = resp.json()
        print(f"Name:{repo_full_name}, Lang:{language}, Keys:{items[0].keys()}, len:{len(items)}")
        lang_patterns = LANG_TEST_PATTERNS.get(language, LANG_TEST_PATTERNS["Other"])
        dir_patterns = [d.lower() for d in lang_patterns["dirs"]]
        file_regexes = [re.compile(p) for p in lang_patterns["files"]]
        for item in items:
            name = item["name"].lower()
            if item["type"] == "dir":
                if name in dir_patterns:
                    return True
            elif item["type"] == "file":
                if any(pat.match(item["name"]) for pat in file_regexes):
                    return True
    except Exception as e:
        print(f"Error checking unit tests in {repo_full_name}: {e}")
    return False


def uses_continuous_integration(repo_full_name: str) -> bool:
    url = f"https://api.github.com/repos/{repo_full_name}/contents"
    try:
        # resp = requests.get(url, headers=HEADERS)
        resp = github_get(url)
        if resp.status_code != 200:
            return False
        items = resp.json()
        for item in items:
            name = item["name"].lower()
            if name in CI_INDICATORS or any(ci in name for ci in CI_INDICATORS):
                return True
            # Handle .github directory traversal
            if item["type"] == "dir" and item["name"].lower() == ".github":
                sub_url = f"{url}/.github"
                sub_resp = requests.get(sub_url, headers=HEADERS)
                if sub_resp.status_code != 200:
                    continue
                sub_items = sub_resp.json()
                for sub_item in sub_items:
                    if sub_item["name"].lower() == "workflows":
                        return True
    except Exception as e:
        print(f"Error checking CI in {repo_full_name}: {e}")
    return False


def fetch_repos_with_tests_and_ci_for_day(day: datetime) -> Counter:
    print(f"Checking repos from {day.date()}")
    lang_counter = Counter()
    day_str = day.strftime("%Y-%m-%d")
    query = f"created:{day_str}"

    for page in range(1, MAX_PAGES + 1):
        params = {
            "q": query,
            "sort": "created",
            "order": "asc",
            "per_page": PER_PAGE,
            "page": page
        }
        resp = requests.get("https://api.github.com/search/repositories", headers=HEADERS, params=params)

        if resp.status_code == 403 and "X-RateLimit-Reset" in resp.headers:
            reset_ts = int(resp.headers["X-RateLimit-Reset"])
            wait = max(0, reset_ts - time.time()) + RATE_BUFFER
            print(f"Rate limit hit. Waiting {wait:.0f} seconds.")
            time.sleep(wait)
            continue

        if resp.status_code != 200:
            raise RuntimeError(f"GitHub API error: {resp.status_code} — {resp.text}")

        items = resp.json().get("items", [])
        if not items:
            break

        for repo in items:
            lang = repo.get("language") or "Unknown"
            full_name = repo.get("full_name")
            if not full_name or not lang:
                continue
            if has_unit_tests(full_name, lang) and uses_continuous_integration(full_name):
                lang_counter[lang] += 1

        if len(items) < PER_PAGE:
            break

        remaining = int(resp.headers.get("X-RateLimit-Remaining", 0))
        reset = int(resp.headers.get("X-RateLimit-Reset", time.time()))
        if remaining < 5:
            wait = max(0, reset - time.time()) + RATE_BUFFER
            print(f"Rate limit low. Sleeping {wait:.0f} seconds.")
            time.sleep(wait)

    return lang_counter

def analyze_tdd_cicd(start: datetime, end: datetime) -> dict:
    agg = Counter()
    current = start
    while current <= end:
        day_counts = fetch_repos_with_tests_and_ci_for_day(current)
        agg.update(day_counts)
        current += timedelta(days=1)

    return {
        "from": start.isoformat(),
        "to": end.isoformat(),
        "languages": dict(agg)
    }


if __name__ == "__main__":
    END_DATE = datetime.now(timezone.utc)
    START_DATE = END_DATE - timedelta(days=1)

    agg = Counter()
    current = START_DATE
    while current <= END_DATE:
        day_counts = fetch_repos_with_tests_and_ci_for_day(current)
        agg.update(day_counts)
        current += timedelta(days=1)

    print("\nLanguages with at least one project using TDD and CI:")
    for lang, count in sorted(agg.items(), key=lambda x: x[1], reverse=True):
        print(f"{lang:<20} {count:>5} projects")