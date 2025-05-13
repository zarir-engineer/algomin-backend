# brokers/smart_trading_client.py

from brokers.base_trading_client import BaseTradingClient
from SmartApi import SmartConnect

class AngelOneConnectClient(BaseTradingClient):
    def __init__(self, session):
        self.api = session.api

    def place_order(self, order_data: dict):
        return self.api.placeOrder(order_data)

    def cancel_order(self, order_id: str):
        return self.api.cancelOrder({"orderid": order_id})

    def modify_order(self, order_id: str, changes: dict):
        data = {"orderid": order_id}
        data.update(changes)
        return self.api.modifyOrder(data)

    def get_positions(self):
        return self.api.position()

    def get_holdings(self):
        return self.api.holdings()
