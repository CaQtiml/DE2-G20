# pulsar_lang.py

import json
import pulsar
from datetime import datetime, timedelta, timezone
from lang import analyze_languages
from config import BROKER_URL, TOPICS

client = pulsar.Client(BROKER_URL)
producer = client.create_producer(TOPICS["lang"])

# Analyze a 7-day window
DAYS_BACK = 7
end = datetime.now(timezone.utc)
start = end - timedelta(days=DAYS_BACK)

result = analyze_languages(start, end)


# Send result
payload = json.dumps(result).encode("utf-8")
producer.send(payload)

print("✅ Language stats sent to Pulsar.")

client.close()
