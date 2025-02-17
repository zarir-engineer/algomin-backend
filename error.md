Enter Order type (bostock/boderivative/market/Limit/StopLoss): bostock
Enter config type (bo_stock_data.yaml/bo_derivative_data.yaml): bo_stock_data.yaml
+++ order type :  bostock
+++ conf type :  bo_stock_data.yaml
[I 250217 18:41:14 smartConnect:124] in pool
Executing <class '__main__.BracketOrderStock'> with config /home/sinhurry/Documents/GitHub/algomin/live/src/data/bo_stock_data.yaml
[E 250217 18:41:14 smartConnect:246] Error occurred while making a POST request to https://apiconnect.angelone.in/rest/secure/angelbroking/order/v1/placeOrder. Error: Invalid symboltoken. URL: https://apiconnect.angelone.in/rest/secure/angelbroking/order/v1/placeOrder, Headers: {'Content-type': 'application/json', 'X-ClientLocalIP': '127.0.0.1', 'X-ClientPublicIP': '106.193.147.98', 'X-MACAddress': 'b5:60:10:30:ee:36', 'Accept': 'application/json', 'X-PrivateKey': 'liiHdetf', 'X-UserType': 'USER', 'X-SourceID': 'WEB'}, Request: {'ob.exchange': 'NSE', 'ob.producttype': 'INTRADAY', 'ob.duration': 'DAY', 'ob.ordertype': 'LIMIT', 'sp.tradingsymbol': 'RELIANCE', 'sp.symboltoken': 2885, 'sp.transactiontype': 'BUY', 'sp.quantity': 10, 'sp.price': 2500.0, 'sp.triggerprice': 2495.0, 'sp.squareoff': 20.0, 'sp.stoploss': 10.0, 'sp.trailingStopLoss': 5.0, 'sp.variety': 'STOPLOSS_BO'}, Response: {'message': 'Invalid symboltoken', 'errorcode': 'AB4006', 'status': False, 'data': None}
[E 250217 18:41:14 smartConnect:339] API request failed: {'message': 'Invalid symboltoken', 'errorcode': 'AB4006', 'status': False, 'data': None}
None
(.algomin) sinhurry@sinhurry-TUF-Gaming-FX505GM-FX505GM:~/Documents/GitHub/algomin$ 

