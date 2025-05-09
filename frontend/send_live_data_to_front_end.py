"""
✅ Live Price Updates (LTP) & EMA Calculation
✅ WebSocket Connection Between Python & Next.js
✅ Dynamic Real-Time Chart with recharts
✅ Auto-Refresh & Smooth Transitions

✅ Decouples logic: New features (email alerts, stop-loss, chart updates) don’t modify the core WebSocket logic.
✅ Easier to extend: You can add/remove observers dynamically.
✅ Modular structure: Each observer handles its own task (alerts, logging, visualization, etc.).
"""
import asyncio
import websockets
import json
import numpy as np
import pandas as pd

#TODO import from ema

async def send_live_data(websocket, path):
    global price_data
    while True:
        ltp = np.random.uniform(100, 200)  # Simulated live price
        price_data.append(ltp)

        if len(price_data) > window_size:
            ema = pd.Series(price_data).ewm(span=window_size, adjust=False).mean().iloc[-1]
        else:
            ema = ltp  # Use LTP as EMA initially

        # Prepare JSON Data
        data = {
            "timestamp": pd.Timestamp.now().strftime("%H:%M:%S"),
            "ltp": round(ltp, 2),
            "ema": round(ema, 2)
        }

        # Send JSON Data to Frontend
        await websocket.send(json.dumps(data))
        await asyncio.sleep(1)  # Send data every second

# Start WebSocket Server
start_server = websockets.serve(send_live_data, "0.0.0.0", 8000)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
