import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from utils.ws_config_loader import ConfigLoader
from brokers.angelone_websocket_client import AngelOneWebSocketV2Client
from observer.ema import EMAObserver
from observer.chart import ChartObserver
from utils.loader_factory import get_loader
from observer.limit_order_trigger import LimitOrderTriggerObserver


router = APIRouter()
ws_client = None  # global-like reference


@router.get("/start")
def start_websocket():
    global ws_client
    if ws_client:
        return {"status": "already running"}

    ws_client = AngelOneWebSocketV2Client.from_config()
    ws_client.load_ws_config()  # Needed to load mode, token_list, etc.


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


@router.post("/start-limit-observers/")
def start_limit_observers():
    config = ConfigLoader("config_loader/common.yaml")
    source = config.get("data_source")
    loader = get_loader(source["type"], source["path"])
    strategies = loader.load().get("limit_order_strategies", [])

    ws_client = AngelOneWebSocketV2Client()

    for strat in strategies:
        observer = LimitOrderTriggerObserver(
            symbol_token=strat["symbol_token"],
            tradingsymbol=strat["tradingsymbol"],
            target_price=strat["target_price"],
            quantity=strat["quantity"],
            order_type=strat["order_type"]
        )
        ws_client.add_observer(observer)

    ws_client.start_websocket()
    return {"status": "WebSocket and observers started."}
