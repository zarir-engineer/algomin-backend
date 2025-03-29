import os

API_KEY = os.getenv("API_KEY", None)
WEBSOCKET_URL = "wss://example.com/websocket"
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DEBUG_MODE = os.getenv("DEBUG_MODE", "false").lower() == "true"
