# brokers/order_client_factory.py

from brokers.angelone_order_client import AngelOneOrderClient
# from brokers.zerodha_order_client import ZerodhaOrderClient

class OrderClientFactory:
    @staticmethod
    def create(broker_name: str, auth_data: dict):
        if broker_name == "smart_connect":
            return AngelOneOrderClient(
                client_id=auth_data["client_id"],
                api_key=auth_data["api_key"],
                access_token=auth_data["access_token"],
                base_url=auth_data.get("base_url", "https://apiconnect.angelone.in/rest")
            )

        # elif broker_name == "zerodha":
        #     return ZerodhaOrderClient(...)

        else:
            raise ValueError(f"Unsupported broker: {broker_name}")

""" EXAMPLE USAGE

client = OrderClientFactory.create("smart_connect", {
    "client_id": "P123456",
    "api_key": "abcd1234",
    "access_token": "your-token",
})

order_response = client.place_order({
    "tradingsymbol": "INFY-EQ",
    "symboltoken": "1594",
    "transactiontype": "BUY",
    "exchange": "NSE",
    "ordertype": "MARKET",
    "producttype": "INTRADAY",
    "quantity": "1"
})

print(order_response)



"""