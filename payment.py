import fastapi
from fastapi import HTTPException
from kafka import KafkaProducer
import json
from datetime import datetime

app = fastapi.FastAPI()


KAFKA_URL = "localhost:9092"
TOPIC = "parking-payments"
TOPIC_NOTIFICATIONS = "notifications"


producer = KafkaProducer(
    bootstrap_servers=[KAFKA_URL]
)

@app.post("/payments")
def process_payment(user_id: str, amount: float, payment_type: str):
    payment = {
        "type": payment_type,
        "timestamp": datetime.now().isoformat(),
        "user_id": user_id,
        "amount": amount
    }
    
    producer.send(TOPIC, json.dumps(payment).encode())
    
    notification = {
        "type": "payment",
        "timestamp": datetime.now().isoformat(),
        "user_id": user_id,
        "message": f"Payment of {amount} processed successfully"
    }
    producer.send(TOPIC_NOTIFICATIONS, json.dumps(notification).encode())
    
    return {"message": "Payment processed successfully", "payment": payment}

@app.get("/payments/{user_id}")
def get_user_payments(user_id: str):
    return {"message": f"Payment history for user {user_id}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=5003) 