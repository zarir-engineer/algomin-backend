import pyotp

from SmartApi import SmartConnect

class AngelOneSession:
    def __init__(self, credentials):
        self.api_key = credentials["api_key"]
        self.client_id = credentials["client_id"]
        self.password = credentials["password"]
        _totp_secret = credentials["totp_secret"]
        self.totp = pyotp.TOTP(_totp_secret).now()
        self.api = SmartConnect(api_key=self.api_key)

        self.auth_token = None
        self.feed_token = None

        self.login()

    def login(self):
        data = self.api.generateSession(self.client_id, self.password, self.totp)
        self.auth_token = data["data"]["jwtToken"]
        self.feed_token = data["data"]["feedToken"]
        # self.access_token = data["data"]["access_token"]

    def get_auth_info(self):
        return {
            "auth_token": self.auth_token,
            "feed_token": self.feed_token,
            "api_key": self.api_key,
            "client_id": self.client_id
        }
