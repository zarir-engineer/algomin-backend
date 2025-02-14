import websocket
import json
from src import config as dd
import pyotp

TRADING_SYMBOL = "SBIN-EQ"  # Replace with the desired future symbol
EXCHANGE = "NSE"
SYMBOL_TOKEN = "3045"

# WebSocket URL
WS_URL = "wss://wsapi.angelbroking.com/live"


def on_message(ws, message):
    """Handle incoming WebSocket messages."""
    print("Received:", message)


def on_error(ws, error):
    """Handle errors."""
    print("Error:", error)


def on_close(ws, close_status_code, close_msg):
    """Handle connection close."""
    print("WebSocket Closed")


def on_open(ws):
    """Send a subscription request when the WebSocket connection opens."""
    print("WebSocket Connected")
    _totp = pyotp.TOTP(dd.TOTP)
    YOUR_ACCESS_TOKEN = _totp.now()

    # Example subscription payload (modify as per Angel Broking API documentation)
    subscribe_payload = {
        "action": "subscribe",
        "token": YOUR_ACCESS_TOKEN,
        "feedtype": "ltp",  # Example: "ltp" (Last Traded Price), "quote", etc.
        "segment": EXCHANGE,  # Example: "NSE", "BSE", etc.
        "symbol": TRADING_SYMBOL  # Example symbol
    }

    ws.send(json.dumps(subscribe_payload))
    print("Subscription message sent")


# Create WebSocketApp
# here call SmartWebSocketV2
ws = websocket.WebSocketApp(
    WS_URL,
    on_message=on_message,
    on_error=on_error,
    on_close=on_close
)

ws.on_open = on_open

# Run WebSocket in blocking mode
ws.run_forever()
