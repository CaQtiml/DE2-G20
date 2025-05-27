# pulsar_producer_commit.py

from datetime import datetime, timedelta, timezone
import pulsar
import json
from commit import aggregate_commit
from config import BROKER_URL, TOPICS

def produce_commit_data():
    client = pulsar.Client(BROKER_URL)
    producer = client.create_producer(TOPICS["commits"])

    END_DATE   = datetime.now(timezone.utc)
    START_DATE = END_DATE - timedelta(days=6)
    
    results = aggregate_commit(START_DATE, END_DATE)

    for repo, count in results.items():
        message = {
            "repo": repo,
            "commit_count": count,
            "timestamp": datetime.now().isoformat()
        }
        producer.send(json.dumps(message).encode("utf-8"))
        print(f"[COMMIT PRODUCER] Sent: {message}")

    client.close()

if __name__ == "__main__":
    produce_commit_data()
