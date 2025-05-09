from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from core.websocket_client import SmartWebSocketV2Client
from base.observer.ema import EMAObserver
from base.observer.chart import ChartObserver

router = APIRouter()
ws_client = None  # global-like reference


@router.get("/start")
def start_websocket():
    global ws_client
    if ws_client:
        return {"status": "already running"}

    ws_client = SmartWebSocketV2Client()
    ws_client.load_ws_config()

    ws_client.add_observer(EMAObserver(period=10))
    ws_client.add_observer(ChartObserver())

    # You can run it in a thread or async task
    import threading
    thread = threading.Thread(target=ws_client.start_websocket, daemon=True)
    thread.start()

    return {"status": "started"}


@router.get("/stop")
def stop_websocket():
    global ws_client
    if ws_client:
        ws_client.stop()
        ws_client = None
        return {"status": "stopped"}
    return {"status": "not running"}


@router.websocket("/ws/stream")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            # Send dummy or real data
            await websocket.send_text("ping")
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        print("WebSocket disconnected")
