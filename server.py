from fastapi import FastAPI, WebSocket
from motor.motor_asyncio import AsyncIOMotorClient
import os
from live.live_api import SmartWebSocketV2Client  # Import your WebSocket client

app = FastAPI()

# MongoDB Connection
MONGO_URI = os.getenv("MONGO_URI")  # Railway injects this automatically
mongo_client = AsyncIOMotorClient(MONGO_URI)
db = mongo_client["trading"]
collection = db["market_data"]

# Initialize WebSocket Client
ws_client = SmartWebSocketV2Client(MONGO_URI)

# Store connected WebSocket clients
active_connections = set()

@app.on_event("startup")
async def startup_event():
    print("Starting WebSocket Client...")
    # Start WebSocket connection (implement connection logic in the class)
    # Example: await ws_client.start() (if async)

@app.get("/latest-data")
async def get_latest_data():
    """Returns the most recent market data"""
    data = await collection.find_one({}, sort=[("_id", -1)])
    if data:
        data["_id"] = str(data["_id"])  # Convert ObjectId to string
        return data
    return {"message": "No data available"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket connection for real-time data streaming"""
    await websocket.accept()
    active_connections.add(websocket)
    try:
        while True:
            message = await websocket.receive_text()
            print(f"Received: {message}")
            await websocket.send_text(f"Echo: {message}")
    except Exception as e:
        print(f"WebSocket Error: {e}")
    finally:
        active_connections.remove(websocket)

async def broadcast_message(data):
    """Send real-time updates to all WebSocket clients"""
    for connection in active_connections:
        try:
            await connection.send_json(data)
        except Exception as e:
            print(f"Error sending to client: {e}")

# Modify WebSocket Client to push data to connected clients
async def on_message(message):
    """When new market data arrives, send it to WebSocket clients"""
    data = {"message": message}
    await collection.insert_one(data)  # Save to MongoDB
    await broadcast_message(data)  # Send to WebSocket clients

# Attach the custom function to SmartWebSocketV2Client
ws_client.on_message = on_message
