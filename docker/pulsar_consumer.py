# pulsar_consumer.py

import pulsar
import json
import os
from config import BROKER_URL, TOPICS

# Map topics to filenames
TOPIC_FILE_MAP = {
    TOPICS["commits"]: "data_commits.jsonl",
    TOPICS["tdd"]: "data_tdd.jsonl",
    TOPICS["lang"]: "data_lang.jsonl",
    TOPICS["tdd_cicd"]: "data_tdd_cicd.jsonl"
}

def consume():
    client = pulsar.Client(BROKER_URL)
    consumer = client.subscribe(
        list(TOPICS.values()),
        subscription_name="gh-subscription",
        consumer_type=pulsar.ConsumerType.Shared
    )

    try:
        print("Subscribed to topics:")
        for topic in TOPICS.values():
            print(f" - {topic}")

        while True:
            msg = consumer.receive()
            data = json.loads(msg.data())
            topic = msg.topic_name()
            
            print(f"[CONSUMER] Received from {topic}: {json.dumps(data, indent=2)}")

            # Write to appropriate file
            if topic in TOPIC_FILE_MAP:
                file_path = TOPIC_FILE_MAP[topic]
                with open(file_path, "a") as f:
                    f.write(json.dumps(data) + "\n")

            consumer.acknowledge(msg)

    except KeyboardInterrupt:
        print("Stopped consumer.")
    finally:
        client.close()

if __name__ == "__main__":
    try:
        consume()
    except KeyboardInterrupt:
        print("Interrupted by user.")
    finally:
        print("🔁 Running analytics...")
        os.system("python3 analytics.py")
