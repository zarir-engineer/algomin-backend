'''
python script.py --auth_token YOUR_AUTH_TOKEN --api_key YOUR_API_KEY --client_id YOUR_CLIENT_ID --feed_token YOUR_FEED_TOKEN --trading_symbol SBIN-EQ --exchange NSE --symbol_token 3045
'''

import argparse
import json
import threading
import time
from collections import deque

#TODO take auth_token, api_key, client_id and feed_token from base AngelOneSession

class SmartWebSocketV2Client:
    def __init__(self, auth_token, api_key, client_id, feed_token, trading_symbol, exchange, symbol_token):
        self.auth_token = auth_token
        self.api_key = api_key
        self.client_id = client_id
        self.feed_token = feed_token
        self.trading_symbol = trading_symbol
        self.exchange = exchange
        self.symbol_token = symbol_token
        self.sws = None  # WebSocket instance
        self.lock = threading.Lock()
        self.data_queue = deque(maxlen=50)

    def on_data(self, wsapp, message):
        print(f"📥 Received message: {message}")
        try:
            data = json.loads(message)
            for item in data["data"]:
                token = item["token"]
                ltp = item.get("ltp", 0)
                print(f"Token: {token}, LTP: {ltp}")
                self.data_queue.append((token, ltp, time.time()))
        except Exception as e:
            print(f"Error processing data: {e}")

    def on_open(self, wsapp):
        print("✅ WebSocket Opened!")

    def on_close(self, wsapp):
        print("❌ WebSocket Closed!")

    def on_error(self, wsapp, error):
        print(f"⚠️ WebSocket Error: {error}")

    def start_websocket(self):
        print("🔄 Starting WebSocket...")
        # Normally, here you'd initialize and connect your WebSocket
        # self.sws = SmartWebSocketV2(...)
        # self.sws.on_data = self.on_data
        # self.sws.on_open = self.on_open
        # self.sws.on_close = self.on_close
        # self.sws.on_error = self.on_error
        # self.sws.connect()
        print("✅ WebSocket connection established...")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Start the Smart WebSocket Client")
    parser.add_argument("--trading_symbol", default="SBIN-EQ", help="Trading Symbol (default: SBIN-EQ)")
    parser.add_argument("--exchange", choices=["NSE", "BSE"], default="NSE", help="Exchange (NSE/BSE)")
    parser.add_argument("--symbol_token", type=int, help="Symbol token (numeric value required)")
    parser.add_argument("--mode", type=int, choices=[1, 2, 3], default=1, help="Mode: 1=LTP, 2=Quote, 3=Market Depth")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    args = parser.parse_args()

    client = SmartWebSocketV2Client(
        auth_token=args.auth_token,
        api_key=args.api_key,
        client_id=args.client_id,
        feed_token=args.feed_token,
        trading_symbol=args.trading_symbol,
        exchange=args.exchange,
        symbol_token=args.symbol_token
    )

    client.start_websocket()


parser = argparse.ArgumentParser(description="SmartWebSocketV2 Client CLI")
args = parser.parse_args()

print(f"Running WebSocket with: {args}")
