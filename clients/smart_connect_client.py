import yaml
from pathlib import Path
from SmartApi import SmartConnect
from orders.order_factory import OrderFactory



class SmartConnectClient:
    def __init__(self, config_path="data/config.yaml"):
        self.config = self.load_config(config_path)
        self.smart_api = SmartConnect(api_key=self.config['api_key'])

        self.login()

    def load_config(self, config_path):
        config_path = Path(config_path)
        if not config_path.is_absolute():
            base_dir = Path(__file__).resolve().parent.parent
            config_path = base_dir / config_path

        with open(config_path, 'r') as f:
            data = yaml.safe_load(f)
        return data.get('smart_connect', {})

    def login(self):
        client_id = self.config['client_id']
        password = self.config['password']
        totp = self.generate_totp(self.config['totp_secret'])

        data = self.smart_api.generateSession(client_id, password, totp)
        self.auth_token = data['data']['access_token']

    def generate_totp(self, secret):
        import pyotp
        return pyotp.TOTP(secret).now()

    def place_order(self, order_params: dict):
        # connect to broker SDK here
        print("Placing order with params:", order_params)
        # return smartApi.placeOrder(order_params)

    def place_strategy_order(self, strategy_config):
        strategy = OrderFactory.get_order_strategy(strategy_config["order_type"])
        order_params = strategy.build_order_params(strategy_config)
        return self.place_order(order_params)

    def get_holdings(self):
        return self.smart_api.holdings()

    def get_order_book(self):
        return self.smart_api.orderBook()

    def get_positions(self):
        return self.smart_api.position()

    def modify_order(self): pass

    def cancel_order(self): pass

