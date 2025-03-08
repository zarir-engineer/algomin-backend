import json
import time
import smtplib
from collections import deque
from pymongo import MongoClient
from smartapi import SmartWebSocketV2

# WebSocket Credentials (Replace with actual values)
AUTH_TOKEN = "your_auth_token"
API_KEY = "your_api_key"
CLIENT_ID = "your_client_id"
FEED_TOKEN = "your_feed_token"

# Observer Interface
class WebSocketObserver:
    def update(self, message):
        raise NotImplementedError("Observer must implement the update method.")

# Logger Observer
class LoggerObserver(WebSocketObserver):
    def update(self, message):
        print(f"📝 [Logger] {message}")

# Email Alert Observer
class EmailAlertObserver(WebSocketObserver):
    def send_email_alert(self, subject, body):
        sender = "your_email@gmail.com"
        receiver = "recipient_email@gmail.com"
        message = f"Subject: {subject}\n\n{body}"
        print(f"📧 [Email Alert] Sending email: {subject}")

        # Uncomment to send actual email (requires SMTP setup)
        # with smtplib.SMTP("smtp.example.com", 587) as server:
        #     server.starttls()
        #     server.login(sender, "your_password")
        #     server.sendmail(sender, receiver, message)

    def update(self, message):
        pass  # Not needed here since alerts are triggered from EMAObserver

# MongoDB Observer
class MongoDBObserver(WebSocketObserver):
    def __init__(self):
        self.client = MongoClient("mongodb://localhost:27017/")
        self.db = self.client["websocketDB"]
        self.collection = self.db["messages"]

    def update(self, message):
        data = json.loads(message)
        self.collection.insert_one(data)
        print(f"✅ [MongoDB] Stored: {data}")

# EMA Observer with Stop-Loss & Take-Profit Tracking
class EMAObserver(WebSocketObserver):
    def __init__(self, period=10, stop_loss_pct=2, take_profit_pct=4):
        self.period = period
        self.stop_loss_pct = stop_loss_pct / 100  # Convert percentage to decimal
        self.take_profit_pct = take_profit_pct / 100  # Convert percentage to decimal
        self.prices = deque(maxlen=period)
        self.ema = None
        self.last_ltp = None
        self.trade_entry_price = None
        self.stop_loss = None
        self.take_profit = None
        self.trade_type = None  # "CALL" or "PUT"

    def update(self, message):
        data = json.loads(message)
        if "ltp" in data:
            ltp = data["ltp"]

            # Store previous LTP before updating EMA
            previous_ltp = self.last_ltp
            self.last_ltp = ltp

            # Update EMA
            self.add_price(ltp)
            print(f"📊 [EMA] Updated EMA({self.period}): {self.ema:.2f}")

            # Handle trade signals, SL, and TP checks
            if previous_ltp is not None and self.ema is not None:
                self.check_trade_signals(previous_ltp, ltp)
                self.check_stop_loss(ltp)
                self.check_take_profit(ltp)

    def add_price(self, price):
        """Update the EMA with the new price."""
        self.prices.append(price)
        if len(self.prices) == self.period:
            self.calculate_ema()

    def calculate_ema(self):
        """Calculate EMA using the smoothing formula."""
        smoothing = 2 / (self.period + 1)
        if self.ema is None:
            self.ema = sum(self.prices) / self.period  # First EMA is SMA
        else:
            self.ema = (self.prices[-1] * smoothing) + (self.ema * (1 - smoothing))

    def check_trade_signals(self, previous_ltp, ltp):
        """Check for trade entry signals."""
        if previous_ltp < self.ema and ltp > self.ema:
            self.trigger_call_alert(ltp)
        elif previous_ltp > self.ema and ltp < self.ema:
            self.trigger_put_alert(ltp)

    def check_stop_loss(self, ltp):
        """Check if the stop-loss has been hit."""
        if self.trade_entry_price and self.stop_loss:
            if self.trade_type == "CALL" and ltp <= self.stop_loss:
                self.trigger_stop_loss_alert()
            elif self.trade_type == "PUT" and ltp >= self.stop_loss:
                self.trigger_stop_loss_alert()

    def check_take_profit(self, ltp):
        """Check if the take-profit has been hit."""
        if self.trade_entry_price and self.take_profit:
            if self.trade_type == "CALL" and ltp >= self.take_profit:
                self.trigger_take_profit_alert()
            elif self.trade_type == "PUT" and ltp <= self.take_profit:
                self.trigger_take_profit_alert()

    def trigger_call_alert(self, price):
        """Trigger an alert and set SL/TP for a CALL trade."""
        print(f"🚀 [CALL ALERT] LTP {price} crossed above EMA {self.ema:.2f}. Consider buying!")

        # Set trade entry price, stop-loss, and take-profit
        self.trade_entry_price = price
        self.stop_loss = price * (1 - self.stop_loss_pct)
        self.take_profit = price * (1 + self.take_profit_pct)
        self.trade_type = "CALL"

        # Send email alert
        email_alert = EmailAlertObserver()
        email_alert.send_email_alert(
            "🚀 CALL SIGNAL ALERT",
            f"LTP {price} crossed above EMA {self.ema:.2f}. Consider taking a CALL!\n"
            f"🎯 Stop-Loss: {self.stop_loss:.2f}\n"
            f"🎯 Take-Profit: {self.take_profit:.2f}"
        )

    def trigger_put_alert(self, price):
        """Trigger an alert and set SL/TP for a PUT trade."""
        print(f"⚠️ [PUT ALERT] LTP {price} dropped below EMA {self.ema:.2f}. Consider selling!")

        # Set trade entry price, stop-loss, and take-profit
        self.trade_entry_price = price
        self.stop_loss = price * (1 + self.stop_loss_pct)
        self.take_profit = price * (1 - self.take_profit_pct)
        self.trade_type = "PUT"

        # Send email alert
        email_alert = EmailAlertObserver()
        email_alert.send_email_alert(
            "⚠️ PUT SIGNAL ALERT",
            f"LTP {price} dropped below EMA {self.ema:.2f}. Consider taking a PUT!\n"
            f"🎯 Stop-Loss: {self.stop_loss:.2f}\n"
            f"🎯 Take-Profit: {self.take_profit:.2f}"
        )

    def trigger_stop_loss_alert(self):
        """Trigger an alert when SL is hit."""
        print(f"🛑 [STOP-LOSS HIT] Trade exited at SL {self.stop_loss:.2f}.")

        # Send email alert
        email_alert = EmailAlertObserver()
        email_alert.send_email_alert(
            "🛑 STOP-LOSS HIT",
            f"Trade exited at SL {self.stop_loss:.2f}. Consider reassessing the market."
        )

        # Reset trade parameters
        self.reset_trade()

    def trigger_take_profit_alert(self):
        """Trigger an alert when TP is hit."""
        print(f"✅ [TAKE-PROFIT HIT] Trade exited at TP {self.take_profit:.2f}.")

        # Send email alert
        email_alert = EmailAlertObserver()
        email_alert.send_email_alert(
            "✅ TAKE-PROFIT HIT",
            f"Trade exited at TP {self.take_profit:.2f}. Profit secured! 🎉"
        )

        # Reset trade parameters
        self.reset_trade()

    def reset_trade(self):
        """Reset trade parameters after an exit."""
        self.trade_entry_price = None
        self.stop_loss = None
        self.take_profit = None
        self.trade_type = None

# Start WebSocket Client
client = SmartWebSocketClient()
client.add_observer(EMAObserver(period=10, stop_loss_pct=2, take_profit_pct=4))  # 2% SL, 4% TP
client.start_websocket()
