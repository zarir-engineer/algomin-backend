from fastapi import FastAPI, WebSocket
import asyncio
import json

app = FastAPI()

# Store active WebSocket connections
active_connections = []

class WebSocketObserver:
    def __init__(self, websocket: WebSocket):
        self.websocket = websocket

    async def update(self, data):
        await self.websocket.send_text(json.dumps(data))  # Send live data

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    observer = WebSocketObserver(websocket)  # Create instance here
    active_connections.append(observer)

    try:
        while True:
            message = await websocket.receive_text()
            print(f"Received message from client: {message}")
    except Exception as e:
        print(f"WebSocket Error: {e}")
    finally:
        active_connections.remove(observer)  # Remove on disconnect
