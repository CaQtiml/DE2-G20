# pulsar_findtdd_cicd.py

import json
import pulsar
from datetime import datetime, timedelta, timezone
from findtdd_cicd import analyze_tdd_cicd
from config import BROKER_URL, TOPICS

client = pulsar.Client(BROKER_URL)
producer = client.create_producer(TOPICS["tdd_cicd"])

# Analyze one day window
end = datetime.now(timezone.utc)
start = end - timedelta(days=6)

result = analyze_tdd_cicd(start, end)

# Send result
payload = json.dumps(result).encode("utf-8")
producer.send(payload)

print("TDD + CI/CD stats sent to Pulsar.")

client.close()
