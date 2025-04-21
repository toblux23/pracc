import fastapi
from kafka import KafkaConsumer
import json
from datetime import datetime
import threading

app = fastapi.FastAPI()

# Kafka Configuration
KAFKA_URL = "localhost:9092"
TOPIC = "notifications"

# Store for reservation events
reservations = []

def consume_messages():
    consumer = KafkaConsumer(
        TOPIC,
        bootstrap_servers=KAFKA_URL
    )
    
    for message in consumer:
        try:
            data = json.loads(message.value.decode('utf-8'))
            if data.get("type") == "reservation":
                # Store all reservation details
                reservation = {
                    "timestamp": data.get("timestamp"),
                    "spot_id": data.get("spot_id"),
                    "user_id": data.get("user_id"),
                    "reservation_id": data.get("reservation_id"),
                    "payment_type": data.get("payment_type")
                }
                reservations.append(reservation)
                print(f"Added reservation to history: {reservation}")
        except Exception as e:
            print(f"Error processing message: {e}")

# Start Kafka consumer in a separate thread
consumer_thread = threading.Thread(target=consume_messages, daemon=True)
consumer_thread.start()

@app.get("/history")
def get_history():
    return sorted(reservations, key=lambda x: x["timestamp"], reverse=True)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=5004) 