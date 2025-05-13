'''

Component	                                      Role
AngelOneSession	                                Handles login + get_auth_info()
SmartWebSocketV2Client	                        Broker-specific client using session
from_config()	                                  External YAML loader (not tied to class logic)
start_websocket.py	                            Entry point to plug it all together

| Advantage            | Why it matters                                           |
| -------------------- | -------------------------------------------------------- |
| 🔁 **Pluggable**     | Each broker can define its own handler style             |
| 🔧 **Maintainable**  | No `if/else` or dynamic binding in the main script       |
| 🔐 **SOLID-aligned** | Open for extension, closed for modification              |
| 🧪 **Testable**      | You can mock or stub event handlers easily in unit tests |


'''

# start_websocket.py
from config_loader.broker_config_loader import BrokerConfigLoader
from sessions.angelone_session import AngelOneSession
from brokers.smart_websocket_client import SmartWebSocketV2Client
from strategy_loader.yaml_strategy_loader import YAMLStrategyLoader
from brokers.smart_event_handler import SmartWebSocketEventHandler

def main():
    # Step 1: Load config
    config_loader = BrokerConfigLoader()
    credentials = config_loader.load_credentials()
    ws_config = config_loader.load_ws_config()

    # Step 2: Load strategies (optional for now)
    strategy_loader = YAMLStrategyLoader()
    strategies = strategy_loader.load_strategies("config/strategies.yaml")
    print("📊 Loaded Strategies:", strategies)

    # Step 3: Start session
    session = AngelOneSession(credentials)

    # Step 4: Init WebSocket Client
    ws_client = SmartWebSocketV2Client(session)
    event_handler = SmartWebSocketEventHandler()
    ws_client.set_callbacks(
        event_handler.on_data,
        event_handler.on_open,
        event_handler.on_close,
        event_handler.on_error
    )

    # Step 5: Subscribe to market data
    ws_client.connect()
    ws_client.subscribe(
        correlation_id=ws_config.get("correlation_id", "sub_default"),
        mode=ws_config.get("mode", "full"),
        token_list=ws_config.get("subscriptions", [])
    )

    # Step 6: Run WebSocket forever
    ws_client.run_forever()


if __name__ == "__main__":
    main()
