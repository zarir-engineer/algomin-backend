# brokers/smart_event_handler.py

from brokers.base_event_handler import BaseEventHandler
import time
import json

class AngelOneWebSocketEventHandler(BaseEventHandler):
		def on_data(self, ws, message):
		    print("📩 TICK:", message)
		    tick_data = json.loads(message)

		    for strategy in loaded_strategies:
		        if strategy.should_trigger(tick_data):  # custom logic
		            order_data = strategy.build_order()
		            result = trading_client.place_order(order_data)
		            print("✅ Order Executed:", result)
#TODO You might pass them into the event handler via a constructor (more on that later).
    def on_open(self, ws):
        print("✅ WebSocket Opened")
        time.sleep(1)
        try:
            # Ensure `self.sws` is properly initialized
            with self.lock:  # Ensure thread safety
                if self.sws:
                    self.sws.subscribe(
                        correlation_id=self.correlation_id,
                        mode=self.mode,
                        token_list=self.token_list
                    )
                    print(f"📡 Subscribed to: {json.dumps(self.token_list, indent=2)}")
                else:
                    print("⚠️ WebSocket instance (self.sws) is not initialized!")
        except Exception as e:
            print(f"⚠️ Subscription failed: {e}")

    def on_close(self, ws):
        print("❌ WebSocket Closed")

    def on_error(self, ws, error):
        print("⚠️ WebSocket Error:", error)
