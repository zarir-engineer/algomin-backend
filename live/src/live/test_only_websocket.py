from SmartApi.smartWebSocketV2 import SmartWebSocketV2
from base.session import Session
import base.config as cnf

sess = Session()
AUTH_TOKEN = sess.auth_token()
FEED_TOKEN = sess.feed_token()

sws = SmartWebSocketV2(AUTH_TOKEN, cnf.API_KEY, cnf.CLIENT_ID, FEED_TOKEN, max_retry_attempt=3)

def on_open(wsapp):
    print("✅ WebSocket Opened!")
    test_message = "Just Testing ..."
    wsapp.on_data(None, test_message)
    sws.close_connection()  # Immediately close after test

def on_close(wsapp):
    print("❌ WebSocket Closed!")

def on_error(wsapp, error):
    print(f"⚠️ Error: {error}")

sws.on_open = on_open
sws.on_close = on_close
sws.on_error = on_error

print("🔄 Connecting WebSocket...")
sws.connect()