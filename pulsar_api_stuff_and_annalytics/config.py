# config.py

import os

BROKER_URL = os.getenv("BROKER_URL", "pulsar://localhost:6650")

TOPICS = {
    "commits": "persistent://public/default/github-commits",
    "tdd": "persistent://public/default/github-tdd",
    "tdd_cicd": "persistent://public/default/github-tdd-cicd",
    "lang": "persistent://public/default/github-lang"
}

