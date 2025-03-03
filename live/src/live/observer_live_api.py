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
        self.logger_observer.update('+++ client ', self.client, '\n\ndb :', self.db, '\n\ncollection : ', self.collection)


    def is_mongodb_running(self):
        """Check if MongoDB is running using systemctl status."""
        try:
            subprocess.run(["systemctl", "is-active", "--quiet", "mongod"])
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
            print('+++ Already running ')

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
        print("[MongoDB] Stored message:", data)

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
            print("Initializing session...")
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
    token_list = [
        {
            "exchangeType": 2,  # NSE
            "tokens": ["26000"]  # NIFTY 50 Token
        }
    ]
    # Store live data
    data_queue = deque(maxlen=50)  # Store the last 50 data points

    def __init__(self):
        # instance of session
        self.observers = []
        self.sws = None
        self.sess = self.session

    def add_observer(self, observer):
        self.observers.append(observer)

    def notify_observers(self, message):
        for observer in self.observers:
            observer.update(message)

    def time_stamp(self, wsapp, message):
        # Convert timestamp from milliseconds to seconds
        timestamp = message['exchange_timestamp'] / 1000  # Convert to seconds
        utc_time = datetime.datetime.utcfromtimestamp(timestamp)

        # Define the timezone for UTC +05:30
        timezone = pytz.timezone('Asia/Kolkata')  # 'Asia/Kolkata' is the timezone for UTC +05:30

        # Convert UTC time to UTC +05:30
        local_time = utc_time.replace(tzinfo=pytz.utc).astimezone(timezone)
        formatted_timestamp = local_time.strftime('%Y-%m-%d %H:%M:%S')
        return formatted_timestamp

    def on_data(self, wsapp, message):
        """Handles incoming live market data."""

        try:
            formatted_timestamp = self.time_stamp(message)
            data = json.loads(message)
            print('+++ incoming data ', data)
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

    def on_open(self, wsapp):
        print("✅ WebSocket Opened!")
        time.sleep(1)  # Add slight delay before subscribing

        try:
            wsapp.subscribe(
                correlation_id=self.correlation_id,  # Unique identifier
                mode=self.mode,  # LTP mode
                token_list=[
                    {
                        "exchangeType": 2,  # NSE
                        "tokens": ["26000"]  # NIFTY 50 Token
                    }
                ]
            )
            print("✅ Subscription successful!")
        except Exception as e:
            print(f"⚠️ Subscription failed: {e}")


    # def on_open(self, wsapp):
    #     """Handles WebSocket opening and subscription."""
    #     print(f"wsapp instance: {wsapp}")
    #     print('corelation id ', self.correlation_id)
    #     print('mode ', self.mode)
    #     print('token list ', self.token_list)
    #     wsapp.subscribe(self.correlation_id, self.mode, self.token_list)

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

        self.sws = SmartWebSocketV2(
            self.AUTH_TOKEN,
            cnf.API_KEY,
            cnf.CLIENT_ID,
            self.FEED_TOKEN,
            max_retry_attempt=5
        )

        self.sws.on_data = self.on_data
        self.sws.on_open = self.on_open
        print('+++ before on open')
        self.sws.on_close = self.on_close
        self.sws.on_error = self.on_error
        self.sws.AUTH_TOKEN = self.AUTH_TOKEN
        self.sws.FEED_TOKEN = self.FEED_TOKEN

        thread = threading.Thread(target=self.sws.connect)
        thread.start()
        #TODO add time check

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

