# package import statement
from SmartApi import SmartConnect #or from smartapi.smartConnect import SmartConnect

import pyotp
from src.session import Session

_session = Session()

#create object of call
obj=SmartConnect(api_key=apikey)

#login api call

data = obj.generateSession(username, pwd, pyotp.TOTP(token).now())
#cls
# print (data)
refreshToken= data['data']['refreshToken']
AUTH_TOKEN = data['data']['jwtToken']

#fetch the feedtoken
FEED_TOKEN =obj.getfeedToken()
#print ("Feed Token: "+FEED_TOKEN)

#fetch User Profile
res= obj.getProfile(refreshToken)
print(res['data']['exchanges'])

