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

| Principle | How it's followed                                      |
| --------- | ------------------------------------------------------ |
| SRP       | Each client class handles only its own API logic       |
| OCP       | New brokers can be added without changing order logic  |
| DIP       | Strategies depend on the abstract base, not the broker |
| Testable  | Easy to stub/mock `BaseTradingClient` in tests         |

'''

# start_websocket.py
from config_loader.broker_config_loader import BrokerConfigLoader
from sessions.angelone_session import AngelOneSession
from brokers.angelone_websocket_client import AngelOneWebSocketV2Client
from strategy_loader.yaml_strategy_loader import YAMLStrategyLoader
from brokers.angelone_trading_client import AngelOneConnectClient
from brokers.angelone_websocket_event_handler import AngelOneWebSocketEventHandler
from core.strategy_executor import StrategyExecutor


def main():
    # Step 1: Load config
    config_loader = BrokerConfigLoader()
    credentials = config_loader.load_credentials()
    ws_config = config_loader.load_ws_config()
    # Step 2: Load strategies
    strategy_loader = YAMLStrategyLoader()
    strategies = strategy_loader.load_strategies("data/strategies.yaml")
    print("📊 Loaded Strategies:", strategies)

    # Step 3: Start session
    session = AngelOneSession(credentials)

    # Step 4: Init trading client
    trading_client = AngelOneConnectClient(session)
    print("✅ Trading client ready")

    # Step 5: Init strategy executor
    strategy_executor = StrategyExecutor(strategies, trading_client)

    # Step 6: Init WebSocket client
    ws_client = AngelOneWebSocketV2Client(session)

    # Step 7: Init event handler
    event_handler = AngelOneWebSocketEventHandler(strategy_executor,
                                                  ws_client,
                                                  ws_config.get("correlation_id", "sub_default"),
                                                  ws_config.get("mode", "full"),
                                                  ws_config.get("subscriptions", [])
                                                  )

    ws_client.set_callbacks(
        event_handler.on_data,
        event_handler.on_open,
        event_handler.on_close,
        event_handler.on_error
    )

    # Step 8: Subscribe and start
    ws_client.connect()
    ws_client.subscribe(
        correlation_id=ws_config.get("correlation_id", "sub_default"),
        mode=ws_config.get("mode", "full"),
        token_list=ws_config.get("subscriptions", [])
    )
    ws_client.run_forever()


if __name__ == "__main__":
    main()
