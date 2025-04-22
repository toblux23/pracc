import fastapi
from fastapi import HTTPException
from kafka import KafkaProducer
import json
from datetime import datetime
import requests

app = fastapi.FastAPI()


KAFKA_URL = "localhost:9092"
TOPIC = "parking-spaces"
TOPIC_NOTIFICATIONS = "notifications"


producer = KafkaProducer(
    bootstrap_servers=[KAFKA_URL]
)

@app.post("/reservations")
def create_reservation(user_id: str, spot_id: str, payment_type: str):
        response = requests.get(f"http://localhost:5000/parking-spots")
        spots = response.json()
        spot_exists = False
        spot_available = False
        
        for spot in spots:
            if spot["id"] == spot_id:
                spot_exists = True
                if spot["status"] == "available":
                    spot_available = True
                break

        if not spot_available:
            raise HTTPException(status_code=400, detail="Parking spot is not available")
            
        
        payment_response = requests.post(
            "http://localhost:5003/payments",
            params={
                "user_id": user_id,
                "amount": 10.00, 
                "payment_type": payment_type
            }
        )
        update_response = requests.post(
            f"http://localhost:5000/parking-spots/{spot_id}/update",
            params={"status": "reserved", "user_id": user_id}
        )
        
        if update_response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to update parking spot status")
        
        reservation_id = f"RES{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        reservation = {
            "type": "reservation",
            "reservation_id": reservation_id,
            "user_id": user_id,
            "spot_id": spot_id,
            "status": "confirmed",
            "timestamp": datetime.now().isoformat(),
            "payment_type": payment_type
        }
        
        
        producer.send(TOPIC, json.dumps(reservation).encode())
        
        
        notification = {
            "type": "reservation",
            "timestamp": datetime.now().isoformat(),
            "user_id": user_id,
            "spot_id": spot_id,
            "reservation_id": reservation_id,
            "payment_type": payment_type,
            "message": f"Reservation {reservation_id} created for spot {spot_id}"
        }
        producer.send(TOPIC_NOTIFICATIONS, json.dumps(notification).encode())
        
        return {"message": "Reservation created successfully", "reservation": reservation}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=5001) 