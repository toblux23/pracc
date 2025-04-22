from kafka import KafkaConsumer
import json

KAFKA_URL = "localhost:9092"
TOPIC = "notifications"


consumer = KafkaConsumer(
    TOPIC,
    bootstrap_servers=KAFKA_URL
)


for message in consumer:
    try:
        data = json.loads(message.value.decode('utf-8'))
        print(json.dumps(data))
    except Exception as e:
        print(f"Error processing message: {e}")