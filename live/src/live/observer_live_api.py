##########################################################
# requirements
# AUTH_TOKEN from session
# API_KEY from cnf,
# CLIENT_ID from cnf
# FEED_TOKEN from session
##########################################################
# system modules
import json
import pytz
import time
import datetime
import threading
import subprocess
import traceback
import pandas as pd
from logzero import logger
from collections import deque
from pymongo import MongoClient
import plotly.graph_objects as go
from SmartApi.smartWebSocketV2 import SmartWebSocketV2

# custom modules
from base import config as cnf
from base.session import Session


# Observer Interface
class WebSocketObserver:
    def update(self, message):
        raise NotImplementedError("Observer must implement the update method.")


# Concrete Observer: Logs messages
class LoggerObserver(WebSocketObserver):
    def update(self, message):
        print("[Logger] Received:", message)


# Concrete Observer: Alerts on a certain condition
class AlertObserver(WebSocketObserver):
    def update(self, message):
        data = json.loads(message)
        print('+++ data ', data)
        # if "price" in data and data["price"] > 1000:  # Example condition
        #     print("[Alert] Price exceeded 1000:", data["price"])


# Concrete Observer: Sends an email alert when price exceeds 1000
class EmailAlertObserver(WebSocketObserver):
    def update(self, message):
        data = json.loads(message)
        if "price" in data and data["price"] > 1000:
            self.send_email_alert(data["price"])

    def send_email_alert(self, price):
        sender = "singhai.nish@gmail.com"
        receiver = "pvhatkar@gmail.com"
        subject = "Price Alert!"
        body = f"Price has exceeded 1000. Current price: {price}"

        message = f"Subject: {subject}\n\n{body}"

        # Simulating email sending
        print(f"[Email Alert] Sending email to {receiver}: {body}")
        # Uncomment below to send actual email (requires SMTP setup)
        # with smtplib.SMTP("smtp.example.com", 587) as server:
        #     server.starttls()
        #     server.login(sender, "your_password")
        #     server.sendmail(sender, receiver, message)


# Concrete Observer: Stores messages in MongoDB
class MongoDBObserver(WebSocketObserver):
    def __init__(self, db_name="websocketDB", collection_name="messages"):
        self.client = self.run_mongodb()
        self.db = self.client[db_name]  # Select database
        self.collection = self.db[collection_name]  # Select collection
        # Integrating other observers
        self.logger_observer = LoggerObserver()
        self.alert_observer = AlertObserver()
        self.logger_observer.update(f'+++ client: {self.client}, db: {self.db}, collection: {self.collection}')



    def is_mongodb_running(self):
        """Check if MongoDB is running using systemctl status."""
        try:
            subprocess.run(["systemctl", "is-active", "--quiet", "mongod"], check=True)
            return True
        except subprocess.CalledProcessError:
            return False

    def start_mongodb(self):
        """Start MongoDB service if not running."""
        try:
            print("Starting MongoDB...")
            subprocess.run(["sudo", "systemctl", "start", "mongod"])
            time.sleep(5)  # Give MongoDB time to start
            return True
        except subprocess.CalledProcessError:
            return False

    def stop_mongodb(self):
        print("Stopping MongoDB...")
        pass

    def run_mongodb(self):
        # Ensure MongoDB is running
        if not self.is_mongodb_running():
            self.start_mongodb()
        else:
            print('+++ ✅ Already running ')

        # Connect to MongoDB
        try:
            client = MongoClient("mongodb://localhost:27017/")
            print("Connected to MongoDB successfully!")
            print("Databases:", client.list_database_names())
        except Exception as e:
            print("Failed to connect to MongoDB:", e)
        return client

    def update(self, message):
        data = json.loads(message)
        self.collection.insert_one(data)  # Store message in MongoDB
        print("✅ [MongoDB] Stored message:", data)

        # Check for alert condition
        self.alert_observer.update(message)

    def get_all_messages(self):
        """Fetch all stored messages from MongoDB."""
        return list(self.collection.find({}, {"_id": 0}))  # Exclude MongoDB's default '_id' field


'''
ws_client.add_observer(ml_observer)  # ML price prediction
'''

