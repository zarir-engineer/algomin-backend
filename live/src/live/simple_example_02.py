# system modules
import json
import pytz
import time
import datetime
import threading
from logzero import logger
from collections import deque
from SmartApi.smartWebSocketV2 import SmartWebSocketV2

# custom modules
from base import config as cnf
from base.session import AngelOneSession

sws = SmartWebSocketV2(AUTH_TOKEN, cnf.API_KEY, cnf.CLIENT_ID, FEED_TOKEN, max_retry_attempt=5)

# Store live data
data_queue = deque(maxlen=50)  # Store the last 50 data points

# Tokens to subscribe (Example: Nifty 50)
token_list = [
    {
        "exchangeType": 2,  # NSE
        "tokens": ["26000"]  # NIFTY 50 Token
    }
]

token_list1 = [
    {
        "exchangeType": 1,              # exchange type ( e.g., NSE )
        "tokens": ["26000", "26009"]    # Instruments tokens for stocks
    }
]

def on_open(wsapp):
    logger.info("on open")
    sws.subscribe(correlation_id, mode, token_list)
    # sws.subscribe(correlation_id, mode, token_list1)


def time_stamp(wsapp, message):
    # Convert timestamp from milliseconds to seconds
    timestamp = message['exchange_timestamp'] / 1000  # Convert to seconds
    utc_time = datetime.utcfromtimestamp(timestamp)

    # Define the timezone for UTC +05:30
    timezone = pytz.timezone('Asia/Kolkata')  # 'Asia/Kolkata' is the timezone for UTC +05:30

    # Convert UTC time to UTC +05:30
    local_time = utc_time.replace(tzinfo=pytz.utc).astimezone(timezone)
    formatted_timestamp = local_time.strftime('%Y-%m-%d %H:%M:%S')
    return formatted_timestamp


# row_format = "Exchange Type: {exchange_type}, Token: {token}, Last Traded Price: {last_traded_price}"
def on_data(wsapp, message):
    """Handles incoming live market data."""
    global data_queue

    try:
        formatted_timestamp = time_stamp(message)
        data = json.loads(message)
        print('+++ data ', data)
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
            data_queue.append(formatted_row)

            # Print latest price
            print(f"Token: {_token}, LTP: {_item_price}")

    except Exception as e:
        print(f"Error processing data: {e}")


def on_close(wsapp):
    """Handles WebSocket closing."""
    print("WebSocket Closed!")
    # sws.unsubscribe(correlation_id, mode, token_list1)


def on_error(wsapp, error):
    """Handles WebSocket errors."""
    print(f"Error: {error}")
    # sws.unsubscribe(correlation_id, mode, token_list1)


def close_connection():
    sws.close_connection()


# Assign the callbacks.
sws.on_data = on_data
sws.on_open = on_open
sws.on_close = on_close
sws.on_error = on_error

#sws.connect()
# or
threading.Thread(target=sws.connect).start()

# Let it run for 5 seconds
time.sleep(5)
stop_event.set()  # Signal the thread to stop


# Ensure thread stops before continuing
t.join()
print("Main program finished.")
