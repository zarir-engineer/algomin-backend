# system modules

from SmartApi.smartConnect import SmartConnect
from config_loader import ConfigLoader  # Load from config.yml


class AngelOneSession:
    def __init__(self):
        self.config = ConfigLoader()
        self.api_key = self.config.get("api.api_key")
        self.client_id = self.config.get("user.client_id")
        self.password = self.config.get("user.password")
        self.totp = self.config.get("user.totp")

        self.auth_token = None
        self.feed_token = None

    def generate_tokens(self):
        """Login to Angel One SmartAPI and generate tokens dynamically."""
        obj = SmartConnect(api_key=self.api_key)

        data = obj.generateSession(self.client_id, self.password, self.totp)

        if "status" in data and data["status"] == True:
            self.auth_token = data["data"]["jwtToken"]
            self.feed_token = obj.getfeedToken()
            print("✅ Auth Token & Feed Token Generated!")
        else:
            raise Exception("⚠️ Failed to generate tokens. Check login credentials!")

        return self.auth_token, self.feed_token
