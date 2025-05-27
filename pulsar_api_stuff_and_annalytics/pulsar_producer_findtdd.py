# pulsar_producer_findtdd.py

from datetime import datetime, timedelta, timezone
import pulsar
import json
from findtdd import fetch_repos_with_tests_for_day
from config import BROKER_URL, TOPICS

def produce_tdd_data():
    client = pulsar.Client(BROKER_URL)
    producer = client.create_producer(TOPICS["tdd"])

    
    END_DATE   = datetime.now(timezone.utc)
    START_DATE = END_DATE - timedelta(days=6)
    
    current = START_DATE
    while current <= END_DATE:
        counts = fetch_repos_with_tests_for_day(current)
        for lang, count in counts.items():
            message = {
                "language": lang,
                "project_count": count,
                "timestamp": datetime.now().isoformat()
            }
            producer.send(json.dumps(message).encode("utf-8"))
            print(f"[TDD PRODUCER] Sent: {message}")
        current += timedelta(days=1)

    client.close()

if __name__ == "__main__":
    produce_tdd_data()
