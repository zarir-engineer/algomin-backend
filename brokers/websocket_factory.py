# brokers/websocket_factory.py

from brokers.smart_websocket_client import SmartWebSocketV2Client
# from brokers.zerodha_websocket_client import ZerodhaWebSocketClient

class WebSocketClientFactory:
    @staticmethod
    def create(broker_name: str, auth_data: dict):
        if broker_name == "smart_connect":
            return SmartWebSocketV2Client(
                auth_token=auth_data["auth_token"],
                api_key=auth_data["api_key"],
                client_id=auth_data["client_id"],
                feed_token=auth_data["feed_token"]
            )
        # elif broker == "zerodha":
        #     return ZerodhaWebSocketClient(...)
        else:
            raise ValueError(f"Unsupported broker: {broker_name}")