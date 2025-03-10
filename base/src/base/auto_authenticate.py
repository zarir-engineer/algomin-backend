# package import statement
from SmartApi import SmartConnect #or from smartapi.smartConnect import SmartConnect

import pyotp
from base.session import Session
from base import config as cnf
_session = Session()

#create object of call
obj=SmartConnect(api_key=cnf.API_KEY)

#login api call

data = obj.generateSession(cnf.CLIENT_ID, cnf.PASSWORD, pyotp.TOTP(cnf.TOTP).now())
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

