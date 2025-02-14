# modules
from SmartApi.smartConnect import SmartConnect
import pyotp
import json
import pandas as pd

# credentials
from src import config as dd

# Constants
TRADING_SYMBOL = "SBIN-EQ"  # Replace with the desired future symbol
EXCHANGE = "NSE"
SYMBOL_TOKEN = "3045"

# ✅ Replace with your Angel Broking credentials
API_KEY = dd.API_KEY
CLIENT_ID = dd.CLIENT_ID
PASSWORD = dd.PASSWORD

# totp
totp = pyotp.TOTP(dd.TOTP)
totp = totp.now()

# ✅ Login to SmartAPI
smart_api = SmartConnect(api_key=API_KEY)
session = smart_api.generateSession(CLIENT_ID, PASSWORD, totp=totp)

# ✅ Define the parameters for historical data request
historicDataParams = {
    "exchange": "NSE",  # Exchange (e.g., NSE, BSE)
    "symboltoken": "3045",  # Token for the stock (Example: "3045" for RELIANCE)
    "interval": "ONE_DAY",  # Timeframe (ONE_MINUTE, FIVE_MINUTE, ONE_DAY, etc.)
    "fromdate": "2024-01-01 09:15",  # Start Date (YYYY-MM-DD HH:MM)
    "todate": "2024-02-01 15:30"  # End Date (YYYY-MM-DD HH:MM)
}

# ✅ Fetch historical candle data
try:
    period = 21
    response = smart_api.getCandleData(historicDataParams)
    candle_data = response["data"]

    # Print formatted JSON response
    print(json.dumps(candle_data, indent=4))
    df = pd.DataFrame(candle_data, columns=["datetime", "open", "high", "low", "close", "volume"])
    df['EMA_21'] = df['close'].ewm(span=period, adjust=False).mean()
    print("ONE DAY \n", df.to_markdown())
    last_row = df.iloc[-1]
    if last_row['close'] > last_row['EMA_21']:
        print("Condition met. Placing order because last close is greater than last ema_21 ")
except Exception as e:
    print(f"Error fetching candle data: {str(e)}")
