import pyotp
from logzero import logger
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
        self.refresh_token = None
        self.login()

    def login(self):
        data = self.api.generateSession(self.client_id, self.password, self.totp)
        if data['status'] == False:
            logger.error(data)
        else:
            # logger.info(f"+++ data: {data}")
            self.auth_token = data["data"]["jwtToken"]
            self.refresh_token = data['data']['refreshToken']
            self.feed_token = self.api.getfeedToken()
            # logger.info(f" +++ from api Feed-Token :{self.feed_token}")
            res = self.api.getProfile(self.refresh_token)
            # logger.info(f"+++ from api Get Profile: {res}")
            self.api.generateToken(self.refresh_token)
            res=res['data']['exchanges']
            # logger.info(f"+++ from api res data exchanges : {res}")


    def get_auth_info(self):
        return {
            "auth_token": self.auth_token,
            "feed_token": self.feed_token,
            "refresh_token": self.refresh_token,
            "api_key": self.api_key,
            "client_id": self.client_id
        }
