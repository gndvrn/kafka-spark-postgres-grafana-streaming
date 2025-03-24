from confluent_kafka import Producer
import json
import time
from datetime import datetime

# Kafka broker details
conf = {'bootstrap.servers': 'kafka:9092'}  # Use 'kafka' because it's the service name in Docker Compose

producer = Producer(conf)

def delivery_report(err, msg):
    """ Callback for message delivery reports """
    if err is not None:
        print(f"Message delivery failed: {err}")
    else:
        print(f"Message delivered to {msg.topic()} [{msg.partition()}]")

topic = "new_topic"

while True:
    # Generate structured message
    message = {
        "message": f"Kafka event at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "timestamp": datetime.now().isoformat()
    }

    # Convert to JSON string
    message_json = json.dumps(message)

    # Produce message to Kafka
    producer.produce(topic, message_json.encode('utf-8'), callback=delivery_report)
    producer.flush()  # Ensure messages are sent
    time.sleep(2)  # Produces a message every 2 seconds