##########################################################
# requirements
# AUTH_TOKEN from session
# API_KEY from cnf,
# CLIENT_ID from cnf
# FEED_TOKEN from session
##########################################################
# system modules
import time
import json
import pytz
import yaml
import asyncio
import datetime
import threading
from logzero import logger
from SmartApi.smartWebSocketV2 import SmartWebSocketV2

# custom modules
from base.session import AngelOneSession
from base.observer import (LoggerObserver,
                           AlertObserver,
                           EmailAlertObserver,
                           DatabaseObserver,
                           MongoDBObserver,
                           EMAObserver,
                           WebSocketRealObserver,
                           LimitOrderTriggerObserver
                           )
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
from tools.strategy_loader import load_limit_order_strategies


'''
ws_client.add_observer(ml_observer)  # ML price prediction
'''


class SmartWebSocketV2Client:
    """
        Core WebSocket client — responsible only for connection and observer dispatch.
        What should SmartWebSocketV2Client ideally be responsible for?
        Only these:
        Initializing and managing the WebSocket (sws)
        Handling lifecycle events (on_open, on_data, etc.)
        Notifying observers
        Managing threading for heartbeat + message listening
        Providing utility methods like time_stamp
    """

    def __init__(self):
        self.session = AngelOneSession()

        self.sws = None  # Store WebSocket instance persistently
        self.lock = threading.Lock()  # Prevent race conditions
        self.observers = []  # Store observer instances
        self.stop_heartbeat = False  # Control flag for stopping heartbeat
        self.correlation_id = f"subscription_{int(time.time())}"  # Generates a unique ID

    def load_ws_config(self, config_path=None):
        """Optional method to configure token list and mode externally"""
        if config_path is None:
            BASE_DIR = os.path.dirname(os.path.abspath(__file__))
            config_path = os.path.join(BASE_DIR, "../live/src", "data", "common.yaml")

        try:
            with open(config_path, "r") as f:
                config = yaml.safe_load(f)
            ws_config = config.get("websocket", {})
            self.mode = ws_config.get("mode", "full")
            self.correlation_id = ws_config.get("correlation_id", self.correlation_id)
            self.token_list = ws_config.get("subscriptions", [])
        except Exception as e:
            print(f"⚠️ Failed to load WebSocket config: {e}")
            self.mode = "full"
            self.token_list = []

    def add_observer(self, observer):
        """Attach an observer."""
        self.observers.append(observer)

    def notify_observers(self, data):
        """Notify all observers when new market data is received."""
        for observer in self.observers:
            if isinstance(observer, WebSocketRealObserver):
                asyncio.run(observer.update(data))  # Async update
            else:
                observer.update(data)  # Sync update

    def send_heartbeat(self):
        '''
        send message every 60 seconds
        '''
        last_message_time = time.time()

        while not self.stop_heartbeat:
            try:
                if self.sws and self.sws.sock and self.sws.sock.connected:
                    print("💓 Sending heartbeat: ping")
                    self.sws.send(json.dumps({
                        "correlationID": self.correlation_id,
                        "action": 1,
                        "params": {
                            "mode": self.mode,
                            "tokenList": self.token_list  # ✅ load from YAML instead of hardcoded
                        }
                    }))
                else:
                    print("⚠️ WebSocket not connected. Reconnecting...")
                    self.reconnect()

                # If no message received for 60 sec, force reconnection
                if time.time() - last_message_time > 60:
                    print("⚠️ No messages received in 60 seconds. Reconnecting...")
                    self.reconnect()
                    last_message_time = time.time()

            except Exception as e:
                print(f"⚠️ Heartbeat error: {e}")

            time.sleep(30)  # Send heartbeat every 30 sec

    def start_heartbeat_thread(self):
        """Starts the heartbeat in a separate thread."""
        print('+++ start_heartbeat_thread')
        heartbeat_thread = threading.Thread(target=self.send_heartbeat, daemon=True)
        heartbeat_thread.start()

    def listen_websocket(self):
        """Listens for messages from the WebSocket."""
        print('+++ listen websocket')
        while self.sws and self.sws.sock and self.sws.sock.connected:
            try:
                message = self.sws.recv()  # Blocking call
                if message:
                    print(f"📩 Received: {message}")
            except Exception as e:
                print(f"⚠️ WebSocket listening error: {e}")
                self.reconnect()  # Reconnect if there's an error

    def on_open(self, wsapp):
        print("✅ WebSocket Opened!")
        time.sleep(1)

        try:
            # Ensure `self.sws` is properly initialized
            with self.lock:  # Ensure thread safety
                if self.sws:
                    self.sws.subscribe(
                        correlation_id=self.correlation_id,
                        mode=self.mode,
                        token_list=self.token_list
                    )
                    print("✅ Subscription successful!")
                else:
                    print("⚠️ WebSocket instance (self.sws) is not initialized!")
        except Exception as e:
            print(f"⚠️ Subscription failed: {e}")

    def start_websocket(self):
        print("🔄 Starting WebSocket connection...")
        auth_info = self.session.get_auth_info()
        if not auth_info or any(i is None for i in auth_info):
            raise RuntimeError("Auth info retrieval failed — aborting WebSocket start")

        self.AUTH_TOKEN, self.FEED_TOKEN, self.API_KEY, self.CLIENT_ID = (
            auth_info["auth_token"],
            auth_info["feed_token"],
            auth_info["api_key"],
            auth_info["client_id"]
        )

        while True:
            try:
                print('Auth Token:', self.AUTH_TOKEN)
                print('Feed Token:', self.FEED_TOKEN)

                with self.lock:  # Ensure thread safety when setting self.sws`
                    if not self.sws:  # Initialize only if not already set
                        self.sws = SmartWebSocketV2(
                            self.AUTH_TOKEN,
                            self.API_KEY,
                            self.CLIENT_ID,
                            self.FEED_TOKEN,
                            max_retry_attempt=5
                        )

                        self.sws.on_data = self.on_data
                        self.sws.on_open = self.on_open
                        self.sws.on_close = self.on_close
                        self.sws.on_error = self.on_error

                self.sws.connect()
                print('✅ WebSocket connection established ...')

                # Start sending heartbeats
                self.start_heartbeat_thread()

                # Start listening for messages in a new thread
                listen_thread = threading.Thread(target=self.listen_websocket, daemon=True)
                listen_thread.start()

                break  # Exit loop after successful connection

            except Exception as e:
                print(f"⚠️ WebSocket connection failed: {e}")
                time.sleep(5)  # Retry after a delay

    def time_stamp(self, message):
        data = json.loads(message)  # Convert JSON string to dictionary
        timestamp = data['exchange_timestamp'] / 1000  # Convert to seconds
        utc_time = datetime.datetime.utcfromtimestamp(timestamp)

        timezone = pytz.timezone('Asia/Kolkata')
        local_time = utc_time.replace(tzinfo=pytz.utc).astimezone(timezone)
        return local_time.strftime('%Y-%m-%d %H:%M:%S')

    def on_data(self, wsapp, message):
        try:
            data = json.loads(message)
            self.notify_observers(data)
        except Exception as e:
            print(f"⚠️ Error in on_data: {e}")

    def on_close(self, wsapp):
        """Handles WebSocket closing."""
        logger.info("WebSocket Closed!")
        wsapp.close_connection()

    def on_error(self, wsapp, error):
        """Handles WebSocket errors."""
        logger.error(f"Error: {error}")
        # wsapp.unsubscribe(correlation_id, mode, self.token_list)

    def on_message(self, wsapp, message):
        print("[WebSocket] Message received")
        self.notify_observers(message)

    def stop(self):
        self._running = False
        if self.sws and self.sws.sock and self.sws.sock.connected:
            self.sws.close_connection()
            print("🔴 WebSocket manually stopped.")

if __name__ == "__main__":
    smart_ws_client = SmartWebSocketV2Client()
    # ✅ Load strategies from YAML
    strategies = load_limit_order_strategies()
    print('+++ strategies ', strategies)
    for strat in strategies:
        observer = LimitOrderTriggerObserver(
            symbol_token=strat["symbol_token"],
            tradingsymbol=strat["tradingsymbol"],
            target_price=strat["target_price"],
            quantity=strat["quantity"],
            order_type=strat["order_type"]
        )
        smart_ws_client.add_observer(observer)

    # Start WebSocket
    smart_ws_client.start_websocket()
