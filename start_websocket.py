from sessions.angelone_session import AngelOneSession
from config_loader.broker_config_loader import BrokerConfigLoader
from brokers.angelone_websocket_event_handler import AngelOneWebSocketEventHandler
from brokers.websocket_client_factory import WebSocketClientFactory
from web_socket_manager import WebSocketManager


def main():
    # Step 1: Load config
    config_loader = BrokerConfigLoader()
    credentials = config_loader.load_credentials()
    ws_config = config_loader.load_websocket_config()

    # Step 2: Optionally load strategies (skip for live tick test)
    strategies = []

    # Step 3: Start session
    session = AngelOneSession(credentials)

    # Step 4: Init WebSocket client
    ws_config["session"] = session
    client = WebSocketClientFactory.create("angel_one", ws_config)

    # Step 5: Init WebSocket manager
    retry_config = ws_config.get("retry_config", {})
    ws_manager = WebSocketManager(client, retry_config)

    # Step 6: Init event handler
    event_handler = AngelOneWebSocketEventHandler(
        strategy_executor=None,
        correlation_id=ws_config.get("correlation_id", "sub_default"),
        mode=ws_config.get("mode", "full"),
        token_list=ws_config.get("subscriptions", []),
        sws=ws_manager.ws_client.sws,
        ws_manager=ws_manager  # inject manager for tick streaming
    )

    # Step 7: Attach callbacks
    ws_manager.ws_client.set_callbacks(
        event_handler.on_data,
        event_handler.on_open,
        event_handler.on_close,
        event_handler.on_error,
        event_handler.on_control_message
    )

    # Step 8: Start WebSocket
    ws_manager.start()


if __name__ == "__main__":
    main()
