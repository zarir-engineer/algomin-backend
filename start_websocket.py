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
from sessions.angelone_session import AngelOneSession
from config_loader.broker_config_loader import BrokerConfigLoader
from brokers.angelone_websocket_client import AngelOneWebSocketV2Client
from brokers.angelone_websocket_event_handler import AngelOneWebSocketEventHandler


def main():
    # Step 1: Load config
    config_loader = BrokerConfigLoader()
    credentials = config_loader.load_credentials()
    # get credentials for AngelOne and what instrument needs live data
    ws_config = config_loader.load_ws_config()

    # Step 2: Optionally load strategies (skip for live tick test)
    strategies = []

    # Step 3: Start session
    session = AngelOneSession(credentials)

    # Step 6: Init WebSocket client
    retry_config = ws_config.get("websocket.retry", {})
    ws_client = AngelOneWebSocketV2Client(
        session,
        max_retry_attempt=retry_config.get("max_attempt", 3),
        retry_strategy=retry_config.get("strategy", 1),
        retry_delay=retry_config.get("delay", 5),
        retry_multiplier=retry_config.get("multiplier", 2),
        retry_duration=retry_config.get("duration", 30)
    )


    # Step 7: Init event handler
    event_handler = AngelOneWebSocketEventHandler(
        strategy_executor=None,
        correlation_id=ws_config.get("correlation_id", "sub_default"),
        mode=ws_config.get("mode", "full"),
        token_list=ws_config.get("subscriptions", []),
        sws=ws_client.sws
    )

    # Step 8: Attach callbacks
    ws_client.set_callbacks(
        event_handler.on_data,
        event_handler.on_open,
        event_handler.on_close,
        event_handler.on_error,
        event_handler.on_control_message
    )

    # Step 9: Connect and wait for ticks
    ws_client.connect()

    if hasattr(ws_client, "add_observer"):
        ws_client.add_observer(event_handler)

    if hasattr(ws_client, "start_heartbeat"):
        ws_client.start_heartbeat()

    ws_client.run_forever()
    # ws_client.sws._ws.run_forever()

if __name__ == "__main__":
    main()
