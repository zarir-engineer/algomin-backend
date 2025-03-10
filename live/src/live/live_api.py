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
import asyncio
import datetime
import threading
import pandas as pd
from logzero import logger
from collections import deque
import plotly.graph_objects as go
from SmartApi.smartWebSocketV2 import SmartWebSocketV2

# custom modules
from base.session import AngelOneSession
from base.observer import (LoggerObserver,
                           AlertObserver,
                           EmailAlertObserver,
                           DatabaseObserver,
                           MongoDbObserver,
                           EMAObserver,
                           WebSocketObserver
                           )


'''
ws_client.add_observer(ml_observer)  # ML price prediction
'''


class SmartWebSocketV2Client:
    """Handles WebSocket connection and observer pattern for market data."""

    def __init__(self):
        session = AngelOneSession()
        self.auth_token, self.feed_token = session.generate_tokens()  # Auto-generate tokens

        self.sws = None  # Store WebSocket instance persistently
        self.lock = threading.Lock()  # Prevent race conditions
        self.observers = []  # Store observer instances
        self.stop_heartbeat = False  # Control flag for stopping heartbeat
        self.data_queue = deque(maxlen=50)  # Store last 50 data points
        self.correlation_id = f"subscription_{int(time.time())}"  # Generates a unique ID

    def add_observer(self, observer):
        """Attach an observer."""
        self.observers.append(observer)

    def notify_observers(self, data):
        """Notify all observers when new market data is received."""
        for observer in self.observers:
            if isinstance(observer, WebSocketObserver):
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
                            "tokenList": [{"exchangeType": 2, "tokens": ["26000"]}]
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
                        token_list=[{"exchangeType": 2, "tokens": ["26000"], "interval":60}]
                    )
                    print("✅ Subscription successful!")
                else:
                    print("⚠️ WebSocket instance (self.sws) is not initialized!")
        except Exception as e:
            print(f"⚠️ Subscription failed: {e}")

    def start_websocket(self):
        print("🔄 Starting WebSocket connection...")

        while True:
            try:
                print('Auth Token:', self.AUTH_TOKEN)
                print('Feed Token:', self.FEED_TOKEN)

                with self.lock:  # Ensure thread safety when setting `self.sws`
                    if not self.sws:  # Initialize only if not already set
                        self.sws = SmartWebSocketV2(
                            self.AUTH_TOKEN,
                            cnf.API_KEY,
                            cnf.CLIENT_ID,
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

    def add_observer(self, observer):
        self.observers.append(observer)

    def notify_observers(self, message):
        for observer in self.observers:
            observer.update(message)

    def time_stamp(self, message):
        data = json.loads(message)  # Convert JSON string to dictionary
        timestamp = data['exchange_timestamp'] / 1000  # Convert to seconds
        utc_time = datetime.datetime.utcfromtimestamp(timestamp)

        timezone = pytz.timezone('Asia/Kolkata')
        local_time = utc_time.replace(tzinfo=pytz.utc).astimezone(timezone)
        return local_time.strftime('%Y-%m-%d %H:%M:%S')

    def on_data(self, wsapp, message):
        """Handles incoming live market data and notifies observers."""
        print(f"📥 Received message: {message}")

        try:
            data = json.loads(message)
            formatted_timestamp = self.time_stamp(message)

            for item in data["data"]:
                _token = item["token"]
                _ltp = item.get("ltp", 0) / 100  # Convert price to proper format

                # Store the latest price
                self.data_queue.append({
                    "timestamp": formatted_timestamp,
                    "ltp": _ltp,
                    "token": _token
                })

                # Compute EMA
                price_series = [entry["ltp"] for entry in self.data_queue]
                ema = pd.Series(price_series).ewm(span=10, adjust=False).mean().iloc[-1]

                # Prepare structured data for observers
                market_data = {
                    "timestamp": formatted_timestamp,
                    "ltp": _ltp,
                    "ema": ema,
                    "prev_close": price_series[-2] if len(price_series) > 1 else _ltp  # Track previous close
                }

                # 🔔 Notify observers (Email alerts, DB storage, WebSocket updates)
                self.notify_observers(market_data)

                print(f"Token: {_token}, LTP: {_ltp}, EMA: {ema}")

        except Exception as e:
            print(f"⚠️ Error processing data: {e}")


    # def on_data(self, wsapp, message):
    #     """Handles incoming live market data."""
    #     print(f"📥 Received message: {message}")  # Debugging
    #     try:
    #         formatted_timestamp = self.time_stamp(message)
    #         data = json.loads(message)
    #         for item in data["data"]:
    #             _token = item["token"]
    #             _item_price = item.get("ltp", 0)  # Last traded price
    #             row_format = "Exchange Type: {exchange_type}, Token: {token}, Last Traded Price: {last_traded_price:.2f}, Timestamp: {timestamp}"
    #
    #             # Format the message data
    #             formatted_row = row_format.format(
    #                 exchange_type=data['exchange_type'],
    #                 token=_token,
    #                 last_traded_price=_item_price / 100,
    #                 # Assuming this division by 100 is required for your specific case
    #                 timestamp=formatted_timestamp
    #             )
    #
    #             # Store data
    #             self.data_queue.append(formatted_row)
    #
    #             # Print latest price
    #             print(f"Token: {_token}, LTP: {_item_price}")
    #
    #     except Exception as e:
    #         print(f"Error processing data: {e}")

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

#TODO this will go inside render cloud server - fastapi
    def live_chart(self):
        fig = go.Figure()

        while True:
            if len(self.data_queue) > 0:
                df = pd.DataFrame([row.split(", ") for row in self.data_queue], columns=["Exchange Type", "Token", "LTP", "Timestamp"])
                df["Timestamp"] = pd.to_datetime(df["Timestamp"])
                df["LTP"] = df["LTP"].str.extract(r"([\d.]+)").astype(float)

                fig.data = []  # Clear old data
                fig.add_trace(go.Scatter(x=df["Timestamp"], y=df["LTP"], mode="lines", name="LTP"))
                fig.update_layout(title="Live Market Price", xaxis_title="Time", yaxis_title="Price")
                fig.show()

            time.sleep(2)  # Update every 2 seconds


# if __name__ == "__main__":
#     client = SmartWebSocketV2Client()
#     client.start_websocket()  # Start WebSocket connection
#     websocket_instance = comes from fastapi running on another server
    smart_ws_client = SmartWebSocketV2Client()
    # Add different observers
    smart_ws_client.add_observer(AlertObserver())
    smart_ws_client.add_observer(DatabaseObserver())
    # smart_ws_client.add_observer(WebSocketObserver(websocket_instance))
    smart_ws_client.add_observer(EMAObserver(period=10, stop_loss_pct=2, take_profit_pct=4))  # 2% SL, 4% TP
    # websocket_instance is coming from fastapi
    # Attach Flask-based WebSocket observer
    smart_ws_client.add_observer(WebSocketObserver())
    # Start WebSocket
    smart_ws_client.start_websocket()
