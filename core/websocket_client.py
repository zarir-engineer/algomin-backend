##########################################################
# requirements
# AUTH_TOKEN from session
# API_KEY from cnf,
# CLIENT_ID from cnf
# FEED_TOKEN from session
##########################################################
# system modules
import os
import sys
import time
import json
import pytz
import asyncio
import datetime
import threading
from logzero import logger
from SmartApi.smartWebSocketV2 import SmartWebSocketV2

# custom modules
from core.session import AngelOneSession
from core.config_loader import ConfigLoader  # adjust import as per your structure
from core.strategy_loader import StrategyLoader
from observer import WebSocketRealObserver
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))


'''
ws_client.add_observer(ml_observer)  # ML price prediction
'''

def is_non_empty_list(value):
    return isinstance(value, list) and len(value) > 0


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
    def __init__(self, api_key, client_id):
        self.api_key = api_key
        self.client_id = client_id
        self.session = AngelOneSession()  # or inject it
        # Strictly use feed_token from session
        self.feed_token = self.session.feed_token
        self.sws = None  # Store WebSocket instance persistently
        self.lock = threading.Lock()  # Prevent race conditions
        self.observers = []  # Store observer instances
        self.stop_heartbeat = False  # Control flag for stopping heartbeat
        self.correlation_id = f"subscription_{int(time.time())}"  # Generates a unique ID
        self.mode = "full"
        self.token_list = []

    @classmethod
    def from_config(cls):
        config_loader = ConfigLoader()

        api_key = config_loader.get("api_key")
        client_code = config_loader.get("client_code")

        instance = cls(api_key, client_code)

        # Load WS config into instance
        instance.load_ws_config(config_loader)

        return instance

    def load_ws_config(self):
        """
        Now loads token_list from strategies.yaml instead of common.yaml
        """
        strategy_loader = StrategyLoader()
        subscriptions = strategy_loader.extract_subscription_tokens("limit_order_strategies")

        self.token_list = subscriptions
        self.mode = "full"
        self.correlation_id = f"limit_order_{int(time.time())}"

        if not self.token_list:
            print("⚠️ No tokens extracted from strategies.yaml")

        print(f"✅ WS mode: {self.mode}")
        print(f"✅ Subscriptions: {self.token_list}")

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
                if self.is_connected():
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
        heartbeat_thread = threading.Thread(target=self.send_heartbeat, daemon=True)
        heartbeat_thread.start()

    def listen_websocket(self):
        """Listens for messages from the WebSocket."""
        while self.is_connected():
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
        print('+++ correlation id ', self.correlation_id)
        print('+++ mode ', self.mode)
        print('+++ token list ', self.token_list)
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
        print('+++ message ', message)
        try:
            data = json.loads(message)
            self.notify_observers(data)
        except json.JSONDecodeError as e:
            logger.error(f"⚠️ Failed to decode JSON: {e}")
        except Exception as e:
            logger.error(f"⚠️ Error in on_data: {e}")

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
        if self.is_connected():
            self.sws.close_connection()
            print("🔴 WebSocket manually stopped.")


    def is_connected(self):
        return self.sws and self.sws.sock and self.sws.sock.connected
