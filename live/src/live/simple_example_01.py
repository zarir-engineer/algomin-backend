import time
from SmartApi.smartWebSocketV2 import SmartWebSocketV2
from base.src.base.auto_authenticate import AUTH_TOKEN as AT, FEED_TOKEN as FT


# WebSocket Instance
sws = SmartWebSocketV2(AUTH_TOKEN, API_KEY, CLIENT_ID, FEED_TOKEN)

# Callback function to handle received messages
def on_data(wsapp, message):
    print(f"📩 Live Data: {message}")  # Print received data

# Callback function when WebSocket opens
def on_open(wsapp):
    print("✅ WebSocket Connection Opened")

    # Example subscription - Replace with actual exchange & token
    subscription_list = [{"exchangeType": 2, "tokens": ["26000"]}]
    sws.subscribe(correlation_id="sub_001", mode=1, token_list=subscription_list)

# Callback function when WebSocket closes
def on_close(wsapp):
    print("❌ WebSocket Closed! Reconnecting...")
    time.sleep(5)
    start_websocket()  # Auto-reconnect

# Callback function for handling errors
def on_error(wsapp, error):
    print(f"⚠️ WebSocket Error: {error}")

# Assign callback functions
sws.on_data = on_data
sws.on_open = on_open
sws.on_close = on_close
sws.on_error = on_error

# Function to start WebSocket
def start_websocket():
    print("🔄 Connecting to WebSocket...")
    sws.connect()

# Start receiving live data
if __name__ == "__main__":
    start_websocket()
