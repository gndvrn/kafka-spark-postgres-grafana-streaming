from kafka import KafkaProducer
import json
import time
from datetime import datetime


producer = KafkaProducer(
    bootstrap_servers=['kafka:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8'),
    api_version=(3, 4, 0)
)

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
        "processed_at": datetime.now().isoformat()
    }

    

    try:
        future = producer.send(topic,  message)

        metadata = future.get(timeout=10)
        print(f"Sent: {message} | Partition: {metadata.partition}, Offset: {metadata.offset}", flush=True)
    
    except Exception as e:
        print(f"Error sending message: {str(e)}", flush=True)
    
    time.sleep(2)

    