# system modules
import json
import pandas as pd


# custom modules
from base.session import Session
# credentials

# Constants
TRADING_SYMBOL = "SBIN-EQ"  # Replace with the desired future symbol
exchange = "NSE"
symbol_token = "3045"
interval = "ONE_DAY"  # Timeframe (ONE_MINUTE, FIVE_MINUTE, ONE_DAY, etc.)
current_session = Session()
fromdate = "2024-01-01 09:15"
todate = "2024-02-01 15:30"

smart_api = current_session.smart_api
# ✅ Define the parameters for historical data request


def hour_history(fromdate, todate, symbol_token, exchange="NSE", interval="ONE_DAY", period=21):
    historicDataParams = {
        "exchange": exchange,  # Exchange (e.g., NSE, BSE)
        "symboltoken": symbol_token,  # Token for the stock (Example: "3045" for RELIANCE)
        "interval": interval,
        "fromdate": fromdate,  # Start Date (YYYY-MM-DD HH:MM)
        "todate": todate  # End Date (YYYY-MM-DD HH:MM)
    }

    # ✅ Fetch historical candle data
    try:
        period = period
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
