# from smartapi import SmartConnect
#
# # Your API credentials
# api_key = "YOUR_API_KEY"
# client_id = "YOUR_CLIENT_ID"
# password = "YOUR_PASSWORD"
#
# # Login to SmartAPI
# smart_api = SmartConnect(api_key)
# session_data = smart_api.generateSession(client_id, password)
# auth_token = session_data['data']['jwtToken']

from base.session import Session
from base import config as cnf
from live.bracket_order_stock import current_session

current_session = Session()

# Fetch User Profile to verify login
profile = current_session.smart_api.getProfile(cnf.CLIENT_ID)

# Order Parameters
order_params = {
    "variety": "STOPLOSS_BO",  # Bracket Order variety
    "tradingsymbol": "NIFTY24FEB18400CE",  # Example Options Symbol
    "symboltoken": "12345",  # Get token from API
    "exchange": "NFO",  # NSE Derivative Segment
    "transactiontype": "BUY",  # Buy or Sell
    "ordertype": "LIMIT",  # LIMIT or MARKET
    "quantity": 50,  # Lot Size
    "price": 100.00,  # Entry Price
    "triggerprice": 98.00,  # Stop Loss Price
    "squareoff": 5.00,  # Target in absolute points
    "stoploss": 2.00,  # Stop Loss in absolute points
    "trailingStopLoss": 1.00,  # Optional trailing SL
    "producttype": "INTRADAY",
    "duration": "DAY"
}

# Place the Bracket Order
order_response = current_session.smart_api.placeOrder(order_params)

# Print Response
print(order_response)
