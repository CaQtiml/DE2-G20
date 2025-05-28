import os
import time
import requests
from datetime import datetime, timedelta, timezone
from collections import Counter
from dotenv import load_dotenv

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
PER_PAGE   = 100
MAX_PAGES  = 10
RATE_BUFFER = 5  # seconds extra padding


def fetch_repos_for_day(day: datetime) -> Counter:
    """
    Fetch all repos that were CREATED or PUSHED on `day`.
    Returns a Counter mapping language -> count.
    Respects GitHub Search’s 1 000-item cap and handles rate-limit sleeps.
    """

    print(f"Start at: {day}")
    print(f"{HEADERS}")
    lang_counter = Counter()
    day_str = day.strftime("%Y-%m-%d")
    
    # match repos created OR updated (pushed) on that day
    query = f"created:{day_str}"

    print(f"query: {query}")

    for page in range(1, MAX_PAGES + 1):
        params = {
            "q":        query,
            "sort":     "created",
            "order":    "asc",
            "per_page": PER_PAGE,
            "page":     page
        }
        resp = requests.get(
            "https://api.github.com/search/repositories",
            headers=HEADERS, params=params
        )
        
        #print(f"Resp URL: {resp.url}, Status: {resp.status_code}, JSON:{resp.json()}")
        
        # If rate-limited, sleep til reset + buffer, then retry once
        if resp.status_code == 403 and "X-RateLimit-Reset" in resp.headers:
            reset_ts = int(resp.headers["X-RateLimit-Reset"])
            wait = max(0, reset_ts - time.time()) + RATE_BUFFER
            print(f"[{day_str}] Rate limit hit; sleeping {wait:.0f}s…")
            time.sleep(wait)
            resp = requests.get(
                "https://api.github.com/search/repositories",
                headers=HEADERS, params=params
            )

        if resp.status_code != 200:
            raise RuntimeError(f"GitHub API error {resp.status_code}: {resp.text}")

        data  = resp.json()
        items = data.get("items", [])
        if not items:
            break

        print(f"Items len: {len(items)}")

        # tally languages
        for repo in items:
            #print(repo.get("language"))
            lang = repo.get("language") or "Unknown"
            lang_counter[lang] += 1

        # if we’re running low on remaining calls, back off until reset
        rem   = int(resp.headers.get("X-RateLimit-Remaining", 0))
        reset = int(resp.headers.get("X-RateLimit-Reset", time.time()))
        print(f"Rate Limit Remaining:{rem}, Rate Limit Reset:{reset}\n")
        if rem < 5:
            wait = max(0, reset - time.time()) + RATE_BUFFER
            print(f"[{day_str}] Low rate-limit (remaining={rem}); sleeping {wait:.0f}s…")
            time.sleep(wait)

        # fewer than a full page? we’ve exhausted this day’s results
        if len(items) < PER_PAGE:
            break

    return lang_counter


def aggregate_languages(start: datetime, end: datetime) -> Counter:
    """
    Loop from start → end (inclusive), fetch per-day counts,
    and accumulate into one master Counter.
    """
    total = Counter()
    current = start
    while current <= end:
        print(f"Processing {current.date()}…")
        day_counts = fetch_repos_for_day(current)
        total.update(day_counts)
        current += timedelta(days=1)
    return total

def analyze_languages(start: datetime, end: datetime) -> dict:
    """
    Analyze GitHub repos created between `start` and `end`, grouped by language.
    """
    aggregated = aggregate_languages(start, end)
    return {
        "from": start.isoformat(),
        "to": end.isoformat(),
        "languages": dict(aggregated)
    }


if __name__ == "__main__":
    # ——— Dynamic one-year window ———
    END_DATE   = datetime.now(timezone.utc)
    START_DATE = END_DATE - timedelta(days=1)

    # print(fetch_repos_for_day(START_DATE).items())

    #print(f"Scanning repos created/updated between {START_DATE.date()} and {END_DATE.date()}…")
    agg = aggregate_languages(START_DATE, END_DATE)

    print("Print All languages:")
    for lang, cnt in agg.items():
        print(f"{lang:<15} {cnt:,} repos")
    #top10 = agg.most_common(10)
    #print("\nTop 10 languages in the last year:")
    #for i, (lang, cnt) in enumerate(top10, start=1):
    #    print(f"{i:>2}. {lang:<15} {cnt:,} repos")

