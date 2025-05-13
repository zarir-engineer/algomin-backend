from SmartApi.smartConnect import SmartConnect
from utils.config_loader import ConfigLoader
import pyotp

class AngelOneSession:
    _instance = None  # Singleton instance

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AngelOneSession, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        self.config = ConfigLoader()
        self.api_key = self.config.get("api.api_key")
        self.client_id = self.config.get("user.client_id")
        self.password = self.config.get("user.password")
        totp_secret = self.config.get("user.totp_secret")
        # Initialize TOTP instance
        self.totp = pyotp.TOTP(totp_secret).now()

        self.smart_api = SmartConnect(api_key=self.api_key)
        self.auth_token = None
        self.feed_token = None

        self.generate_tokens()

    def generate_tokens(self):
        data = self.smart_api.generateSession(self.client_id, self.password, self.totp)
        if "status" in data and data["status"]:
            self.auth_token = data["data"]["jwtToken"]
            self.feed_token = self.smart_api.getfeedToken()
            print("✅ Auth Token & Feed Token Generated!")
        else:
            raise Exception("❌ Failed to generate tokens")

    def get_auth_info(self):
        return {
            "auth_token": self.auth_token,
            "feed_token": self.feed_token,
            "api_key": self.api_key,
            "client_id": self.client_id
        }

    def get_api(self):
        return self.smart_api  # For placing orders etc.
