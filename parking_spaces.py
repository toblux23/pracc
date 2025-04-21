import fastapi
from fastapi import HTTPException
from kafka import KafkaProducer
import json
from datetime import datetime

app = fastapi.FastAPI()

# Kafka Configuration
KAFKA_URL = "localhost:9092"
TOPIC = "parking-spaces"
TOPIC_NOTIFICATIONS = "notifications"

# Initialize Kafka producer
producer = KafkaProducer(
    bootstrap_servers=[KAFKA_URL]
)

# Parking spots data
parking_spots = {
    "P1": {"status": "available", "user_id": None},
    "P2": {"status": "available", "user_id": None},
    "P3": {"status": "available", "user_id": None},
    "P4": {"status": "available", "user_id": None},
    "P5": {"status": "available", "user_id": None},
    "P6": {"status": "available", "user_id": None},
    "P7": {"status": "available", "user_id": None},
    "P8": {"status": "available", "user_id": None},
    "P9": {"status": "available", "user_id": None},
    "P10": {"status": "available", "user_id": None},
    "P11": {"status": "available", "user_id": None},
    "P12": {"status": "available", "user_id": None},
    "P13": {"status": "available", "user_id": None},
    "P14": {"status": "available", "user_id": None},
    "P15": {"status": "available", "user_id": None},
    "P16": {"status": "available", "user_id": None},
    "P17": {"status": "available", "user_id": None},
    "P18": {"status": "available", "user_id": None},
    "P19": {"status": "available", "user_id": None},
    "P20": {"status": "available", "user_id": None}
}

@app.get("/parking-spots")
def get_parking_spots():
    return [{"id": id, **spot} for id, spot in parking_spots.items()]

@app.post("/parking-spots/{spot_id}/update")
def update_spot(spot_id: str, status: str, user_id: str = None):
    if spot_id not in parking_spots:
        raise HTTPException(status_code=404, detail="Spot not found")
    
    parking_spots[spot_id]["status"] = status
    parking_spots[spot_id]["user_id"] = user_id
    
    # Send to parking-spaces topic
    message = {
        "type": "spot_update",
        "timestamp": datetime.now().isoformat(),
        "spot_id": spot_id,
        "status": status,
        "user_id": user_id
    }
    producer.send(TOPIC, json.dumps(message).encode())
    
    # Send notification
    notification = {
        "type": "spot_update",
        "timestamp": datetime.now().isoformat(),
        "user_id": user_id,
        "message": f"Spot {spot_id} status updated to {status}"
    }
    producer.send(TOPIC_NOTIFICATIONS, json.dumps(notification).encode())
    
    return {"message": f"Spot {spot_id} updated successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=5000) 