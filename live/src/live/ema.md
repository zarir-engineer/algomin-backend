How the EMA Calculation Works
Stores the last 10 price values in a queue
Computes the first EMA as the Simple Moving Average (SMA)
Updates the EMA dynamically using the formula:

EM At =(P t × S)+(EMA t−1 × (1−S) )

where Smoothing Factor (S) = 2/𝑛+1
 
Example: If n = 10, then 
S= 2/11 =0.1818



Expected Output

🔄 Connecting to WebSocket...
✅ WebSocket Connected!
📩 [WebSocket] {"token": "26000", "ltp": 980.50}
✅ [MongoDB] Stored: {"token": "26000", "ltp": 980.50}
📊 [EMA] Updated EMA(10): 980.50
📩 [WebSocket] {"token": "26000", "ltp": 990.00}
📊 [EMA] Updated EMA(10): 981.85
📩 [WebSocket] {"token": "26000", "ltp": 1020.00}
🚨 [ALERT] Price exceeded 1000: 1020.00
📧 [Email Alert] Sending email to recipient_email@gmail.com: Price has exceeded 1000. Current price: 1020.00
📊 [EMA] Updated EMA(10): 985.72

EMA Calculation Integrated in Observer Pattern
✅ Live EMA Updates Every Time New Data Arrives
✅ Stores Only the Last 10 Prices for Efficient Calculation
✅ Auto-reconnects on Disconnection


Enhancing the Code: Adding a "Sell" Alert Condition
We'll modify the EMAObserver to check for a bullish crossover, which happens when:
✅ The last traded price (LTP) was below EMA
✅ The current closing price crosses above EMA

When this condition is met, we'll:
📩 Send an email alert
🚨 Trigger a sell alert notification


Adding a "PUT" Alert Condition
This update introduces a bearish crossover condition to detect when the current price drops below the EMA, which may indicate a potential PUT (Sell) opportunity.

🚀 Conditions for PUT Alert
✅ The last traded price (LTP) was above EMA
✅ The current closing price crosses below EMA

When this condition is met, we will:
📩 Send an email alert
🚨 Trigger an alert notification


How the PUT Condition Works
Tracks the previous LTP value (previous_ltp)
Compares it with the EMA to detect a bearish crossover:
If previous LTP > EMA (Price was above EMA)
And current LTP < EMA (Price just dropped below EMA)
⚠️ Trigger PUT Alert + Send Email


Expected Output

📩 [WebSocket] {"token": "26000", "ltp": 1010.00}
📊 [EMA] Updated EMA(10): 1005.50
📩 [WebSocket] {"token": "26000", "ltp": 1000.00}
📊 [EMA] Updated EMA(10): 1004.30
📩 [WebSocket] {"token": "26000", "ltp": 995.00}
⚠️ [PUT ALERT] LTP 995.00 dropped below EMA 1002.60. Consider selling!
📧 [Email Alert] Sending email: ⚠️ PUT SIGNAL ALERT


Features Added
✅ Detects Bullish EMA Crossovers (CALL Alert)
✅ Detects Bearish EMA Crossovers (PUT Alert)
✅ Triggers Alerts & Sends Email for Buy & Sell Calls

This update introduces a take-profit (TP) level alongside stop-loss (SL) for risk management.

Take-Profit Mechanism
CALL Trade: TP is set above the entry price
PUT Trade: TP is set below the entry price
Triggers an alert + email if TP is hit

Take-Profit Level Added
✅ TP Alert & Email When Hit
✅ Improved Risk Management

Now, your trades lock in profits automatically! 🚀