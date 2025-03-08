from smartapi import SmartWebSocketV2

# Replace with your credentials
AUTH_TOKEN = "your_auth_token"
API_KEY = "your_api_key"
CLIENT_ID = "your_client_id"
FEED_TOKEN = "your_feed_token"

# Initialize WebSocket
sws = SmartWebSocketV2(AUTH_TOKEN, API_KEY, CLIENT_ID, FEED_TOKEN)

# Callback functions
def on_data(wsapp, message):
    print(f'+++ {message}')

def on_open(wsapp):
    print(f'+++ socket opened')
    # Subscribe to a sample token (Replace with an actual token)
    sws.subscribe("nse_cm", "26000")

def on_close(wsapp):
    print(f'+++ socket closed')

def on_error(wsapp, error):
    print(f'+++ error {error}')

# Assign the event handlers
sws.on_data = on_data
sws.on_open = on_open
sws.on_close = on_close
sws.on_error = on_error

# Start WebSocket
sws.connect()
