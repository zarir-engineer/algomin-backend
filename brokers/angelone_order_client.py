# brokers/angelone_order_client.py

import requests
from brokers.abstract_trading_client import AbstractOrderClient

class AngelOneOrderClient(AbstractOrderClient):
    def __init__(self, client_id, api_key, access_token, base_url):
        self.client_id = client_id
        self.api_key = api_key
        self.access_token = access_token
        self.base_url = base_url.rstrip("/")

        self.headers = {
            "Content-Type": "application/json",
            "X-PrivateKey": self.api_key,
            "X-SourceID": "WEB",
            "X-ClientLocalIP": "127.0.0.1",
            "X-ClientPublicIP": "127.0.0.1",
            "X-MACAddress": "00:00:00:00:00:00",
            "X-UserType": "USER",
            "Authorization": f"Bearer {self.access_token}"
        }

    def place_order(self, order_data: dict) -> dict:
        url = f"{self.base_url}/secure/angelbroking/order/v1/placeOrder"

        payload = {
            "variety": order_data.get("variety", "NORMAL"),
            "tradingsymbol": order_data["tradingsymbol"],
            "symboltoken": order_data["symboltoken"],
            "transactiontype": order_data["transactiontype"],
            "exchange": order_data["exchange"],
            "ordertype": order_data["ordertype"],
            "producttype": order_data.get("producttype", "INTRADAY"),
            "duration": order_data.get("duration", "DAY"),
            "price": order_data.get("price", "0"),
            "squareoff": order_data.get("squareoff", "0"),
            "stoploss": order_data.get("stoploss", "0"),
            "quantity": order_data["quantity"]
        }

        try:
            response = requests.post(url, json=payload, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {"error": str(e), "payload": payload}

    # Stubbed methods
    def modify_order(self, order_id: str, updated_data: dict) -> dict:
        raise NotImplementedError("Modify order not implemented")

    def cancel_order(self, order_id: str) -> dict:
        raise NotImplementedError("Cancel order not implemented")

    def get_order_book(self) -> list:
        raise NotImplementedError("Order book not implemented")

    def get_trade_book(self) -> list:
        raise NotImplementedError("Trade book not implemented")
