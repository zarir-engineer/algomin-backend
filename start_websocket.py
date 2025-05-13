from observer.limit_order_trigger import LimitOrderTriggerObserver
from clients.websocket_client import SmartWebSocketV2Client
from utils.config_loader import ConfigLoader
from utils.loader_factory import get_loader  # optional helper

def load_limit_order_strategies():
    config = ConfigLoader("config/common.yaml")
    data_source = config.get("data_source")
    loader = get_loader(data_source["type"], data_source["path"])
    data = loader.load()
    return data.get("limit_order_strategies", [])

def main():
    ws_client = SmartWebSocketV2Client.from_config()
    strategies = load_limit_order_strategies()
    for strat in strategies:
        observer = LimitOrderTriggerObserver(
            symbol_token=strat["symbol_token"],
            tradingsymbol=strat["tradingsymbol"],
            target_price=strat["target_price"],
            quantity=strat["quantity"],
            order_type=strat["order_type"]
        )
        ws_client.add_observer(observer)

    ws_client.start_websocket()

if __name__ == "__main__":
    main()
