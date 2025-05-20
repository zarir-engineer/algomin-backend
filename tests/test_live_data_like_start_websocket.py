from sessions.angelone_session import AngelOneSession
from config_loader.broker_config_loader import BrokerConfigLoader
from brokers.angelone_websocket_client import AngelOneWebSocketV2Client
from brokers.WebSocketManager import WebSocketManager
from brokers.angelone_websocket_event_handler import AngelOneWebSocketEventHandler


def main():
    # Step 1: Load config
    config_loader = BrokerConfigLoader()
    credentials = config_loader.load_credentials()
    # get credentials for AngelOne and what instrument needs live data
    ws_config = config_loader.load_websocket_config()

    # Step 2: Optionally load strategies (skip for live tick test)
    strategies = []

    # Step 3: Start session
    session = AngelOneSession(credentials)

    # Step 4: Init WebSocket client
    retry_config = ws_config.get("retry", {})
    # ws_client = AngelOneWebSocketV2Client(
    #     session,
    #     max_retry_attempt=retry_config.get("max_attempt", 5),
    #     retry_strategy=retry_config.get("strategy", 2),
    #     retry_delay=retry_config.get("delay", 2),
    #     retry_multiplier=retry_config.get("multiplier", 2),
    #     retry_duration=retry_config.get("duration", 60)
    # )
    ws_manager = WebSocketManager(session)
    print('+++ ws client sws is_connected  ', ws_manager.ws_client)

    # Step 5: Init event handler
    event_handler = AngelOneWebSocketEventHandler(
        strategy_executor=None,
        correlation_id=ws_config.get("correlation_id", "sub_default"),
        mode=ws_config.get("mode", "full"),
        token_list=ws_config.get("subscriptions", []),
        sws=ws_manager.ws_client.sws
    )

    # Step 6: Attach callbacks
    ws_manager.ws_client.set_callbacks(
        event_handler.on_data,
        event_handler.on_open,
        event_handler.on_close,
        event_handler.on_error,
        event_handler.on_control_message
    )

    # Step 9: Connect and wait for ticks
    ws_manager.ws_client.connect()

    if hasattr(ws_manager.ws_client, "add_observer"):
        ws_manager.ws_client.add_observer(event_handler)

    if hasattr(ws_manager.ws_client, "start_heartbeat"):
        ws_manager.ws_client.start_heartbeat()

    if hasattr(ws_manager.ws_client, "sws"):
        ws_manager.ws_client.sws._ws.run_forever()
    else:
        ws_manager.ws_client.run_forever()
    # ws_manager.ws_client.sws._ws.run_forever()

if __name__ == "__main__":
    main()
