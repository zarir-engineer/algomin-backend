# brokers/smart_event_handler.py
from logzero import logger
import json

class AngelOneWebSocketEventHandler:
    def __init__(self, strategy_executor, ws_client=None, correlation_id=None, mode=None, token_list=None):
        self.strategy_executor = strategy_executor
        self.ws_client = ws_client  # optional
        self.correlation_id = correlation_id
        self.mode = mode
        self.token_list = token_list

    def on_data(self, ws, message):
        logger.info("Ticks: {}".format(message))
        self.close_connection()

        # print("📩 TICK:", message)
        # try:
        #     tick_data = json.loads(message)
        #     print("🔍 Parsed Tick:", tick_data)
        #     self.strategy_executor.evaluate(tick_data)
        # except json.JSONDecodeError:
        #     print("⚠️ Received non-JSON message:", message)
        # except Exception as e:
        #     print(f"⚠️ Error in on_data: {e}")

    def on_open(self, ws):
        print("✅ WebSocket Opened")
        logger.info("on open")
        some_error_condition = False
        if some_error_condition:
            error_message = "Simulated error"
            if hasattr(ws, 'on_error'):
                ws.on_error("Custom Error Type", error_message)
        else:
            self.ws_client.subscribe(self.correlation_id, self.mode, self.token_list)
            # sws.unsubscribe(correlation_id, mode, token_list1)

    def on_close(self, ws): print("❌ WebSocket Closed")
    def on_error(self, ws, error): print("⚠️ WebSocket Error:", error)

    def close_connection(self):
        if self.ws_client:
            self.ws_client.close()
