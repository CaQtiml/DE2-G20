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
    commit_counter = Counter()
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
        # https://docs.github.com/en/rest/search/search?apiVersion=2022-11-28#search-repositories
        
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
        
        #print(f"Item's Key: {items[0].keys()}")

        for repo in items:
            default_branch = repo['default_branch']
            repo_name = repo['full_name']
            print(f"Default Branch: {repo['default_branch']}, Repo Name: {repo['full_name']}")
            for page in range(1, MAX_PAGES + 1):
                api_commit = f'https://api.github.com/repos/{repo_name}/commits'
                query_commit = f'sha:{default_branch}'
                params_commit = {
                    "q":        query_commit,
                    "per_page": PER_PAGE,
                    "page":     page
                }
                resp = requests.get(
                    api_commit,
                    headers=HEADERS, params=params_commit
                )
                #https://docs.github.com/en/rest/commits/commits?apiVersion=2022-11-28#list-commits
                print(f"Resp URL: {resp.url}, Status: {resp.status_code}")

                # If rate-limited, sleep til reset + buffer, then retry once
                if resp.status_code == 403 and "X-RateLimit-Reset" in resp.headers:
                    reset_ts = int(resp.headers["X-RateLimit-Reset"])
                    wait = max(0, reset_ts - time.time()) + RATE_BUFFER
                    print(f"[{day_str}] Rate limit hit; sleeping {wait:.0f}s…")
                    time.sleep(wait)
                    resp = requests.get(
                        api_commit,
                        headers=HEADERS, params=params_commit
                    )

                if resp.status_code == 409:
                    break

                if resp.status_code != 200:
                    raise RuntimeError(f"GitHub API error {resp.status_code}: {resp.text}")
                
                if resp.status_code == 200 and resp.json() == []:
                    break
                
                data = resp.json()
                data_len = len(data)
                #print(data[0].keys())
                commit_counter[repo_name] += data_len
                
                if data_len < PER_PAGE:
                    break

        ## if we’re running low on remaining calls, back off until reset
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

    return commit_counter


def aggregate_commit(start: datetime, end: datetime) -> Counter:
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


if __name__ == "__main__":
    # ——— Dynamic one-year window ———
    END_DATE   = datetime.now(timezone.utc)
    START_DATE = END_DATE - timedelta(days=1)

    # print(fetch_repos_for_day(START_DATE).items())

    #print(f"Scanning repos created/updated between {START_DATE.date()} and {END_DATE.date()}…")
    agg = aggregate_commit(START_DATE, END_DATE)

    print("All Repos:")
    for i, (repo, cnt) in enumerate(agg.most_common(), start=1):
        print(f"{i:>2}. {repo:<15} {cnt:,} commits")
    #top10 = agg.most_common(10)
    #print("\nTop 10 languages in the last year:")
    #for i, (lang, cnt) in enumerate(top10, start=1):
    #    print(f"{i:>2}. {lang:<15} {cnt:,} repos")

