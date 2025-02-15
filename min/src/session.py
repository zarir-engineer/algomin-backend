# modules
from SmartApi.smartConnect import SmartConnect
import pyotp

# credentials
from src import config as cnf


class Session:

    def __init__(self):
        self.init()

    def init(self):
        _totp = pyotp.TOTP(cnf.TOTP)
        _totp = _totp.now()
        self.smart_api = SmartConnect(api_key=cnf.API_KEY)
        self.login_response = self.smart_api.generateSession(cnf.CLIENT_ID, cnf.PASSWORD, totp=_totp)

    def auth_token(self):
        if self.login_response.get("status"):
            _auth_token = self.login_response["data"]["jwtToken"]
            # print(f"Auth Token: {_auth_token}")
            return _auth_token

    def refresh_token(self):
        if self.login_response.get("status"):
            _refresh_token = self.login_response["data"]["refreshToken"]
            print(f"Refresh Token: {_refresh_token}")
            return _refresh_token

    def feed_token(self):
        return self.smart_api.getfeedToken()
