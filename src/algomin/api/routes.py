from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from pydantic import BaseModel
from src.algomin.brokers.order_client_factory import OrderClientFactory
from src.algomin.sessions.angelone_session import AngelOneSession
from src.algomin.config_loader import BrokerConfigLoader
from src.algomin.utils.order_builder import OrderBuilder

from src.algomin.web_socket_manager import WebSocketManager
from src.algomin.brokers.websocket_client_factory import WebSocketClientFactory

router = APIRouter()

class OrderRequest(BaseModel):
    tradingsymbol: str
    symboltoken: str
    transactiontype: str
    exchange: str
    ordertype: str
    quantity: int
    price: str = "0"
    squareoff: str = "0"
    stoploss: str = "0"
    producttype: str = "INTRADAY"
    duration: str = "DAY"
    variety: str = "NORMAL"
    is_exit: bool = False
    trailing_sl: bool = False

@router.get("/")
def root():
    return {"status": "ok"}


@router.post("/order/place")
def place_order(order: OrderRequest):
    builder = OrderBuilder(order.dict())
    valid, reason = builder.validate()
    if not valid:
        return {"status": "error", "reason": reason}

    config_loader = BrokerConfigLoader()
    credentials = config_loader.load_credentials()
    session = AngelOneSession(credentials)
    client = OrderClientFactory.create("smart_connect", session)

    clean_order = builder.build()
    return client.place_order(clean_order)


@router.get("/health")
def health_check():
    return {"status": "ok"}


@router.get("/ping")
def ping():
    return {"status": "ok", "message": "algomin backend is live"}


@router.websocket("/ws/stream")
async def stream_data(websocket: WebSocket, broker: str = "angel_one"):
    await websocket.accept()

    config_loader = BrokerConfigLoader()
    credentials = config_loader.load_credentials()
    session = AngelOneSession(credentials)  # in future, use broker condition

    ws_config = config_loader.load_websocket_config()
    ws_config["session"] = session

    client = WebSocketClientFactory.create(broker, ws_config)
    ws_manager = WebSocketManager(client)
    ws_manager.start()

    try:
        while True:
            data = await websocket.receive_json()
            action = data.get("action")
            symbol = data.get("symbol")

            if action == "subscribe":
                ws_manager.register(symbol, websocket)
            elif action == "unsubscribe":
                ws_manager.unregister(symbol, websocket)
    except WebSocketDisconnect:
        ws_manager.unregister_all(websocket)
