from base.session import Session

# # Step 1: Login to SmartAPI
current_session = Session()

# Step 2: Get Stock Symbol Token (Example: RELIANCE)
symbol_token = "2885"  # Fetch correct token using API


# Step 3: Define Bracket Order Parameters
order_params = {
    "variety": "STOPLOSS_BO",  # Bracket Order type
    "tradingsymbol": "RELIANCE",  # Stock symbol
    "symboltoken": symbol_token,  # Token for the stock
    "exchange": "NSE",  # NSE or BSE
    "transactiontype": "BUY",  # BUY or SELL
    "ordertype": "LIMIT",  # Bracket orders allow only LIMIT orders
    "quantity": 10,  # Number of shares
    "price": 2500.00,  # Entry price
    "triggerprice": 2495.00,  # Stop-loss trigger price
    "squareoff": 20.00,  # Target (profit) in absolute points
    "stoploss": 10.00,  # Stop-loss in absolute points
    "trailingStopLoss": 5.00,  # Optional trailing SL
    "producttype": "INTRADAY",  # Bracket Order only supports INTRADAY
    "duration": "DAY"
}

# Step 4: Place the Bracket Order
order_response = current_session.smart_api.placeOrder(order_params)

# Print Response
print(order_response)


# Step 1: Fetch User Profile to verify login
profile = current_session.smart_api.getProfile(current_session.smart_api.cnf.CLIENT_ID)