class SmartWebSocketV2Client:
    # get smart_api
    _session = None
    AUTH_TOKEN = None
    FEED_TOKEN = None

    @property
    def session(self):
        if self._session is None:  # Only initialize when accessed
            print(" ✅ Initializing session...")
            self._session = Session()
            self.AUTH_TOKEN = self._session.auth_token()
            self.FEED_TOKEN = self._session.feed_token()
        return self._session

    ACTION = "subscribe"
    FEED_TYPE = "ltp"
    YOUR_ACCESS_TOKEN = cnf.TOTP
    SYMBOL_TOKEN = "3045" # used to get historical data
    TRADING_SYMBOL = "SBIN-EQ"
    EXCHANGE = "NSE"
    # variables
    correlation_id = f"subscription_{int(time.time())}"  # Generates a unique ID
    action = 1  # action = 1, subscribe to the feeds action = 2 - unsubscribe
    mode = 1  # mode = 1 , Fetches LTP quotes
    # Tokens to subscribe (Example: Nifty 50)
    # token_list = [
    #     {
    #         "exchangeType": 2,  # NSE
    #         "tokens": ["26000"],  # NIFTY 50 Token
    #         "interval": 60
    #     }
    # ]
    # Store live data
    data_queue = deque(maxlen=50)  # Store the last 50 data points

    def __init__(self):
        self.sws = None  # Store WebSocket instance persistently
        self.lock = threading.Lock()  # To prevent race conditions
        self.observers = []
        self.sess = self.session
        self.stop_heartbeat = False  # Control flag for stopping heartbeat

    def send_heartbeat(self):
        """Sends a 'ping' message every 30 seconds to keep the WebSocket alive."""
        while not self.stop_heartbeat:
            try:
                if self.sws:
                    print("💓 Sending heartbeat: ping")
                    heartbeat_message = json.dumps({
                        "correlationID": self.correlation_id,
                        "action": 1,
                        "params": {
                            "mode": self.mode,
                            "tokenList": [
                                {"exchangeType": 2, "tokens": ["26000"]}
                            ]
                        }
                    })
                    print("🔄 Sending heartbeat...")
                    self.sws.send(heartbeat_message)  # Send ping message
                time.sleep(30)  # Wait 30 seconds before sending the next ping
            except Exception as e:
                print(f"⚠️ Heartbeat error: {e}")

    def start_heartbeat_thread(self):
        """Starts the heartbeat in a separate thread."""
        heartbeat_thread = threading.Thread(target=self.send_heartbeat, daemon=True)
        heartbeat_thread.start()

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
                # Start sending heartbeats after connection is established
                self.start_heartbeat_thread()

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
        """Handles incoming live market data."""
        print(f"📥 Received message: {message}")  # Debugging
        try:
            formatted_timestamp = self.time_stamp(message)
            data = json.loads(message)
            for item in data["data"]:
                _token = item["token"]
                _item_price = item.get("ltp", 0)  # Last traded price
                row_format = "Exchange Type: {exchange_type}, Token: {token}, Last Traded Price: {last_traded_price:.2f}, Timestamp: {timestamp}"

                # Format the message data
                formatted_row = row_format.format(
                    exchange_type=data['exchange_type'],
                    token=_token,
                    last_traded_price=_item_price / 100,
                    # Assuming this division by 100 is required for your specific case
                    timestamp=formatted_timestamp
                )

                # Store data
                self.data_queue.append(formatted_row)

                # Print latest price
                print(f"Token: {_token}, LTP: {_item_price}")

        except Exception as e:
            print(f"Error processing data: {e}")

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

    def start(self):
        thread = threading.Thread(target=self.send_heartbeat) # ❌ Remove daemon=True
        thread.start()
        thread.join()  # 🔥 Wait for the thread to finish before exiting

    def get_latest_close_greater_than_ema(self, _live_data, time_interval, start_date, end_date):
        # _flag = None
        # try:
        _ema_data = self.calculate_ema(_live_data)
        _ema_sorted = _ema_data.sort_values(by='EMA_21', ascending=True)
        print('+++ ema sorted \n\n', _ema_sorted)
        _greater_than = _ema_sorted[_ema_sorted['close'] > _ema_sorted['EMA_21']]
        print('+++ all greater than \n\n', _greater_than)
        last_row = _ema_sorted.iloc[-1]
        if last_row['close'] > last_row['EMA_21']:
            print("Condition met. Placing order because last close {} is greater than last ema_21 {}\n".format(
                last_row['close'], last_row['EMA_21']))

        _greater_last_row = _greater_than.iloc[-1]
        if _greater_last_row['close'] > _greater_last_row['EMA_21']:
            print("_greater_last_row : Condition met. Placing order because last close {} is greater than last ema_21 {}\n".format(
                _greater_last_row['close'], _greater_last_row['EMA_21']))

        # except Exception as e:
        #     print(f"Error fetching candle data: {str(e)}")
        # return _flag

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

#
# #sws.connect()
# # or
# swsc = SmartWebSocketV2Client()
# swsc.start()
# # Run the live chart function
# swsc.live_chart()

# if __name__ == "__main__":
#     client = SmartWebSocketV2Client()
#     client.start_websocket()  # Start WebSocket connection
