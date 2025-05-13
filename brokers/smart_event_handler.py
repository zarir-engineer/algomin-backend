# brokers/smart_event_handler.py

from brokers.base_event_handler import BaseEventHandler

class SmartWebSocketEventHandler(BaseEventHandler):
    def on_data(self, ws, message):
        print("📩 TICK:", message)

    def on_open(self, ws):
        print("✅ WebSocket Opened")

    def on_close(self, ws):
        print("❌ WebSocket Closed")

    def on_error(self, ws, error):
        print("⚠️ WebSocket Error:", error)
