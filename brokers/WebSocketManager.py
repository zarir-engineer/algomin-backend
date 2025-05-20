import time
import threading
import logging

from brokers.angelone_websocket_client import AngelOneWebSocketV2Client
# Optional: configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WebSocketManager:
    def __init__(self, session, retry_config=None, heartbeat_interval=15):
        self.retry_config = retry_config or {
            "max_attempt": 5,
            "strategy": 2,
            "delay": 1,
            "multiplier": 2,
            "duration": 60
        }
        self.heartbeat_interval = heartbeat_interval
        self.session = session
        self.ws_client = None
        self._stop_flag = threading.Event()
        self._watchdog_thread = threading.Thread(target=self._watchdog_loop, daemon=True)

    def start(self):
        logger.info("Starting WebSocket client...")
        self._connect_with_retry()
        self._watchdog_thread.start()

    def _connect_with_retry(self):
        attempt = 0
        delay = self.retry_config["delay"]
        start_time = time.time()

        while attempt < self.retry_config["max_attempt"]:
            try:
                logger.info(f"Connecting (Attempt {attempt + 1})...")
                self.ws_client = AngelOneWebSocketV2Client(
                    self.session,
                    max_retry_attempt=self.retry_config["max_attempt"],
                    retry_strategy=self.retry_config["strategy"],
                    retry_delay=self.retry_config["delay"],
                    retry_multiplier=self.retry_config["multiplier"],
                    retry_duration=self.retry_config["duration"]
                )
                self.ws_client.connect()
                logger.info("WebSocket connection established.")
                return
            except Exception as e:
                logger.warning(f"Connection attempt {attempt + 1} failed: {e}")
                attempt += 1
                time.sleep(delay)
                if self.retry_config["strategy"] == 2:  # Exponential backoff
                    delay *= self.retry_config["multiplier"]
                if time.time() - start_time > self.retry_config["duration"]:
                    logger.error("Retry duration exceeded. Giving up.")
                    break

    def _watchdog_loop(self):
        while not self._stop_flag.is_set():
            try:
                if not self.ws_client or not self.ws_client.is_connected():
                    logger.warning("WebSocket disconnected. Reconnecting...")
                    self._connect_with_retry()
            except Exception as e:
                logger.error(f"Watchdog check failed: {e}")
            time.sleep(self.heartbeat_interval)

    def stop(self):
        self._stop_flag.set()
        if self.ws_client:
            try:
                self.ws_client.disconnect()
                logger.info("WebSocket disconnected cleanly.")
            except Exception as e:
                logger.warning(f"Error while disconnecting: {e}")

    def subscribe(self, instruments):
        if self.ws_client and self.ws_client.is_connected():
            self.ws_client.subscribe(instruments)
        else:
            logger.warning("Cannot subscribe. WebSocket not connected.")

    def is_connected(self):
        return self.ws_client and self.ws_client.is_connected()
