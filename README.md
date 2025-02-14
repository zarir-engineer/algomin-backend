# Algo_Test
> Installation
> 
> pip install SmartApi websocket-client pandas matplotlib plotly


#####TODO
>   Initialize WebSocket (SmartWebSocketV2)
    Subscribe to live data
    Process incoming data
    Plot live prices using Matplotlib

#### ✅ python -m unittest tests/test_session.py

#### ~~python3 -m tests.test_candle_data > results/test_candle_data_results.txt~~


##### ***TODO*** 

>Breaking up of EMA:
The previous close has to be below EMA and the close of this candle has to be above EMA.
So we take bullish trade on the open of the new candle


> Get current data. Also,
> * For a ONE_DAY interval , current data becomes history after 3:30 pm of current day
> * For a ONE_MINUTE interval, current data becomes history after a minute and likewise for ONE_HOUR and so on
> * All history is uploaded to database on cloud
> * * So Find a cloud which allows to host database for free
> * * What does work, docker and database as a microservice


##### Observer Pattern for live data

>   WebSocketObserver defines an interface for all observers.
    LoggerObserver logs every received message.
    AlertObserver triggers an alert if a certain price threshold is exceeded.


>   Manages WebSocket connection.
    Maintains a list of observers.
    Notifies observers whenever a message is received.

>   Runs ws.run_forever() inside a separate thread, allowing the main program to remain responsive.

##### Run the script

###### This implementation makes it easy to add new observers (e.g., a database logger) without modifying the core WebSocket handling logic.
> python websocket_observer.py
