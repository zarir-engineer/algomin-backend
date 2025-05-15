# smart_websocket_client.pya
from SmartApi.smartWebSocketV2 import SmartWebSocketV2
from brokers.base_websocket_client import BaseWebSocketClient
import threading
import time

from tests.test_live_data import on_control_message


class AngelOneWebSocketV2Client(BaseWebSocketClient):
    def __init__(self,
                 session,
                 max_retry_attempt,
                 retry_strategy,
                 retry_delay,
                 retry_multiplier,
                 retry_duration
                 ):

        self.session = session
        auth_info = self.session.get_auth_info()
        self.max_retry_attempt = max_retry_attempt
        self.retry_strategy = retry_strategy
        self.retry_delay = retry_delay
        self.retry_multiplier = retry_multiplier
        self.retry_duration = retry_duration


        self.auth_token = auth_info["auth_token"]
        self.feed_token = auth_info["feed_token"]
        self.api_key = auth_info["api_key"]
        self.client_id = auth_info["client_id"]

        self.sws = SmartWebSocketV2(
            self.auth_token,
            self.api_key,
            self.client_id,
            self.feed_token,
            self.max_retry_attempt,
            self.retry_strategy,
            self.retry_delay,
            self.retry_multiplier,
            self.retry_duration
        )
        self.lock = threading.Lock()
        self.correlation_id = f"subscription_{int(time.time())}"
        self.mode = "full"
        self.token_list = []

    def set_callbacks(self, on_data, on_open, on_close, on_error, on_control_message):
        self.sws.on_data = on_data
        self.sws.on_open = on_open
        self.sws.on_close = on_close
        self.sws.on_error = on_error
        self.sws.on_control_message = on_control_message

    def connect(self):
        self.sws.connect()

    def subscribe(self, correlation_id: str, mode: str, token_list: list):
        self.correlation_id = correlation_id
        self.mode = mode
        self.token_list = token_list
        print(f'+++ subscribe to : {token_list}')
        self.sws.subscribe(
            correlation_id=self.correlation_id,
            mode=self.mode,
            token_list=self.token_list
        )

    def run_forever(self):
        if self.sws and self.sws._ws:
            self.sws._ws.run_forever()

    # def run_forever(self):
    #     pass

    def close(self):
        self.sws.close_connection()
