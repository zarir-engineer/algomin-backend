# brokers/websocket_factory.py

from brokers.angelone_websocket_client import AngelOneWebSocketV2Client
# from brokers.zerodha_websocket_client import ZerodhaWebSocketClient

class WebSocketClientFactory:
    @staticmethod
    def create(broker_name: str, auth_data: dict):
        if broker_name == "smart_connect":
            retry_config = auth_data.get("retry_config", {})

            return AngelOneWebSocketV2Client(
                session=auth_data["session"],
                max_retry_attempt=retry_config.get("max_attempt", 3),
                retry_strategy=retry_config.get("strategy", 1),
                retry_delay=retry_config.get("delay", 5),
                retry_multiplier=retry_config.get("multiplier", 2),
                retry_duration=retry_config.get("duration", 30)
            )

        # elif broker_name == "zerodha":
        #     return ZerodhaWebSocketClient(...)

        else:
            raise ValueError(f"Unsupported broker: {broker_name}")

"""
# EXAMPLE USAGE


client = WebSocketClientFactory.create("smart_connect", {
    "session": angelone_session,
    "retry_config": {
        "max_attempt": 5,
        "strategy": 2,
        "delay": 3,
        "multiplier": 2,
        "duration": 60
    }
})

BROKER_CLIENTS = {
    "smart_connect": AngelOneWebSocketV2Client,
    "zerodha": ZerodhaWebSocketClient
}
"""