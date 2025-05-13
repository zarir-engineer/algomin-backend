from SmartApi import SmartConnect
import pyotp
import yaml

class AngelOneSession:
    def __init__(self, config_path="config_loader/common.yaml"):
        with open(config_path) as f:
            config = yaml.safe_load(f).get("smart_connect", {})

        self.api_key = config["api_key"]
        self.client_id = config["client_id"]
        self.password = config["password"]
        self.totp_secret = config["totp_secret"]

        self.api = SmartConnect(api_key=self.api_key)
        self.login()

    def login(self):
        totp = pyotp.TOTP(self.totp_secret).now()
        data = self.smart_api.generateSession(self.client_id, self.password, totp)
        self.feed_token = data["data"]["feedToken"]
        self.access_token = data["data"]["access_token"]

    def get_auth_info(self):
        return {
            "auth_token": self.auth_token,
            "feed_token": self.feed_token,
            "api_key": self.api_key,
            "client_id": self.client_id
        }
