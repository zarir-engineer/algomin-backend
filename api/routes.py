from fastapi import APIRouter

router = APIRouter()

from pydantic import BaseModel
from brokers.order_client_factory import OrderClientFactory
from sessions.angelone_session import AngelOneSession
from config_loader.broker_config_loader import BrokerConfigLoader
from utils.order_builder import OrderBuilder

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

