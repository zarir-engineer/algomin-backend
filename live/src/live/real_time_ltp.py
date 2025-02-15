#################################################
# How It Works
# Connects to WebSocket using SmartWebSocketV2
# Subscribes to stock tokens
# Receives live market data via on_message()
# Stores latest 50 price points in time_series and price_series
# Plots real-time price movements with Matplotlib
# Updates the chart dynamically every second
#################################################

import json
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from SmartApi.smartWebSocketV2 import SmartWebSocketV2
from base import config as cnf

from auto_authenticate import AUTH_TOKEN as AT, FEED_TOKEN as FT

# Authentication Details
AUTH_TOKEN = AT
FEED_TOKEN = FT
API_KEY = cnf.API_KEY
CLIENT_ID = cnf.CLIENT_ID

# Subscription Tokens
token_list = [
    {"exchangeType": 2, "tokens": ["57920"]}  # Example: Token for a stock (NSE)
]

# Initialize SmartWebSocketV2
sws = SmartWebSocketV2(AUTH_TOKEN, API_KEY, CLIENT_ID, FEED_TOKEN)

# Live data storage
time_series = []
price_series = []

# Matplotlib Setup
fig, ax = plt.subplots()
line, = ax.plot([], [], 'r-', label="Live Price")

# Initialize plot
def init():
    ax.set_xlim(0, 50)  # Time window (last 50 ticks)
    ax.set_ylim(1000, 2000)  # Adjust based on expected price range
    ax.set_xlabel("Time")
    ax.set_ylabel("Price")
    ax.legend()
    return line,

# Callback function to process live data
def on_message(message):
    global time_series, price_series
    data = json.loads(message)

    if "data" in data:
        for entry in data["data"]:
            token = entry["token"]  # Extract token
            last_price = entry["ltp"]  # Last traded price

            print(f"Token: {token}, Price: {last_price}")

            # Store live price data
            time_series.append(len(time_series))
            price_series.append(last_price)

            # Keep only last 50 data points
            if len(time_series) > 50:
                time_series = time_series[-50:]
                price_series = price_series[-50:]

# Matplotlib animation function
def update(frame):
    line.set_data(time_series, price_series)
    ax.set_xlim(max(0, len(time_series) - 50), len(time_series))  # Dynamic x-axis
    ax.set_ylim(min(price_series, default=1000) - 10, max(price_series, default=2000) + 10)
    return line,

# Attach callback to WebSocket
sws.on_message = on_message

# Start WebSocket and subscribe
def start_websocket():
    sws.connect()
    sws.subscribe(token_list)

# Run WebSocket in background
import threading
thread = threading.Thread(target=start_websocket, daemon=True)
thread.start()

# Start live chart animation
ani = animation.FuncAnimation(fig, update, init_func=init, interval=1000, blit=False)
plt.show()

# Close WebSocket when done
sws.close_connection()
